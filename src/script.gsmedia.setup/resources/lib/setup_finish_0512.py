"""Private one-time handoff marker between verified setup and Kodi restart.

Never changes Kodi's skin or system settings. A restart is confirmed using a
different process PID. Retain failures locally for the optional log view.
"""
import json
import os
from pathlib import Path
import tempfile

MARKER = "auto-setup-0512-handoff.json"


def _path(profile):
    folder = Path(profile).resolve()
    if folder.name != "script.gsmedia.setup" or folder.is_symlink():
        raise ValueError("Untrusted setup profile")
    return folder / MARKER


def _write(profile, document):
    path = _path(profile)
    if path.is_symlink():
        raise ValueError("Untrusted setup marker")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    if len(raw) > 2000:
        raise ValueError("Unbounded marker")
    fd, tmp = tempfile.mkstemp(prefix=".xcmate-0512-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def mark_restart_pending(profile):
    _write(profile, {"schema": 1, "status": "restart_pending",
                     "before_pid": str(os.getpid()), "error": ""})


def read(profile):
    path = _path(profile)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 2000:
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or set(d) != {"schema", "status", "before_pid", "error"}:
        raise ValueError("Invalid marker")
    if d["schema"] != 1 or d["status"] not in ("restart_pending", "complete", "failed"):
        raise ValueError("Invalid marker status")
    if not isinstance(d["before_pid"], str) or not isinstance(d["error"], str):
        raise ValueError("Invalid marker data")
    return d


def finish(profile, status, error=""):
    if status not in ("complete", "failed"):
        raise ValueError("Invalid post-boot state")
    d = read(profile)
    if d is None or d["status"] != "restart_pending":
        raise ValueError("No pending handoff")
    d["status"] = status
    d["error"] = error[:180]
    _write(profile, d)
