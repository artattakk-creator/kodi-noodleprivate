"""Private GitHub-only EPG v1 transport; no real data or credentials in source.

Standalone testable transport, to be wired into XCMate's worker and stream_epg
import path. A read-only PAT is supplied only by a private installer build step.
"""
import gzip
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
from urllib import error as urlerror
from urllib import request
from xml.parsers import expat

API_ROOT = 'https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/'
MANIFEST_URL = API_ROOT + 'manifest.json'
EPG_URL = API_ROOT + 'xcmate-epg.xml.gz'
GZIP_NAME = 'xcmate-epg.xml.gz'
MAX_GZIP_BYTES = 64 * 1024 * 1024
MAX_XML_BYTES = 256 * 1024 * 1024
TOKEN_BASENAME = 'epg-agent-read-token.txt'


class EPGAgentError(ValueError):
    """Safe non-credential error code for UI/status."""


def packaged_token(lib_file=__file__):
    """Read *optional* build-injected credential, not checked into Git.

    This is accessible to anyone who can unpack the installer ZIP. Use only a
    fine-grained read-only token for the dedicated artifact-only repository.
    """
    root = Path(lib_file).resolve().parent.parent
    filename = root / TOKEN_BASENAME
    try:
        raw = filename.read_bytes()
    except OSError:
        return None
    if len(raw) > 512:
        return None
    try:
        value = raw.decode('ascii').strip()
    except UnicodeDecodeError:
        return None
    return value if re.fullmatch(r'[A-Za-z0-9_-]+', value) and 20 <= len(value) <= 512 else None


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise EPGAgentError('REDIRECT_REFUSED')


def _network_fetch(url, headers, maximum):
    if url not in (MANIFEST_URL, EPG_URL):
        raise EPGAgentError('ENDPOINT_NOT_ALLOWED')
    req = request.Request(url, method='GET', headers=headers)
    try:
        with request.build_opener(_NoRedirect).open(req, timeout=20) as response:
            if response.status != 200:
                raise EPGAgentError('HTTP_NOT_READY')
            chunks = []
            total = 0
            while True:
                block = response.read(min(65536, maximum - total + 1))
                if not block:
                    break
                chunks.append(block)
                total += len(block)
                if total > maximum:
                    raise EPGAgentError('HTTP_TOO_LARGE')
            return b''.join(chunks)
    except urlerror.HTTPError as exc:
        if exc.code == 401:
            raise EPGAgentError('AUTH_EXPIRED') from None
        if exc.code in (403, 404):
            raise EPGAgentError('PRIVATE_ACCESS_DENIED') from None
        if exc.code == 429:
            raise EPGAgentError('RATE_LIMITED') from None
        raise EPGAgentError('HTTP_UNAVAILABLE') from None
    except urlerror.URLError:
        raise EPGAgentError('NETWORK_UNAVAILABLE') from None


def _fetch(url, token, maximum, transport):
    # Never include the token in URL, diagnostics, exceptions or output files.
    headers = {'Accept': 'application/vnd.github.raw+json',
               'Authorization': 'Bearer ' + token,
               'X-GitHub-Api-Version': '2022-11-28',
               'User-Agent': 'XCMate-EPG-Agent/1.0'}
    data = transport(url, headers, maximum)
    if not isinstance(data, bytes) or len(data) > maximum:
        raise EPGAgentError('HTTP_RESPONSE_INVALID')
    return data


def _manifest(raw):
    try:
        m = json.loads(raw.decode('utf-8'))
    except (ValueError, UnicodeError):
        raise EPGAgentError('MANIFEST_INVALID') from None
    if not isinstance(m, dict) or m.get('schema_version') != 1 or m.get('file') != GZIP_NAME:
        raise EPGAgentError('MANIFEST_INVALID')
    state = m.get('status')
    if state == 'PRIVATE_PENDING':
        return m
    if state != 'PRIVATE_READY':
        raise EPGAgentError('MANIFEST_INVALID')
    try:
        created = datetime.fromisoformat(m['generated_at_utc'].replace('Z', '+00:00'))
        if created.tzinfo is None:
            raise ValueError('timezone missing')
    except (KeyError, AttributeError, ValueError, TypeError):
        raise EPGAgentError('MANIFEST_INVALID') from None
    if not isinstance(m.get('sha256'), str) or not re.fullmatch('[a-f0-9]{64}', m['sha256']):
        raise EPGAgentError('MANIFEST_INVALID')
    if not isinstance(m.get('bytes'), int) or isinstance(m['bytes'], bool) or not 1 <= m['bytes'] <= MAX_GZIP_BYTES:
        raise EPGAgentError('MANIFEST_INVALID')
    for key in ('channel_count', 'programme_count'):
        if not isinstance(m.get(key), int) or isinstance(m[key], bool) or m[key] < 1:
            raise EPGAgentError('MANIFEST_INVALID')
    return m


