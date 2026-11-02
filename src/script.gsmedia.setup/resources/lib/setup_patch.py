"""Strict, rollback-capable GS Media BINGIE 2.2.3 source patch installer.

The four patch payloads are copied from XCMate 0.1.29.60 review and carry
GPLv2 license text. NEVER patch a modified skin: the full original SHA256
for EVERY target must match the historical manifest before writing anything.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

FILES = ("xml/IncludesHomeWidgets.xml", "xml/IncludesHomeBingie.xml",
         "shortcuts/overrides.xml", "shortcuts/template.xml")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for part in iter(lambda: f.read(65536), b""):
            h.update(part)
    return h.hexdigest()


def _manifest(package):
    data = json.loads((package / "manifest.json").read_text("utf-8"))
    if data.get("skin_version") != "2.2.3" or set(data.get("files", {})) != set(FILES):
        raise ValueError("Unapproved skin patch manifest")
    return data


def inspect(package_dir, skin_dir, version):
    """No writes; reports exactly why a file is not compatible."""
    package, skin = Path(package_dir).resolve(), Path(skin_dir).resolve()
    if skin.name != "skin.titan.bingie.mod" or version != "2.2.3":
        return {"code": "UNSUPPORTED_SKIN_VERSION"}
    if not (package / "LICENSE.BINGIE").is_file():
        return {"code": "MISSING_LICENSE"}
    try:
        manifest = _manifest(package)
    except (ValueError, OSError, KeyError):
        return {"code": "INVALID_MANIFEST"}
    statuses = {}
    for relative in FILES:
        origin = skin / relative
        target = package / relative
        if (origin.is_symlink() or target.is_symlink() or
                not origin.is_file() or not target.is_file()):
            return {"code": "SKIN_FILE_MISSING_OR_LINK", "file": relative}
        actual = digest(origin)
        expected = manifest["files"][relative]
        if digest(target) != expected["after"]:
            return {"code": "PATCH_PAYLOAD_HASH_MISMATCH", "file": relative}
        if actual == expected["before"]:
            statuses[relative] = "NEEDS_PATCH"
        elif actual == expected["after"]:
            statuses[relative] = "ALREADY_PATCHED"
        else:
            return {"code": "SOURCE_HASH_MISMATCH", "file": relative}
    return {"code": "READY", "files": statuses,
            "pending": tuple(k for k, v in statuses.items() if v == "NEEDS_PATCH")}


def apply(package_dir, skin_dir, backup_root, version, user_approved=False):
    if not user_approved:
        return {"code": "NOT_AUTHORIZED"}
    package, skin = Path(package_dir).resolve(), Path(skin_dir).resolve()
    dest = Path(backup_root).resolve()
    if dest.name != "skinpatch-060" or "script.gsmedia.setup" not in dest.parts:
        return {"code": "UNTRUSTED_BACKUP_PATH"}
    status = inspect(package, skin, version)
    if status["code"] != "READY":
        return status
    todo = status["pending"]
    if not todo:
        return {"code": "ALREADY_PATCHED"}
    # Backup all ORIGINAL skin XMLs to private addon_data before changing any.
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    for relative in FILES:
        target = dest / relative
        if target.exists():
            return {"code": "PREEXISTING_BACKUP_PRESERVED", "file": relative}
    written = []
    replaced = []
    try:
        for relative in FILES:
            backup_file = dest / relative
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            with backup_file.open("xb") as output, (skin / relative).open("rb") as source:
                shutil.copyfileobj(source, output)
            written.append(backup_file)
        for relative in todo:
            original = skin / relative
            fd, temporary = tempfile.mkstemp(prefix=".gsmedia-", dir=str(original.parent))
            try:
                with os.fdopen(fd, "wb") as output, (package / relative).open("rb") as source:
                    shutil.copyfileobj(source, output)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(temporary, original)
                replaced.append(relative)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        after = inspect(package, skin, version)
        if after.get("code") != "READY" or after.get("pending"):
            raise ValueError("Post-apply hash check failed")
        return {"code": "APPLIED_AND_VERIFIED", "backup": str(dest)}
    except (OSError, ValueError):
        for relative in reversed(replaced):
            try:
                shutil.copyfile(str(dest / relative), str(skin / relative))
            except OSError:
                return {"code": "ROLLBACK_FAILED_MANUAL_RESTORE_REQUIRED"}
        return {"code": "PATCH_FAILED_ROLLED_BACK"}
