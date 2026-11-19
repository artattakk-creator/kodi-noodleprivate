#!/usr/bin/env python3
"""NeoDark3 exactly-one-XCMate ZIP and Pilot catalog/sidecar release contract."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ONLINE = ROOT / "online-test"
NAME = "plugin.video.xtreammate-0.1.29.100.zip"
SHA = "9fbea224f9417193b85f8b57a390653eb4d77aeff85196973f3520d51acb26de"
SINGLE = re.compile(r"plugin\.video\.xtreammate-\d+\.\d+\.\d+\.\d+\.zip$")

def verify():
    raw = (ONLINE / "addons.xml").read_bytes()
    assert hashlib.md5(raw).hexdigest() == (ONLINE / "addons.xml.md5").read_text().strip(), "CATALOG_MD5"
    root = ET.fromstring(raw)
    addons = [x for x in root.findall("addon") if x.get("id") == "plugin.video.xtreammate"]
    assert len(addons) == 1 and addons[0].get("version") == "0.1.29.100", "PILOT_VERSION"
    installer = [x for x in root.findall("addon") if x.get("id") == "script.gsmedia.setup"]
    assert len(installer) == 1 and installer[0].get("version") == "0.5.27", "INSTALLER_CATALOG_NOT_CHANGED"
    direct = [p.name for p in ONLINE.iterdir() if p.is_file() and SINGLE.fullmatch(p.name)]
    assert direct == [NAME], "NEODARK3_LATEST_ONLY"
    for folder in (ONLINE, ONLINE / "plugin.video.xtreammate"):
        data = (folder / NAME).read_bytes()
        assert len(data) == 6055446 and hashlib.sha256(data).hexdigest() == SHA, "ZIP_SHA256"
        assert (folder / (NAME + ".sha256")).read_text().strip() == SHA + "  " + NAME, "CHECKSUM_FILE"
    manifest = json.loads((ONLINE / "manifest.json").read_text())
    entry = manifest.get("xcmate100", {})
    assert entry.get("channels") == ["pilot", "neodark3"] and entry.get("sha256") == SHA, "MANIFEST_RECORD"
    assert manifest["zip_sha256"]["plugin.video.xtreammate"] == SHA, "MANIFEST_CURRENT_SHA"
    index = (ONLINE / "index.html").read_text(encoding="utf-8")
    links = re.findall(r'<a\s+href="([^"]+)"', index)
    required = [
        NAME, NAME + ".sha256", "repository.gsmedia.pilot-1.9.12.zip",
        "repository.gsmedia-1.8.1.zip", "script.gsmedia.setup-0.5.26.zip",
        "script.gsmedia.setup-0.5.27.zip", "script.gsmedia.setup-0.5.27.zip.sha256",
        "script.gsmedia.setup-0.5.28.zip", "script.gsmedia.setup-0.5.28.zip.sha256",
    ]
    assert set(links) == set(required) and len(links) == len(required), "NEODARK3_LINKS"
    assert all((ONLINE / link).exists() for link in required), "NEODARK3_LINK_TARGETS"
    assert "0.1.29.100" in index and "PRIVATE_PENDING" in index, "USER_NOTICE"
    assert entry.get("user_approved_regular_release") is False, "RELEASE_SCOPE"
    regular = ET.fromstring((ROOT / "addons.xml").read_bytes())
    assert not any(x.get("version") == "0.1.29.100" for x in regular.findall("addon") if x.get("id") == "plugin.video.xtreammate"), "REGULAR_UNCHANGED"
    print("PASS XCMate .100 Pilot and NeoDark3 | 6055446 bytes | SHA256 " + SHA)

if __name__ == "__main__":
    try:
        verify()
    except (AssertionError, KeyError, ValueError, OSError, ET.ParseError) as exc:
        print("FAIL NeoDark3 release: " + str(exc), file=sys.stderr)
        sys.exit(1)
