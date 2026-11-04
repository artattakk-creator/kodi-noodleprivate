"""Strict, uncached Xtream VOD contracts; bounded streaming and safe errors.

Never infer an empty catalog from a failed request or an unknown JSON shape.
Only the explicit rescan and wizard's remote VOD discovery use this path.
"""
import json
import socket
import ssl
from urllib.error import HTTPError

KINDS = ('vod', 'series')
ACTIONS = {'vod': ('get_vod_categories', 'get_vod_streams', 'stream_id'),
           'series': ('get_series_categories', 'get_series', 'series_id')}


class SyncError(RuntimeError):
    def __init__(self, code, http=0, number=0):
        self.code, self.http, self.number = code, int(http or 0), int(number or 0)
        super().__init__(code)  # Never retain a transport's URL-bearing text.


def failure(exc):
    if isinstance(exc, SyncError):
        return exc
    if isinstance(exc, InterruptedError):
        return SyncError('CANCELLED')
    status = getattr(exc, 'code', 0) if isinstance(exc, HTTPError) else getattr(getattr(exc, 'response', None), 'status_code', 0)
    if isinstance(exc, HTTPError):
        exc.close()
    if status:
        return SyncError({401: 'AUTH', 403: 'FORBIDDEN', 404: 'ENDPOINT_MISSING', 429: 'RATE_LIMIT'}.get(status, 'HTTP'), status)
    if isinstance(exc, (TimeoutError, socket.timeout)) or 'timeout' in type(exc).__name__.lower():
        return SyncError('TIMEOUT')
    if isinstance(exc, ssl.SSLError) or isinstance(getattr(exc, 'reason', None), ssl.SSLError):
        return SyncError('TLS')
    if isinstance(exc, (UnicodeError, ValueError)):
        return SyncError('SCHEMA')
    import sqlite3
    if isinstance(exc, sqlite3.Error):
        primary = getattr(exc, 'sqlite_errorcode', 0) & 255
        return SyncError({8: 'READONLY', 13: 'SPACE'}.get(primary, 'SQLITE'), number=primary)
    if isinstance(exc, OSError):
        import errno
        number = getattr(exc, 'errno', 0) or 0
        return SyncError({errno.ENOSPC: 'SPACE', errno.EDQUOT: 'SPACE', errno.EROFS: 'READONLY',
                          errno.EACCES: 'PERMISSION', errno.EPERM: 'PERMISSION'}.get(number, 'NETWORK'), number=number)
    return SyncError('INTERNAL')


def check_error(value, kind=None):
    if not isinstance(value, dict):
        return
    if value.get('error') or value.get('errors') or value.get('success') is False:
        raise SyncError('API_ERROR')
    if str(value.get('auth', '1')).lower() not in ('1', 'true'):
        raise SyncError('AUTH')
    if 'status' in value and str(value['status']).lower() in ('disabled', 'expired', 'banned', 'error', 'failed'):
        raise SyncError('ACCOUNT_DISABLED')
    if kind and str(value.get(kind + '_enabled', '1')).lower() in ('0', 'false', 'no'):
        raise SyncError('VOD_DISABLED' if kind == 'vod' else 'SERIES_DISABLED')


def authenticate(client, cancel=lambda: False):
    from utils import http_get
    try:
        if cancel():
            raise InterruptedError()
        raw, _ = http_get(client._api_url(), params=client._base_params(), timeout=12,
                          max_bytes=2*1024*1024, max_seconds=30, retry_limit=0)
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get('user_info'), dict):
            raise SyncError('AUTH_SCHEMA')
        user = data['user_info']
        if str(user.get('auth', '0')).lower() not in ('1', 'true'):
            raise SyncError('AUTH')
        check_error(user)
        if cancel():
            raise InterruptedError()
        return user
    except Exception as exc:
        raise failure(exc) from None


