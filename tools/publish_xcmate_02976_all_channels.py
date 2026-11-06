#!/usr/bin/env python3
"""Publish the existing verified XCMate .76 ZIP to main GS Media as authorized.

Pilot & NeoDark3 already publish .76; this staged release updates ONLY the
regular Kodi XCMate entry and its checksum, and adds an identical ZIP copy.
No Kodi profile, TMDB token, installed package or installer is modified.
"""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from publish_xcmate_02976_pilot import verify_source_and_zip
from release_channel75 import regular_allowed

ROOT = Path(__file__).resolve().parents[1]
NAME = "plugin.video.xtreammate"
VERSION = "0.1.29.76"
PREVIOUS_REGULAR = "0.1.29.74"
DIGEST = "c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc"
BLOB = "f665607d2784bc29315ee88007530c9b4b34ddb9"
ROOT_ZIP = ROOT / NAME / (NAME + "-" + VERSION + ".zip")
OLD_ROOT_ZIP = ROOT / NAME / (NAME + "-" + PREVIOUS_REGULAR + ".zip")
PILOT_ZIP = ROOT / "online-test" / NAME / (NAME + "-" + VERSION + ".zip")
PILOT = ROOT / "online-test/addons.xml"
PILOT_MD5 = ROOT / "online-test/addons.xml.md5"
MAIN = ROOT / "addons.xml"
MAIN_MD5 = ROOT / "addons.xml.md5"
INDEX = ROOT / "index.html"
NEODARK3 = ROOT / "online-test/index.html"
APPROVAL = ROOT / "docs/XCMate/releases/user-approved-untested-0.1.29.76.json"


def md5(data):
    return hashlib.md5(data).hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def entries(data):
    root = ET.fromstring(data)
    addons = list(root.findall("addon"))
    ids = [a.get("id") for a in addons]
    if len(addons) != len(ids) or len(ids) != len(set(ids)) or NAME not in ids:
        raise ValueError("XCMATE_INDEX_MALFORMED_OR_DUPLICATE")
    return {a.get("id"): a for a in addons}


