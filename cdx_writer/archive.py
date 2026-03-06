"""
Augments Warctools with features needed for genrating CDX from real-world
web archive files. When we're convinced these modification are good for wider
audiences, submit patch to Warctools.

Historically, these modifications were once implemented as local Warctool
modifications. Unfortunately major changes to Warctool after the fork made those
changes very difficult to merge. Here we reimplement them as runtime patches.

As this module monkey-patches hanzo.warctools modules upon import, all access to
hanzo.warctools shall be made after importing this module.
"""
from __future__ import unicode_literals, print_function

import io
import sys
import re
import struct
import hanzo
import zlib
from hanzo.warctools import ArchiveRecord
from hanzo.warctools.stream import open_record_stream as _open_record_stream

from hanzo.warctools.arc import SPLIT, ArcParser, ArcRecord
from hanzo.warctools.warc import WarcRecord
from hanzo.warctools.stream import RecordStream, GeeZipFile, GzipRecordStream

try:
    from .zstdstream import ZstdRecordStream, get_zstd_dictionary
except ImportError:
    ZstdRecordStream = None

ARC_HEADER_V1 = [ArcRecord.URL, ArcRecord.IP, ArcRecord.DATE, ArcRecord.CONTENT_TYPE,
                 ArcRecord.CONTENT_LENGTH]

class RecordParseError(Exception):
    pass

ARC_HEADER_FIELDS = {
    ArcRecord.URL: br"([a-z]+:.*)",
    # some IP-Address field has hostname
    ArcRecord.IP: br"((?:\d{1,3}\.){3}\d{1,3}|)",
    # some timestamps have more or less digits than 14
    ArcRecord.DATE: br"(\d{12,16})",
    ArcRecord.CONTENT_TYPE: br"(\S+)(?:;\s*\S+)*",
    ArcRecord.CONTENT_LENGTH: br"(\d+)",
    ArcRecord.RESULT_CODE: br"(\d{3})",
    ArcRecord.CHECKSUM: br"(\S+)",
    # many redirect URLs contain white spaces
    ArcRecord.LOCATION: br"(-|[a-z]+:\S.*)",
    ArcRecord.OFFSET: br"(\d+)",
    # filename often contains spaces
    ArcRecord.FILENAME: br"(\S[\S ]*\S)"
}

RE_DATE = re.compile(ARC_HEADER_FIELDS[ArcRecord.DATE] + b'$')
RE_IP = re.compile(ARC_HEADER_FIELDS[ArcRecord.IP] + b'$')

def F(spec):
    fields = [getattr(ArcRecord, a) for a in spec.split()]
    regex = re.compile(
        b" ".join(ARC_HEADER_FIELDS[f] for f in fields) + b"$"
    )
    return fields, regex

ARC_HEADER_FORMATS = [
    # standard v1 header
    F("URL IP DATE CONTENT_TYPE CONTENT_LENGTH"),
    # standard v2 header
    F("URL IP DATE CONTENT_TYPE RESULT_CODE CHECKSUM LOCATION OFFSET FILENAME CONTENT_LENGTH"),
    # some Alexa ARC files have only 4 fields for v1, missing Content-Type
    F("URL IP DATE CONTENT_LENGTH"),
]

class PatchedArcParser(ArcParser):
    def __init__(self):
        self.version = 1
        self.headers = ARC_HEADER_V1

    def parse_header_list(self, line):
        """replaces ArcParser.parse_header_list to support
        unusual ARC header.
        """
        line = line.rstrip(b'\r\n')
        values = SPLIT(line)
        headers = self.headers
        if len(values) == len(headers):
            header_dict = dict(zip(headers, values))
            # some old Alexa ARC files have IP-Address and Date field transposed in ARC header.register_record_type
            # see small_warcs/transposed_header.arc.gz
            date = header_dict.get(ArcRecord.DATE, '')
            ip = header_dict.get(ArcRecord.IP, '')
            if (RE_IP.match(date) and RE_DATE.match(ip)):
                header_dict[ArcRecord.DATE] = ip
                header_dict[ArcRecord.IP] = date

            return header_dict.items()

        for headers, regex in ARC_HEADER_FORMATS:
            m = regex.match(line)
            if m:
                values = m.groups()
                return list(zip(headers, values))

        raise Exception('Malformed ARC header: %r does not match declared %r'
                        % (line, b" ".join(self.headers)))
        # if len(values) > len(headers):
        #     # line has more fields than declared - following is copy of warctools 4.10 code.
        #     if self.headers[0] in (ArcRecord.URL, ArcRecord.CONTENT_TYPE):
        #         # guess URL or Content-type field has stray space
        #         values = [s[::-1] for s in reversed(SPLIT(line[::-1], len(headers) - 1))]
        #     else:
        #         # leave extra fields in the last item
        #         values = SPLIT(line, len(headers) - 1)
        # elif len(values) < len(headers):
        #     if len(values) == 5:
        #         # 1. some ARC writes out v1 header while declaring v2 header in filedesc.
        #         headers = ARC_HEADER_V1
        #     elif len(values) == 4:
        #         # 2. some Alexa ARC files have just 4 fields, missing Content-Type.
        #         headers = [ArcRecord.URL, ArcRecord.IP, ArcRecord.DATE, ArcRecord.CONTENT_LENGTH]

        # if len(headers) != len(values):
        #     raise Exception('ARC header %s does not match declared %s',
        #                     ",".join(values), ",".join(self.headers))

        # # 3. some old Alexa ARC files have IP-Address and Date field transposed in ARC header
        # # see small_warcs/transposed_header.arc.gz
        # if len(values) == 5:
        #     if RE_DATE.match(values[1]) and RE_IP.match(values[2]):
        #         values[1:3] = values[2:0:-1]

        # return list(zip(headers, values))

