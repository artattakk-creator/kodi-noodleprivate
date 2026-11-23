"""Private local before-images for the setup transaction and XCMate user data."""
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import tempfile
import time
import xml.etree.ElementTree as ET

from setup_bingie_apply import MENU_FILENAME, PROPS_FILENAME
from setup_compat27 import BINGIE, BRANDING, XCMATE, Blocked
from setup_patch import FILES, digest
from setup_tmdb_player import PLAYER_FILE
from setup_tmdb_apply import ALT_PLAYER_FILE

TMDB = "plugin.video.themoviedb.helper"
BRAND_FILES = (
    "xml/Custom_1101_StartUp.xml", "xml/Custom_1102_StartUp2.xml",
    "xml/Custom_1103_StartUpMask.xml", "colors/defaults.xml",
    "extras/media/bingie_splash.png", "extras/media/bingie_splash2.png",
    "extras/media/netflix_intro_2_1080p.mp4", "extras/media/netflix_intro_2_2160p.mp4",
    "extras/media/netflix_intro_1080p.mp4", "extras/media/netflix_intro_2160p.mp4",
    "extras/media/netflix_intro_extended_1080p.mp4",
)
WRITE_PATHS = {
    "skin": FILES + BRAND_FILES,
    "skin_settings": ("settings.xml",),
    "shortcuts": (MENU_FILENAME, PROPS_FILENAME),
    "tmdb": ("settings.xml", "players/" + PLAYER_FILE, "players/" + ALT_PLAYER_FILE),
    "branding": ("state.json",),
    "patch": FILES,
}
MAX_MANIFEST = 16 * 1024 * 1024


def path_at(root, relative):
    parts = relative.split("/")
    if any(not part or part in (".", "..") or "\\" in part for part in parts):
        raise ValueError("UNSAFE_BACKUP_PATH")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("UNSAFE_BACKUP_PATH")
    return path


def roots(profile):
    import xbmcaddon
    import xbmcvfs

    def translated(path):
        path = Path(xbmcvfs.translatePath(path))
        if not path.is_absolute():
            raise ValueError("PROFILE_IS_NOT_LOCAL")
        # Kodi owns the profile anchor. Reject links below it in path_at().
        return path.resolve()

    def profile_of(ident):
        base = translated("special://profile/")
        return path_at(base, "addon_data/" + ident)

    skin = Path(xbmcvfs.translatePath(xbmcaddon.Addon(BINGIE).getAddonInfo("path")))
    if not skin.is_absolute() or skin.name != BINGIE or skin.is_symlink():
        raise ValueError("UNSAFE_SKIN_LOCATION")
    return {
        "skin": skin.resolve(), "skin_settings": profile_of(BINGIE),
        "shortcuts": profile_of("script.skinshortcuts"), "tmdb": profile_of(TMDB),
        "branding": profile_of(BRANDING), "xcmate": profile_of(XCMATE),
        "kodi": translated("special://profile/"), "patch": path_at(Path(profile).resolve(), "skinpatch-060"),
    }


def atomic(path, write, mode=0o600):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("UNSAFE_WRITE_PATH")
    fd, tmp = tempfile.mkstemp(prefix=".gsmedia27-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path, value):
    atomic(path, lambda stream: stream.write(json.dumps(value, sort_keys=True).encode("utf-8")))


def copy(source, target, mode=0o600):
    def stream_copy(out):
        with source.open("rb") as stream:
            shutil.copyfileobj(stream, out, length=1024 * 1024)
    atomic(target, stream_copy, mode)


def identity(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("UNSAFE_BACKUP_FILE")
    return info.st_size, info.st_mtime_ns, info.st_ino, stat.S_IMODE(info.st_mode) & 0o777


def inventory(mapping, *, managed_only=False):
    for group, paths in WRITE_PATHS.items():
        for name in paths:
            source = path_at(mapping[group], name)
            yield group, name, source, identity(source) if source.exists() else None
    if managed_only:
        return
    for group in ("xcmate", "shortcuts", "tmdb", "kodi"):
        root = mapping[group]
        if group == "kodi":
            files = (root / "favourites.xml",)
        elif root.is_dir():
            files = root.rglob("*")
        else:
            continue
        for source in files:
            name = source.relative_to(root).as_posix()
            if name in WRITE_PATHS.get(group, ()) or source.is_dir() and not source.is_symlink():
                continue
            # SQLite online backup includes WAL state. These sidecars and
            # packaging/cache temporaries must not be restored independently.
            if source.name.endswith(("-wal", "-shm", "-journal", ".tmp", ".lock", ".pyc")):
                continue
            source = path_at(root, name)
            if source.exists():
                yield group, name, source, identity(source)


def sqlite_copy(source, destination, cancel):
    deadline = time.monotonic() + 90

    def progress(status, remaining, total):
        if cancel():
            raise Blocked("CANCELLED_OR_SHUTDOWN")
        if time.monotonic() > deadline:
            raise TimeoutError("SQLITE_BACKUP_TIMEOUT")

    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True, timeout=2)) as db:
        with closing(sqlite3.connect(destination)) as target:
            db.backup(target, pages=256, progress=progress, sleep=0.05)
    with closing(sqlite3.connect(destination.as_uri() + "?mode=ro", uri=True)) as check:
        if check.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("SQLITE_BACKUP_INTEGRITY")
    with destination.open("rb") as stream:
        os.fsync(stream.fileno())


