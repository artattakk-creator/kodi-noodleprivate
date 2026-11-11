#!/usr/bin/env python3
"""Safety gate: NeoDark3's public root must carry exactly one XCMate release.

Does not touch the separate nested Kodi Pilot archive needed for older
repo-indexed versions and rollback. Keeps repository and installer ZIPs.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ONLINE=ROOT/"online-test"
DIRECT_ZIP=re.compile(r"plugin\.video\.xtreammate-(\d+\.\d+\.\d+\.\d+)\.zip$")
DIRECT_HASH=re.compile(r"plugin\.video\.xtreammate-(\d+\.\d+\.\d+\.\d+)\.zip\.sha256$")
def verify():
    root=ET.fromstring((ONLINE/"addons.xml").read_bytes())
    addons=[x for x in root.findall("addon") if x.get("id")=="plugin.video.xtreammate"]
    if len(addons)!=1:raise AssertionError("Pilot katalog XCMate entry not unique")
    version=addons[0].get("version")
    names={p.name for p in ONLINE.iterdir() if p.is_file()}
    actual_zip={DIRECT_ZIP.fullmatch(n).group(1) for n in names if DIRECT_ZIP.fullmatch(n)}
    actual_sha={DIRECT_HASH.fullmatch(n).group(1) for n in names if DIRECT_HASH.fullmatch(n)}
    if actual_zip!={version}:raise AssertionError("NeoDark3 root must have only current XCMate ZIP, found "+repr(sorted(actual_zip)))
    if actual_sha!={version}:raise AssertionError("NeoDark3 root must have only current XCMate SHA256")
    index=(ONLINE/"index.html").read_text(encoding="utf-8")
    hrefs=re.findall(r'<a\s+href="([^"]+)"',index)
    expected={
        "repository.gsmedia.pilot-1.9.12.zip",
        "script.gsmedia.setup-0.5.26.zip",
        "repository.gsmedia-1.8.1.zip",
        f"plugin.video.xtreammate-{version}.zip",
    }
    if len(hrefs)!=len(expected) or set(hrefs)!=expected:
        raise AssertionError("NeoDark3 index must list current XCMate plus the repos/installer, no old versions")
    for link in expected:
        if link not in names:raise AssertionError("Missing required linked installer/repository file: "+link)
    print("PASS NeoDark3: XCMate "+version+" only; Pilot repo, regular repo and setup installer preserved")

if __name__=="__main__":
    try:verify()
    except (AssertionError,ET.ParseError,OSError) as exc:
        print("FAIL NeoDark3 latest-only:",exc,file=sys.stderr)
        sys.exit(1)
