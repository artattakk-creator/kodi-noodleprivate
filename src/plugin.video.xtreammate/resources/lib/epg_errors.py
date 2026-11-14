"""Safe EPG error classification; never copy exception messages or source URLs."""
import gzip
import socket,ssl,sqlite3
import zlib
from xml.etree import ElementTree as ET

from epg_io import XMLTVLimitError, MAX_XML_BYTES, MAX_CHANNELS, MAX_PROGRAMMES
from network_io import ResponseLimitError, HTTPCompressionError


class EmptyGuideError(ValueError):
    pass


def failure_details(exc, stage):
    fields = {'failure_stage': stage, 'exception_class': type(exc).__name__}
    if isinstance(exc,sqlite3.Error):
        code={5:'SQLITE_BUSY',6:'SQLITE_BUSY',13:'SQLITE_FULL',10:'SQLITE_IO',9:'SQLITE_CANCELLED'}.get(getattr(exc,'sqlite_errorcode',0)&255,'SQLITE_ERROR')
    elif isinstance(exc,InterruptedError):code='CANCELLED'
    elif isinstance(getattr(exc,'reason',exc),socket.gaierror):code='DNS_FAILED'
    elif isinstance(getattr(exc,'reason',exc),ssl.SSLError):code='TLS_FAILED'
    elif getattr(exc,'code69','') in ('SAFE_RESERVE_BLOCKED','RESERVE_BLOCKED'):code='RESERVE_BLOCKED'
    elif isinstance(exc,OSError) and str(exc) in ('EPG_READBACK_MISMATCH','EPG_READBACK_REVISION_CHANGED'):code=str(exc)
    elif isinstance(exc, (XMLTVLimitError, ResponseLimitError)):
        kind = exc.kind
        fields['limit_kind'] = kind
        fields['limit_value'] = {'channels': MAX_CHANNELS,
                                 'programmes': MAX_PROGRAMMES,'field_bytes':256*1024,'nesting':32}.get(kind, MAX_XML_BYTES)
        if kind in ('bytes', 'input_bytes', 'decoded_bytes'):
            fields['limit_bytes'] = MAX_XML_BYTES
        prefix = 'HTTP_' if isinstance(exc, ResponseLimitError) else 'XMLTV_'
        code = prefix + kind.upper() + '_LIMIT'
    elif isinstance(exc, EmptyGuideError):
        code = 'NO_CHANNEL_MATCH' if getattr(exc,'xcmate_no_match59',False) else 'EMPTY_GUIDE'
    elif isinstance(exc, (gzip.BadGzipFile, EOFError, zlib.error, HTTPCompressionError)):
        code = 'GZIP_INVALID' if stage == 'PARSE' else 'HTTP_COMPRESSION_FAILED'
    elif type(exc).__name__ == 'UnsafeXMLTV':
        code = 'XMLTV_UNSAFE_DECLARATION'
    elif type(exc).__name__ == 'XMLTVSyntaxError' or isinstance(exc, ET.ParseError):
        code = 'INVALID_XMLTV'
    elif isinstance(exc, TimeoutError) or type(exc).__name__ in (
            'ReadTimeout', 'ConnectTimeout', 'WriteTimeout', 'PoolTimeout'):
        code = 'PARSE_TIMEOUT' if stage == 'PARSE' else 'DOWNLOAD_TIMEOUT'
    elif isinstance(exc, ValueError) and stage == 'PARSE':
        code = 'INVALID_XMLTV'
    else:
        code = 'DOWNLOAD_FAILED' if stage == 'DOWNLOAD' else 'PARSE_FAILED'
    # HTTP libraries expose status codes differently; never serialize the
    # response, request, exception string or redirect URL.
    status = getattr(getattr(exc, 'response', None), 'status_code', None)
    if status is None: status = getattr(exc, 'code', None)
    if isinstance(status, int) and 100 <= status <= 599:
        fields['http_status'] = status
    from import_budget import safe_failure
    details=safe_failure(exc)
    fields['error_file']=details['frames'][-1][0] if details['frames'] else ''
    fields['error_line']=details['frames'][-1][1] if details['frames'] else 0
    fields['failure_code'] = code
    return code, fields
