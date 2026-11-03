#!/usr/bin/env python3
"""GS Media 0.5.8: reproducible, source-audited MP3 Echoed and EZ Maintenance+ packaging.

MP3 Echoed application code and updated artwork are imported from the user's
authorised Drive backup. Legacy unchanged assets are fetched from the older
author's immutable public Git commit and individually verified as Git blobs.
EZ Maintenance+ is reconstructed from an immutable original developer commit.
No user profile, cookies, databases, logs, *.pyc or cache directories ship.
"""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import posixpath
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ECHOED = ROOT / "vendor/mp3-echoed-2026-source/plugin.audio.m3sr2019"
ECHOED_MEDIA_MANIFEST = ROOT / "vendor/mp3-echoed-2026-source/legacy-media-git-blobs.json"
EZ_MANIFEST = ROOT / "vendor/ezmaintenanceplus-official-20260405/upstream-git-blobs.json"
ECHOED_VERSION = "2026.1.0"
EZ_VERSION = "2026.04.05.0"


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def get_upstream(owner, repository, commit, maximum=22_000_000):
    url = "https://codeload.github.com/{}/{}/zip/{}".format(owner, repository, commit)
    req = urllib.request.Request(url, headers={"User-Agent": "GS-Media-Test-Beta-Source-Verify/0.5.8"})
    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read(maximum + 1)
    assert 1000 < len(data) <= maximum, "Upstream download exceeds bound or is empty"
    result = {}
    with zipfile.ZipFile(BytesIO(data)) as archive:
        assert archive.testzip() is None, "Invalid upstream ZIP"
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename
            pathparts = name.split("/", 1)
            assert len(pathparts) == 2
            path = pathparts[1]
            assert path and not path.startswith("/") and not path.startswith("../")
            assert posixpath.normpath(path) == path
            assert path not in result
            result[path] = archive.read(member)
    return result


def verify_manifest(files, document):
    expected = document["files"]
    for path, spec in expected.items():
        assert path in files, "Upstream source missing: " + path
        data = files[path]
        assert len(data) == spec["size"], "Source length mismatch: " + path
        assert git_blob_sha1(data) == spec["sha1"], "Original Git blob mismatch: " + path


def write_zip(target, ident, source_files):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as archive:
        for path, data in sorted(source_files.items()):
            assert path and not path.startswith("/") and ".." not in path.split("/")
            meta = zipfile.ZipInfo(ident + "/" + path, date_time=(2020, 1, 1, 0, 0, 0))
            meta.compress_type = zipfile.ZIP_DEFLATED
            meta.external_attr = 0o644 << 16
            archive.writestr(meta, data)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        xml = ET.fromstring(archive.read(ident + "/addon.xml"))
        assert xml.get("id") == ident
    return xml


def echo_package(destination):
    doc = json.loads(ECHOED_MEDIA_MANIFEST.read_text(encoding="utf-8"))
    assert doc["commit"] == "2a0f3d44e9d3dfbc853574621682fd377663f541"
    upstream = get_upstream("L2501", "plugin.audio.m3sr2019", doc["commit"])
    verify_manifest(upstream, doc)
    legacy = {key: upstream[key] for key in doc["files"]}
    assert len(legacy) == 244, "Unexpected source-media inventory"
    assert ECHOED.is_dir()
    modern = {}
    for file in ECHOED.rglob("*"):
        if not file.is_file():
            continue
        path = file.relative_to(ECHOED).as_posix()
        assert "__pycache__" not in path and not path.endswith(".pyc")
        assert path not in modern
        modern[path] = file.read_bytes()
    required = {
        "addon.xml", "default.py", "README.md", "LICENSE",
        "resources/__init__.py", "resources/settings.xml",
        "resources/lib/musicmp3.py", "resources/lib/peewee.py",
        "resources/media/icon.png", "resources/media/icon.jpg",
        "resources/media/fanart.jpg",
    }
    assert required <= modern.keys(), "Modern Echoed snapshot incomplete"
    assert len(modern) >= 20, "Missing modern Python modules"
    # Explicitly replace the 2022-era artwork with the user's 2026 artwork.
    legacy.update(modern)
    assert not any(k.startswith("musicmp3/") or k.startswith("userdata/") for k in legacy)
    assert len(legacy) >= 260, "Missing artwork source or modern code"
    ident = "plugin.audio.m3sr2019"
    target = Path(destination) / ident / (ident + "-" + ECHOED_VERSION + ".zip")
    xml = write_zip(target, ident, legacy)
    assert xml.get("version") == ECHOED_VERSION
    deps = {r.get("addon") for r in xml.findall("./requires/import")}
    assert {"xbmc.python", "script.module.requests", "script.module.routing", "script.module.beautifulsoup4"} <= deps
    meta_license = xml.findtext("./extension[@point='xbmc.addon.metadata']/license")
    assert meta_license == "GPL-3.0"
    assert b"Version 2, June 1991" in modern["LICENSE"]
    note = (
        "MP3 Streams Echoed 2026.1.0. Core source and updated artwork: authorised "
        "Google Drive owner backup (captured 2026-10-21); legacy unchanged media: "
        "L2501/plugin.audio.m3sr2019 commit " + doc["commit"] +
        ", independently checked using 244 Git blob SHA-1 values. "
        "Distribution includes all original source, README and LICENSE. "
        "License notice discrepancy retained: addon.xml states GPL-3.0; "
        "inherited LICENSE contains GPL version 2. No ownership claim made. "
        "No private cookies, database, caches or credentials included.\n"
    )
    (target.parent / "SOURCE.txt").write_text(note, encoding="utf-8")
    (target.parent / "icon.png").write_bytes(modern["resources/media/icon.png"])
    (target.parent / "fanart.jpg").write_bytes(modern["resources/media/fanart.jpg"])
    return target, xml


def ez_package(destination):
    doc = json.loads(EZ_MANIFEST.read_text(encoding="utf-8"))
    assert doc["commit"] == "0e8a5bf26917f25ec79a67de1a896d440708c8e3"
    upstream = get_upstream("peno64", "script.ezmaintenanceplus", doc["commit"])
    verify_manifest(upstream, doc)
    original = {path: upstream[path] for path in doc["files"] if not path.startswith(".git")}
    assert len(original) >= 20
    ident = "script.ezmaintenanceplus"
    target = Path(destination) / ident / (ident + "-" + EZ_VERSION + ".zip")
    xml = write_zip(target, ident, original)
    assert xml.get("version") == EZ_VERSION
    assert xml.findtext("./extension[@point='xbmc.addon.metadata']/license") == "The MIT License"
    assert "service.py" in original and "default.py" in original
    assert "script.module.requests" in {x.get("addon") for x in xml.findall("./requires/import")}
    note = (
        "Original EZ Maintenance+ source by aenema, peno, from "
        "https://github.com/peno64/script.ezmaintenanceplus commit " +
        doc["commit"] + ". All 27 upstream source objects verified against "
        "pinned Git blob hashes, original addon.xml and MIT license "
        "statement preserved. No userdata or caches.\n"
    )
    (target.parent / "SOURCE.txt").write_text(note, encoding="utf-8")
    for asset in ("icon.png", "fanart.jpg"):
        if asset in original:
            (target.parent / asset).write_bytes(original[asset])
    return target, xml


if __name__ == "__main__":
    import sys
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / ".build/gsmedia-058-sources")
    print("MP3_ECHOED", echo_package(dest)[0])
    print("EZ_MAINTENANCE", ez_package(dest)[0])
