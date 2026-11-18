#!/usr/bin/env python3
"""Stage the private XCMate backup to a new local directory with Kodi closed."""
import argparse
from hashlib import sha256
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from build_gsmedia_setup_0527 import NAME, PREFIX


def restore(installer, profile, backup, destination):
    if installer.name != NAME or not re.fullmatch(r"backup-0527-[a-z0-9_]+", backup):
        raise ValueError("RECOVERY_INPUT_INVALID")
    expected = installer.with_suffix(".zip.sha256").read_text(encoding="ascii").split()
    if expected != [sha256(installer.read_bytes()).hexdigest(), NAME]:
        raise ValueError("RECOVERY_INSTALLER_HASH_INVALID")
    with TemporaryDirectory(prefix="gsmedia0527-recovery-") as folder, ZipFile(installer) as archive:
        for name in archive.namelist():
            if re.fullmatch(re.escape(PREFIX) + r"resources/lib/[a-zA-Z0-9_]+\.py", name):
                (Path(folder) / Path(name).name).write_bytes(archive.read(name))
        sys.path.insert(0, folder)
        try:
            from setup_backup27 import stage_xcmate
            stage_xcmate(profile, {"directory": backup}, destination)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installer", type=Path, required=True)
    parser.add_argument("--setup-profile", type=Path, required=True)
    parser.add_argument("--backup", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    restore(args.installer, args.setup_profile, args.backup, args.out)
    print("XCMate-Sicherung in neuem Verzeichnis wiederhergestellt und verifiziert.")
