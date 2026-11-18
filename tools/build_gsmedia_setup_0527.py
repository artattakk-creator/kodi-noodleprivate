#!/usr/bin/env python3
"""Build the review ZIP from the released 0.5.26 package. Local output only."""
import argparse
import ast
from hashlib import sha256
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "script.gsmedia.setup/"
BASE = ROOT / PREFIX / "script.gsmedia.setup-0.5.26.zip"
BASE_SHA = "5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af"
NAME = "script.gsmedia.setup-0.5.27.zip"
OVERLAYS = ROOT / "tools/gsmedia_setup0527/overlays"


def build(output):
    if sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError("BASE_0526_SHA256_MISMATCH")
    with zipfile.ZipFile(BASE) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    # Reuse the exact released implementation of Kodi's native package flow.
    ui = PREFIX + "resources/lib/setup_auto_ui50.py"
    files[PREFIX + "resources/lib/setup_omega26.py"] = files[ui]
    for path in OVERLAYS.rglob("*"):
        if path.is_file() and path.suffix in (".py", ".xml", ".json"):
            files[PREFIX + path.relative_to(OVERLAYS).as_posix()] = path.read_bytes()
    xcmate = ROOT / "src/plugin.video.xtreammate/resources/lib"
    for name in ("tmdb_token61.py", "token_destination65.py", "tmdb_import63.py"):
        files[PREFIX + "resources/lib/" + name] = (xcmate / name).read_bytes()
    for name, data in files.items():
        if not name.startswith(PREFIX) or ".." in PurePosixPath(name).parts or "\\" in name:
            raise ValueError("INVALID_ARCHIVE_PATH")
        if name.endswith(".py"):
            ast.parse(data, filename=name, feature_version=(3, 8))
    addon = ET.fromstring(files[PREFIX + "addon.xml"])
    if (addon.get("id"), addon.get("version")) != ("script.gsmedia.setup", "0.5.27"):
        raise ValueError("UNEXPECTED_ADDON_IDENTITY")

    output.mkdir(parents=True, exist_ok=True)
    result = output / NAME
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 18, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(result) as archive:
        if archive.testzip() or {name: archive.read(name) for name in archive.namelist()} != files:
            raise ValueError("ZIP_READBACK_FAILED")
    result.with_suffix(".zip.sha256").write_text(
        sha256(result.read_bytes()).hexdigest() + "  " + result.name + "\n", encoding="ascii")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    print(build(parser.parse_args().out))
