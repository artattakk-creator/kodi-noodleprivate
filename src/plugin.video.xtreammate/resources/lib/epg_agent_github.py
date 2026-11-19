"""Read and validate immutable XMLTV and artwork candidates from private GitHub."""
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
ARTWORK_FILE = "xcmate-artwork.jsonl.gz"
EXPECTED_SOURCES = 3
MAX_GZIP_BYTES = 48 * 1024 * 1024
MAX_XML_UNCOMPRESSED = 768 * 1024 * 1024
MAX_ARTWORK_UNCOMPRESSED = 192 * 1024 * 1024
MAX_MANIFEST_BYTES = 65536
MAX_SIDE_RECORDS = 500000
USER_AGENT = "XCMate-EPG-Agent/1.0"
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
GIT_REF_RE = re.compile(r"^[a-f0-9]{40}$")
ETAG_RE = re.compile(r'^(?:W/)?"[!-~]{1,128}"$')
ROLE_SET = frozenset(("poster", "backdrop", "fanart", "episode_still",
                      "thumb", "channel_logo", "clearlogo", "season_poster"))


class DeliveryError(ValueError):
    """Only a short, non-credential-bearing code may cross UI/log boundaries."""
    def __init__(self, code):
        self.code = str(code)
        super().__init__(self.code)


def packaged_token_path():
    # resources/lib/epg_agent_github.py -> resources/private/<file>.
    # Inject only into the explicitly authorised private Kodi build, not Git.
    return Path(__file__).resolve().parent.parent / "private" / "xcmate_epg_read_token.txt"


def read_packaged_token(path=None):
    path = Path(path or packaged_token_path())
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
    if path not in ("manifest.json", XMLTV_FILE, ARTWORK_FILE):
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
    response_etag = getattr(response, "headers", {}).get("ETag", "")
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
    if obj.get("status") != "PRIVATE_READY" or obj.get("schema_version") != 2:
        raise DeliveryError("UNSUPPORTED_MANIFEST_VERSION")
    if obj.get("file") != XMLTV_FILE:
        raise DeliveryError("INVALID_MANIFEST")
    if "payload_ref" in obj and (not isinstance(obj["payload_ref"], str) or
                                 not GIT_REF_RE.fullmatch(obj["payload_ref"])):
        raise DeliveryError("INVALID_PAYLOAD_REF")
    try:
        valid = (type(obj["bytes"]) is int and 0 < obj["bytes"] <= MAX_GZIP_BYTES and
                 type(obj["channel_count"]) is int and 1 <= obj["channel_count"] <= 100000 and
                 type(obj["programme_count"]) is int and 1 <= obj["programme_count"] <= 3000000 and
                 type(obj["source_count"]) is int and obj["source_count"] >= EXPECTED_SOURCES and
                 bool(SHA_RE.fullmatch(obj["sha256"])))
        art = obj["artwork"]
        valid = (valid and isinstance(art, dict) and
                 art.get("file") == ARTWORK_FILE and
                 type(art["bytes"]) is int and 0 < art["bytes"] <= MAX_GZIP_BYTES and
                 type(art["records"]) is int and 1 <= art["records"] <= MAX_SIDE_RECORDS and
                 bool(SHA_RE.fullmatch(art["sha256"])))
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise DeliveryError("INCOMPLETE_FULL_EPG_MANIFEST")
    return obj, response_etag


def probe(token_path=None, opener=None):
    """Read-only status probe, no data download when server is PRIVATE_PENDING."""
    token = read_packaged_token(token_path)
    return _read_manifest(token, opener)[0]


def _download_to(path, token, dest, expected_size, expected_sha, opener=None, *,
                 payload_ref="", reuse=None, cancel=lambda: False):
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
            if reuse and reuse.is_file() and not reuse.is_symlink():
                response = reuse.open("rb")
            else:
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


def _validate_gzip(path, max_uncompressed, cancel=lambda: False):
    if path.stat().st_size == 0:
        raise DeliveryError("EMPTY_PAYLOAD")
    count = 0
    try:
        with gzip.open(str(path), "rb") as stream:
            while True:
                if cancel():
                    raise InterruptedError("CANCELLED")
                data = stream.read(65536)
                if not data:
                    break
                count += len(data)
                if count > max_uncompressed:
                    raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
    except InterruptedError:
        raise
    except (OSError, EOFError):
        raise DeliveryError("INVALID_GZIP") from None
    if not count:
        raise DeliveryError("EMPTY_PAYLOAD")


