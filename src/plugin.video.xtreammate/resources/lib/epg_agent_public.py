"""Anonymous, repository-scoped transport for the public Schema-5 EPG."""
import hashlib
import json
import os
from pathlib import Path
import re
from urllib import error, parse, request

from epg_agent_github import (
    DeliveryError, ETAG_RE, MAX_MANIFEST_BYTES, USER_AGENT, _consume,
)

REPO = "artattakk-creator/xcmate-epg-public"
MANIFEST_URL = "https://raw.githubusercontent.com/" + REPO + "/main/manifest.json"
RELEASE_URL = "https://github.com/" + REPO + "/releases/download/"
DELIVERY = "public-github-release-assets"
CDN_HOSTS = {"objects.githubusercontent.com", "release-assets.githubusercontent.com"}
FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}\.xml\.gz\Z")


def asset_url(record, tag):
    name = record.get("file")
    expected = RELEASE_URL + tag + "/" + name if isinstance(name, str) else ""
    urls = [record[key] for key in ("download_url", "browser_download_url", "url") if key in record]
    if (not isinstance(name, str) or not FILENAME.fullmatch(name) or not urls
            or any(url != expected for url in urls)):
        raise DeliveryError("PUBLIC_INVALID_ASSET_URL", phase="manifest")
    return expected


class _ReleaseRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        destination = parse.urlsplit(newurl)
        if (not req.full_url.startswith(RELEASE_URL) or destination.scheme != "https"
                or destination.netloc not in CDN_HOSTS or destination.fragment):
            raise DeliveryError("PUBLIC_UNTRUSTED_REDIRECT", phase="asset")
        return request.Request(newurl, headers={"User-Agent": USER_AGENT}, method="GET")


def _open(url, opener, phase, etag=""):
    headers = {"User-Agent": USER_AGENT}
    if etag and ETAG_RE.fullmatch(etag):
        headers["If-None-Match"] = etag
    req = request.Request(url, headers=headers, method="GET")
    try:
        response = (opener or request.build_opener(_ReleaseRedirect())).open(req, timeout=35)
        status = response.status
        if status != 200:
            response.close()
            raise DeliveryError("PUBLIC_ENDPOINT_HTTP_ERROR", phase=phase, http_status=status)
        return response
    except error.HTTPError as exc:
        status = exc.code
        exc.close()
        if status == 304 and "If-None-Match" in headers and phase == "manifest":
            return None
        raise DeliveryError("PUBLIC_ENDPOINT_HTTP_ERROR", phase=phase, http_status=status) from None
    except DeliveryError:
        raise
    except OSError:
        raise DeliveryError("PUBLIC_ENDPOINT_NETWORK_ERROR", phase=phase) from None


def _read(response, limit, sink, cancel, phase):
    try:
        _consume(response, limit, sink, cancel)
    except DeliveryError as exc:
        code = ("PUBLIC_ENDPOINT_NETWORK_ERROR" if exc.code == "PRIVATE_ENDPOINT_NETWORK_ERROR"
                else exc.code)
        raise DeliveryError(code, phase=phase, http_status=response.status) from None


def download_asset(record, tag, dest, opener, cancel, *, on_http=None, on_bytes=None):
    target = dest / record["file"]
    response = _open(asset_url(record, tag), opener, "asset")
    if on_http is not None:
        on_http(response.status)
    digest = hashlib.sha256()
    with response, target.open("xb") as output:
        def sink(data):
            output.write(data)
            digest.update(data)
            if on_bytes is not None:
                on_bytes(output.tell())
        _read(response, record["bytes"], sink, cancel, "asset")
        output.flush()
        os.fsync(output.fileno())
    if target.stat().st_size != record["bytes"] or digest.hexdigest() != record["sha256"]:
        raise DeliveryError("CHECKSUM_OR_SIZE_MISMATCH", phase="asset", http_status=response.status)
    return target


def stage_public_candidate(directory, opener=None, *, known="", etag="", cancel=lambda: False, progress=None):
    from epg_agent_hub5 import stage

    response = _open(MANIFEST_URL, opener, "manifest", etag)
    if response is None:
        return dict(status="NOT_MODIFIED", etag=etag)
    received = response.headers.get("ETag") or ""
    received = received if ETAG_RE.fullmatch(received) else ""
    pieces = []
    _read(response, MAX_MANIFEST_BYTES, pieces.append, cancel, "manifest")
    try:
        data = json.loads(b"".join(pieces))
    except (ValueError, RecursionError):
        raise DeliveryError("PUBLIC_INVALID_MANIFEST", phase="manifest") from None
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] != 5 or data.get("schema") != "gsmedia-hub-github-v3"
            or data.get("repo") != REPO or data.get("delivery") != DELIVERY):
        raise DeliveryError("PUBLIC_INVALID_MANIFEST", phase="manifest")
    if data.get("status") == "PUBLIC_PENDING":
        if any(data.get(field) != [] for field in ("profiles", "variants", "files")):
            raise DeliveryError("PUBLIC_INVALID_MANIFEST", phase="manifest")
        return dict(status="PUBLIC_PENDING", etag="")
    if data.get("status") != "PUBLIC_READY":
        raise DeliveryError("PUBLIC_INVALID_MANIFEST", phase="manifest")
    return stage(Path(directory), None, data, received, opener, known=known, cancel=cancel, progress=progress)
