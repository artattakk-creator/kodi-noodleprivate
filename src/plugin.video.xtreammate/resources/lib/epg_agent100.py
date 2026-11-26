"""GitHub EPG delivery and verified import receipts in the Kodi profile."""
import json
import shutil
from pathlib import Path
import sqlite3
import time

from epg_agent_github import DeliveryError, SHA_RE, candidate_path, stage_full_candidate
from epg_schedule53 import AGENT_INTERVAL, agent_due

SOURCE_ID = "agent"
SOURCE_NAME = "XCMate EPG Agent"
SOURCE_RANK = 1000
RETRY_INTERVAL = 15 * 60
SETTING = "epg_agent_enabled"
REQUEST = "XCMate.EPGAgent.Request"
FORCE = "XCMate.EPGAgent.Force"
STATE_LIMIT = 64 * 1024
SUCCESS = {"READY", "PARTIAL_PRESERVED"}


def enabled():
    from utils import setting_bool
    return setting_bool(SETTING, True)


def use_private():
    from utils import setting_bool
    return setting_bool("epg_agent_private", False)


def profile():
    from utils import addon_data_dir
    return Path(addon_data_dir()) / "epg-agent"


def state(directory=None):
    path = (profile() if directory is None else directory) / "status.json"
    try:
        if path.is_symlink():
            return {}
        with path.open("rb") as stream:
            raw = stream.read(STATE_LIMIT + 1)
        value = json.loads(raw) if len(raw) <= STATE_LIMIT else {}
        return value if isinstance(value, dict) else {}
    except (ValueError, OSError):
        return {}


def _save(directory, record):
    from epg_gate95 import atomic
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink():
        raise DeliveryError("CANDIDATE_DIRECTORY_UNSAFE")
    atomic(directory / "status.json", record)


def request_check(*, force=False):
    """Ask the existing service to check once, without a request on the GUI."""
    import xbmcgui
    window = xbmcgui.Window(10000)
    stamp = str(time.time())
    if force:
        window.setProperty(FORCE, stamp)
    window.setProperty(REQUEST, stamp)
    return float(stamp)


def _request_time(key=REQUEST):
    import xbmcgui
    try:
        return float(xbmcgui.Window(10000).getProperty(key) or 0)
    except ValueError:
        return 0


def pending_request(record, *, seconds=80):
    stamp = _request_time()
    return record.get("request", 0) < stamp and 0 <= time.time() - stamp < seconds


def publish_variant(variant):
    """Expose the read-back profile choice to renderers without profile file I/O."""
    import xbmcgui
    from epg_handoff63 import profile_scope

    window = xbmcgui.Window(10000)
    key = "XCMate.Agent103.Variant." + profile_scope()
    if window.getProperty(key) != variant:
        window.setProperty(key, variant)


def _publish_initial_variant(directory, public):
    try:
        import xbmcgui
        from epg_handoff63 import profile_scope
        from epg_agent_hub5 import selection

        if not xbmcgui.Window(10000).getProperty("XCMate.Agent103.Variant." + profile_scope()):
            publish_variant(selection(directory, public=public)[1])
    except (DeliveryError, ImportError, AttributeError, RuntimeError):
        # Leave existing pictures intact when a stored selection cannot be read.
        pass



def _due(record, now):
    checked = record.get("last_checked", 0)
    if not checked or now < checked or record.get("code") == "CHECKING":
        return True
    if record.get("remote_failures") or record.get("remote") == "PUBLIC_PENDING":
        return now >= record.get("next_check", checked)
    return agent_due(checked, now)


def _failed(record, now, code, *, phase="", http_status=None):
    failures = (record.get("remote_failures", 0) % 3) + 1
    delay = (RETRY_INTERVAL, 4 * RETRY_INTERVAL, AGENT_INTERVAL)[failures - 1]
    record.update(remote="ERROR", code=code, remote_failures=failures,
                  last_checked=now, next_check=now + delay,
                  remote_phase=phase, remote_http_status=http_status)


