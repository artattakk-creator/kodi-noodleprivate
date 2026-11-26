"""Shared validation and staging for public and private Hub Schema-5 profiles."""
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
import zlib
from xml.etree import ElementTree as ET

from epg_agent_github import DeliveryError, SHA_RE, XMLTV_FILE, candidate_path, local_manifest
from epg_agent_hub4 import REPO, BASE, _download, _verify, _combine

PROFILES_RE = re.compile(r"[a-z]{2,8}(?:-[a-z0-9]{2,8})?\Z")
TAG_RE = re.compile(r"gs-hub-[A-Za-z0-9TZ-]{15,72}\Z")
VARIANTS = ("artwork", "standard")
MAX_PROFILES = 24
MAX_ASSET_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_SELECTION_BYTES = 4096
DEFAULT_PROFILES = ("all", "de", "at", "en", "es", "pl")
SELECTION_FILE = "profiles.json"
MAX_PROFILE_REPORT_BYTES = 4 * 1024 * 1024


def fail(code):
    raise DeliveryError(code)


def _utc(value):
    try:
        if not isinstance(value, str):
            return False
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0
    except (ValueError, OverflowError, AttributeError):
        return False


def validate_manifest(obj):
    """Returns (profiles, two-variant-by-profile), or a safe error code."""
    from epg_agent_public import DELIVERY as PUBLIC_DELIVERY, REPO as PUBLIC_REPO, asset_url

    public = isinstance(obj, dict) and obj.get("status") == "PUBLIC_READY"
    expected_status = "PUBLIC_READY" if public else "PRIVATE_READY"
    expected_delivery = PUBLIC_DELIVERY if public else "private-github-release-assets"
    expected_repo = PUBLIC_REPO if public else REPO
    if not isinstance(obj, dict) or any((
        obj.get("schema_version") != 5,
        obj.get("schema") != "gsmedia-hub-github-v3",
        obj.get("status") != expected_status,
        obj.get("delivery") != expected_delivery,
        obj.get("repo") != expected_repo,
        obj.get("default_profile") != "all",
        obj.get("variants") != list(VARIANTS),
        not _utc(obj.get("generated_utc")),
        not public and (type(obj.get("release_id")) is not int or obj["release_id"] < 1),
        not isinstance(obj.get("tag"), str) or not TAG_RE.fullmatch(obj["tag"]),
        not isinstance(obj.get("fingerprint"), str) or not SHA_RE.fullmatch(obj["fingerprint"]),
    )):
        fail("HUB5_INVALID_MANIFEST")
    profiles = obj.get("profiles")
    entries = obj.get("files")
    if (not isinstance(profiles, list) or
            not 1 <= len(profiles) <= MAX_PROFILES or
            any(not isinstance(p, str) or not PROFILES_RE.fullmatch(p) for p in profiles) or
            len(profiles) != len(set(profiles)) or
            "all" not in profiles or
            not isinstance(entries, list) or len(entries) != 2 * len(profiles)):
        fail("HUB5_PROFILE_SET_INVALID")
    pairs, locations, total_bytes = {}, set(), 0
    for row in entries:
        if not isinstance(row, dict):
            fail("HUB5_INVALID_ASSET")
        p, variant = row.get("profile"), row.get("variant")
        if p not in profiles or variant not in VARIANTS or (p, variant) in pairs:
            fail("HUB5_INVALID_ASSET")
        aid = row.get("asset_id")
        filename = "epg-" + p + ("-standard" if variant == "standard" else "") + ".xml.gz"
        size = row.get("bytes")
        if public:
            location = asset_url(row, obj["tag"])
        else:
            if (row.get("file") != filename or type(aid) is not int or aid < 1
                    or row.get("api_url") != BASE + str(aid)):
                fail("HUB5_INVALID_ASSET")
            location = aid
        if (location in locations or type(size) is not int or not 0 < size <= MAX_ASSET_BYTES or
            type(row.get("channels")) is not int or not 0 < row["channels"] <= 100000 or
            type(row.get("programmes")) is not int or not 0 < row["programmes"] <= 3000000 or
            not isinstance(row.get("sha256"), str) or not SHA_RE.fullmatch(row["sha256"]) or
            not _utc(row.get("generated_utc"))):
            fail("HUB5_INVALID_ASSET")
        total_bytes += size
        pairs[(p, variant)] = row
        locations.add(location)
    if total_bytes > MAX_TOTAL_BYTES:
        fail("HUB5_TOTAL_SIZE_LIMIT")
    for p in profiles:
        a, b = pairs.get((p, "artwork")), pairs.get((p, "standard"))
        if (not a or not b or a["channels"] != b["channels"] or
                a["programmes"] != b["programmes"]):
            fail("HUB5_INCONSISTENT_PAIR")
    return tuple(profiles), pairs


