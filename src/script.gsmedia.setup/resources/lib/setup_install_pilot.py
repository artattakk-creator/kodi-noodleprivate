"""GS Media Setup 0.3.0: fail-closed small-scale install pilot.

Installations are requested via Kodi's documented InstallAddon builtin.
The call is asynchronous: a launch is NEVER proof of an install. A later
explicit user action must confirm the installed/enabled addon via JSON-RPC.
No downloader, arbitrary ZIP, skin edits, or wizard autorun is implemented.
"""
import json
import os
import tempfile
from pathlib import Path

# Verified as published in Kodi Omega or the GS Media 1.8.1 catalogue.
# Entries here are not a grant to install unrelated dependencies or packages.
APPROVED = (
    ("script.cabertoss", "repository.xbmc.org", "1.0.2"),
    ("plugin.audio.shoutcast", "repository.xbmc.org", "2.5.2"),
    ("plugin.video.xtreammate", "repository.gsmedia", "0.1.29.69"),
)
APPROVED_IDS = tuple(x[0] for x in APPROVED)
JOURNAL_FILE = "install-pilot-030.json"
JOURNAL_VERSION = 1
MAX_JOURNAL = 8192
PROTECTED_EXISTING = ("skin.titan.bingie.mod", "plugin.video.xvault",
                      "plugin.video.cumination", "plugin.audio.m3sr2019")


def protected_existing(inventory):
    """Guard from accidental installation into an established BINGIE box."""
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return ("INVENTORY_UNKNOWN",)
    return tuple(x for x in PROTECTED_EXISTING if x in inventory.get("addons", {}))


def _version(value):
    import re
    m = re.match(r"^\d+(?:\.\d+)*", str(value))
    return tuple(int(part) for part in m.group().split(".")) if m else ()


def _installed(inventory, addon_id, minimum=""):
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return False
    item = inventory.get("addons", {}).get(addon_id)
    if not isinstance(item, dict) or item.get("enabled") is not True:
        return False
    actual = _version(item.get("version", ""))
    return bool(actual and (not minimum or actual >= _version(minimum)))


def plan(inventory):
    """Return the only approved installable subset of the 11-addon setup."""
    return tuple({
        "addon_id": addon_id,
        "repository": repo,
        "minimum": minimum,
        "installed": _installed(inventory, addon_id, minimum),
        "repository_ready": _installed(inventory, repo),
    } for addon_id, repo, minimum in APPROVED)


def blank_state():
    return {"schema": JOURNAL_VERSION, "phase": "ACTIVE", "pending": "",
            "attempted": [], "completed": [], "last_error": ""}


def assess(state, inventory):
    """Pure transition function. No automatic retry and no side effects."""
    if not isinstance(state, dict) or state.get("schema") != JOURNAL_VERSION:
        return {"code": "INVALID_JOURNAL"}
    if state.get("phase") not in ("ACTIVE", "PILOT_DONE"):
        return {"code": "INVALID_PHASE"}
    if not isinstance(inventory, dict) or inventory.get("code") != "READY":
        return {"code": "INVENTORY_UNAVAILABLE"}
    pending = state.get("pending", "")
    if pending and pending not in APPROVED_IDS:
        return {"code": "INVALID_PENDING"}
    rows = plan(inventory)
    if pending:
        row = next(r for r in rows if r["addon_id"] == pending)
        if not row["installed"]:
            return {"code": "AWAITING_KODI_INSTALL", "addon_id": pending}
        # Caller must persist a successful pending transition before next action.
        return {"code": "CONFIRM_INSTALLED", "addon_id": pending}
    for row in rows:
        if not row["installed"]:
            if not row["repository_ready"]:
                return {"code": "REPOSITORY_UNAVAILABLE",
                        "addon_id": row["addon_id"], "repository": row["repository"]}
            if row["addon_id"] in state["attempted"]:
                return {"code": "RETRY_REQUIRES_USER", "addon_id": row["addon_id"]}
            return {"code": "REQUEST_INSTALL", "addon_id": row["addon_id"]}
    return {"code": "PILOT_DONE_NOT_FULL_SETUP"}


def after_confirm(state, addon_id):
    """Record a post-install verification; no invented success state."""
    if addon_id != state.get("pending") or addon_id not in APPROVED_IDS:
        raise ValueError("Mismatched verification")
    s = dict(state)
    s["pending"] = ""
    s["completed"] = sorted(set(state.get("completed", ())) | {addon_id})
    return s


def after_request(state, addon_id):
    if state.get("pending") or addon_id not in APPROVED_IDS:
        raise ValueError("Unapproved or overlapping install")
    s = dict(state)
    s["pending"] = addon_id
    s["attempted"] = sorted(set(state.get("attempted", ())) | {addon_id})
    return s


def retry_explicitly(state, addon_id):
    if state.get("pending") != addon_id:
        raise ValueError("No pending install for retry")
    s = dict(state)
    s["pending"] = ""
    s["attempted"] = [x for x in state.get("attempted", ()) if x != addon_id]
    return s


def _safe_location(profile):
    """Profile path is provided by Kodi; resolve only within GS Media addon_data."""
    p = Path(profile).resolve()
    if p.name != "script.gsmedia.setup":
        raise ValueError("Unsafe GS Media profile")
    return p / JOURNAL_FILE


def load(profile):
    target = _safe_location(profile)
    if target.is_symlink():
        raise ValueError("Symlink journal denied")
    if not target.exists():
        return None
    if target.stat().st_size > MAX_JOURNAL:
        raise ValueError("Journal too large")
    with target.open("r", encoding="utf-8") as stream:
        s = json.load(stream)
    if not isinstance(s, dict) or s.get("schema") != JOURNAL_VERSION:
        raise ValueError("Invalid journal")
    if s.get("phase") not in ("ACTIVE", "PILOT_DONE"):
        raise ValueError("Invalid journal phase")
    if not isinstance(s.get("attempted"), list) or not isinstance(s.get("completed"), list):
        raise ValueError("Invalid journal shape")
    for key in ("attempted", "completed"):
        if not set(s[key]).issubset(APPROVED_IDS):
            raise ValueError("Journal contains unapproved package")
    if s.get("pending") not in ("",) + APPROVED_IDS:
        raise ValueError("Invalid pending package")
    return s


def save(profile, state):
    """Atomic, private, restricted journal. Stores only nonsecret addon IDs."""
    target = _safe_location(profile)
    if state.get("schema") != JOURNAL_VERSION:
        raise ValueError("Invalid journal schema")
    if state.get("phase") not in ("ACTIVE", "PILOT_DONE"):
        raise ValueError("Invalid journal phase")
    if target.is_symlink():
        raise ValueError("Symlink journal denied")
    if not set(state.get("attempted", ())).issubset(APPROVED_IDS):
        raise ValueError("Unapproved journal contents")
    if not set(state.get("completed", ())).issubset(APPROVED_IDS):
        raise ValueError("Unapproved journal contents")
    if state.get("pending") not in ("",) + APPROVED_IDS:
        raise ValueError("Invalid journal pending id")
    raw = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_JOURNAL:
        raise ValueError("Journal too big")
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=JOURNAL_FILE + ".tmp.", dir=str(target.parent))
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(str(temp), str(target))
    finally:
        if temp.exists():
            temp.unlink()