def cycle(directory, token_path, portals, *, now=None, request=0,
          fetch=None, install=None, cancel=lambda: False, public=False, force=False):
    """Persist manifest outcomes and only advance a portal after verified readback."""
    if install is None:
        from epg_agent100_import import install
    now = time.time() if now is None else now
    current = state(directory)
    if not portals or cancel():
        return current
    transport = "public" if public else "private"
    if current.get("transport", "private") != transport:
        # Cached proofs remain usable while the newly selected endpoint is checked.
        for key in ("etag", "remote", "remote_failures", "available_profiles",
                    "last_checked", "last_successful_check", "manifest_revision"):
            current.pop(key, None)
    current["transport"] = transport
    manual = current.get("request", 0) < request <= now
    if manual:
        current["request"] = request
    if manual or _due(current, now):
        current.update(last_checked=now, next_check=now + AGENT_INTERVAL, code="CHECKING",
                       delivery_phase="manifest", download_bytes=0, download_total=0,
                       remote_phase="", remote_http_status=None)
        _save(directory, current)
        # A region or picture-mode change needs a fresh manifest even when
        # its HTTP ETag has not changed. Otherwise 304 masks that selection.
        fetch_etag = "" if manual and force else current.get("etag", "")
        if current.get("available_profiles"):
            from epg_agent_hub5 import selection
            desired, picture_mode = selection(directory, public=public)
            if ("all" in desired):
                desired = ("all",)
            if (list(desired) != current.get("selected_profiles") or
                    picture_mode != current.get("selected_variant", "artwork")):
                fetch_etag = ""
        next_progress = 0
        def progress(done, total):
            nonlocal next_progress
            tick = time.monotonic()
            if tick >= next_progress or done == total:
                current.update(download_bytes=done, download_total=total)
                _save(directory, current)
                next_progress = tick + 2

        def phase(value):
            if current["delivery_phase"] != value:
                current["delivery_phase"] = value
                _save(directory, current)

        try:
            options = dict(known=current.get("generation", ""), etag=fetch_etag, cancel=cancel)
            if fetch is None:
                options.update(phase=phase, progress=progress)
            if public:
                from epg_agent_public import stage_public_candidate
                if fetch is not None:
                    options["progress"] = progress
                payload = (fetch or stage_public_candidate)(directory, **options)
            else:
                from epg_agent_token_bootstrap import ensure_local_token, fetch_with_recovery
                if token_path is None:
                    token_path = ensure_local_token(directory)
                payload = fetch_with_recovery(fetch or stage_full_candidate, directory,
                                              token_path, **options)
        except DeliveryError as exc:
            _failed(current, now, exc.code, phase=exc.phase, http_status=exc.http_status)
        except InterruptedError:
            current.update(last_checked=0, next_check=0, code="CANCELLED")
        except OSError:
            _failed(current, now, "STORAGE_ERROR")
        except MemoryError:
            _failed(current, now, "MEMORY_PRESSURE")
        else:
            current.update(remote_failures=0, remote_phase="manifest",
                           remote_http_status=payload.get("manifest_http"),
                           last_successful_check=now, remote_reason="")
            if payload.get("revision"):
                current["manifest_revision"] = payload["revision"]
            status = payload["status"]
            if "available_profiles" in payload:
                current["available_profiles"] = payload["available_profiles"]
                current["selected_profiles"] = payload.get("selected_profiles", [])
                current["selected_variant"] = payload.get("variant", "artwork")
            if status in ("STAGED_FULL_CANDIDATE", "UNCHANGED"):
                old = current.get("generation", "")
                if old and old != payload["generation"]:
                    current["previous_generation"] = old
                current.update(remote="AVAILABLE", generation=payload["generation"],
                               channels=payload["channels"], programmes=payload["programmes"],
                               artwork_records=payload["artwork_records"],
                               image_counts=payload.get("image_counts", {}), etag=payload["etag"])
            elif status == "NOT_MODIFIED":
                current.update(remote="AVAILABLE", etag=payload["etag"])
            elif status in ("PRIVATE_PENDING", "PUBLIC_PENDING", "NO_PROFILE_SELECTED"):
                current.update(remote=status, code=status, etag="",
                               remote_reason=payload.get("reason", ""))
                if status == "PUBLIC_PENDING":
                    current["next_check"] = now + RETRY_INTERVAL
        _save(directory, current)
    if current.get("remote") != "AVAILABLE" or cancel():
        return current
    generation = current.get("generation")
    folder = candidate_path(directory, generation)
    if folder is None:
        current.update(last_checked=0, code="CANDIDATE_MISSING", etag="")
        _save(directory, current)
        return current
    receipts = current.setdefault("portals", {})
    for portal in portals:
        if cancel():
            return current
        pid = str(portal["id"])
        last = receipts.get(pid, {})
        if last.get("generation") == generation:
            continue
        previous_attempt = last.get("attempt", 0)
        if not manual and last.get("candidate") == generation and 0 <= now - previous_attempt < RETRY_INTERVAL:
            continue
        current["code"] = "IMPORTING"
        _save(directory, current)
        try:
            result = install(portal, folder, cancel)
        except MemoryError:
            result = dict(code="MEMORY_PRESSURE")
        except (DeliveryError, OSError, ValueError, sqlite3.Error) as exc:
            result = dict(code=exc.code if isinstance(exc, DeliveryError) else "IMPORT_ERROR")
        if result["code"] in SUCCESS and result.get("verified", 0) > 0:
            receipts[pid] = dict(result, generation=generation, attempt=now, last_success=now)
        else:
            receipts[pid] = dict(last, attempt=now, candidate=generation, code=result["code"])
        _save(directory, current)
    available = sum(receipts.get(str(p["id"]), {}).get("generation") == generation for p in portals)
    code = "CURRENT" if available == len(portals) else "IMPORT_PENDING"
    if current["code"] != code or current.get("ready_portals") != available:
        current.update(ready_portals=available, code=code)
        _save(directory, current)
    if available == len(portals):
        _prune(directory, current)
    return current