hanzo.warctools.arc.ArcParser = PatchedArcParser

class GzipMemberFile(io.RawIOBase):
    def __init__(self, raw_fh):
        self.raw_fh = raw_fh
        self.member_offset = raw_fh.tell()
        self.at_eom = False
        self._decomp = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
        self._buf = b''
        self._crc = zlib.crc32(b'')
        self._size = 0
        self._skip_gzip_header()

    def _read_raw(self, n):
        return self.raw_fh.read(n)

    def _skip_gzip_header(self):
        header = self._read_raw(10)
        if len(header) < 10 or header[:2] != b'\x1f\x8b':
            raise IOError('Not a gzip file')
        if header[2] != 8:
            raise IOError('Unsupported compression method')
        flg = header[3]
        if flg & 0x04:  # FEXTRA
            xlen = struct.unpack('<H', self._read_raw(2))[0]
            self._read_raw(xlen)
        if flg & 0x08:  # FNAME
            while self._read_raw(1) not in (b'\x00', b''):
                pass
        if flg & 0x10:  # FCOMMENT
            while self._read_raw(1) not in (b'\x00', b''):
                pass
        if flg & 0x02:  # FHCRC
            self._read_raw(2)

    def _fill_buf(self):
        """Decompress more data into self._buf. Returns False at end of member."""
        if self.at_eom:
            return False
        while not self._buf:
            chunk = self._read_raw(4096)
            if not chunk:
                raise EOFError('Unexpected EOF in gzip member')
            self._buf = self._decomp.decompress(chunk)
            if self._decomp.unused_data or self._decomp.eof:
                # end of deflate stream - unused_data is empty when stream ends
                # exactly on a chunk boundary, so we check eof as well
                unused = self._decomp.unused_data
                if unused:
                    self.raw_fh.seek(-len(unused), 1)
                # raw_fh is now positioned at the gzip trailer
                if not self._buf:
                    self._read_trailer()
                    self.at_eom = True
                    return False
                self._pending_eom = True
                break
        return bool(self._buf)

    def _deliver(self, n=None):
        """Take up to n bytes from self._buf, handle EOM if pending."""
        if n is None:
            data = self._buf
            self._buf = b''
        else:
            data = self._buf[:n]
            self._buf = self._buf[n:]
        self._crc = zlib.crc32(data, self._crc)
        self._size += len(data)
        if not self._buf and getattr(self, '_pending_eom', False):
            self._read_trailer()
            self.at_eom = True
            self._pending_eom = False
        return data

    def _read_trailer(self):
        trailer = self.raw_fh.read(8)
        if len(trailer) < 8:
            return
        crc32, isize = struct.unpack('<II', trailer)
        if crc32 != (self._crc & 0xffffffff):
            raise IOError('CRC check failed 0x%08x != 0x%08x' % (
                crc32, self._crc & 0xffffffff))
        if isize != (self._size & 0xffffffff):
            raise IOError('Incorrect length of data produced')

    def readable(self):
        return True

    def read(self, n=-1):
        if n == -1:
            chunks = []
            while self._fill_buf():
                chunks.append(self._deliver())
            return b''.join(chunks)
        result = b''
        while n > 0:
            if not self._buf and not self._fill_buf():
                break
            result += self._deliver(n)
            n -= len(result)
        return result

    def readinto(self, b):
        data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def readline(self, size=-1):
        """Readline without BufferedReader - no read-ahead into raw_fh."""
        chunks = []
        while True:
            if not self._buf and not self._fill_buf():
                break
            if size != -1:
                chunk = self._buf[:size]
            else:
                chunk = self._buf
            nl = chunk.find(b'\n')
            if nl != -1:
                line = self._deliver(nl + 1)
                chunks.append(line)
                break
            chunks.append(self._deliver())
            if size != -1:
                size -= len(chunks[-1])
                if size <= 0:
                    break
        return b''.join(chunks)

    def finish(self):
        """Drain remainder so raw_fh is at start of next member."""
        if not self.at_eom:
            while self._fill_buf():
                self._deliver()