def start(profile, mapping, skin, cancel=lambda: False, *, managed_only=False):
    """Make and read back all before-images before any managed configuration write."""
    profile = Path(profile).resolve()
    profile.mkdir(mode=0o700, parents=True, exist_ok=True)
    entries = list(inventory(mapping, managed_only=managed_only))
    sizes = [meta[0] for _, _, _, meta in entries if meta is not None]
    # Account for an atomic replacement, private copies and active SQLite WALs.
    wal = sum(Path(str(source) + "-wal").stat().st_size
              for _, _, source, meta in entries if meta and Path(str(source) + "-wal").is_file())
    if shutil.disk_usage(profile).free < sum(sizes) + max(sizes, default=0) + wal:
        raise Blocked("BACKUP_LOCAL_SPACE_INSUFFICIENT")
    backup = Path(tempfile.mkdtemp(prefix="backup-0527-", dir=profile))
    record = {"directory": backup.name, "previous_skin": skin, "status": "pending"}
    manifest = []
    try:
        for index, (group, name, source, before) in enumerate(entries):
            if cancel():
                raise Blocked("CANCELLED_OR_SHUTDOWN")
            item = {"group": group, "name": name, "backup": None}
            if before is not None:
                target = backup / str(index)
                with source.open("rb") as stream:
                    is_sqlite = stream.read(16) == b"SQLite format 3\x00"
                if is_sqlite:
                    sqlite_copy(source, target, cancel)
                    expected = digest(target)
                else:
                    expected = digest(source)
                    copy(source, target)
                    if identity(source) != before or digest(source) != expected:
                        raise Blocked("BACKUP_SOURCE_CHANGED")
                if digest(target) != expected:
                    raise Blocked("BACKUP_READBACK_FAILED")
                item.update(backup=target.name, sha256=expected, mode=before[3])
            manifest.append(item)
        skin_xml = path_at(mapping["skin"], "addon.xml").read_bytes()
        atomic_json(backup / "identity.json", {
            "skin": str(mapping["skin"]), "skin_manifest": digest(mapping["skin"] / "addon.xml"),
            "userdata": str(mapping["kodi"]), "skin_version": ET.fromstring(skin_xml).get("version"),
        })
        atomic_json(backup / "manifest.json", manifest)
        verify(profile, record)
        return record
    except (OSError, ValueError, sqlite3.Error, Blocked):
        shutil.rmtree(backup)
        raise


def verify(profile, record):
    backup_name = record["directory"]
    if not isinstance(backup_name, str) or not backup_name.startswith("backup-0527-"):
        raise ValueError("BACKUP_REFERENCE_INVALID")
    backup = path_at(Path(profile).resolve(), backup_name)
    path = path_at(backup, "manifest.json")
    if path.stat().st_size > MAX_MANIFEST:
        raise ValueError("BACKUP_MANIFEST_TOO_LARGE")
    entries = json.loads(path.read_text(encoding="utf-8"))
    for row in entries:
        if row["backup"] is not None:
            source = path_at(backup, row["backup"])
            identity(source)
            if digest(source) != row["sha256"]:
                raise ValueError("BACKUP_READBACK_FAILED")
    return backup, entries


def writable_preflight(mapping):
    """Exercise create/fsync/rename/readback in each directory the patch writes."""
    parents = set()
    for group, paths in WRITE_PATHS.items():
        for name in paths:
            parent = path_at(mapping[group], name).parent
            while not parent.exists():
                parent = parent.parent
            parents.add(parent)
    for parent in parents:
        with tempfile.TemporaryDirectory(prefix=".gsmedia27-probe-", dir=parent) as tmp:
            target = Path(tmp) / "write"
            atomic(target, lambda stream: stream.write(b"GS Media Setup 0.5.27"))
            if target.read_bytes() != b"GS Media Setup 0.5.27":
                raise ValueError("PATCH_WRITABILITY_READBACK_FAILED")


def restore_config(profile, record, mapping):
    backup, entries = verify(profile, record)
    before = json.loads(path_at(backup, "identity.json").read_text(encoding="utf-8"))
    if (before["skin"] != str(mapping["skin"]) or before["userdata"] != str(mapping["kodi"])
            or before["skin_version"] != "2.2.3"
            or before["skin_manifest"] != digest(path_at(mapping["skin"], "addon.xml"))):
        raise ValueError("ROLLBACK_SKIN_OR_PROFILE_CHANGED")
    managed = [row for row in entries if row["name"] in WRITE_PATHS.get(row["group"], ())]
    if {(row["group"], row["name"]) for row in managed} != {
            (group, name) for group, names in WRITE_PATHS.items() for name in names}:
        raise ValueError("BACKUP_MANAGED_INVENTORY_MISMATCH")
    # Keep a separate verified copy of the current configuration, including
    # user/Kodi edits since the original transaction, before overwriting it.
    writable_preflight(mapping)
    start(profile, mapping, record["previous_skin"], managed_only=True)
    for row in managed:
        dest = path_at(mapping[row["group"]], row["name"])
        if row["backup"] is None:
            dest.unlink(missing_ok=True)
            if dest.exists():
                raise ValueError("ROLLBACK_REMOVAL_FAILED")
        else:
            copy(path_at(backup, row["backup"]), dest, row["mode"])
            if digest(dest) != row["sha256"]:
                raise ValueError("ROLLBACK_READBACK_FAILED")


def stage_xcmate(profile, record, destination):
    """Recover the protected XCMate profile to a new, private directory."""
    backup, entries = verify(profile, record)
    rows = [row for row in entries if row["group"] == "xcmate" and row["backup"] is not None]
    if not rows:
        raise ValueError("XCMATE_BACKUP_EMPTY")
    destination.mkdir(mode=0o700, exist_ok=False)
    try:
        for row in rows:
            target = path_at(destination, row["name"])
            copy(path_at(backup, row["backup"]), target)
            if digest(target) != row["sha256"]:
                raise ValueError("XCMATE_RECOVERY_READBACK_FAILED")
    except (ValueError, OSError):
        shutil.rmtree(destination)
        raise