def _check_xmltv(blob, expected_channels, expected_programmes):
    channels = 0
    programmes = 0
    depth = 0
    root_seen = False
    parser = expat.ParserCreate()
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)

    def start(name, attrs):
        nonlocal channels, programmes, depth, root_seen
        depth += 1
        if depth > 25:
            raise EPGAgentError('XML_DEPTH_LIMIT')
        if depth == 1:
            if name != 'tv':
                raise EPGAgentError('XMLTV_INVALID')
            root_seen = True
        if depth == 2 and name == 'channel':
            if not attrs.get('id'):
                raise EPGAgentError('XMLTV_INVALID')
            channels += 1
        if depth == 2 and name == 'programme':
            if not attrs.get('channel') or not attrs.get('start') or not attrs.get('stop'):
                raise EPGAgentError('XMLTV_INVALID')
            programmes += 1
        if channels > 200000 or programmes > 1000000:
            raise EPGAgentError('XMLTV_TOO_MANY_RECORDS')

    def end(name):
        nonlocal depth
        depth -= 1

    def reject(*unused):
        raise EPGAgentError('XML_ENTITIES_FORBIDDEN')

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.StartDoctypeDeclHandler = reject
    parser.EntityDeclHandler = reject
    parser.ExternalEntityRefHandler = reject
    expanded = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(blob), mode='rb') as g:
            while True:
                block = g.read(65536)
                if not block:
                    break
                expanded += len(block)
                if expanded > MAX_XML_BYTES:
                    raise EPGAgentError('XML_TOO_LARGE')
                parser.Parse(block, False)
            parser.Parse(b'', True)
    except (OSError, EOFError, expat.ExpatError):
        raise EPGAgentError('XMLTV_CORRUPT') from None
    if not root_seen or depth != 0 or channels != expected_channels or programmes != expected_programmes:
        raise EPGAgentError('XMLTV_COUNT_MISMATCH')


def _atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.epg-v1-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sync_once(profile_directory, token=None, transport=None):
    """Return a status and LastGood path; NEVER mutate Kodi guide/portal state.

    Calling worker decides whether/how to ingest the versioned, verified file.
    All error results preserve the previous LastGood and provider EPG.
    """
    folder = Path(profile_directory) / 'epg-agent-v1'
    pointer = folder / 'current.json'
    prior = None
    try:
        prior = json.loads(pointer.read_text(encoding='utf-8'))
        if not isinstance(prior, dict) or not re.fullmatch('[a-f0-9]{64}', prior.get('sha256', '')):
            prior = None
    except (OSError, ValueError, TypeError):
        pass
    def good_path():
        if prior is None:
            return None
        path = folder / 'versions' / (prior['sha256'] + '.xml.gz')
        return str(path) if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == prior['sha256'] else None
    fallback = good_path()
    if token is None:
        token = packaged_token()
    if not token or not isinstance(token, str) or not 20 <= len(token) <= 512 or not re.fullmatch(r'[A-Za-z0-9_-]+', token):
        return {'status': 'CREDENTIAL_PENDING', 'path': fallback}
    fetch = transport or _network_fetch
    try:
        raw = _fetch(MANIFEST_URL, token, 64 * 1024, fetch)
        m = _manifest(raw)
        if m['status'] == 'PRIVATE_PENDING':
            return {'status': 'PRIVATE_PENDING', 'path': fallback}
        if m['sha256'] == (prior or {}).get('sha256') and fallback:
            return {'status': 'UNCHANGED', 'path': fallback}
        data = _fetch(EPG_URL, token, MAX_GZIP_BYTES, fetch)
        if len(data) != m['bytes'] or hashlib.sha256(data).hexdigest() != m['sha256']:
            raise EPGAgentError('HASH_MISMATCH')
        _check_xmltv(data, m['channel_count'], m['programme_count'])
        versioned = folder / 'versions' / (m['sha256'] + '.xml.gz')
        _atomic(versioned, data)
        _atomic(pointer, json.dumps(m, sort_keys=True, separators=(',', ':')).encode('utf-8'))
        return {'status': 'UPDATED', 'path': str(versioned)}
    except EPGAgentError as exc:
        return {'status': str(exc), 'path': fallback}
    except (OSError, ValueError, TypeError):
        return {'status': 'STORAGE_OR_FORMAT_ERROR', 'path': fallback}
