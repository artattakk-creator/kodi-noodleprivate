"""Atomic, private, add-on-ID-only journal for the 0.5 installer."""
import json
import os
import tempfile
from pathlib import Path
from setup_auto50 import validate

JOURNAL = "auto-setup-050.json"
MAX_BYTES = 20000


def _target(profile):
    folder = Path(profile).resolve()
    if folder.name != "script.gsmedia.setup":
        raise ValueError("Untrusted addon profile")
    return folder / JOURNAL


def load(profile):
    target = _target(profile)
    if target.is_symlink():
        raise ValueError("Setup journal symlink")
    if not target.exists():
        return None
    if target.stat().st_size > MAX_BYTES:
        raise ValueError("Oversized setup journal")
    with target.open("r", encoding="utf-8") as stream:
        return validate(json.load(stream))


def save(profile, state):
    validate(state)
    target = _target(profile)
    if target.is_symlink():
        raise ValueError("Setup journal symlink")
    raw = json.dumps(state, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Oversized setup journal")
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=str(target.parent), prefix=".gs50-")
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, str(target))
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)
