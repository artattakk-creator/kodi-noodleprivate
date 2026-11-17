"""Conservative widget50 transaction retention, scoped to disposable plan snapshots.

The only automatically disposable objects are complete private plan directories
inside widget50_plans. Never touch real BINGIE XML, skinshortcuts, or userdata DBs.

A plan is retained only if it is the latest complete transaction whose hashes
match the current target bytes. If current files have diverged or metadata is
ambiguous, retain history rather than guess. PREPARED plans get a grace period.
"""
import hashlib
import json
import os
import re
import stat
import time
from pathlib import Path

HEX_ID = re.compile(r"^[0-9a-f]{32}$")
READY = {"APPLIED", "RESTORED", "ROLLED_BACK"}
IN_FLIGHT = {"PREPARED", "APPLYING", "RESTORING", "INTERRUPTED"}
STALE_PREPARED_SECONDS = 48 * 3600
MAX_PLAN_FILES = 3 * 8 + 2
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
PRUNING = re.compile(r"^\.pruning-([0-9a-f]{32})$")


def _regular(path, max_size=None):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or (max_size is not None and s.st_size > max_size):
        raise ValueError("INVALID_BACKUP_SNAPSHOT")
    return path.read_bytes()


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _valid_plan(root, entry):
    p = root / entry
    if not HEX_ID.fullmatch(entry) or not stat.S_ISDIR(p.lstat().st_mode):
        raise ValueError("INVALID_BACKUP_DIRECTORY")
    plan = json.loads(_regular(p / "plan.json", 128 * 1024))
    status = json.loads(_regular(p / "state.json", 512)).get("state")
    if plan.get("id") != entry or plan.get("kind") not in ("skin", "binding"):
        raise ValueError("INVALID_BACKUP_PLAN")
    if status not in READY | IN_FLIGHT:
        raise ValueError("INVALID_BACKUP_STATE")
    entries = plan.get("entries")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 8:
        raise ValueError("INVALID_BACKUP_ENTRIES")
    at = plan.get("at")
    if not isinstance(at, (int, float)) or at <= 0:
        raise ValueError("INVALID_BACKUP_TIMESTAMP")
    expected_names = {"plan.json", "state.json"}
    seen = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or not isinstance(e.get("target"), str) or not Path(e["target"]).is_absolute():
            raise ValueError("INVALID_BACKUP_ENTRY")
        if not re.fullmatch("[a-f0-9]{64}", str(e.get("before"))) or not re.fullmatch("[a-f0-9]{64}", str(e.get("after"))):
            raise ValueError("INVALID_BACKUP_HASH")
        for kind in ("original", "candidate", "restore-check"):
            expected_names.add(f"{kind}.{i}")
        before = _regular(p / f"original.{i}", MAX_SNAPSHOT_BYTES)
        after = _regular(p / f"candidate.{i}", MAX_SNAPSHOT_BYTES)
        check = _regular(p / f"restore-check.{i}", MAX_SNAPSHOT_BYTES)
        if _digest(before) != e["before"] or _digest(after) != e["after"] or check != before:
            raise ValueError("BACKUP_SNAPSHOT_HASH_MISMATCH")
        seen.append(e["target"])
    if len(set(seen)) != len(seen):
        raise ValueError("DUPLICATE_TARGET")
    if set(os.listdir(p)) != expected_names or len(expected_names) > MAX_PLAN_FILES:
        raise ValueError("UNEXPECTED_BACKUP_FILE")
    return {"id": entry, "kind": plan["kind"], "status": status, "at": float(at),
            "entries": entries, "path": p,
            "group": (plan["kind"], tuple(seen))}


def _matching_reference(plan):
    """Only complete applied/restored plans may identify the live reference."""
    if plan["status"] not in READY:
        return False
    expected = "after" if plan["status"] == "APPLIED" else "before"
    try:
        for entry in plan["entries"]:
            path = Path(entry["target"])
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SNAPSHOT_BYTES:
                return False
            if _digest(path.read_bytes()) != entry[expected]:
                return False
    except (OSError, ValueError):
        return False
    return True


