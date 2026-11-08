#!/usr/bin/env python3
"""Publish the previously reviewed XCMate .79 ZIP to regular GS Media MAIN only.

Explicit approval is limited to .79 and the regular main channel. The Pilot and
NeoDark3 catalogs and installer stay untouched. Android remains NOT_TESTED.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ADDON = "plugin.video.xtreammate"
VERSION = "0.1.29.79"
PREVIOUS = "0.1.29.78"
NAME = ADDON + "-" + VERSION + ".zip"
PACKAGE = ROOT / "docs/XCMate/test-builds/02979" / NAME
DESTINATION = ROOT / ADDON / NAME
INDEX = ROOT / "addons.xml"
CHECKSUM = ROOT / "addons.xml.md5"
HTML = ROOT / "index.html"
EXPECTED_SHA = "cb68d09c84c7190bf1459d0d46532920d6c5a7dfea15a96a6d5e6cb4f244c20a"
EXPECTED_BYTES = 3460002
EXPECTED_COUNT = 749
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/"
RELEASE_AUDIT = ROOT / "docs/XCMate/releases/user-approved-untested-0.1.29.79.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def catalog(data: bytes) -> dict[str, ET.Element]:
    elements = ET.fromstring(data).findall("addon")
    ids = [x.get("id") for x in elements]
    if not elements or len(ids) != len(set(ids)):
        raise ValueError("KODI_INDEX_DUPLICATE_OR_EMPTY")
    return dict(zip(ids, elements))


def canonical(element: ET.Element) -> str:
    return ET.canonicalize(
        ET.tostring(element, encoding="unicode"), strip_text=True
    )


def approved() -> None:
    from release_channel75 import regular_allowed
    info = json.loads(RELEASE_AUDIT.read_text(encoding="utf-8"))
    required = {
        "addon_id": ADDON,
        "version": VERSION,
        "exception_applies_only_to_version": VERSION,
        "user_approved_regular_release": True,
        "user_approved_all_channels": False,
        "android_status": "NOT_TESTED",
        "android_pass_claimed": False,
        "source_merge_pr": 388,
        "authorization_issue": 387,
        "sha256": EXPECTED_SHA,
        "installer_0_5_26_unchanged": True,
    }
    if any(info.get(k) != v for k, v in required.items()):
        raise ValueError("XCMATE_02979_MAIN_USER_APPROVAL_INVALID")
    if not regular_allowed():
        raise ValueError("XCMATE_02979_MAIN_RELEASE_GATE_CLOSED")


def reviewed_package() -> tuple[bytes, bytes]:
    raw = PACKAGE.read_bytes()
    if len(raw) != EXPECTED_BYTES or sha256(raw) != EXPECTED_SHA:
        raise ValueError("XCMATE_02979_REVIEW_ZIP_CHANGED")
    if PACKAGE.with_suffix(".zip.sha256").read_text("ascii").split()[0] != EXPECTED_SHA:
        raise ValueError("XCMATE_02979_REVIEW_CHECKSUM_CHANGED")
    report = json.loads((PACKAGE.parent / "package-report.json").read_text(encoding="utf-8"))
    for field, expected in (
        ("bytes", EXPECTED_BYTES), ("files", EXPECTED_COUNT),
        ("sha256", EXPECTED_SHA), ("version", VERSION)
    ):
        if report.get(field) != expected:
            raise ValueError("XCMATE_02979_REVIEW_REPORT_CHANGED:" + field)
    source = ROOT / "src" / ADDON
    root = ET.parse(source / "addon.xml").getroot()
    if (root.get("id"), root.get("version")) != (ADDON, VERSION):
        raise ValueError("XCMATE_02979_SOURCE_VERSION_MISMATCH")
    manifest = (source / "addon.xml").read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError("XCMATE_02979_CRC_FAILED")
        names = z.namelist()
        if len(names) != EXPECTED_COUNT or len(names) != len(set(names)):
            raise ValueError("XCMATE_02979_ENTRY_COUNT_MISMATCH")
        for name in names:
            posix = PurePosixPath(name)
            if posix.is_absolute() or ".." in posix.parts or not name.startswith(ADDON + "/"):
                raise ValueError("XCMATE_02979_UNSAFE_ARCHIVE_PATH")
        sources = {
            ADDON + "/" + p.relative_to(source).as_posix(): p
            for p in source.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
            and p.suffix not in (".pyc", ".pyo") and p.name != ".DS_Store"
        }
        if set(sources) != set(names):
            raise ValueError("XCMATE_02979_SOURCE_FILESET_MISMATCH")
        for name, path in sources.items():
            if z.read(name) != path.read_bytes():
                raise ValueError("XCMATE_02979_SOURCE_BYTES_MISMATCH:" + name)
        if z.read(ADDON + "/addon.xml") != manifest:
            raise ValueError("XCMATE_02979_MANIFEST_BYTES_MISMATCH")
    return raw, manifest


def expected_index(before: bytes, manifest: bytes) -> bytes:
    old_catalog = catalog(before)
    if ADDON not in old_catalog:
        raise ValueError("XCMATE_MAIN_ENTRY_MISSING")
    if old_catalog[ADDON].get("version") not in (PREVIOUS, VERSION):
        raise ValueError("XCMATE_MAIN_UNEXPECTED_PREVIOUS_VERSION")
    inner = re.sub(r'^\s*<\?xml[^>]*\?>\s*', "", manifest.decode("utf-8")).strip()
    pattern = rb'<addon\b(?=[^>]*\bid="plugin\.video\.xtreammate")[^>]*>.*?</addon>'
    replacement = inner.encode("utf-8")
    after, n = re.subn(pattern, lambda _: replacement, before, flags=re.S)
    if n != 1:
        raise ValueError("XCMATE_MAIN_ENTRY_REPLACEMENT_COUNT")
    new_catalog = catalog(after)
    if old_catalog.keys() != new_catalog.keys():
        raise ValueError("XCMATE_MAIN_UNRELATED_ADDON_IDS_CHANGED")
    for addon, value in old_catalog.items():
        if addon != ADDON and canonical(value) != canonical(new_catalog[addon]):
            raise ValueError("XCMATE_MAIN_UNRELATED_ADDON_CHANGED:" + addon)
    if canonical(new_catalog[ADDON]) != canonical(ET.fromstring(manifest)):
        raise ValueError("XCMATE_MAIN_SOURCE_METADATA_MISMATCH")
    if new_catalog["script.gsmedia.setup"].get("version") != "0.5.26":
        raise ValueError("GS_MEDIA_INSTALLER_FROZEN_VERSION_CHANGED")
    return after


def stage() -> dict:
    approved()
    payload, manifest = reviewed_package()
    previous_root = ROOT / ADDON / (ADDON + "-" + PREVIOUS + ".zip")
    if not previous_root.is_file():
        raise ValueError("XCMATE_02978_PREVIOUS_PACKAGE_MISSING")
    if DESTINATION.exists() and DESTINATION.read_bytes() != payload:
        raise ValueError("XCMATE_02979_ALREADY_PUBLISHED_WITH_DIFFERENT_BYTES")
    before = INDEX.read_bytes()
    if CHECKSUM.read_text("ascii").strip() != md5(before):
        raise ValueError("XCMATE_MAIN_PRIOR_MD5_MISMATCH")
    updated = expected_index(before, manifest)
    pilot = (ROOT / "online-test/addons.xml").read_bytes()
    if catalog(pilot)[ADDON].get("version") != PREVIOUS:
        raise ValueError("XCMATE_PILOT_UNEXPECTED_VERSION")
    if (ROOT / "online-test/addons.xml.md5").read_text("ascii").strip() != md5(pilot):
        raise ValueError("XCMATE_PILOT_MD5_MISMATCH")
    html = HTML.read_text(encoding="utf-8")
    link = ADDON + "/" + NAME
    fragment = '<a href="' + link + '">XCMate ' + VERSION + '</a>  GS Media regulär (Android-Abnahme offen)'
    if fragment not in html:
        if html.count("<pre>") != 1:
            raise ValueError("XCMATE_ROOT_INDEX_LAYOUT_CHANGED")
        html = html.replace("<pre>", "<pre>\n" + fragment, 1)
    # All checks completed. Only the regular MAIN repository artifacts mutate.
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(payload)
    DESTINATION.with_suffix(".zip.sha256").write_text(
        EXPECTED_SHA + "  " + NAME + "\n", encoding="ascii"
    )
    INDEX.write_bytes(updated)
    CHECKSUM.write_text(md5(updated) + "\n", encoding="ascii")
    HTML.write_text(html, encoding="utf-8")
    return verify(lambda p: (ROOT / p).read_bytes())


def verify(fetch) -> dict:
    approved()
    raw, manifest = reviewed_package()
    index = fetch("addons.xml")
    checksum = fetch("addons.xml.md5").decode("ascii").strip()
    if checksum != md5(index):
        raise ValueError("MAIN_INDEX_MD5_MISMATCH")
    entries = catalog(index)
    if entries[ADDON].get("version") != VERSION:
        raise ValueError("MAIN_INDEX_NOT_02979")
    if canonical(entries[ADDON]) != canonical(ET.fromstring(manifest)):
        raise ValueError("MAIN_SOURCE_CATALOG_METADATA_MISMATCH")
    if entries["script.gsmedia.setup"].get("version") != "0.5.26":
        raise ValueError("MAIN_INSTALLER_VERSION_CHANGED")
    zip_path = ADDON + "/" + NAME
    if fetch(zip_path) != raw:
        raise ValueError("MAIN_ZIP_NOT_IDENTICAL_TO_REVIEW")
    if fetch(zip_path + ".sha256").decode("ascii").split() != [EXPECTED_SHA, NAME]:
        raise ValueError("MAIN_RELEASE_HASH_MISMATCH")
    if ('href="' + zip_path + '"') not in fetch("index.html").decode("utf-8"):
        raise ValueError("MAIN_DIRECTORY_DOWNLOAD_NOT_LISTED")
    if fetch("online-test/addons.xml") and catalog(fetch("online-test/addons.xml"))[ADDON].get("version") != PREVIOUS:
        raise ValueError("PILOT_WAS_UNEXPECTEDLY_UPDATED")
    return {
        "version": VERSION,
        "main": "RELEASED",
        "pilot": "PRESERVED_02978",
        "neodark3": "PRESERVED_02978",
        "zip_bytes": len(raw),
        "sha256": EXPECTED_SHA,
        "crc": "PASS",
        "source_bytes": "PASS",
        "android": "NOT_TESTED",
        "installer": "0.5.26 unchanged",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    if args.stage:
        result = stage()
    elif args.public:
        def fetch(path):
            with urllib.request.urlopen(BASE + path, timeout=45) as response:
                if response.status != 200:
                    raise ValueError("HTTP_NON_200")
                return response.read(32 * 1024 * 1024)
        result = verify(fetch)
    else:
        result = verify(lambda p: (ROOT / p).read_bytes())
    print(json.dumps(result, indent=2, sort_keys=True))
