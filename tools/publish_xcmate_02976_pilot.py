#!/usr/bin/env python3
"""Release exactly the already merged XCMate 0.1.29.76 review ZIP to Pilot only.

No code rebuild, no regular GS Media publication, no Android-userdata changes.
Fail closed if the preserved review ZIP or the expected .75 Pilot state changes.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = "plugin.video.xtreammate"
VERSION = "0.1.29.76"
PREVIOUS = "0.1.29.75"
PINNED_SHA256 = "c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc"
PINNED_BYTES = 3426830
PINNED_COUNT = 729
CANDIDATE = ROOT / "docs/XCMate/test-builds/02976" / (ADDON + "-" + VERSION + ".zip")
PILOT = ROOT / "online-test"
ZIP_OUT = PILOT / ADDON / (ADDON + "-" + VERSION + ".zip")
ZIP_PREVIOUS = PILOT / ADDON / (ADDON + "-" + PREVIOUS + ".zip")
REGULAR = ROOT / "addons.xml"
REGULAR_MD5 = ROOT / "addons.xml.md5"
PILOT_INDEX = PILOT / "addons.xml"
PILOT_CHECKSUM = PILOT / "addons.xml.md5"
PILOT_MANIFEST = PILOT / "manifest.json"
PILOT_HTML = PILOT / "index.html"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def catalog_entries(document: bytes) -> dict[str, ET.Element]:
    entries = ET.fromstring(document).findall("addon")
    ids = [a.get("id") for a in entries]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("PILOT_DUPLICATE_OR_EMPTY_ADDON_INDEX")
    return {a.get("id"): a for a in entries}


def verify_source_and_zip() -> bytes:
    payload = CANDIDATE.read_bytes()
    if len(payload) != PINNED_BYTES or sha256(payload) != PINNED_SHA256:
        raise ValueError("XCMATE_02976_ZIP_PIN_CHANGED")
    sha_file = CANDIDATE.with_suffix(".zip.sha256")
    if sha_file.read_text("ascii").split()[0] != PINNED_SHA256:
        raise ValueError("XCMATE_02976_REVIEW_SHA_FILE_CHANGED")
    source = ROOT / "src" / ADDON
    manifest_source = ET.parse(source / "addon.xml").getroot()
    if (manifest_source.get("id"), manifest_source.get("version")) != (
        ADDON, VERSION
    ):
        raise ValueError("XCMATE_MAIN_SOURCE_IS_NOT_MERGED_02976")
    with zipfile.ZipFile(CANDIDATE) as z:
        if z.testzip() is not None:
            raise ValueError("XCMATE_02976_CRC_FAILED")
        names = z.namelist()
        if len(names) != PINNED_COUNT or len(names) != len(set(names)):
            raise ValueError("XCMATE_02976_ZIP_FILESET_MISMATCH")
        for name in names:
            if not name.startswith(ADDON + "/") or ".." in Path(name).parts or "\\" in name:
                raise ValueError("XCMATE_02976_UNSAFE_ZIP_PATH")
        manifest_zip = ET.fromstring(z.read(ADDON + "/addon.xml"))
        if (manifest_zip.get("id"), manifest_zip.get("version")) != (
            ADDON, VERSION
        ):
            raise ValueError("XCMATE_02976_ZIP_ADDON_ID_VERSION_MISMATCH")
        source_files = [p for p in source.rglob("*") if p.is_file()
                        and "__pycache__" not in p.parts and p.name != ".DS_Store"]
        if len(source_files) != PINNED_COUNT:
            raise ValueError("XCMATE_02976_SOURCE_FILE_COUNT_CHANGED")
        source_names = {ADDON + "/" + p.relative_to(source).as_posix() for p in source_files}
        if set(names) != source_names:
            raise ValueError("XCMATE_02976_SOURCE_FILESET_DIFFERS_FROM_ZIP")
        for p in source_files:
            if z.read(ADDON + "/" + p.relative_to(source).as_posix()) != p.read_bytes():
                raise ValueError("XCMATE_02976_SOURCE_BYTES_DIFFER_FROM_ZIP")
    return payload


def publish() -> dict:
    payload = verify_source_and_zip()
    regular_before = REGULAR.read_bytes()
    regular_md5_before = REGULAR_MD5.read_bytes()
    xml_before = PILOT_INDEX.read_bytes()
    prior = catalog_entries(xml_before)
    if ADDON not in prior or prior[ADDON].get("version") not in (PREVIOUS, VERSION):
        raise ValueError("XCMATE_PILOT_NOT_EXPECTED_075_OR_076")
    if not ZIP_PREVIOUS.is_file():
        raise ValueError("XCMATE_PREVIOUS_PILOT_ZIP_NOT_PRESERVED")
    previous_bytes = ZIP_PREVIOUS.read_bytes()
    if ZIP_OUT.exists() and ZIP_OUT.read_bytes() != payload:
        raise ValueError("XCMATE_EXISTING_076_ZIP_CONFLICT")
    old_entry = re.search(
        rb'<addon id="plugin\.video\.xtreammate"[\s\S]*?</addon>',
        xml_before,
    )
    if old_entry is None:
        raise ValueError("XCMATE_PILOT_ENTRY_MISSING")
    source_text = (ROOT / "src" / ADDON / "addon.xml").read_bytes()
    new_entry = source_text[source_text.index(b'<addon id="plugin.video.xtreammate"'):]
    if not new_entry.rstrip().endswith(b"</addon>"):
        raise ValueError("XCMATE_SOURCE_XML_FORMAT_INVALID")
    new_xml = xml_before[:old_entry.start()] + new_entry.rstrip() + xml_before[old_entry.end():]
    after = catalog_entries(new_xml)
    if set(prior) != set(after):
        raise ValueError("XCMATE_UNRELATED_PILOT_IDS_CHANGED")
    for addon_id, entry in prior.items():
        if addon_id != ADDON and ET.tostring(entry) != ET.tostring(after[addon_id]):
            raise ValueError("XCMATE_UNRELATED_PILOT_ENTRY_CHANGED:" + addon_id)
    if after[ADDON].get("version") != VERSION:
        raise ValueError("XCMATE_PILOT_VERSION_NOT_076")
    if catalog_entries(regular_before)[ADDON].get("version") != "0.1.29.74":
        raise ValueError("XCMATE_REGULAR_RELEASE_MUST_REMAIN_074")
    # All preconditions validated; stage only the Pilot files.
    ZIP_OUT.parent.mkdir(parents=True, exist_ok=True)
    ZIP_OUT.write_bytes(payload)
    ZIP_OUT.with_suffix(".zip.sha256").write_text(
        PINNED_SHA256 + "  " + ZIP_OUT.name + "\n", encoding="ascii"
    )
    PILOT_INDEX.write_bytes(new_xml)
    PILOT_CHECKSUM.write_text(hashlib.md5(new_xml).hexdigest() + "\n", encoding="ascii")
    manifest = json.loads(PILOT_MANIFEST.read_text(encoding="utf-8"))
    manifest["xcmate_02976"] = {
        "addon": ADDON,
        "version": VERSION,
        "source": "docs/XCMate/test-builds/02976/" + ZIP_OUT.name,
        "sha256": PINNED_SHA256,
        "bytes": len(payload),
        "files": PINNED_COUNT,
        "channel": "GS_MEDIA_PILOT_ONLY",
        "source_merge_pr": 370,
        "android_test": "NOT_TESTED",
        "regular_channel_untouched": True,
    }
    PILOT_MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    html = PILOT_HTML.read_text(encoding="utf-8")
    marker = "<tr><th>Name</th><th>Version</th></tr>"
    row = (
        '<tr><td><a href="plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.76.zip">'
        'plugin.video.xtreammate-0.1.29.76.zip</a></td>'
        '<td>XCMate 0.1.29.76 Pilot – nur zum Testen, Android-Abnahme offen</td></tr>'
    )
    if row not in html:
        if html.count(marker) != 1:
            raise ValueError("XCMATE_PILOT_INDEX_HTML_UNEXPECTED")
        html = html.replace(marker, marker + "\n" + row)
        PILOT_HTML.write_text(html, encoding="utf-8")
    if REGULAR.read_bytes() != regular_before or REGULAR_MD5.read_bytes() != regular_md5_before:
        raise ValueError("XCMATE_REGULAR_CATALOG_CHANGED")
    if ZIP_PREVIOUS.read_bytes() != previous_bytes:
        raise ValueError("XCMATE_075_ZIP_MUTATED")
    if ZIP_OUT.read_bytes() != payload:
        raise ValueError("XCMATE_076_STAGE_MISMATCH")
    if PILOT_CHECKSUM.read_text("ascii").strip() != hashlib.md5(PILOT_INDEX.read_bytes()).hexdigest():
        raise ValueError("XCMATE_PILOT_MD5_MISMATCH")
    return {
        "version": VERSION,
        "channel": "pilot_only",
        "sha256": PINNED_SHA256,
        "bytes": len(payload),
        "files": PINNED_COUNT,
        "old_zip_preserved": True,
        "regular_unchanged": True,
        "android": "NOT_TESTED",
        "pilot_xml_md5": hashlib.md5(new_xml).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(publish(), indent=2, sort_keys=True))