def _directory(directory=None):
    if directory is not None:
        return Path(directory)
    from epg_agent100 import profile
    return profile()


def selection(directory=None, *, public=False):
    """Persistent selection for future profiles, without changing addon.xml."""
    path = _directory(directory) / SELECTION_FILE
    try:
        if path.is_symlink() or path.stat().st_size > MAX_SELECTION_BYTES:
            fail("HUB5_SELECTION_UNSAFE")
        value = json.loads(path.read_text(encoding="utf-8"))
        selected = value["selected"]
        variant = value.get("variant", "artwork")
        if (value.get("schema_version") != 1 or not isinstance(selected, list) or
                len(selected) > MAX_PROFILES or len(set(selected)) != len(selected) or
                any(not isinstance(x, str) or not PROFILES_RE.fullmatch(x) for x in selected) or
                variant not in VARIANTS):
            fail("HUB5_SELECTION_UNSAFE")
        return tuple(selected), variant
    except FileNotFoundError:
        from utils import setting_bool
        variant = "standard" if public and not setting_bool("programme_xmltv96", True) else "artwork"
        if setting_bool("epg_agent_country_all", False):
            return ("all",), variant
        return tuple(p for p in ("de", "at") if setting_bool(
            "epg_agent_country_" + p, p == "de" or not public)), variant
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        fail("HUB5_SELECTION_UNSAFE")


