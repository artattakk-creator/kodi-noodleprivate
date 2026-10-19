"""Bounded stdlib JSON-array reader for Kodi's Python (no native dependency).

A single object is limited; the array is not. Input must be binary, reads are
bounded, UTF-8 is incremental, and the complete document/trailing data validate
before the caller publishes its staging generation.
"""
import codecs
import json

CHUNK = 32768
MAX_ITEM = 512 * 1024
MAX_DEPTH = 64


def iter_array(stream, cancel=lambda: False, envelope=False):
    decoder = codecs.getincrementaldecoder('utf-8-sig')('strict')
    buffer = ''
    pos = 0
    eof = False
    def more():
        nonlocal buffer, pos, eof
        if cancel(): raise InterruptedError('catalogue import cancelled')
        raw = stream.read(CHUNK)
        buffer = buffer[pos:] + decoder.decode(raw, final=not raw)
        pos = 0
        eof = not raw
    def char():
        nonlocal pos
        while pos >= len(buffer) and not eof: more()
        return buffer[pos] if pos < len(buffer) else ''
    def whitespace():
        nonlocal pos
        while char() and char() in ' \t\r\n': pos += 1
    whitespace()
    if char() != '[': raise ValueError('catalogue must be a JSON array')
    pos += 1
    whitespace()
    if char() == ']': pos += 1
    else:
        while True:
            whitespace()
            if char() != '{': raise ValueError('catalogue entry must be an object')
            parts = []; length = 0; depth = 0; quoted = escaped = False
            while True:
                c = char()
                if not c: raise ValueError('truncated catalogue object')
                pos += 1
                parts.append(c); length += 1
                if length > MAX_ITEM: raise ValueError('catalogue entry exceeds memory budget')
                if quoted:
                    if escaped: escaped = False
                    elif c == '\\': escaped = True
                    elif c == '"': quoted = False
                elif c == '"': quoted = True
                elif c in '{[':
                    depth += 1
                    if depth > MAX_DEPTH: raise ValueError('catalogue nesting budget exceeded')
                elif c in '}]':
                    depth -= 1
                    if depth == 0: break
            yield json.loads(''.join(parts), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
            whitespace()
            c = char(); pos += 1
            if c == ']': break
            if c != ',': raise ValueError('invalid catalogue separator')
    whitespace()
    if envelope:
        if char() != '}': raise ValueError('invalid cache envelope')
        pos += 1
        whitespace()
    if char(): raise ValueError('trailing catalogue data')


def cached_array(stream, cancel=lambda:False):
    import re
    prefix = stream.read(4096)
    if prefix.lstrip().startswith(b'['):
        stream.seek(0)
        yield from iter_array(stream,cancel)
        return
    match = re.match(rb'\s*\{\s*"ts"\s*:\s*[0-9.eE+-]+\s*,\s*"data"\s*:',prefix)
    if not match: raise ValueError('invalid catalogue cache envelope')
    stream.seek(match.end())
    yield from iter_array(stream,cancel,envelope=True)