def _prune(directory, current):
    """Clear only our verified, superseded candidate directories."""
    keep = {current.get("generation"), current.get("previous_generation")}
    keep.update(p.get("generation") for p in current["portals"].values())
    for folder in directory.glob("candidate-*"):
        generation = folder.name.removeprefix("candidate-")
        if generation in keep or not SHA_RE.fullmatch(generation):
            continue
        if candidate_path(directory, generation) != folder:
            continue
        shutil.rmtree(folder, ignore_errors=True)


def installed_source(pid):
    """Resolve the last locally verified Agent generation for an explicit preview."""
    if not enabled():
        return None
    from epg_agent100_art import INDEX
    from epg_agent_github import XMLTV_FILE
    directory = profile()
    receipt = state(directory).get("portals", {}).get(str(pid), {})
    folder = candidate_path(directory, receipt.get("generation"))
    if folder is None:
        return None
    index = folder / INDEX
    if index.is_symlink() or not index.is_file():
        return None
    return dict(id=SOURCE_ID, name=SOURCE_NAME, local=True, enabled=True,
                uri=str(folder / XMLTV_FILE), _agent_artwork=str(index))


def run(portals, cancel):
    directory = profile()
    public = not use_private()
    _publish_initial_variant(directory, public)
    eligible = [p for p in portals if p.get("include_live", True) and
                p.get("epg_show", True)]
    if not eligible or not enabled() or cancel():
        return
    now = time.time()
    request = _request_time()
    record = state(directory)
    generation = record.get("generation")
    receipts = record.get("portals", {})
    pending_import = record.get("remote") == "AVAILABLE" and any(
        receipts.get(str(p["id"]), {}).get("generation") != generation for p in eligible)
    if (_due(record, now) or request > record.get("request", 0)
            or record.get("transport", "private") != ("public" if public else "private")
            or pending_import or record.get("code") in ("IMPORTING", "CHECKING")):
        next_consent = 0
        consent = True

        def cancelled():
            nonlocal next_consent, consent
            if cancel():
                return True
            tick = time.monotonic()
            if tick >= next_consent:
                consent = enabled() and public != use_private()
                next_consent = tick + .1
            return not consent

        cycle(directory, None, eligible, now=now, request=request,
              cancel=cancelled, public=public, force=bool(request and request == _request_time(FORCE)))
