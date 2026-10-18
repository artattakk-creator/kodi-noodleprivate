"""Shared XMLTV budgets; parse gzip incrementally without a second full copy."""
import gzip
import io
import time

MAX_XML_BYTES = 80 * 1024 * 1024
MAX_PROGRAMMES = 150000
MAX_CHANNELS = 10000
MAX_PARSE_SECONDS = 60


class XMLTVReader:
    def __init__(self, content, max_bytes=MAX_XML_BYTES):
        if len(content) > max_bytes:
            raise ValueError('XMLTV input exceeds size limit')
        self._raw = io.BytesIO(content)
        self._stream = (gzip.GzipFile(fileobj=self._raw)
                        if content[:2] == b'\x1f\x8b' else self._raw)
        self._remaining = max_bytes
        self._deadline = time.monotonic() + MAX_PARSE_SECONDS
        self._tail = b''

    def read(self, size=-1):
        if time.monotonic() > self._deadline:
            raise TimeoutError('XMLTV parsing time limit exceeded')
        count = self._remaining + 1 if size < 0 else min(size, self._remaining + 1)
        data = self._stream.read(count)
        if len(data) > self._remaining:
            raise ValueError('Decompressed XMLTV exceeds size limit')
        self._remaining -= len(data)
        # Check every chunk, including declarations after long XML comments.
        scan = self._tail + data.replace(b'\x00', b'').upper()
        if b'<!DOCTYPE' in scan or b'<!ENTITY' in scan:
            raise ValueError('XMLTV DTD/entities are not supported')
        self._tail = scan[-16:]
        return data

    def close(self):
        self._stream.close()
        self._raw.close()