def save_selection(selected, variant="artwork", directory=None):
    if (not isinstance(selected, (list, tuple)) or len(selected) > MAX_PROFILES or
            len(set(selected)) != len(selected) or
            any(not isinstance(p, str) or not PROFILES_RE.fullmatch(p) for p in selected) or
            variant not in VARIANTS):
        fail("HUB5_SELECTION_UNSAFE")
    root = _directory(directory)
    if root.is_symlink():
        fail("HUB5_SELECTION_UNSAFE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = {"schema_version": 1, "selected": list(selected), "variant": variant}
    fd, name = tempfile.mkstemp(prefix=".selection-", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            json.dump(payload, handle, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, root / SELECTION_FILE)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def selected_for(manifest, directory=None):
    available, pairs = validate_manifest(manifest)
    wanted, variant = selection(directory, public=manifest["status"] == "PUBLIC_READY")
    if "all" in wanted:
        wanted = ("all",)
    chosen = tuple(p for p in available if p in wanted)
    return chosen, variant, pairs, available


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()



def _coverage_file(folder, profile):
    return folder / ("coverage-" + profile + ".json.gz")


def _channel_digest(cid):
    return hashlib.sha256(cid.encode("utf-8")).hexdigest()[:32]


def _verify_profile(path, record, cancel, now, http_status, *, report_dir, public=False):
    from epg_horizon102 import Coverage

    coverage = Coverage(now)
    event_channels = set()

    def measure(event):
        cid = event["channel"]
        event_channels.add(cid)
        coverage.add(cid, event["start_timestamp"], event["stop_timestamp"])

    _verify(path, record, cancel, on_event=measure, reject_credentials=public)
    report = dict(horizon=coverage.result(), http_status=http_status,
                  channels=sorted(_channel_digest(cid) for cid in event_channels))
    target = _coverage_file(report_dir, record["profile"])
    try:
        with gzip.open(target, "wt", encoding="utf-8") as output:
            json.dump(report, output, separators=(",", ":"))
    except OSError:
        # A diagnostic write must never invalidate an already verified feed.
        pass


def coverage_report(folder, aliases):
    """Read staged per-profile evidence, matching shared channels in each profile."""
    from collections import Counter

    saved = local_manifest(folder)
    if saved.get("schema_version") != 5:
        return []
    try:
        _, records = validate_manifest(saved)
    except DeliveryError:
        return []
    variant = saved.get("variant")
    profiles = saved.get("selected_profiles")
    if variant not in VARIANTS or not isinstance(profiles, list):
        return []
    streams = Counter(_channel_digest(cid) for cid in aliases.values())
    result = []
    for profile in profiles[:MAX_PROFILES]:
        record = records.get((profile, variant)) if isinstance(profile, str) else None
        if not record:
            continue
        file = _coverage_file(folder, profile)
        report = {}
        try:
            if file.is_file() and not file.is_symlink():
                with gzip.open(file, "rb") as stream:
                    body = stream.read(MAX_PROFILE_REPORT_BYTES + 1)
                if len(body) <= MAX_PROFILE_REPORT_BYTES:
                    report = json.loads(body)
        except (OSError, ValueError, EOFError, zlib.error):
            pass
        channels = report.get("channels") if isinstance(report, dict) else None
        measured = isinstance(channels, list) and len(channels) <= record["channels"]
        http_status = report.get("http_status") if measured else None
        horizon = report.get("horizon") if measured else None
        if not isinstance(horizon, dict) or not isinstance(horizon.get("days"), list):
            horizon = None
        matched = None
        if measured:
            profile_ids = {value for value in channels if isinstance(value, str)}
            matched = sum(streams[channel] for channel in profile_ids)
        result.append(dict(profile=profile, variant=variant, sha256=record["sha256"],
                           generated=datetime.fromisoformat(record["generated_utc"].replace("Z", "+00:00")).timestamp(),
                           horizon=horizon,
                           http_status=http_status if type(http_status) is int and 100 <= http_status <= 599 else None,
                           matched=matched))
    return result

def stage(root, token, manifest, etag, opener=None, *, known="", cancel=lambda: False,
          progress=None, phase=None):
    """Download only chosen variants; stage full XMLTV before any portal install."""
    public = manifest.get("status") == "PUBLIC_READY"
    profiles, variant, records, available = selected_for(manifest, root)
    common = {"etag": etag, "available_profiles": list(available),
              "selected_profiles": list(profiles), "variant": variant,
              "revision": manifest["fingerprint"]}
    if not profiles:
        return dict(common, status="NO_PROFILE_SELECTED", reason="NO_PROFILE_SELECTED")
    rows = [(p, records[(p, variant)]) for p in profiles]
    signature = [[p, variant, row["sha256"], row["bytes"]] for p, row in rows]
    identity = ["public", signature] if public else signature
    generation = hashlib.sha256(json.dumps(identity, separators=(",", ":")).encode()).hexdigest()
    response = dict(common, generation=generation)
    previous = candidate_path(root, generation)
    if previous is not None:
        if phase is not None:
            phase("validate")
        saved = local_manifest(previous)
        if (saved.get("schema_version") != 5 or saved.get("asset_generation") != signature or
                saved.get("selected_profiles") != list(profiles) or
                saved.get("variant") != variant or
                _sha256(previous / XMLTV_FILE) != saved.get("staged_sha256")):
            fail("HUB5_LOCAL_LASTGOOD_MISMATCH")
        counts = saved.get("image_counts") or {}
        return dict(response, status="UNCHANGED", channels=saved["channel_count"],
                    programmes=saved["programme_count"], image_counts=counts,
                    artwork_records=sum(counts.values()))
    root = Path(root)
    if root.is_symlink():
        fail("HUB5_STORAGE_UNSAFE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    from import_budget import check_space
    unique_assets = {(row["sha256"], row["bytes"]) for _, row in rows}
    total = sum(size for _, size in unique_assets)
    check_space(str(root / "manifest.json"), total * (3 if len(rows) > 1 else 2))
    temporary = Path(tempfile.mkdtemp(prefix=".hub5-", dir=root))
    try:
        downloads = temporary / "assets"
        downloads.mkdir()
        sources = []
        verified_assets = {}
        observed = time.time()
        transferred = 0
        callbacks = {}
        if progress is not None:
            def on_bytes(size):
                progress(transferred + size, total)

            callbacks["on_bytes"] = on_bytes
        if phase is not None:
            def on_verify():
                phase("validate")

            callbacks["on_verify"] = on_verify
        for p, record in rows:
            key = (record["sha256"], record["bytes"])
            if key in verified_assets:
                original = verified_assets[key]
                if any(record[field] != original[field] for field in ("channels", "programmes")):
                    fail("HUB5_COUNT_MISMATCH")
                evidence = _coverage_file(temporary, original["profile"])
                if evidence.is_file():
                    try:
                        shutil.copyfile(evidence, _coverage_file(temporary, p))
                    except OSError:
                        pass  # Optional diagnostic. The same bytes were already verified.
                continue
            status = []
            if phase is not None:
                phase("download")
            if progress is not None:
                progress(transferred, total)
            if public:
                from epg_agent_public import download_asset
                path = download_asset(record, manifest["tag"], downloads, opener, cancel,
                                      on_http=status.append, **callbacks)
            else:
                path = _download(record, token, downloads, opener, cancel, on_http=status.append,
                                 **callbacks)
            transferred += record["bytes"]
            _verify_profile(path, record, cancel, observed, status[0] if status else None,
                            report_dir=temporary, public=public)
            verified_assets[key] = record
            sources.append((p, path))
        final = temporary / XMLTV_FILE
        if len(sources) == 1:
            os.replace(sources[0][1], final)
        else:
            _combine(sources, final, cancel)
        counts = {"channels": 0, "programmes": 0}
        images = {}
        def on_channel(cid, _name):
            counts["channels"] += 1
        def on_logo(cid, url):
            images["channel_logo"] = images.get("channel_logo", 0) + 1
        def on_event(event):
            counts["programmes"] += 1
            for item in event.get("images", ()):
                key = item["type"]
                images[key] = images.get(key, 0) + 1
            images["programme_icon"] = images.get("programme_icon", 0) + len(event.get("icons", ()))
        from xmltv_stream import parse as parse_xmltv
        try:
            with final.open("rb") as stream:
                result = parse_xmltv(stream, on_channel, on_event, cancel=cancel,
                                     max_seconds=900, include_icons=True,
                                     include_images=True, channel_image=on_logo,
                                     strict_images=True)
        except (OSError, ValueError, EOFError, zlib.error):
            fail("HUB5_XMLTV_INVALID")
        if result["skipped"] or not counts["channels"] or not counts["programmes"]:
            fail("HUB5_XMLTV_INVALID")
        if len(sources) == 1 and (counts["channels"] != rows[0][1]["channels"] or
                                  counts["programmes"] != rows[0][1]["programmes"]):
            fail("HUB5_COUNT_MISMATCH")
        if public:
            manifest = {k: manifest[k] for k in ("schema_version", "schema", "status", "repo",
                        "delivery", "default_profile", "profiles", "variants", "tag",
                        "generated_utc", "fingerprint", "files")}
            from epg_agent_public import asset_url
            manifest["files"] = [
                dict({k: row[k] for k in ("profile", "variant", "file", "bytes", "sha256",
                                         "generated_utc", "channels", "programmes")},
                     download_url=asset_url(row, manifest["tag"]))
                for row in manifest["files"]
            ]
        saved = dict(manifest, selected_profiles=list(profiles), variant=variant,
                     asset_generation=signature, channel_count=counts["channels"],
                     programme_count=counts["programmes"], image_counts=images,
                     staged_sha256=_sha256(final))
        with (temporary / "manifest.json").open("w", encoding="utf-8") as output:
            json.dump(saved, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())
        for _, old in sources:
            if old.exists():
                old.unlink()
        downloads.rmdir()
        destination = root / ("candidate-" + generation)
        os.replace(temporary, destination)
        return dict(response, status="STAGED_FULL_CANDIDATE",
                    path=str(destination), channels=counts["channels"],
                    programmes=counts["programmes"], image_counts=images,
                    artwork_records=sum(images.values()))
    finally:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
