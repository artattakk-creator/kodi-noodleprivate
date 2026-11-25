"""Private GS Media Hub schema-4 Release assets -> one verified local XMLTV.

Keep the existing schema-3 reader untouched.  Never send auth to a CDN;
read-only token is only sent to pinned api.github.com release endpoints.
"""
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from urllib import error, parse, request
from xml.etree import ElementTree as ET

REPO = "artattakk-creator/xcmate-epg-private"
BASE = "https://api.github.com/repos/" + REPO + "/releases/assets/"
PROFILES = {"all": "epg-all.xml.gz", "de": "epg-de.xml.gz", "at": "epg-at.xml.gz"}
MAX_FILE = 48 * 1024 * 1024
MAX_XML = 768 * 1024 * 1024


def _failed(code):
    from epg_agent_github import DeliveryError
    raise DeliveryError(code)


def _utc(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.tzinfo is not None and dt.utcoffset() == timezone.utc.utcoffset(None)
    except (TypeError, ValueError, AttributeError):
        return False


def validate_manifest(manifest):
    """Reject unsigned destinations, unknown profiles, partial releases."""
    from epg_agent_github import SHA_RE
    if not isinstance(manifest, dict) or (
        manifest.get("schema_version") != 4 or
        manifest.get("schema") != "gsmedia-hub-github-v2" or
        manifest.get("status") != "PRIVATE_READY" or
        manifest.get("delivery") != "private-github-release-assets" or
        manifest.get("repo") != REPO or
        manifest.get("default_profile") != "all" or
        not _utc(manifest.get("generated_utc")) or
        not isinstance(manifest.get("release_id"), int) or
        isinstance(manifest["release_id"], bool) or manifest["release_id"] < 1 or
        not isinstance(manifest.get("tag"), str) or
        not re.fullmatch(r"gs-hub-[A-Za-z0-9T-Z-]{15,72}", manifest["tag"]) or
        not isinstance(manifest.get("fingerprint"), str) or
        not SHA_RE.fullmatch(manifest["fingerprint"])
    ):
        _failed("HUB4_INVALID_MANIFEST")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 3:
        _failed("HUB4_INVALID_MANIFEST")
    seen = set()
    for record in files:
        if not isinstance(record, dict):
            _failed("HUB4_INVALID_MANIFEST")
        p = record.get("profile")
        asset = record.get("asset_id")
        if (p not in PROFILES or p in seen or record.get("file") != PROFILES[p] or
            type(asset) is not int or asset <= 0 or
            record.get("api_url") != BASE + str(asset) or
            type(record.get("bytes")) is not int or not 0 < record["bytes"] <= MAX_FILE or
            type(record.get("channels")) is not int or not 0 < record["channels"] <= 100000 or
            type(record.get("programmes")) is not int or not 0 < record["programmes"] <= 3000000 or
            not isinstance(record.get("sha256"), str) or
            not SHA_RE.fullmatch(record["sha256"]) or
            not _utc(record.get("generated_utc"))):
            _failed("HUB4_INVALID_MANIFEST")
        seen.add(p)
    if seen != set(PROFILES):
        _failed("HUB4_INCOMPLETE_PROFILES")
    return {row["profile"]: row for row in files}


def selected():
    """User regions are explicit; unimplemented countries are not guessed."""
    from utils import setting_bool
    if setting_bool("epg_agent_country_all", False):
        return ("all",)
    return tuple(key for key in ("de", "at")
                 if setting_bool("epg_agent_country_" + key, True))


def _open_asset(record, token, opener):
    from epg_agent_github import DeliveryError, _LimitedGitHubRedirect, USER_AGENT
    req = request.Request(record["api_url"], method="GET", headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/octet-stream",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    })
    try:
        return (opener or request.build_opener(_LimitedGitHubRedirect())).open(req, timeout=35)
    except error.HTTPError as exc:
        status = exc.code
        exc.close()
        code = ("PRIVATE_ENDPOINT_ACCESS_DENIED" if status in (401, 403, 404)
                else "PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE" if status in (429, 500, 502, 503, 504)
                else "HUB4_HTTP_ERROR")
        raise DeliveryError(code, phase="asset", http_status=status) from None
    except DeliveryError:
        raise
    except (OSError, ValueError, TimeoutError):
        _failed("PRIVATE_ENDPOINT_NETWORK_ERROR")


def _download(record, token, dest, opener, cancel, *, on_http=None):
    from epg_agent_github import _consume
    target = dest / record["file"]
    # Created inside an owned temporary staging directory, no path supplied by feed.
    digest = hashlib.sha256()
    with target.open("xb") as output:
        def sink(part):
            digest.update(part)
            output.write(part)
        response = _open_asset(record, token, opener)
        if on_http is not None:
            on_http(getattr(response, "status", None))
        _consume(response, record["bytes"], sink, cancel)
        output.flush()
        os.fsync(output.fileno())
    if target.stat().st_size != record["bytes"] or digest.hexdigest() != record["sha256"]:
        _failed("CHECKSUM_OR_SIZE_MISMATCH")
    return target


def _verify(path, record, cancel, *, on_event=None, reject_credentials=False):
    """Read every programme and validate gzip trailer and XMLTV channel refs."""
    from xmltv_stream import parse as parse_xmltv
    identifiers = set()
    items = [0]
    decompressed = [0]
    def channel(cid, _name):
        if not cid or cid in identifiers or len(identifiers) >= record["channels"]:
            _failed("HUB4_CHANNEL_INVALID")
        identifiers.add(cid)
    def programme(event):
        items[0] += 1
        if event["channel"] not in identifiers or not event["name"]:
            _failed("HUB4_PROGRAMME_INVALID")
        if on_event is not None:
            on_event(event)
    def progress(counts):
        decompressed[0] = counts["bytes"]
        if counts["bytes"] > MAX_XML or counts["programmes"] > record["programmes"]:
            _failed("HUB4_UNCOMPRESSED_LIMIT")
    try:
        with path.open("rb") as raw:
            if raw.read(2) != b"\x1f\x8b":
                _failed("INVALID_GZIP")
            raw.seek(0)
            counts = parse_xmltv(raw, channel, programme, cancel=cancel,
                                 max_seconds=720, progress=progress, strict_images=True,
                                 reject_credentials=reject_credentials)
    except (OSError, ValueError, EOFError, gzip.BadGzipFile) as exc:
        from epg_agent_github import DeliveryError
        if isinstance(exc, DeliveryError):
            raise
        _failed("HUB4_XMLTV_INVALID")
    if (counts["skipped"] or len(identifiers) != record["channels"] or
            items[0] != record["programmes"] or counts["programmes"] != items[0]):
        _failed("HUB4_COUNT_MISMATCH")
    return identifiers


def _records(filename, tag, cancel):
    """Stream one channel/programme node at a time after integrity verification."""
    with gzip.open(filename, "rb") as stream:
        root = None
        depth = 0
        for action, node in ET.iterparse(stream, events=("start", "end")):
            if cancel():
                raise InterruptedError("CANCELLED")
            if action == "start":
                depth += 1
                if depth == 1:
                    root = node
                continue
            if depth == 2 and node.tag == tag:
                yield node
            if depth == 2:
                root.remove(node)
            depth -= 1


def _combine(files, output, cancel):
    """DE+AT is the actual union, never the unselected international 'all' file."""
    channels = {}
    duplicated = set()
    seen_intervals = set()
    with gzip.open(output, "wb", compresslevel=6) as result:
        result.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="XCMate EPG Agent">\n')
        for country, file in files:
            for row in _records(file, "channel", cancel):
                key = row.get("id")
                name = row.findtext("display-name", "").strip()
                if key in channels:
                    # Avoid collisions with different channel identities, without guessing.
                    if channels[key] != name:
                        _failed("HUB4_CHANNEL_CONFLICT")
                    duplicated.add(key)
                    continue
                channels[key] = name
                result.write(ET.tostring(row, encoding="utf-8") + b"\n")
        for country, file in files:
            for row in _records(file, "programme", cancel):
                cid = row.get("channel")
                if cid in duplicated:
                    interval = (cid, row.get("start"), row.get("stop"))
                    if interval in seen_intervals:
                        continue  # DE wins a genuinely conflicting same-slot event.
                    seen_intervals.add(interval)
                result.write(ET.tostring(row, encoding="utf-8") + b"\n")
        result.write(b"</tv>\n")
    return len(channels)


def stage(root, token, manifest, etag, opener=None, *, known="", cancel=lambda: False):
    """Stage selected asset(s) atomically; existing verified generation stays intact."""
    from epg_agent_github import XMLTV_FILE, candidate_path, local_manifest
    files = validate_manifest(manifest)
    profiles = selected()
    if not profiles:
        return {"status": "PRIVATE_PENDING", "reason": "NO_COUNTRY_SELECTED", "etag": etag}
    digest_items = [[p, files[p]["sha256"], files[p]["bytes"]] for p in profiles]
    generation = hashlib.sha256(json.dumps(digest_items, separators=(",", ":")).encode()).hexdigest()
    response = {"generation": generation, "etag": etag,
                "profile": "+".join(profiles)}
    previous = candidate_path(root, generation)
    if previous is not None:
        saved = local_manifest(previous)
        if (saved.get("schema_version") != 4 or saved.get("selected_profiles") != list(profiles) or
                saved.get("asset_generation") != digest_items):
            _failed("HUB4_STALE_CANDIDATE")
        image_counts = saved.get("image_counts") or {}
        return dict(response, status="UNCHANGED", channels=saved["channel_count"],
                    programmes=saved["programme_count"],
                    artwork_records=sum(image_counts.values()), image_counts=image_counts)
    root = Path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        _failed("CANDIDATE_DIRECTORY_UNSAFE")
    from import_budget import check_space
    check_space(str(root / "manifest.json"), sum(files[p]["bytes"] for p in profiles) +
                (sum(files[p]["bytes"] for p in profiles) if len(profiles) > 1 else 0))
    folder = Path(tempfile.mkdtemp(prefix=".hub4-", dir=root))
    try:
        input_files = []
        for p in profiles:
            source = _download(files[p], token, folder, opener, cancel)
            _verify(source, files[p], cancel)
            input_files.append((p, source))
        final = folder / XMLTV_FILE
        if len(input_files) == 1:
            os.replace(input_files[0][1], final)
        else:
            _combine(input_files, final, cancel)
        # Check the exact combined document with the same constrained streaming parser.
        counts = {"channels": 0, "programmes": 0}
        image_counts = {}
        def channel(cid, _name):
            counts["channels"] += 1
        def channel_image(cid, url):
            image_counts["channel_logo"] = image_counts.get("channel_logo", 0) + 1
        def programme(event):
            counts["programmes"] += 1
            for picture in event.get("images", ()):
                role = picture["type"]
                image_counts[role] = image_counts.get(role, 0) + 1
            image_counts["programme_icon"] = image_counts.get("programme_icon", 0) + len(event.get("icons", ()))
        from xmltv_stream import parse as parse_xmltv
        with final.open("rb") as stream:
            result = parse_xmltv(stream, channel, programme, cancel=cancel, max_seconds=720,
                                 include_icons=True, include_images=True,
                                 channel_image=channel_image, strict_images=True)
        if result["skipped"] or not counts["channels"] or not counts["programmes"]:
            _failed("HUB4_COUNT_MISMATCH")
        if len(input_files) == 1 and (counts["channels"] != files[profiles[0]]["channels"] or
                                     counts["programmes"] != files[profiles[0]]["programmes"]):
            _failed("HUB4_COUNT_MISMATCH")
        checksum = hashlib.sha256()
        with final.open("rb") as source:
            while True:
                block = source.read(65536)
                if not block:
                    break
                checksum.update(block)
        payload = dict(manifest, asset_generation=digest_items, selected_profiles=list(profiles),
                       channel_count=counts["channels"], programme_count=counts["programmes"],
                       image_counts=image_counts, staged_sha256=checksum.hexdigest())
        with (folder / "manifest.json").open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        for _, source in input_files:
            if source.exists():
                source.unlink()
        installed = root / ("candidate-" + generation)
        os.replace(folder, installed)
        return dict(response, status="STAGED_FULL_CANDIDATE", path=str(installed),
                    channels=counts["channels"], programmes=counts["programmes"],
                    artwork_records=sum(image_counts.values()), image_counts=image_counts)
    finally:
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
