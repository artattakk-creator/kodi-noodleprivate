"""Read one immutable, verified XMLTV generation from private GitHub."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import tempfile
from urllib import error, parse, request


API_BASE = ("https://api.github.com/repos/"
            "artattakk-creator/xcmate-epg-private/contents/")
MANIFEST_URL = API_BASE + "manifest.json"
XMLTV_FILE = "xcmate-epg.xml.gz"
SCHEMA_VERSION = 3
EXPECTED_SOURCES = 3
MAX_GZIP_BYTES = 48 * 1024 * 1024
MAX_XML_UNCOMPRESSED = 768 * 1024 * 1024
MAX_MANIFEST_BYTES = 65536
USER_AGENT = "XCMate-EPG-Agent/3.0"
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
GIT_REF_RE = re.compile(r"^[a-f0-9]{40}$")
ETAG_RE = re.compile(r'^(?:W/)?"[!-~]{1,128}"$')
XMLTV_IMAGE_TYPES = ("poster", "backdrop", "still", "person", "character")
IMAGE_COUNT_KEYS = (*XMLTV_IMAGE_TYPES, "programme_icon", "channel_logo")


class DeliveryError(ValueError):
    """Only a short, non-credential-bearing code may cross UI/log boundaries."""
    def __init__(self, code):
        self.code = str(code)
        super().__init__(self.code)


def read_token(path):
    if path is None:
        raise DeliveryError("AUTH_NOT_PROVISIONED")
    path = Path(path)
    try:
        if path.is_symlink() or not path.is_file():
            raise DeliveryError("AUTH_NOT_PROVISIONED")
        if path.stat().st_size > 512:
            raise DeliveryError("AUTH_INVALID")
        value = path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError):
        raise DeliveryError("AUTH_NOT_PROVISIONED") from None
    if (not 20 <= len(value) <= 400 or
            not re.fullmatch(r"[A-Za-z0-9_]+", value) or
            not value.startswith(("github_pat_", "ghp_", "ghu_", "ghs_"))):
        raise DeliveryError("AUTH_INVALID")
    return value


class _LimitedGitHubRedirect(request.HTTPRedirectHandler):
    """Remove Authorization entirely on allowed GitHub binary CDN redirects."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        dest = parse.urlsplit(newurl)
        if (dest.scheme != "https" or dest.username or dest.password or
                dest.hostname not in ("objects.githubusercontent.com",
                                      "release-assets.githubusercontent.com")):
            raise DeliveryError("UNTRUSTED_REDIRECT")
        return request.Request(newurl, headers={"User-Agent": USER_AGENT},
                               method="GET")


def _open(path, token, opener=None, *, etag="", payload_ref=""):
    if path not in ("manifest.json", XMLTV_FILE):
        raise DeliveryError("UNEXPECTED_REMOTE_PATH")
    if not token:
        raise DeliveryError("AUTH_NOT_PROVISIONED")
    url = API_BASE + path
    if payload_ref:
        if path == "manifest.json" or not GIT_REF_RE.fullmatch(payload_ref):
            raise DeliveryError("INVALID_PAYLOAD_REF")
        url += "?ref=" + payload_ref
    req = request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }, method="GET")
    if etag and ETAG_RE.fullmatch(etag):
        req.add_header("If-None-Match", etag)
    getter = opener or request.build_opener(_LimitedGitHubRedirect())
    try:
        return getter.open(req, timeout=35)
    except error.HTTPError as exc:
        code = exc.code
        exc.close()
        if code == 304 and etag and path == "manifest.json":
            return None
        if code in (401, 403, 404):
            raise DeliveryError("PRIVATE_ENDPOINT_ACCESS_DENIED") from None
        if code in (429, 500, 502, 503, 504):
            raise DeliveryError("PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE") from None
        raise DeliveryError("PRIVATE_ENDPOINT_HTTP_ERROR") from None
    except DeliveryError:
        raise
    except (OSError, ValueError, TimeoutError):
        raise DeliveryError("PRIVATE_ENDPOINT_NETWORK_ERROR") from None


def _consume(response, max_bytes, sink, cancel=lambda: False):
    total = 0
    deadline = time.monotonic() + 240
    with response:
        while True:
            if cancel():
                raise InterruptedError("CANCELLED")
            if time.monotonic() > deadline:
                raise DeliveryError("PRIVATE_ENDPOINT_NETWORK_ERROR")
            try:
                part = response.read(min(65536, max_bytes + 1 - total))
            except (OSError, ValueError):
                raise DeliveryError("PRIVATE_ENDPOINT_NETWORK_ERROR") from None
            if not part:
                break
            total += len(part)
            if total > max_bytes:
                raise DeliveryError("DOWNLOAD_SIZE_LIMIT")
            sink(part)
    return total


