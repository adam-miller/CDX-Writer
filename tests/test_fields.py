"""
Tests for variations in field values, like different formats of dates, etc.

Converted from small_warcs as it is tedious to prepare W/ARC files for each
different value.
"""
import io
from gzip import GzipFile

from cdx_writer.command import CDX_Writer
from cdx_writer.archive import ArchiveRecordReader

import pytest
import py

def write_arc_record(w, fields, content):
    assert isinstance(content, bytes)
    with GzipFile(fileobj=w, mode="wb") as z:
        z.write(b' '.join(fields) + b' ' + 
                format(len(content)).encode('ascii') + b'\n')
        z.write(content)
        z.write(b'\n')

def write_warc_record(w, headers, content):
    assert isinstance(content, bytes)
    with GzipFile(fileobj=w, mode="wb") as z:
        z.write(b'WARC/1.0\r\n')
        for n, v in headers:
            z.write(n + b': ' + v + b'\r\n')
        z.write('Content-Length: {}\r\n'.format(len(content)).encode('ascii'))
        z.write(b'\r\n')
        z.write(content)
        z.write(b'\r\n\r\n')

def http_response():
    CONTENT = b'test\n'
    b = io.BytesIO()
    b.write(b'HTTP/1.0 200 OK\r\n')
    b.write(b'Content-Type: text/plain\r\n')
    b.write('Content-Length: {}\r\n'.format(len(CONTENT)).encode('ascii'))
    b.write(b'\r\n')
    b.write(CONTENT)
    return b.getvalue()

def get_cdx_fields(inpath):
    out = io.BytesIO()
    cw = CDX_Writer(str(inpath), out)
    cw.make_cdx()
    output = out.getvalue().splitlines()
    assert len(output) == 2
    return output[1].split(b' ')

@pytest.mark.parametrize("date,expected", [
    # 10_digit_date from IMF NLI ingest 2018-08
    (b'2016020900', b'20160209000000'),
    # 14_digit_plus_text_date from IMF ingest 2018-08
    (b'20160211000000jpg', b'20160211000000'),
    # 15_digit_date from IMF UNESCO ingest 2018-08
    (b'201512000000000', b'20151200000000'),
    # 16_digit_date from INA-HISTORICAL-1996-GROUP-AAA-20100812000000-00000-c/INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc.gz
    (b'2000082305410049', b'20000823054100'),
    # 18_digit_date from IMG_XAB_001010144441-c/IMG_XBB_000918161534.arc.gz
    (b'200009180023002953', b'20000918002300')
])
def test_date_arc(tmpdir, date, expected):
    arc = tmpdir / 'a.arc.gz'

    with arc.open('wb') as w:
        write_arc_record(w, [
            b'filedesc://a.arc.gz', b'0.0.0.0', b'20160209153640', b'text/plain'
        ], (
            b"1 1 InternetArchive\n"
            b"URL IP-address Archive-date Content-type Archive-length\n"
        ))
        write_arc_record(w, [
            b'http://example.com/', b'1.2.3.4', date, b'text/plain'
        ], http_response())

    timestamp = get_cdx_fields(arc)[1]
    assert timestamp == expected

# WARC-1.1 specification says "WARC-Date is a UTC timestamp as described in the W3C profile
# of ISO 8601:1988 [W3CDTF], for example YYYY-MM-DDThh:mm:ssZ. ... WARC-Date may be specified
# at any of the levels of granularity described in [W3CDTF]. If WARC-Date includes a decimal
# fraction of a second, the decimal fraction of a second shall have a minimum of 1 digit and a
# maximum of 9 digits. WARC-Date should be specified with as much precision as is accurately
# known.
@pytest.mark.parametrize("date,expected", [
    (b'2010-09-26T11:23:46', b'20100926112346'),
    (b'2010-09-26T11:23:46', b'20100926112346'),
    (b'2019-11-18T12:56:03.352903Z', b'20191118125603'),
    (b'2019-11-18T12:56:03.352903999Z', b'20191118125603')
])
def test_date_warc(tmpdir, date, expected):
    warc = tmpdir / 'a.warc.gz'

    with warc.open('wb') as w:
        write_warc_record(w, [
            (b'WARC-Type', b'response'),
            (b'WARC-Target-URI', b'http://example.com/'),
            (b'WARC-Date', date),
            (b'Content-Type', b'application/http;msgtype=request')
        ], http_response())

    timestamp = get_cdx_fields(warc)[1]
    assert timestamp == expected