class PatchedGzipRecordStream(GzipRecordStream):
    def __init__(self, file_handle, record_parser):
        RecordStream.__init__(self, file_handle, record_parser)
        self.raw_fh = file_handle
        self._member = None

    def _finish_member_and_sync(self):
        if self._member is None:
            return
        self._member.finish()
        self._member = None
        self.fh = None

    def _open_member(self, raw_fh):
        self._member = GzipMemberFile(raw_fh)
        return self._member

    @property
    def member_offset(self):
        return self._member.member_offset

    def _find_gzip_header(self):
        # unchanged - operates on self.raw_fh directly
        f = self.raw_fh
        b = bytearray(f.read(4))
        while len(b) == 4:
            if b[0] == 0x1f and b[1] == 0x8b:
                if b[2] == 8:
                    if (b[3] & 0x20) == 0:
                        f.seek(-4, 1)
                        return True
                b = b[2:]
                b.extend(f.read(2))
            else:
                b = b[1:]
                b.extend(f.read(1))
        return False

    def reset(self, start_offset=None):
        if start_offset is not None:
            self.raw_fh.seek(start_offset + 1, 0)
        else:
            saved_offset = self.raw_fh.tell()
            try:
                self._finish_member_and_sync()
            except Exception:
                pass
            start_offset = self.raw_fh.tell()
            if start_offset < saved_offset:
                self.raw_fh.seek(saved_offset, 0)
                start_offset = self.raw_fh.tell()
        magic = self.raw_fh.read(2)
        if magic == b'':
            self._remaining = 0
            return
        if magic == b'\x1f\x8b':
            self.raw_fh.seek(-2, 1)
        else:
            if len(magic) > 1:
                self.raw_fh.seek(-1, 1)
            if self._find_gzip_header():
                found_offset = self.raw_fh.tell()
                if found_offset > start_offset:
                    print('!!! skipped unusable data up to offset %d' % (
                        found_offset - 1), file=sys.stderr)
            else:
                if self.raw_fh.tell() > start_offset:
                    print('!!! skipped unusable data up to EOF', file=sys.stderr)
        self.fh = self._open_member(self.raw_fh)

    def _finish_record(self):
        self._finish_member_and_sync()

    def _read_record(self, offsets):
        while True:
            self._finish_member_and_sync()
            # check for EOF before attempting to open next member
            if self.raw_fh.read(1) == b'':
                return None, None, []
            self.raw_fh.seek(-1, 1)
            self.fh = self._open_member(self.raw_fh)
            self.bytes_to_eoc = None
            record, errors, _offset = \
                self.record_parser.parse(self, offset=None, line=None)
            offset = self._member.member_offset
            if record is not None or errors:
                return offset, record, errors
            # empty gzip member produced no record and no errors - skip it
            # and try the next member rather than signalling EOF to the caller.

    def close(self):
        self.raw_fh.close()


hanzo.warctools.stream.GzipRecordStream = PatchedGzipRecordStream

def open_record_stream(record_class=None, filename=None, file_handle=None,
                       mode='rb', gzip='auto', offset=None, length=None):
    # assumes our specific way of calling. does not support general usage.
    assert record_class is None and filename is not None and file_handle is None
    assert offset is None
    if filename.endswith('.zst'):
        if ZstdRecordStream is None:
            raise RuntimeError('.zst archive support is not available (requires zstandard.cffi)')
        file_handle = open(filename, mode=mode)
        record_parser = WarcRecord.make_parser()
        # find dictionary
        zdict = get_zstd_dictionary(file_handle)
        return ZstdRecordStream(file_handle, record_parser, zdict=zdict)
    return _open_record_stream(record_class, filename, file_handle, mode, gzip, offset, length)

from hanzo.warctools.archive_detect import register_record_type

# some ARC files are missing the filedesc record at the beginning
register_record_type(
    # pattern for ARC v1 header
    re.compile(br'^https?://\S+ (?:\d{1,3}\.){3}\d{1,3} \d{14} \S* \d+$'),
    ArcRecord
)

