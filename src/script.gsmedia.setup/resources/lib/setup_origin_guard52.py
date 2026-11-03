"""GS Media 0.5.2: temporary, consent-based Kodi official-add-on source exception.

Kodi 21 (Omega) values verified from xbmc/xbmc system/settings/settings.xml:
  addons.updatemode: 0 = OFFICIAL_ONLY, 1 = ANY_REPOSITORY
  general.addonupdates: 0 = AUTOMATIC, 1 = NOTIFY, 2 = NEVER

Security contract:
- Only the pinned, already approved Skin Shortcuts 2.1.0 retry uses this.
- Never silently lower protection for all Kodi addons.
- Before changing anything, persist both original settings atomically.
- Pause automatic updates while ANY_REPOSITORY is active.
- Restore settings in all outcomes (success, error, timeout, Kodi shutdown).
- Also restore on next Kodi boot through service.py after a hard crash.
- If JSON-RPC is unavailable or values cannot be proven, fail closed.
"""
import json
import os
import tempfile
from pathlib import Path

MODE = "addons.updatemode"
UPDATES = "general.addonupdates"
OFFICIAL_ONLY = 0
ANY_REPOSITORY = 1
NEVER_AUTO = 2
JOURNAL_FILE = "origin-policy-restore-052.json"
MAX_BYTES = 1500


def _marker(profile):
    folder = Path(profile).resolve()
    if folder.name != "script.gsmedia.setup":
        raise ValueError("Untrusted Kodi add-on profile")
    target = folder / JOURNAL_FILE
    if target.is_symlink():
        raise ValueError("Unsafe policy journal path")
    return target


def _read_marker(profile):
    target = _marker(profile)
    if not target.exists():
        return None
    if target.stat().st_size > MAX_BYTES:
        raise ValueError("Policy journal too large")
    data = json.loads(target.read_text(encoding="ascii"))
    if (not isinstance(data, dict) or set(data) !=
            {"schema", "mode", "updates", "addon"} or data["schema"] != 1 or
            data["addon"] != "script.skinshortcuts" or
            type(data["mode"]) is not int or data["mode"] not in (0, 1) or
            type(data["updates"]) is not int or data["updates"] not in (0, 1, 2)):
        raise ValueError("Corrupt policy journal")
    return data


def _save_marker(profile, record):
    target = _marker(profile)
    if target.exists():
        raise ValueError("Policy transaction already pending")
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii")
    if len(raw) > MAX_BYTES:
        raise ValueError("Unexpectedly large journal")
    fd, tmp = tempfile.mkstemp(prefix=".gsmedia-policy-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _call(rpc, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 52, "method": method,
                          "params": params}, separators=(",", ":"))
    raw = rpc(payload)
    if not isinstance(raw, str) or len(raw) > 4096:
        raise RuntimeError("Invalid Kodi Settings response")
    result = json.loads(raw)
    if (not isinstance(result, dict) or result.get("error") or
            "result" not in result):
        raise RuntimeError("Kodi denied setting operation: " + method)
    return result["result"]


def read_value(rpc, setting):
    result = _call(rpc, "Settings.GetSettingValue", {"setting": setting})
    value = result.get("value") if isinstance(result, dict) else None
    if type(value) is not int:
        raise RuntimeError("Unexpected Kodi setting type: " + setting)
    return value


def set_value(rpc, setting, value):
    result = _call(rpc, "Settings.SetSettingValue",
                   {"setting": setting, "value": value})
    if result is not True and result != "OK":
        # Kodi JSON-RPC often returns {"result": true}. Never assume a
        # successful operation without reading the actual new setting.
        if result not in ("ACK", "OK", True):
            raise RuntimeError("Kodi rejected new setting: " + setting)
    if read_value(rpc, setting) != value:
        raise RuntimeError("Kodi setting not persisted: " + setting)


def restore(profile, rpc):
    """Idempotent crash recovery; journal retained unless BOTH values match."""
    marker = _read_marker(profile)
    if marker is None:
        return False
    errors = []
    # Restore update restriction BEFORE enabling automatic checks again.
    for name, expected in ((MODE, marker["mode"]), (UPDATES, marker["updates"])):
        try:
            if read_value(rpc, name) != expected:
                set_value(rpc, name, expected)
        except (RuntimeError, ValueError, TypeError) as exc:
            errors.append(name + ": " + type(exc).__name__)
    if errors:
        raise RuntimeError("Kodi policy RESTORE FAILED " + ",".join(errors))
    _marker(profile).unlink()
    return True


class TemporaryOfficialAddonSource:
    def __init__(self, profile, rpc):
        self.profile = profile
        self.rpc = rpc
        self.active = False

    def __enter__(self):
        if _read_marker(self.profile) is not None:
            raise RuntimeError("Older Kodi security policy change still pending recovery")
        original_mode = read_value(self.rpc, MODE)
        original_updates = read_value(self.rpc, UPDATES)
        if original_mode not in (OFFICIAL_ONLY, ANY_REPOSITORY):
            raise RuntimeError("Unknown Kodi origin update protection")
        if original_updates not in (0, 1, 2):
            raise RuntimeError("Unknown Kodi auto-update policy")
        _save_marker(self.profile, {
            "schema": 1, "mode": original_mode, "updates": original_updates,
            "addon": "script.skinshortcuts"})
        try:
            # Prevent unrelated repos auto-updating under the brief global
            # permission window. This is still a global setting.
            if original_updates != NEVER_AUTO:
                set_value(self.rpc, UPDATES, NEVER_AUTO)
            if original_mode != ANY_REPOSITORY:
                set_value(self.rpc, MODE, ANY_REPOSITORY)
        except (RuntimeError, ValueError, TypeError):
            restore(self.profile, self.rpc)
            raise
        self.active = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.active = False
        restore(self.profile, self.rpc)
        return False