def publish():
    payload = verify_source_and_zip()
    if sha256(payload) != DIGEST or git_blob(payload) != BLOB:
        raise ValueError("XCMATE_076_ORIGINAL_REVIEW_PACKAGE_CHANGED")
    if PILOT_ZIP.read_bytes() != payload:
        raise ValueError("XCMATE_PILOT_NOT_IDENTICAL_TO_REVIEW_PACKAGE")
    if not regular_allowed():
        raise ValueError("XCMATE_076_REGULAR_USER_APPROVAL_GATE_FAILED")
    approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
    if (approval.get("android_status") != "NOT_TESTED"
            or approval.get("user_approved_regular_release") is not True
            or approval.get("sha256") != DIGEST):
        raise ValueError("XCMATE_UNVERIFIED_USER_APPROVAL_RECORD")

    pbytes = PILOT.read_bytes()
    pentries = entries(pbytes)
    if pentries[NAME].get("version") != VERSION:
        raise ValueError("XCMATE_PILOT_REPO_NOT_076")
    if PILOT_MD5.read_text("ascii").strip() != md5(pbytes):
        raise ValueError("XCMATE_PILOT_MD5_WRONG")
    neodark = NEODARK3.read_text(encoding="utf-8")
    link = NAME + "/" + NAME + "-" + VERSION + ".zip"
    if neodark.count(link) != 1:
        raise ValueError("XCMATE_NEODARK3_076_LINK_MISSING")
    regular_before = MAIN.read_bytes()
    regular_entries_before = entries(regular_before)
    if regular_entries_before[NAME].get("version") not in (
            PREVIOUS_REGULAR, VERSION):
        raise ValueError("XCMATE_MAIN_REPO_UNEXPECTED_VERSION")
    if MAIN_MD5.read_text("ascii").strip() != md5(regular_before):
        raise ValueError("XCMATE_MAIN_REPO_PRIOR_MD5_MISMATCH")
    if not OLD_ROOT_ZIP.is_file():
        raise ValueError("XCMATE_REGULAR_074_ZIP_NOT_PRESERVED")
    if ROOT_ZIP.exists() and ROOT_ZIP.read_bytes() != payload:
        raise ValueError("XCMATE_REGULAR_076_DIFFERENT_EXISTING_ZIP")
    old_entry = re.search(
        rb'<addon id="plugin\.video\.xtreammate"[\s\S]*?</addon>',
        regular_before,
    )
    if old_entry is None:
        raise ValueError("XCMATE_MAIN_ENTRY_MISSING")
    source = (ROOT / "src" / NAME / "addon.xml").read_bytes()
    begin = source.index(b'<addon id="plugin.video.xtreammate"')
    new_entry = source[begin:].strip()
    if not new_entry.endswith(b"</addon>"):
        raise ValueError("XCMATE_MANIFEST_SOURCE_INVALID")
    future = (regular_before[:old_entry.start()] + new_entry +
              regular_before[old_entry.end():])
    future_entries = entries(future)
    if set(regular_entries_before) != set(future_entries):
        raise ValueError("XCMATE_MAIN_UNRELATED_ADDON_IDS_CHANGED")
    for ident, item in regular_entries_before.items():
        if ident != NAME and ET.tostring(item) != ET.tostring(future_entries[ident]):
            raise ValueError("XCMATE_MAIN_UNRELATED_ADDON_CHANGED:" + ident)
    if future_entries[NAME].get("version") != VERSION:
        raise ValueError("XCMATE_MAIN_NEW_VERSION_WRONG")
    # XML renderers may emit different insignificant whitespace between
    # elements (especially different <addon> tails). Kodi's metadata must be
    # semantically identical, not byte-identical in formatting.
    root_semantic = ET.canonicalize(
        ET.tostring(future_entries[NAME], encoding="unicode"), strip_text=True)
    pilot_semantic = ET.canonicalize(
        ET.tostring(pentries[NAME], encoding="unicode"), strip_text=True)
    if root_semantic != pilot_semantic:
        raise ValueError("XCMATE_MAIN_AND_PILOT_METADATA_MISMATCH")

    html_before = INDEX.read_text(encoding="utf-8")
    release_line = (
        '<a href="plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.76.zip">'
        'XCMate 0.1.29.76</a>  Reguläres GS Media (Android-Abnahme ausstehend)'
    )
    if release_line not in html_before:
        if html_before.count("</pre>") != 1:
            raise ValueError("XCMATE_MAIN_HTML_UNEXPECTED")
        html_after = html_before.replace("</pre>", release_line + "\n</pre>")
    else:
        html_after = html_before
    # All checks complete. Only regular channel package, index and checksum
    # are staged. Pilot and NeoDark3 remain byte-for-byte identical.
    ROOT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    ROOT_ZIP.write_bytes(payload)
    ROOT_ZIP.with_suffix(".zip.sha256").write_text(
        DIGEST + "  " + ROOT_ZIP.name + "\n", encoding="ascii"
    )
    MAIN.write_bytes(future)
    MAIN_MD5.write_text(md5(future) + "\n", encoding="ascii")
    if html_after != html_before:
        INDEX.write_text(html_after, encoding="utf-8")
    if (MAIN_MD5.read_text("ascii").strip() != md5(MAIN.read_bytes())
            or ROOT_ZIP.read_bytes() != PILOT_ZIP.read_bytes()
            or git_blob(ROOT_ZIP.read_bytes()) != BLOB
            or PILOT.read_bytes() != pbytes
            or NEODARK3.read_text(encoding="utf-8") != neodark
            or not OLD_ROOT_ZIP.exists()):
        raise ValueError("XCMATE_CROSS_CHANNEL_OR_PRESERVATION_FAILED")
    return {
        "version": VERSION,
        "regular": "PUBLISHED",
        "pilot": "PUBLISHED_UNCHANGED",
        "neodark3": "PUBLISHED_UNCHANGED",
        "android": "NOT_TESTED",
        "user_authorized_without_android_pass": True,
        "source_blob": BLOB,
        "sha256": DIGEST,
        "root_md5": md5(future),
        "regular_previous_zip_preserved": True,
        "installer_0_5_26_untouched": True,
    }


if __name__ == "__main__":
    print(json.dumps(publish(), sort_keys=True, indent=2))