def _read_manifest(token, opener=None, *, etag="", cancel=lambda: False):
    pieces = []
    response = _open("manifest.json", token, opener, etag=etag)
    if response is None:
        return {"status": "NOT_MODIFIED"}, etag
    response_etag = getattr(response, "headers", {}).get("ETag") or ""
    if not ETAG_RE.fullmatch(response_etag):
        response_etag = ""
    _consume(response, MAX_MANIFEST_BYTES, pieces.append, cancel)
    try:
        obj = json.loads(b"".join(pieces))
    except (ValueError, UnicodeError):
        raise DeliveryError("INVALID_MANIFEST") from None
    if not isinstance(obj, dict):
        raise DeliveryError("INVALID_MANIFEST")
    if obj.get("status") == "PRIVATE_PENDING":
        if obj.get("file") != XMLTV_FILE:
            raise DeliveryError("INVALID_MANIFEST")
        reason = obj.get("reason_code")
        return {"status": "PRIVATE_PENDING", "reason": (reason if reason ==
                "PRODUCTION_DATA_NOT_APPROVED" else "PRIVATE_PENDING")}, response_etag
    if obj.get("status") != "PRIVATE_READY" or obj.get("schema_version") != SCHEMA_VERSION:
        raise DeliveryError("UNSUPPORTED_MANIFEST_VERSION")
    _validate_manifest(obj)
    return obj, response_etag


def _utc(value):
    if not isinstance(value, str) or not 20 <= len(value) <= 35:
        raise ValueError("INVALID_UTC")
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError("INVALID_UTC")
    return date.timestamp()


def _validate_manifest(obj):
    if obj.get("file") != XMLTV_FILE:
        raise DeliveryError("INVALID_MANIFEST")
    try:
        roles = obj["image_counts"]
        _, start, stop = (_utc(obj["generated_at_utc"]), _utc(obj["window"]["start_utc"]),
                           _utc(obj["window"]["stop_utc"]))
        valid = (type(obj["bytes"]) is int and 0 < obj["bytes"] <= MAX_GZIP_BYTES and
                 type(obj["channel_count"]) is int and 1 <= obj["channel_count"] <= 100000 and
                 type(obj["programme_count"]) is int and 1 <= obj["programme_count"] <= 3000000 and
                 type(obj["source_count"]) is int and EXPECTED_SOURCES <= obj["source_count"] <= 32 and
                 bool(SHA_RE.fullmatch(obj["sha256"])) and obj["revision"] == obj["sha256"] and
                 bool(GIT_REF_RE.fullmatch(obj["payload_ref"])) and start < stop and
                 start.is_integer() and stop.is_integer() and
                 isinstance(roles, dict) and set(roles) == set(IMAGE_COUNT_KEYS) and
                 all(type(count) is int and 0 <= count <= 16_000_000 for count in roles.values()))
    except (KeyError, TypeError, ValueError, OverflowError):
        valid = False
    if not valid:
        raise DeliveryError("INCOMPLETE_FULL_EPG_MANIFEST")


def probe(token_path=None, opener=None):
    """Read-only status probe, no data download when server is PRIVATE_PENDING."""
    token = read_token(token_path)
    return _read_manifest(token, opener)[0]


def _download_to(path, token, dest, expected_size, expected_sha, opener=None, *,
                 payload_ref="", cancel=lambda: False):
    fd, name = tempfile.mkstemp(prefix=".xcmate-agent-", dir=str(dest))
    digest = hashlib.sha256()
    count = 0
    try:
        with os.fdopen(fd, "wb") as stream:
            def sink(chunk):
                nonlocal count
                stream.write(chunk)
                digest.update(chunk)
                count += len(chunk)
            response = _open(path, token, opener, payload_ref=payload_ref)
            _consume(response, expected_size, sink, cancel)
            stream.flush()
            os.fsync(stream.fileno())
        if count != expected_size or digest.hexdigest() != expected_sha:
            raise DeliveryError("CHECKSUM_OR_SIZE_MISMATCH")
        return Path(name)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