class ArrayResponse:
    """Expose the sole allowlisted envelope array without buffering the body.

    Validate the complete header/trailer and pagination before a group may be
    published. Unknown wrappers and API error objects are explicit failures.
    """
    def __init__(self, stream, cancel):
        self.stream, self.cancel = stream, cancel
        self.buffer = b''; self.pos = 0; self.prefix = bytearray()
        quoted = escaped = False; braces = 0
        while True:
            c = self.byte()
            if c is None:
                try:
                    check_error(json.loads(self.prefix))
                except (ValueError, UnicodeError):
                    pass
                raise SyncError('SCHEMA')
            if not quoted and c == 91:
                break
            self.prefix.append(c)
            if len(self.prefix) > 65536:
                raise SyncError('SCHEMA')
            if quoted:
                if escaped: escaped = False
                elif c == 92: escaped = True
                elif c == 34: quoted = False
            elif c == 34: quoted = True
            elif c == 123: braces += 1
            elif c == 125: braces -= 1
        shape = json.loads(bytes(self.prefix) + b'[]' + b'}'*braces)
        self.array_path = []
        current = shape
        while isinstance(current, dict):
            check_error(current)
            keys = [k for k in ('data', 'items', 'results', 'categories', 'streams', 'series')
                    if isinstance(current.get(k), (list, dict))]
            if len(keys) != 1 or len(self.array_path) >= 2:
                raise SyncError('SCHEMA')
            self.array_path.append(keys[0]); current = current[keys[0]]
        if current != []:
            raise SyncError('SCHEMA')
        self.started = False; self.depth = 1; self.quoted = self.escaped = False
        self.metadata = {}

    def byte(self):
        if self.pos >= len(self.buffer):
            if self.cancel():
                raise InterruptedError()
            self.buffer = self.stream.read(32768); self.pos = 0
            if not self.buffer:
                return None
        value = self.buffer[self.pos]; self.pos += 1
        return value

    def read(self, n):
        if not 0 <= n <= 65536:
            raise SyncError('SCHEMA')
        if not n or not self.depth:
            return b''
        out = bytearray()
        if not self.started:
            out.append(91); self.started = True
        while len(out) < n and self.depth:
            c = self.byte()
            if c is None:
                raise SyncError('TRUNCATED')
            out.append(c)
            if self.quoted:
                if self.escaped: self.escaped = False
                elif c == 92: self.escaped = True
                elif c == 34: self.quoted = False
            elif c == 34: self.quoted = True
            elif c == 91: self.depth += 1
            elif c == 93: self.depth -= 1
        if not self.depth:
            tail = bytearray(self.buffer[self.pos:]); self.pos = len(self.buffer)
            while True:
                if self.cancel():
                    raise InterruptedError()
                raw = self.stream.read(32768)
                if not raw:
                    break
                tail.extend(raw)
                if len(tail) > 65536:
                    raise SyncError('SCHEMA')
            document = json.loads(bytes(self.prefix) + b'[]' + tail)
            current = document
            for key in self.array_path:
                check_error(current)
                self.metadata.update({k: v for k, v in current.items() if k != key})
                current = current[key]
            if isinstance(self.metadata.get('pagination'), dict):
                self.metadata.update(self.metadata.pop('pagination'))
            check_error(self.metadata)
        return bytes(out)


def iterate(client, kind, categories=False, cid=None, cancel=lambda: False):
    from utils import http_stream
    from streaming_json import iter_array
    if kind not in KINDS:
        raise SyncError('SCOPE')
    action = ACTIONS[kind][0 if categories else 1]
    received = 0; page = 1
    try:
        while page <= 10000:
            if cancel():
                raise InterruptedError()
            params = dict(client._base_params(), action=action)
            if cid is not None:
                params['category_id'] = str(cid)
            if page > 1:
                params['page'] = page
            with http_stream(client._api_url(), params=params, timeout=12,
                             max_seconds=None, cancel=cancel) as stream:
                reader = ArrayResponse(stream, cancel); count = 0
                for row in iter_array(reader, cancel):
                    count += 1; received += 1
                    yield row
                meta = reader.metadata
            check_error(meta, kind)
            total = meta.get('total_items', meta.get('total'))
            pages = meta.get('total_pages', meta.get('pages'))
            for value in (total, pages, meta.get('page'), meta.get('next_page')):
                if value is not None and (isinstance(value, bool) or not str(value).isdigit()):
                    raise SyncError('PAGINATION')
            if meta.get('page') is not None and int(meta['page']) != page:
                raise SyncError('PAGINATION')
            next_page = meta.get('next_page')
            more = (next_page is not None and int(next_page) > 0) or pages is not None and page < int(pages)
            if meta.get('has_more') is True and not more:
                raise SyncError('PAGINATION')
            if more:
                if not count or next_page is not None and int(next_page) != page+1:
                    raise SyncError('PAGINATION')
                page += 1
                continue
            if total is not None and int(total) != received:
                raise SyncError('PARTIAL_RESPONSE')
            return
        raise SyncError('PAGINATION')
    except Exception as exc:
        raise failure(exc) from None


def identity(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).strip() or len(str(value)) > 256:
        raise SyncError('IDENTITY')
    return str(value)


def categories(client, kind, cancel=lambda: False):
    result = []; seen = set()
    for row in iterate(client, kind, categories=True, cancel=cancel):
        cid = identity(row.get('category_id', row.get('id')))
        if cid in seen or len(result) >= 20000:
            raise SyncError('DUPLICATE_ID' if cid in seen else 'CATEGORY_BUDGET')
        seen.add(cid)
        name = row.get('category_name') or row.get('name') or row.get('title')
        if not isinstance(name, str) or not name.strip():
            raise SyncError('SCHEMA')
        result.append(dict(category_id=cid, category_name=name[:512]))
    return result
