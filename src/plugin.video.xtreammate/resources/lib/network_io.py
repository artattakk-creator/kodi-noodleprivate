"""Bound raw and HTTP-decoded bytes before allocating full response bodies."""
import io
import time
import zlib

MAX_HTTP_BYTES = 80 * 1024 * 1024


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
                raise ValueError('HTTP response exceeds size limit')
            data = decoder.decompress(chunk, max_bytes-decoded+1) if decoder else chunk
            decoded += len(data)
            if decoded > max_bytes or (decoder and decoder.unconsumed_tail):
                raise ValueError('Decoded HTTP response exceeds size limit')
            output.write(data)
        if decoder and not decoder.eof:
            raise ValueError('Truncated HTTP compressed response')
        if time.monotonic() > deadline:
            raise TimeoutError('HTTP response time budget exceeded')
        return output.getvalue()
