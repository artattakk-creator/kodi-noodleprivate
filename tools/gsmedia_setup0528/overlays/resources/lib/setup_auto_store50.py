"""Atomic private setup journal with a read-only 0.5.27 fallback."""
import json
import os
import stat
import tempfile
from pathlib import Path
from setup_auto50 import validate

JOURNAL = "auto-setup-0528.json"
LEGACY_JOURNAL = "auto-setup-0527.json"
MAX_BYTES = 20000


def _target(profile, name):
    folder = Path(profile).resolve()
    if folder.name != "script.gsmedia.setup":
        raise ValueError("Untrusted addon profile")
    return folder / name


def _read(target):
    try:
        fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("Untrusted setup journal")
        raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Oversized setup journal")
    return validate(json.loads(raw.decode("utf-8")))


def load(profile, *, legacy=True):
    state = _read(_target(profile, JOURNAL))
    if state is None and legacy:
        return _read(_target(profile, LEGACY_JOURNAL))
    return state


def migrate(profile):
    """Called after user approval while holding the shared .27/.28 lease."""
    if load(profile, legacy=False) is None:
        previous = _read(_target(profile, LEGACY_JOURNAL))
        if previous is not None:
            save(profile, previous)


def save(profile, state):
    validate(state)
    target = _target(profile, JOURNAL)
    if target.is_symlink():
        raise ValueError("Setup journal symlink")
    raw = json.dumps(state, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("Oversized setup journal")
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=str(target.parent), prefix=".gs28-")
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        directory = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        if _read(target) != state:
            raise OSError("SETUP_JOURNAL_READBACK_FAILED")
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)