def _check_xmltv(path, manifest, cancel=lambda: False):
    """Full SAX parse; no arbitrary 150k-programme legacy in-memory limit."""
    from xmltv_stream import parse as parse_xmltv_stream
    channel_ids = set()
    def channel(cid, _name):
        if not cid or len(cid) > 512 or cid in channel_ids:
            raise DeliveryError("XMLTV_CHANNEL_INVALID")
        channel_ids.add(cid)
    def programme(event):
        if event["channel"] not in channel_ids or not event["name"]:
            raise DeliveryError("XMLTV_EVENT_INVALID")
    try:
        with open(path, "rb") as stream:
            def progress(counts):
                if counts["bytes"] > MAX_XML_UNCOMPRESSED:
                    raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
            counts = parse_xmltv_stream(stream, channel, programme,
                                        cancel=cancel, max_seconds=720, progress=progress)
    except (DeliveryError, InterruptedError):
        raise
    except (OSError, ValueError, EOFError, TimeoutError):
        raise DeliveryError("XMLTV_INVALID") from None
    if (counts["skipped"] or counts["programmes"] != manifest["programme_count"] or
            len(channel_ids) != manifest["channel_count"]):
        raise DeliveryError("XMLTV_COUNT_MISMATCH")


def _check_artwork(path, expected_records, cancel=lambda: False):
    count = 0
    total = 0
    try:
        with gzip.open(str(path), "rt", encoding="utf-8") as source:
            while line := source.readline(131073):
                if cancel():
                    raise InterruptedError("CANCELLED")
                total += len(line.encode("utf-8"))
                if total > MAX_ARTWORK_UNCOMPRESSED:
                    raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
                if len(line) > 131072:
                    raise DeliveryError("ARTWORK_RECORD_TOO_LARGE")
                item = json.loads(line)
                if (not isinstance(item, dict) or item.get("type") not in ROLE_SET or
                        not isinstance(item.get("url"), str) or
                        not item["url"].startswith("https://")):
                    raise DeliveryError("ARTWORK_RECORD_INVALID")
                count += 1
                if count > MAX_SIDE_RECORDS:
                    raise DeliveryError("ARTWORK_RECORD_LIMIT")
    except (DeliveryError, InterruptedError):
        raise
    except (OSError, ValueError, UnicodeError, EOFError):
        raise DeliveryError("ARTWORK_INVALID") from None
    if count != expected_records:
        raise DeliveryError("ARTWORK_COUNT_MISMATCH")


def generation_of(manifest):
    """Cover both files: artwork updates can leave the programme gzip unchanged."""
    return hashlib.sha256((manifest["sha256"] + manifest["artwork"]["sha256"]).encode()).hexdigest()


def candidate_path(directory, generation):
    if not isinstance(generation, str) or not SHA_RE.fullmatch(generation):
        return None
    root = Path(directory)
    if root.is_symlink():
        return None
    folder = root / ("candidate-" + generation)
    if folder.is_symlink() or not folder.is_dir():
        return None
    for name in (XMLTV_FILE, ARTWORK_FILE, "manifest.json"):
        path = folder / name
        if path.is_symlink() or not path.is_file():
            return None
    return folder


def stage_full_candidate(directory, token_path=None, opener=None, *,
                         known="", etag="", cancel=lambda: False):
    """Return the current generation or stage both validated payloads privately."""
    token = read_packaged_token(token_path)
    root = Path(directory)
    previous = candidate_path(root, known)
    manifest, response_etag = _read_manifest(token, opener,
                                            etag=etag if previous else "",
                                            cancel=cancel)
    response = {"status": manifest["status"], "etag": response_etag}
    if manifest["status"] != "PRIVATE_READY":
        if "reason" in manifest:
            response["reason"] = manifest["reason"]
        return response
    generation = generation_of(manifest)
    response.update(generation=generation, channels=manifest["channel_count"],
                    programmes=manifest["programme_count"],
                    artwork_records=manifest["artwork"]["records"])
    if candidate_path(root, generation):
        return dict(response, status="UNCHANGED")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    previous_manifest = {}
    if previous:
        try:
            with (previous / "manifest.json").open("rb") as stream:
                previous_manifest = json.loads(stream.read(MAX_MANIFEST_BYTES))
        except (OSError, ValueError):
            previous = None
    from import_budget import check_space
    check_space(str(root / "manifest.json"), manifest["bytes"] + manifest["artwork"]["bytes"])
    stage = Path(tempfile.mkdtemp(prefix=".candidate-", dir=root))
    try:
        for filename, spec, old_spec, limit in (
                (XMLTV_FILE, manifest, previous_manifest, MAX_XML_UNCOMPRESSED),
                (ARTWORK_FILE, manifest["artwork"], previous_manifest.get("artwork", {}),
                 MAX_ARTWORK_UNCOMPRESSED)):
            reuse = previous / filename if previous and old_spec.get("sha256") == spec["sha256"] else None
            options = dict(payload_ref=manifest.get("payload_ref", ""), cancel=cancel)
            try:
                item = _download_to(filename, token, stage, spec["bytes"], spec["sha256"],
                                    opener, reuse=reuse, **options)
            except DeliveryError as exc:
                if reuse is None or exc.code != "CHECKSUM_OR_SIZE_MISMATCH":
                    raise
                item = _download_to(filename, token, stage, spec["bytes"], spec["sha256"],
                                    opener, **options)
            _validate_gzip(item, limit, cancel)
            if filename == XMLTV_FILE:
                _check_xmltv(item, manifest, cancel)
            else:
                _check_artwork(item, spec["records"], cancel)
            os.replace(item, stage / filename)
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
