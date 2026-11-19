"""Optional GitHub Agent in the shared Kodi EPG scheduler and profile."""
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
STATE_LIMIT = 64 * 1024
SUCCESS = {"READY", "PARTIAL_PRESERVED"}


def enabled():
    from utils import setting_bool
    return setting_bool(SETTING, False)


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


def request_check():
    """Ask the existing service to check once, without a request on the GUI."""
    import xbmcgui
    xbmcgui.Window(10000).setProperty(REQUEST, str(time.time()))


def _request_time():
    import xbmcgui
    try:
        return float(xbmcgui.Window(10000).getProperty(REQUEST) or 0)
    except ValueError:
        return 0


def cycle(directory, token_path, portals, *, now=None, request=0,
          fetch=stage_full_candidate, install=None, cancel=lambda: False):
    """Persist manifest outcomes and only advance a portal after verified readback."""
    if install is None:
        from epg_agent100_import import install
    now = time.time() if now is None else now
    current = state(directory)
    if not portals or cancel():
        return current
    manual = current.get("request", 0) < request <= now
    if manual:
        current["request"] = request
    if manual or agent_due(current.get("last_checked", 0), now):
        current.update(last_checked=now, next_check=now + AGENT_INTERVAL, code="CHECKING")
        _save(directory, current)
        try:
            payload = fetch(directory, token_path, known=current.get("generation", ""),
                            etag=current.get("etag", ""), cancel=cancel)
        except DeliveryError as exc:
            current.update(remote="ERROR", code=exc.code)
        except InterruptedError:
            current.update(last_checked=0, code="CANCELLED")
        except OSError:
            current.update(remote="ERROR", code="STORAGE_ERROR")
        else:
            status = payload["status"]
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
            elif status == "PRIVATE_PENDING":
                current.update(remote=status, code=status, etag="", remote_reason=payload.get("reason", ""))
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
    from wizard_epg54 import pending
    eligible = [p for p in portals if p.get("include_live", True) and
                p.get("epg_show", True) and not pending(p)]
    if not eligible or not enabled() or cancel():
        return
    directory = profile()
    now = time.time()
    request = _request_time()
    record = state(directory)
    generation = record.get("generation")
    receipts = record.get("portals", {})
    pending_import = record.get("remote") == "AVAILABLE" and any(
        receipts.get(str(p["id"]), {}).get("generation") != generation for p in eligible)
    if (agent_due(record.get("last_checked", 0), now) or request > record.get("request", 0)
            or pending_import or record.get("code") in ("IMPORTING", "CHECKING")):
        next_consent = 0
        consent = True

        def cancelled():
            nonlocal next_consent, consent
            if cancel():
                return True
            tick = time.monotonic()
            if tick >= next_consent:
                consent = enabled()
                next_consent = tick + .1
            return not consent

        cycle(directory, directory / "reader-token.txt", eligible, now=now,
              request=request, cancel=cancelled)
