#!/usr/bin/env python3
"""Guard the direct NeoDark3 latest-only ZIP independently of nested Pilot updates.

The pilot catalog may advance before the standalone NeoDark3 download *only*
when the exact version has an explicit, cryptographically pinned pilot-only
authorization. This does not authorize automatic regular/NeoDark3 release.
"""
from pathlib import Path
import re
import json
import hashlib
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ONLINE=ROOT/"online-test"
DIRECT_ZIP=re.compile(r"plugin\.video\.xtreammate-(\d+\.\d+\.\d+\.\d+)\.zip$")
DIRECT_HASH=re.compile(r"plugin\.video\.xtreammate-(\d+\.\d+\.\d+\.\d+)\.zip\.sha256$")

def verify():
    raw=(ONLINE/"addons.xml").read_bytes()
    md5=hashlib.md5(raw).hexdigest()
    if (ONLINE/"addons.xml.md5").read_text(encoding="ascii").strip()!=md5:
        raise AssertionError("Pilot addons.xml.md5 does not match catalog")
    catalog=ET.fromstring(raw)
    addons=[x for x in catalog.findall("addon") if x.get("id")=="plugin.video.xtreammate"]
    if len(addons)!=1:raise AssertionError("Pilot catalog XCMate entry not unique")
    pilot_version=addons[0].get("version")
    names={p.name for p in ONLINE.iterdir() if p.is_file()}
    actual_zip={DIRECT_ZIP.fullmatch(n).group(1) for n in names if DIRECT_ZIP.fullmatch(n)}
    actual_sha={DIRECT_HASH.fullmatch(n).group(1) for n in names if DIRECT_HASH.fullmatch(n)}
    if len(actual_zip)!=1 or actual_zip!=actual_sha:
        raise AssertionError("NeoDark3 direct root must have exactly one matching ZIP and SHA256")
    direct_version=next(iter(actual_zip))
    index=(ONLINE/"index.html").read_text(encoding="utf-8")
    hrefs=re.findall(r'<a\s+href="([^"]+)"',index)
    expected={
        "repository.gsmedia.pilot-1.9.12.zip",
        "script.gsmedia.setup-0.5.26.zip",
        "repository.gsmedia-1.8.1.zip",
        f"plugin.video.xtreammate-{direct_version}.zip",
    }
    if len(hrefs)!=len(expected) or set(hrefs)!=expected:
        raise AssertionError("NeoDark3 index must list one direct XCMate version and unchanged repos/installer")
    for link in expected:
        if link not in names:raise AssertionError("Missing NeoDark3 linked package: "+link)
    if pilot_version!=direct_version:
        if tuple(map(int,pilot_version.split(".")))<=tuple(map(int,direct_version.split("."))):
            raise AssertionError("Pilot version behind direct NeoDark3 without explicit release policy")
        approved=ROOT/"docs"/"XCMate"/"releases"/("user-approved-pilot-only-"+pilot_version+".json")
        try:record=json.loads(approved.read_text(encoding="utf-8"))
        except (OSError,ValueError) as e:raise AssertionError("Pilot-only release authorization missing") from e
        if not (record.get("version")==pilot_version
                and record.get("addon_id")=="plugin.video.xtreammate"
                and record.get("user_approved_pilot_release") is True
                and record.get("user_approved_regular_release") is False
                and record.get("user_approved_neodark3_direct_release") is False
                and record.get("regular_catalog_unchanged") is True
                and record.get("neodark3_direct_unchanged") is True
                and record.get("android_status")=="NOT_TESTED"):
            raise AssertionError("Insufficient pilot-only user authorization")
        filename=f"plugin.video.xtreammate-{pilot_version}.zip"
        nested=ONLINE/"plugin.video.xtreammate"/filename
        sha=nested.with_name(filename+".sha256")
        if not nested.is_file() or not sha.is_file():
            raise AssertionError("Pilot ZIP or SHA256 missing")
        digest=hashlib.sha256(nested.read_bytes()).hexdigest()
        if digest!=record.get("zip_sha256"):
            raise AssertionError("Pilot ZIP differs from user-approved SHA256")
        if sha.read_text(encoding="ascii").strip()!=digest+"  "+filename:
            raise AssertionError("Pilot ZIP checksum sidecar is invalid")
        manifest=json.loads((ONLINE/"manifest.json").read_text(encoding="utf-8"))
        if manifest["zip_sha256"]["plugin.video.xtreammate"]!=digest:
            raise AssertionError("Pilot manifest checksum differs")
        if manifest.get("xcmate92",{}).get("channels")!=["pilot"]:
            raise AssertionError("Pilot manifest release scope not isolated")
    print("PASS NeoDark3 direct latest-only:",direct_version,"| Pilot:",pilot_version,
          "| single direct ZIP, protected split and installer preserved")

if __name__=="__main__":
    try:verify()
    except (AssertionError,ET.ParseError,OSError,KeyError,TypeError) as exc:
        print("FAIL NeoDark3/Pilot release scope:",exc,file=sys.stderr)
        sys.exit(1)