def _finish_quarantine(directory):
    """Complete an earlier interrupted cleanup of a renamed, known-only folder."""
    if not PRUNING.fullmatch(directory.name) or not stat.S_ISDIR(directory.lstat().st_mode):
        raise ValueError("UNSAFE_PRUNING_DIRECTORY")
    content = list(directory.iterdir())
    if len(content) > MAX_PLAN_FILES:
        raise ValueError("UNEXPECTED_BACKUP_FILE")
    allowed = re.compile(r"^(?:plan\.json|state\.json|(?:original|candidate|restore-check)\.[0-7])$")
    for file in content:
        if not allowed.fullmatch(file.name) or not stat.S_ISREG(file.lstat().st_mode):
            raise ValueError("UNEXPECTED_BACKUP_FILE")
    for file in content:
        file.unlink()
    directory.rmdir()


def _purge(plan):
    """Atomically quarantine complete plans, then delete only their files."""
    path = plan["path"]
    filenames = ["plan.json", "state.json"]
    for i in range(len(plan["entries"])):
        filenames.extend([f"original.{i}", f"candidate.{i}", f"restore-check.{i}"])
    if set(os.listdir(path)) != set(filenames):
        raise ValueError("BACKUP_CHANGED_NO_DELETE")
    for filename in filenames:
        if not stat.S_ISREG((path / filename).lstat().st_mode):
            raise ValueError("BACKUP_CHANGED_NO_DELETE")
    quarantine = path.parent / (".pruning-" + plan["id"])
    if quarantine.exists() or quarantine.is_symlink():
        raise ValueError("QUARANTINE_EXISTS")
    path.rename(quarantine)
    _finish_quarantine(quarantine)


def prune(*, directory=None, commit=False, already_locked=False, now=None):
    """Compute or perform a fail-closed, single-live-reference cleanup.

    A group may be pruned only when a complete plan matches all current target
    hashes. All malformed/unknown/in-flight entries are protected. Result is a
    serializable report; no deletion occurs unless commit=True.
    """
    if directory is None:
        from widget_transaction50 import folder
        directory = folder()
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("UNSAFE_BACKUP_FOLDER")
    now = float(time.time() if now is None else now)
    lock = None
    if not already_locked:
        import fcntl
        lock = open(root / ".lock", "a")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError):
            lock.close()
            raise ValueError("PLAN_BUSY") from None
    try:
        valid = []
        blocked = []
        recovered = []
        # Resume interrupted deletes, but never recursively walk arbitrary dirs.
        for item in root.iterdir():
            if PRUNING.fullmatch(item.name):
                if commit:
                    try:
                        _finish_quarantine(item)
                        recovered.append(item.name)
                    except (OSError, ValueError) as exc:
                        blocked.append({"item": item.name, "reason": type(exc).__name__})
                else:
                    blocked.append({"item": item.name, "reason": "PENDING_PRUNE_RECOVERY"})
        for item in root.iterdir():
            if item.name == ".lock" or PRUNING.fullmatch(item.name):
                continue
            try:
                valid.append(_valid_plan(root, item.name))
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                blocked.append({"item": item.name, "reason": type(exc).__name__})
        groups = {}
        for plan in valid:
            groups.setdefault(plan["group"], []).append(plan)
        delete = []
        kept = []
        for key, members in groups.items():
            matches = [p for p in members if _matching_reference(p)]
            # If any unknown/unverified plan exists, don't change retention.
            # Nor change a group without a proven current reference.
            if not matches or blocked:
                kept.extend(members)
                continue
            current = max(matches, key=lambda p: (p["at"], p["id"]))
            for p in members:
                if p is current:
                    kept.append(p)
                elif p["status"] == "PREPARED" and 0 <= now - p["at"] < STALE_PREPARED_SECONDS:
                    kept.append(p)
                elif p["status"] in ("APPLYING", "RESTORING", "INTERRUPTED"):
                    kept.append(p)
                elif p["at"] > now + 300:
                    kept.append(p)
                else:
                    delete.append(p)
        report = {"verified_current": sorted(set(p["id"] for key, members in groups.items() for p in members if _matching_reference(p))),
                  "retained": sorted(p["id"] for p in kept),
                  "deletable": sorted(p["id"] for p in delete),
                  "blocked": blocked, "dry_run": not commit,
                  "removed": [], "recovered": recovered}
        if commit:
            for p in delete:
                try:
                    # Inspect again immediately before the deletion to prevent stale assumptions.
                    current = _valid_plan(root, p["id"])
                    if current["at"] != p["at"] or current["status"] != p["status"]:
                        raise ValueError("BACKUP_CHANGED_NO_DELETE")
                    _purge(current)
                    report["removed"].append(p["id"])
                except (OSError, ValueError) as exc:
                    report["blocked"].append({"item": p["id"], "reason": type(exc).__name__})
        return report
    finally:
        if lock is not None:
            lock.close()
