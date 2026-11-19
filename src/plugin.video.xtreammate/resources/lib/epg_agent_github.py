"""GitHub-only private XCMate EPG delivery: complete candidate staging, never a live cutover.

This module intentionally performs NO Kodi service registration and NO guide mutation.
Full client integration must stage/import/match/commit and pass device gates first.
Never place real GitHub credentials in this repository.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
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


def _open(path, token, opener=None):
    if path not in ("manifest.json", XMLTV_FILE, ARTWORK_FILE):
        raise DeliveryError("UNEXPECTED_REMOTE_PATH")
    if not token:
        raise DeliveryError("AUTH_NOT_PROVISIONED")
    url = API_BASE + path
    req = request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }, method="GET")
    getter = opener or request.build_opener(_LimitedGitHubRedirect())
    try:
        return getter.open(req, timeout=35)
    except error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            raise DeliveryError("PRIVATE_ENDPOINT_ACCESS_DENIED") from None
        if exc.code in (429, 500, 502, 503, 504):
            raise DeliveryError("PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE") from None
        raise DeliveryError("PRIVATE_ENDPOINT_HTTP_ERROR") from None
    except DeliveryError:
        raise
    except (OSError, ValueError, TimeoutError):
        raise DeliveryError("PRIVATE_ENDPOINT_NETWORK_ERROR") from None


def _consume(response, max_bytes, sink):
    total = 0
    with response:
        while True:
            part = response.read(min(65536, max_bytes + 1 - total))
            if not part:
                break
            total += len(part)
            if total > max_bytes:
                raise DeliveryError("DOWNLOAD_SIZE_LIMIT")
            sink(part)
    return total


def _read_manifest(token, opener=None):
    pieces = []
    _consume(_open("manifest.json", token, opener), MAX_MANIFEST_BYTES, pieces.append)
    try:
        obj = json.loads(b"".join(pieces))
    except (ValueError, UnicodeError):
        raise DeliveryError("INVALID_MANIFEST") from None
    if not isinstance(obj, dict):
        raise DeliveryError("INVALID_MANIFEST")
    if obj.get("status") == "PRIVATE_PENDING":
        if obj.get("file") != XMLTV_FILE:
            raise DeliveryError("INVALID_MANIFEST")
        return {"status": "PRIVATE_PENDING", "reason": str(obj.get("reason_code") or "")[:80]}
    if obj.get("status") != "PRIVATE_READY" or obj.get("schema_version") != 2:
        raise DeliveryError("UNSUPPORTED_MANIFEST_VERSION")
    if obj.get("file") != XMLTV_FILE:
        raise DeliveryError("INVALID_MANIFEST")
    try:
        valid = (int(obj["bytes"]) > 0 and int(obj["bytes"]) <= MAX_GZIP_BYTES and
                 int(obj["channel_count"]) >= 1 and int(obj["programme_count"]) >= 1 and
                 int(obj["source_count"]) >= EXPECTED_SOURCES and
                 bool(SHA_RE.fullmatch(obj["sha256"])))
        art = obj["artwork"]
        valid = (valid and isinstance(art, dict) and
                 art.get("file") == ARTWORK_FILE and
                 0 < int(art["bytes"]) <= MAX_GZIP_BYTES and
                 int(art["records"]) >= 1 and
                 bool(SHA_RE.fullmatch(art["sha256"])))
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise DeliveryError("INCOMPLETE_FULL_EPG_MANIFEST")
    return obj


def probe(token_path=None, opener=None):
    """Read-only status probe, no data download when server is PRIVATE_PENDING."""
    token = read_packaged_token(token_path)
    return _read_manifest(token, opener)


def _download_to(path, token, dest, expected_size, expected_sha, opener=None):
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
            _consume(_open(path, token, opener), expected_size, sink)
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


def _validate_gzip(path, max_uncompressed):
    if path.stat().st_size == 0:
        raise DeliveryError("EMPTY_PAYLOAD")
    count = 0
    try:
        with gzip.open(str(path), "rb") as stream:
            while True:
                data = stream.read(65536)
                if not data:
                    break
                count += len(data)
                if count > max_uncompressed:
                    raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
    except (OSError, EOFError):
        raise DeliveryError("INVALID_GZIP") from None
    if not count:
        raise DeliveryError("EMPTY_PAYLOAD")


def _check_xmltv(path, manifest):
    """Full SAX parse; no arbitrary 150k-programme legacy in-memory limit."""
    from xmltv_stream import parse as parse_xmltv_stream
    channel_ids = set()
    def channel(cid, _name):
        if cid:
            channel_ids.add(cid)
    def programme(_event):
        return
    try:
        with open(path, "rb") as stream:
            def progress(counts):
                if counts["bytes"] > MAX_XML_UNCOMPRESSED:
                    raise DeliveryError("UNCOMPRESSED_SIZE_LIMIT")
            counts = parse_xmltv_stream(stream, channel, programme,
                                        max_seconds=720, progress=progress)
    except DeliveryError:
        raise
    except (OSError, ValueError, EOFError, TimeoutError):
        raise DeliveryError("XMLTV_INVALID") from None
    if (counts["programmes"] != manifest["programme_count"] or
            len(channel_ids) != manifest["channel_count"]):
        raise DeliveryError("XMLTV_COUNT_MISMATCH")


def _check_artwork(path, expected_records):
    count = 0
    total = 0
    try:
        with gzip.open(str(path), "rt", encoding="utf-8") as source:
            for line in source:
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
    except DeliveryError:
        raise
    except (OSError, ValueError, UnicodeError, EOFError):
        raise DeliveryError("ARTWORK_INVALID") from None
    if count != expected_records:
        raise DeliveryError("ARTWORK_COUNT_MISMATCH")


def stage_full_candidate(directory, token_path=None, opener=None):
    """Download both complete files into a PRIVATE candidate; no live-EPG mutation.

    Source-ID mapping, full provider catalogue reconciliation, SQL transaction and
    local LastGood promotion belong to the separately device-tested importer.
    """
    token = read_packaged_token(token_path)
    manifest = _read_manifest(token, opener)
    if manifest["status"] == "PRIVATE_PENDING":
        return manifest
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    candidates = []
    try:
        for filename, spec in ((XMLTV_FILE, manifest),
                               (ARTWORK_FILE, manifest["artwork"])):
            item = _download_to(filename, token, root, spec["bytes"], spec["sha256"], opener)
            candidates.append(item)
            _validate_gzip(item, MAX_XML_UNCOMPRESSED if filename == XMLTV_FILE
                           else MAX_ARTWORK_UNCOMPRESSED)
        _check_xmltv(candidates[0], manifest)
        _check_artwork(candidates[1], manifest["artwork"]["records"])
        # The two files are staged under one generation and deliberately are NOT
        # promoted to current/LastGood. No incomplete candidate is published.
        generation = manifest["sha256"][:16]
        final = root / ("candidate-" + generation)
        if final.exists():
            raise DeliveryError("CANDIDATE_ALREADY_EXISTS")
        stage = root / (".candidate-" + generation)
        stage.mkdir(exist_ok=False)
        try:
            for source, filename in zip(candidates, (XMLTV_FILE, ARTWORK_FILE)):
                os.replace(source, stage / filename)
            (stage / "manifest.json").write_text(
                json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")
            os.replace(stage, final)
        except Exception:
            import shutil
            shutil.rmtree(stage, ignore_errors=True)
            raise
        return {"status": "STAGED_FULL_CANDIDATE",
                "generation": generation, "path": str(final),
                "channels": manifest["channel_count"],
                "programmes": manifest["programme_count"],
                "artwork_records": manifest["artwork"]["records"]}
    finally:
        for item in candidates:
            try:
                item.unlink()
            except OSError:
                pass
