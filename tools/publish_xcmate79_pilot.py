#!/usr/bin/env python3
"""Publish reviewed XCMate .79 only into the Kodi Pilot update catalog.

Required because the user's Kodi logs show repository.gsmedia.pilot installed.
Regular main is already .79; NeoDark3 flat download intentionally stays .78.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

from publish_xcmate79_main import (
    ROOT, ADDON, VERSION, PREVIOUS, NAME, PACKAGE, EXPECTED_SHA, BASE,
    approved as main_approved, reviewed_package, catalog, canonical, md5, expected_index,
)

PILOT=ROOT/"online-test"
PILOT_INDEX=PILOT/"addons.xml"
PILOT_MD5=PILOT/"addons.xml.md5"
PILOT_ZIP=PILOT/ADDON/NAME
PILOT_MANIFEST=PILOT/"manifest.json"
PILOT_HTML=PILOT/"index.html"


def approved():
    main_approved()
    info=json.loads((ROOT/"docs/XCMate/releases/user-approved-untested-0.1.29.79.json").read_text(encoding="utf-8"))
    assert info.get("user_approved_pilot_release") is True, "PILOT_UPDATE_NOT_APPROVED"
    assert info.get("user_approved_all_channels") is False, "PILOT_ONLY_NOT_ALL_CHANNELS"
    assert info.get("android_status")=="NOT_TESTED", "FALSE_ANDROID_PASS"
    assert info.get("sha256")==EXPECTED_SHA, "PILOT_REVIEW_PACKAGE_NOT_PINNED"


def stage():
    approved()
    raw,manifest=reviewed_package()
    regular=(ROOT/"addons.xml").read_bytes()
    assert catalog(regular)[ADDON].get("version")==VERSION, "REGULAR_MAIN_MUST_BE_079"
    assert (ROOT/"addons.xml.md5").read_text("ascii").strip()==md5(regular), "REGULAR_MAIN_MD5_CHANGED"
    assert (ROOT/ADDON/NAME).read_bytes()==raw, "PILOT_AND_MAIN_PACKAGE_CONFLICT"
    before=PILOT_INDEX.read_bytes()
    assert PILOT_MD5.read_text("ascii").strip()==md5(before), "PILOT_PRIOR_MD5_INVALID"
    if catalog(before)[ADDON].get("version") not in (PREVIOUS,VERSION):
        raise ValueError("UNEXPECTED_PILOT_VERSION")
    old=PILOT/ADDON/(ADDON+"-"+PREVIOUS+".zip")
    assert old.is_file(), "MISSING_PREVIOUS_PILOT_PACKAGE"
    if PILOT_ZIP.exists():
        assert PILOT_ZIP.read_bytes()==raw, "PUBLISHED_079_CONFLICT"
    updated=expected_index(before,manifest)
    meta=json.loads(PILOT_MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(meta.get("zip_sha256"),dict), "PILOT_MANIFEST_FORMAT"
    meta["zip_sha256"][ADDON]=EXPECTED_SHA
    meta["xcmate_02979"]={
        "version": VERSION,
        "channel":"GS_MEDIA_PILOT",
        "sha256":EXPECTED_SHA,
        "origin_review_zip":"docs/XCMate/test-builds/02979/"+NAME,
        "user_approved_pilot_update":True,
        "android_test":"NOT_TESTED",
        "neodark3_flat_unchanged":True,
    }
    html=PILOT_HTML.read_text(encoding="utf-8")
    link=ADDON+"/"+NAME
    row='<tr><td><a href="'+link+'">'+NAME+'</a></td><td>XCMate '+VERSION+' Pilot – Android-Abnahme offen</td></tr>'
    if row not in html:
        marker='<tr><th>Name</th><th>Version</th></tr>'
        assert html.count(marker)==1, "PILOT_HTML_LAYOUT_CHANGED"
        html=html.replace(marker,marker+"\n"+row,1)
    PILOT_ZIP.parent.mkdir(parents=True,exist_ok=True)
    PILOT_ZIP.write_bytes(raw)
    PILOT_ZIP.with_suffix(".zip.sha256").write_text(EXPECTED_SHA+"  "+NAME+"\n",encoding="ascii")
    PILOT_INDEX.write_bytes(updated)
    PILOT_MD5.write_text(md5(updated)+"\n",encoding="ascii")
    PILOT_MANIFEST.write_text(json.dumps(meta,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    PILOT_HTML.write_text(html,encoding="utf-8")
    return verify(lambda p:(ROOT/p).read_bytes())


def verify(fetch):
    approved()
    raw,manifest=reviewed_package()
    index=fetch("online-test/addons.xml")
    assert md5(index)==fetch("online-test/addons.xml.md5").decode().strip(), "PILOT_MD5_MISMATCH"
    entries=catalog(index)
    assert entries[ADDON].get("version")==VERSION, "PILOT_INDEX_NOT_079"
    assert canonical(entries[ADDON])==canonical(ET.fromstring(manifest)), "PILOT_METADATA_MISMATCH"
    assert entries["script.gsmedia.setup"].get("version")=="0.5.26", "INSTALLER_VERSION_CHANGED"
    assert fetch("online-test/"+ADDON+"/"+NAME)==raw, "PILOT_PACKAGE_BYTES_DIFFER"
    assert fetch("online-test/"+ADDON+"/"+NAME+".sha256").decode().split()==[EXPECTED_SHA,NAME],"PILOT_SHA256_INVALID"
    meta=json.loads(fetch("online-test/manifest.json"))
    assert meta["zip_sha256"][ADDON]==EXPECTED_SHA, "PILOT_MANIFEST_SHA_MISMATCH"
    assert NAME in fetch("online-test/index.html").decode(), "PILOT_LINK_NOT_LISTED"
    assert (ROOT/"addons.xml").is_file(), "REGULAR_MAIN_ABSENT"
    reg=fetch("addons.xml")
    assert catalog(reg)[ADDON].get("version")==VERSION, "REGULAR_MAIN_VERSION_CHANGED"
    assert fetch(ADDON+"/"+NAME)==raw, "REGULAR_MAIN_ZIP_DIFFERS"
    neodark=fetch("online-test/index.html").decode()
    assert 'href="'+NAME+'"' not in neodark, "NEODARK3_WAS_UNEXPECTEDLY_ADVANCED"
    return dict(version=VERSION,pilot="RELEASED",regular="PRESERVED_079",
                neodark3="PRESERVED_078",sha256=EXPECTED_SHA,
                zip_bytes=len(raw),android="NOT_TESTED",installer="0.5.26 UNCHANGED")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--stage",action="store_true")
    parser.add_argument("--public",action="store_true")
    args=parser.parse_args()
    if args.stage:r=stage()
    elif args.public:
        def fetch(path):
            with urllib.request.urlopen(BASE+path,timeout=45) as response:
                assert response.status==200
                return response.read(32*1024*1024)
        r=verify(fetch)
    else:r=verify(lambda p:(ROOT/p).read_bytes())
    print(json.dumps(r,indent=2,sort_keys=True))
