"""Bound raw and HTTP-decoded bytes before allocating full response bodies."""
import io
import time
import zlib

MAX_HTTP_BYTES = 80 * 1024 * 1024


class ResponseLimitError(ValueError):
    def __init__(self, message, kind='input_bytes'):
        super().__init__(message)
        self.kind = kind


class HTTPCompressionError(ValueError):
    pass


def read_http_chunks(chunks, headers, max_bytes, deadline):
    encoding = next((str(v).lower() for k, v in headers.items()
                     if k.lower() == 'content-encoding'), '')
    if encoding not in ('', 'identity', 'gzip', 'deflate'):
        raise ValueError('Unsupported HTTP content encoding')
    decoder = (zlib.decompressobj(31 if encoding == 'gzip' else 15)
               if encoding in ('gzip', 'deflate') else None)
    received = decoded = 0
    with io.BytesIO() as output:
        for chunk in chunks:
            if time.monotonic() > deadline:
                raise TimeoutError('HTTP response time budget exceeded')
            received += len(chunk)
            if received > max_bytes:
                raise ResponseLimitError('HTTP response exceeds size limit')
            data = decoder.decompress(chunk, max_bytes-decoded+1) if decoder else chunk
            decoded += len(data)
            if decoded > max_bytes or (decoder and decoder.unconsumed_tail):
                raise ResponseLimitError('Decoded HTTP response exceeds size limit', 'decoded_bytes')
            output.write(data)
        if decoder and not decoder.eof:
            raise HTTPCompressionError('Truncated HTTP compressed response')
        if time.monotonic() > deadline:
            raise TimeoutError('HTTP response time budget exceeded')
        return output.getvalue()


def decoded_chunks(chunks, headers, deadline, cancel=lambda: False):
    """Streaming alternative: 64-KiB working buffers, no collection-size cap.

    Caller must persist incrementally under a disk-space budget. Compression
    trailing streams are rejected (rather than silently truncating JSON/XML).
    """
    encoding = next((str(v).lower() for k,v in headers.items()
                     if k.lower() == 'content-encoding'), '')
    if encoding not in ('', 'identity', 'gzip', 'deflate'):
        raise ValueError('Unsupported HTTP content encoding')
    decoder = zlib.decompressobj(31 if encoding == 'gzip' else 15) if encoding in ('gzip','deflate') else None
    for raw in chunks:
        if cancel(): raise InterruptedError('HTTP request cancelled')
        if time.monotonic() > deadline: raise TimeoutError('HTTP streaming deadline')
        # A transport may deliver large chunks; never pass them whole to zlib.
        for offset in range(0, len(raw), 65536):
            data = raw[offset:offset+65536]
            if decoder:
                while data:
                    out = decoder.decompress(data, 65536)
                    data = decoder.unconsumed_tail
                    if decoder.unused_data: raise HTTPCompressionError('Trailing compressed HTTP data')
                    if cancel(): raise InterruptedError('HTTP request cancelled')
                    if time.monotonic() > deadline: raise TimeoutError('HTTP streaming deadline')
                    if out: yield out
            elif data: yield data
    if decoder and not decoder.eof: raise HTTPCompressionError('Truncated HTTP compressed response')


class ChunkReader:
    """Binary read(n) adapter, retaining at most one bounded decoded chunk."""
    def __init__(self, chunks):
        self.chunks = iter(chunks)
        self.pending = b''
        self.total = 0

    def read(self, size=65536):
        if size < 0 or size > 65536: raise ValueError('bounded reads required')
        result = bytearray()
        while len(result) < size:
            if not self.pending:
                self.pending = next(self.chunks, b'')
                if not self.pending: break
            count = min(size-len(result), len(self.pending))
            result.extend(self.pending[:count]); self.pending = self.pending[count:]
        self.total += len(result)
        return bytes(result)
