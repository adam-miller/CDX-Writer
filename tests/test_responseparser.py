import pytest

import io
from cdx_writer.handler import HTTPResponseParser

@pytest.mark.parametrize("statusline,expected", [
    # original HTTPResponse raises UnknownProtocol
    (b'HTTP/0.0 400 Bad Request', (10, 400, 'Bad Request')),
    (b'HTTP/2.0 404 Not Found', (10, 404, 'Not Found'))
])
def test_read_status_incorrect_but_acceptable(statusline, expected):
    fobj = io.BytesIO(statusline + b'\r\nContent-Length: 0\r\n\r\n')

    parser = HTTPResponseParser(fobj)

    assert (parser.version, parser.status, parser.reason) == expected