def _check_xmltv(path, manifest, cancel):
    """Validate every event and image count in one bounded streaming pass."""
    from xmltv_stream import parse as parse_xmltv_stream
    from epg_agent100_art import validator

    channel_ids = set()
    images = dict.fromkeys(IMAGE_COUNT_KEYS, 0)
    first = last = None
    validate = validator()
    expanded_limit = min(MAX_XML_UNCOMPRESSED, max(8 * 1024 * 1024, manifest["bytes"] * 512))

    def image(role, url, system=""):
        if not validate(url, system):
            raise DeliveryError("ARTWORK_REFERENCE_INVALID")
        images[role] += 1

    def channel(cid, _name):
        if not cid or len(cid) > 512 or cid in channel_ids or len(channel_ids) >= manifest["channel_count"]:
            raise DeliveryError("XMLTV_CHANNEL_INVALID")
        channel_ids.add(cid)

    def programme(event):
        nonlocal first, last
        if event["channel"] not in channel_ids or not event["name"]:
            raise DeliveryError("XMLTV_EVENT_INVALID")
        start, stop = event["start_timestamp"], event["stop_timestamp"]
        first = start if first is None else min(first, start)
        last = stop if last is None else max(last, stop)
        for reference in event["images"]:
            image(reference["type"], reference["url"], reference["system"])
        for url in event["icons"]:
            image("programme_icon", url)

    def progress(counts):
        if counts["bytes"] > expanded_limit:
            raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
        if counts["programmes"] > manifest["programme_count"]:
            raise DeliveryError("XMLTV_COUNT_MISMATCH")

    try:
        with path.open("rb") as stream:
            if stream.read(2) != b"\x1f\x8b":
                raise DeliveryError("INVALID_GZIP")
            stream.seek(0)
            counts = parse_xmltv_stream(
                stream, channel, programme, cancel=cancel, max_seconds=720,
                progress=progress, include_icons=True, include_images=True,
                channel_image=lambda cid, url: image("channel_logo", url),
                strict_images=True,
            )
    except (gzip.BadGzipFile, EOFError):
        raise DeliveryError("INVALID_GZIP") from None
    except (DeliveryError, InterruptedError):
        raise
    except (OSError, ValueError):
        raise DeliveryError("XMLTV_INVALID") from None
    if (counts["skipped"] or counts["programmes"] != manifest["programme_count"]
            or len(channel_ids) != manifest["channel_count"]):
        raise DeliveryError("XMLTV_COUNT_MISMATCH")
    if images != manifest["image_counts"]:
        raise DeliveryError("ARTWORK_COUNT_MISMATCH")
    if (first, last) != (_utc(manifest["window"]["start_utc"]), _utc(manifest["window"]["stop_utc"])):
        raise DeliveryError("XMLTV_WINDOW_MISMATCH")


def candidate_path(directory, generation):
    if not isinstance(generation, str) or not SHA_RE.fullmatch(generation):
        return None
    root = Path(directory)
    if root.is_symlink():
        return None
    folder = root / ("candidate-" + generation)
    if folder.is_symlink() or not folder.is_dir():
        return None
    for name in (XMLTV_FILE, "manifest.json"):
        path = folder / name
        if path.is_symlink() or not path.is_file():
            return None
    return folder


def local_manifest(folder):
    if folder is None:
        return {}
    try:
        with (folder / "manifest.json").open("rb") as stream:
            raw = stream.read(MAX_MANIFEST_BYTES + 1)
        value = json.loads(raw) if len(raw) <= MAX_MANIFEST_BYTES else {}
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def stage_full_candidate(directory, token_path=None, opener=None, *,
                         known="", etag="", cancel=lambda: False):
    """Stage one GZIP and its manifest. Keep prior V1/V2 snapshots offline."""
    token = read_token(token_path)
    root = Path(directory)
    previous = local_manifest(candidate_path(root, known))
    manifest, response_etag = _read_manifest(token, opener,
        etag=etag if previous.get("schema_version") == SCHEMA_VERSION else "", cancel=cancel)
    response = {"status": manifest["status"], "etag": response_etag}
    if manifest["status"] != "PRIVATE_READY":
        if "reason" in manifest:
            response["reason"] = manifest["reason"]
        return response
    generation = manifest["revision"]
    response.update(generation=generation, channels=manifest["channel_count"],
                    programmes=manifest["programme_count"], image_counts=manifest["image_counts"],
                    artwork_records=sum(manifest["image_counts"].values()))
    existing = candidate_path(root, generation)
    if existing is not None:
        remembered = local_manifest(existing)
        fields = ("schema_version", "sha256", "revision", "bytes", "channel_count",
                  "programme_count", "image_counts", "window")
        if any(remembered.get(field) != manifest[field] for field in fields):
            raise DeliveryError("XMLTV_MANIFEST_CHANGED_WITHOUT_REVISION")
        if (existing / XMLTV_FILE).stat().st_size != manifest["bytes"]:
            raise DeliveryError("LOCAL_LASTGOOD_SIZE_MISMATCH")
        return dict(response, status="UNCHANGED")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    from import_budget import check_space
    check_space(str(root / "manifest.json"), manifest["bytes"])
    stage = Path(tempfile.mkdtemp(prefix=".candidate-", dir=root))
    try:
        item = _download_to(XMLTV_FILE, token, stage, manifest["bytes"], manifest["sha256"],
                            opener, payload_ref=manifest["payload_ref"], cancel=cancel)
        _check_xmltv(item, manifest, cancel)
        os.replace(item, stage / XMLTV_FILE)
        with (stage / "manifest.json").open("w", encoding="utf-8") as stream:
            json.dump(manifest, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        final = root / ("candidate-" + generation)
        os.replace(stage, final)
        return dict(response, status="STAGED_FULL_CANDIDATE", path=str(final))
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