class ArchiveRecordEx(object):
    def __init__(self, reader, offset, record):
        self._reader = reader
        self.offset = offset
        self.wrapped_record = record

    RE_RESPONSE_CONTENT_TYPE = re.compile('application/http;\s*msgtype=response$', re.I)

    @property
    def compressed_record_size(self):
        # read off up to the end-of-record
        stream = self.wrapped_record.content_file
        if stream is not None:
            # TODO: define finish_record() in all ArchiveStream
            while True:
                d = stream.read(8192)
                if not d: break
        # above is enough for plain RecordStream. For GzipRecordStream
        # we need to further read up to the end of current member to get
        # correct end-of-member offset. we cannot use content_file here.
        self._reader._finish_record()
        end_offset = self._reader._stream_offset()
        return end_offset - self.offset
        #return self._reader._next_offset() - self.offset

    def is_response(self):
        """Return ``True`` if this record is WARC ``response`` record
        (i.e. currently returns ``False`` for ARC response records).
        It is determined by ``Content-Type`` in WARC header, not ``WARC-Type``.
        """
        content_type = self.content_type
        return content_type and self.RE_RESPONSE_CONTENT_TYPE.match(content_type.decode('latin1'))

    # following methods makes ArchiveRecordEx compatible with ArchiveRecord
    @property
    def type(self):
        return self.wrapped_record.type

    @property
    def url(self):
        return self.wrapped_record.url

    @property
    def date(self):
        return self.wrapped_record.date

    @property
    def content(self):
        # ArchiveRecord.content shall not be used because it breaks RecordHandler's
        # reading content_file, and loads entire record content into memory.
        raise Exception('content shall not be used')
        #return self.wrapped_record.content

    @property
    def content_file(self):
        return self.wrapped_record.content_file

    @property
    def content_type(self):
        # we cannot use ArchiveRecord.content_type because it accesses its content[0]
        # (i.e. it invalidates content_file)
        #return self.wrapped_record.content_type
        # this returns record-level content-type.
        return self.get_header(self.wrapped_record.CONTENT_TYPE)

    @property
    def content_length(self):
        # XXX ArchiveRecord.content_length resorts to content[1] if Content-Length
        # header does not exist.
        return self.wrapped_record.content_length

    @property
    def ip_address(self):
        # XXX ArcRecord and WarcRecord use different symbol for IP address
        # (IP and IP_ADDRESS, respectively). using literals here.
        return (self.get_header(b'ip-address') or
                self.get_header(b'warc-ip-address'))

    def get_header(self, name):
        return self.wrapped_record.get_header(name)

    # XXX CONTENT_LENGTH has different value for WARC and ARC
    # ("Length" for WARC, "Archive-length" for ARC). It'd be beter to
    # define a common method for retrieving Record's content-length.
    @property
    def CONTENT_LENGTH(self):
        return self.wrapped_record.CONTENT_LENGTH

class ArchiveRecordReader(object):
    def __init__(self, filepath):
        self._stream = open_record_stream(None, filename=filepath, gzip="auto", mode="rb")
        self._records = iter(self._stream.read_records(limit=None, offsets=True))
        self._next_record = None

    def __iter__(self):
        return self

    def reset(self, start_offset=None):
        # XXX - works only with gzip W/ARCs
        self._stream.reset(start_offset)

    def _stream_offset(self):
        if hasattr(self._stream, 'raw_fh'):
            return self._stream.raw_fh.tell()
        else:
            return self._stream.fh.tell()

    def _finish_record(self):
        if hasattr(self._stream, '_finish_record'):
            self._stream._finish_record()

    def _next_offset(self):
        if self._next_record:
            return self._next_record[0]
        while True:
            rectuple = next(self._records, None)
            if rectuple is None or (rectuple[1] or rectuple[2]):
                break
        if rectuple is None:
            self._next_record = () # end marker
            return self._stream_offset()
        self._next_record = rectuple
        return rectuple[0]

    def __next__(self):
        while True:
            if self._next_record is None:
                # raises StopIterator at the end
                self._next_record = next(self._records)
            if self._next_record:
                offset, record, errors = self._next_record
                self._next_record = None
                # errors can be non-empty even when record is not
                # None, but they are non-critical errors. we ignore
                # them. record.errors can also carry non-critical errors.
                if record is None:
                    # RecordStream can return None for both record and error
                    # at the end of WARC file. safely ignored.
                    if errors:
                        raise RecordParseError(errors[0])
                    continue
                return ArchiveRecordEx(self, offset, record)
            # end marker
            raise StopIteration()

    next = __next__

    def close(self):
        self._stream.close()
