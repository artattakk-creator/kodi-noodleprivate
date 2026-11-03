#!/usr/bin/env python3
"""Build a test-only GS Media 1.8.3 pilot catalog with Apache BINGIE bootstrap.

Never publishes to main. The original BINGIE ZIP is retained byte-for-byte.
"""
from pathlib import Path
import hashlib
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/bingie-repository/repository.titan.bingie.mod-2.0.1.zip"
ORIGINAL_GIT_BLOB = "da6e2b22b9bdb3baaf12da362fcbadb0b17628e6"
TEST_URL = ("https://raw.githubusercontent.com/artattakk-creator/"
            "kodi-noodleprivate/main/online-test/")
PILOT_ID = "repository.gsmedia.pilot"
PILOT_VERSION = "1.8.3"


def _bytes_in_zip(data, prefix):
    with zipfile.ZipFile(data) as archive:
        assert archive.testzip() is None
        return ET.fromstring(archive.read(prefix + "/addon.xml"))


def build(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    vendor = VENDOR.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(vendor)).encode("ascii")
                            + b"\0" + vendor).hexdigest()
    assert git_blob == ORIGINAL_GIT_BLOB, "Upstream BINGIE package changed"
    original = _bytes_in_zip(VENDOR, "repository.titan.bingie.mod")
    assert original.get("id") == "repository.titan.bingie.mod"
    assert original.get("version") == "2.0.1"
    assert (ROOT / "vendor/bingie-repository/LICENSE").is_file()

    all_addons = []
    for addon_id, version, package in [
        ("plugin.video.xtreammate", "0.1.29.70",
         ROOT / "plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.70.zip"),
        ("plugin.video.noodleprivate", "0.4.2",
         ROOT / "plugin.video.noodleprivate/plugin.video.noodleprivate-0.4.2.zip"),
        ("script.gsmedia.setup", "0.5.0",
         ROOT / ".build/gsmedia-050/script.gsmedia.setup-0.5.0.zip"),
        ("repository.titan.bingie.mod", "2.0.1", VENDOR),
    ]:
        root = _bytes_in_zip(package, addon_id)
        assert root.get("id") == addon_id and root.get("version") == version
        all_addons.append(root)
        target = destination / addon_id / (addon_id + "-" + version + ".zip")
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(package, target)
        if addon_id == "repository.titan.bingie.mod":
            # Preserve upstream attribution with the bootstrap.
            shutil.copyfile(ROOT/"vendor/bingie-repository/LICENSE",
                            destination/addon_id/"LICENSE")
            shutil.copyfile(ROOT/"vendor/bingie-repository/SOURCE.txt",
                            destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    source = addon_id + "/" + name
                    if source in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(source))
    # Repository metadata is derived from own repo, but pilot has distinct ID.
    repo_source = ROOT / "src/repository.gsmedia/addon.xml"
    pilot = ET.parse(repo_source).getroot()
    pilot.set("id", PILOT_ID)
    pilot.set("version", PILOT_VERSION)
    pilot.set("name", "GS Media Online-Test 1.8.3")
    dir_ = pilot.find("extension[@point='xbmc.addon.repository']/dir")
    assert dir_ is not None
    dir_.find("info").text = TEST_URL + "addons.xml"
    dir_.find("checksum").text = TEST_URL + "addons.xml.md5"
    dir_.find("datadir").text = TEST_URL
    for node in pilot.findall("extension[@point='xbmc.addon.metadata']/summary"):
        node.text = "GS Media Online-Test 1.8.3, nicht produktiv"
    for node in pilot.findall("extension[@point='xbmc.addon.metadata']/description"):
        node.text = "Entwicklungs-Installer mit geprüfter BINGIE-Repository-Vorstufe; keine vollständige Geräteabnahme."
    pilot_xml = ET.tostring(pilot, encoding="utf-8", xml_declaration=True)
    pack = destination/PILOT_ID/(PILOT_ID+"-"+PILOT_VERSION+".zip")
    pack.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(pack, "w", compression=zipfile.ZIP_DEFLATED) as out:
        out.writestr(PILOT_ID+"/addon.xml",pilot_xml)
        for asset in ("icon-1.8.png","fanart.png"):
            p = ROOT/"src/repository.gsmedia"/asset
            if p.exists():
                out.write(p, PILOT_ID+"/"+asset)
    assert _bytes_in_zip(pack, PILOT_ID).get("id") == PILOT_ID
    shutil.copyfile(pack, destination / pack.name)
    all_addons.append(pilot)
    idx = ET.Element("addons")
    for entry in all_addons:
        idx.append(entry)
    xml = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(idx, encoding="utf-8") + b'\n'
    ET.fromstring(xml)
    (destination/"addons.xml").write_bytes(xml)
    (destination/"addons.xml.md5").write_text(
        hashlib.md5(xml).hexdigest()+"\n", encoding="ascii")
    print("VENDOR_BINGIE_SHA256", hashlib.sha256(vendor).hexdigest())
    print("TEST_ONLY", destination, "CATALOG", len(all_addons))
    print("NO_PUBLICATION_NO_ANDROID_PASS")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv)>1 else ROOT/".build/gsmedia-050-pilot")
