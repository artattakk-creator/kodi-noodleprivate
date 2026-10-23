"""Explicit HTTPS catalogue/download jobs. Never used by navigation callbacks."""
import hashlib
import os
from pathlib import PurePosixPath
import re
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

from theme_package import MAX_ZIP, MAX_METADATA, fail, json_object, version

ORIGIN = 'https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/8ab1a566877ed0a71573f90d0f82b11457bf9da4/'
CATALOG = 'https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/0452bc9e9799faf87ed71de81c0422a78fcdfb76/themes/xcmate/catalog-v1.json'


def trusted_url(url):
    if url==CATALOG:return url
    if not isinstance(url, str) or not url.startswith(ORIGIN+'themes/xcmate/'): fail('CATALOG')
    parts = urlsplit(url)
    relative = url[len(ORIGIN):]
    if (parts.scheme != 'https' or parts.netloc != 'raw.githubusercontent.com' or parts.query or parts.fragment
            or not re.fullmatch(r'[A-Za-z0-9_./-]+', relative) or '..' in PurePosixPath(relative).parts):
        fail('CATALOG')
    return url


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        fail('CATALOG')


def stream(url, sink, limit, cancel=lambda: False):
    trusted_url(url)
    start = time.monotonic(); count = 0; digest = hashlib.sha256()
    request = Request(url, headers={'Accept-Encoding':'identity', 'User-Agent':'XCMate-Theme/1'})
    with build_opener(NoRedirect()).open(request, timeout=10) as response:
        if response.status != 200 or response.headers.get('Content-Encoding', 'identity') != 'identity': fail('DOWNLOAD')
        advertised = response.headers.get('Content-Length')
        if advertised and (not advertised.isdigit() or int(advertised) > limit): fail('LIMIT')
        while True:
            if cancel(): fail('CANCELLED')
            if time.monotonic()-start > 120: fail('DOWNLOAD')
            chunk = response.read1(min(65536, limit-count+1))
            if not chunk: break
            count += len(chunk)
            if count > limit: fail('LIMIT')
            sink.write(chunk); digest.update(chunk)
        if advertised and count != int(advertised): fail('DOWNLOAD')
    return digest.hexdigest(), count


def catalogue(core, cancel=lambda: False):
    import io
    sink = io.BytesIO()
    try: stream(CATALOG, sink, MAX_METADATA, cancel)
    except HTTPError as error:
        fail('CATALOG_NOT_PUBLISHED' if error.code==404 else 'DOWNLOAD')
    except (URLError,TimeoutError): fail('DOWNLOAD')
    return parse_catalogue(json_object(sink.getvalue()), core)


def parse_catalogue(data, core):
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1 or not isinstance(data.get('themes'), list): fail('CATALOG')
    if len(data['themes']) > 32: fail('LIMIT')
    result = []; identities = set()
    for row in data['themes']:
        if not isinstance(row, dict) or row.get('approved') is not True: continue
        if not isinstance(row.get('id'), str) or not re.fullmatch('[a-z][a-z0-9-]{0,47}', row['id']): fail('CATALOG')
        name = row.get('name')
        if not isinstance(name, str) or not 1 <= len(name) <= 80 or any(ord(c)<32 or c in '[]' for c in name): fail('CATALOG')
        version(row.get('version')); trusted_url(row.get('url'))
        if not isinstance(row.get('sha256'), str) or not re.fullmatch('[a-f0-9]{64}', row['sha256']): fail('CATALOG')
        if type(row.get('bytes')) is not int or not 0 < row['bytes'] <= MAX_ZIP: fail('CATALOG')
        support = row.get('supported_xcmate')
        if not isinstance(support, dict): fail('CATALOG')
        identity = (row['id'], version(row['version']))
        if identity in identities: fail('CATALOG')
        identities.add(identity)
        low,high=version(support.get('min')),version(support.get('max_exclusive'))
        if low>=high: fail('CATALOG')
        if low <= version(core) < high: result.append(row)
    return result


def download(row, cancel=lambda: False):
    from theme_store import root, install, check_space
    class ReservedSink:
        def __init__(self, target): self.target=target
        def write(self, data):
            check_space(len(data))
            return self.target.write(data)
    fd, temp = tempfile.mkstemp(prefix='.download-', dir=root())
    try:
        with os.fdopen(fd, 'wb') as sink:
            digest, size = stream(row['url'], ReservedSink(sink), min(row['bytes'], MAX_ZIP), cancel)
        if digest != row['sha256'] or size != row['bytes']: fail('CHECKSUM')
        # Prevent catalogue confusion: inspect identity before installing.
        import zipfile
        from theme_package import check_archive, check_container
        from theme_store import core_version
        check_container(temp)
        try:
            with zipfile.ZipFile(temp) as archive:
                spec, _ = check_archive(archive, core_version())
                if spec['id'] != row['id'] or spec['version'] != row['version']: fail('CATALOG')
        except (zipfile.BadZipFile, EOFError): fail('ARCHIVE')
        return install(temp, row['sha256'], cancel)
    finally:
        if os.path.exists(temp): os.unlink(temp)