@pytest.mark.parametrize("contenttype,expected", [
    (b'text/plain', b'text/plain'),
    # bad_mime_type
    (b'imag\xEF\xBF\xBDm)', b'unk'),
    # alexa_charset_in_header
    # INA-HISTORICAL-1996-GROUP-AAA-20100812000000-00000-c/INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc.gz, fixed in warctools changeset 92:ca95fa09848b
    (b'text/html; Charset=iso-8859-1', b'text/html'),
    # aug-000823102923-c/aug-000823104637.arc.gz
    (b'text/html; charset=koi8-r; charset=windows-1251', b'text/html')
])
def test_contenttype_arc(tmpdir, contenttype, expected):
    arc = tmpdir / 'a.arc.gz'

    with arc.open('wb') as w:
        write_arc_record(w, [
            b'filedesc://a.arc.gz', b'0.0.0.0', b'20160209153640', b'text/plain'
        ], (
            b"1 1 InternetArchive\n"
            b"URL IP-address Archive-date Content-type Archive-length\n"
        ))
        write_arc_record(w, [
            b'http://example.com/', b'1.2.3.4', b'20100926112346', contenttype
        ], http_response())

    mimetype = get_cdx_fields(arc)[3]
    assert mimetype == expected

@pytest.mark.parametrize("contenttype,expected", [
    (b'text/html', b'text/html'),
    (b'text/html;', b'text/html'),
    (b'text/html; charset=UTF-8', b'text/html'),
    (b'text/html ; charset=UTF-8', b'text/html'),
    (b'text/html;charset=UTF-8', b'text/html'),
    # uppercase
    (b'Text/Html', b'text/html'),
    (b'Text/Html; charset=UTF-8', b'text/html'),
    (b'image/GIF', b'image/gif')
])
def test_contenttype_warc(tmpdir, contenttype, expected):
    date = b'2020-09-01T11:22:33'
    warc = tmpdir / 'a.warc.gz'

    with warc.open('wb') as w:
        write_warc_record(w, [
            (b'WARC-Type', b'response'),
            (b'WARC-Target-URI', b'http://example.com/'),
            (b'WARC-Date', date),
            (b'Content-Type', contenttype)
        ], http_response())

    mimetype = get_cdx_fields(warc)[3]
    assert mimetype == expected

@pytest.mark.parametrize("ipaddr,expected", [
    (b'1.2.3.4', b'1.2.3.4'),
    # empty value; green-000008-20000228185217-951859964-c/green-000008-20000407021139-955146423.arc.gz
    (b'', None)
])
def test_ipaddr_arc(tmpdir, ipaddr, expected):
    arc = tmpdir / 'a.arc.gz'

    with arc.open('wb') as w:
        write_arc_record(w, [
            b'filedesc://a.arc.gz', b'0.0.0.0', b'20160209153640', b'text/plain'
        ], (
            b"1 1 InternetArchive\n"
            b"URL IP-address Archive-date Content-type Archive-length\n"
        ))
        write_arc_record(w, [
            b'http://example.com/', ipaddr, b'20100926112346', b'text/html'
        ], http_response())

    record_reader = ArchiveRecordReader(str(arc))
    records = list(iter(record_reader))
    ipaddr_read = records[1].ip_address
    assert ipaddr_read == expected
