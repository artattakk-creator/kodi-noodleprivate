#!/usr/bin/env python3
"""Build a test-only GS Media 1.8.7 pilot catalog with Apache BINGIE bootstrap.

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
SHORTCUTS_VENDOR = ROOT / "vendor/bingie-skinshortcuts-210/script.skinshortcuts-2.1.0.zip"
JURIAL_VENDOR = ROOT / "vendor/jurialmunkey-common-0235/script.module.jurialmunkey-0.2.35.zip"
JURIAL_BLOB_SHA1 = "98556ddadf9ea88db9809728663ddc08fe9a0990"
SHORTCUTS_BLOB_SHA1 = "abb2627aef68e15c40e4a33144b1d4cc7bf4d3e6"
SHORTCUTS_MD5 = "69d497c8884da6b169b6f9727d29910f"
SHORTCUTS_SHA256 = "865ee5ea5bf0accee27b82539caabce1c8a9fbb8f94b2900fe5ace4f82c80b23"
ORIGINAL_GIT_BLOB = "da6e2b22b9bdb3baaf12da362fcbadb0b17628e6"
ORIGINAL_SHA256 = "dba0a2e670e2d93158cb030ea52fe3e237bb19177e0a165d99c8f72a8492ef46"
TEST_URL = ("https://raw.githubusercontent.com/artattakk-creator/"
            "kodi-noodleprivate/main/online-test/")
PILOT_ID = "repository.gsmedia.pilot"
PILOT_VERSION = "1.8.7"


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
    assert hashlib.sha256(vendor).hexdigest() == ORIGINAL_SHA256, "BINGIE SHA256 mismatch"
    original = _bytes_in_zip(VENDOR, "repository.titan.bingie.mod")
    assert original.get("id") == "repository.titan.bingie.mod"
    assert original.get("version") == "2.0.1"
    assert (ROOT / "vendor/bingie-repository/LICENSE").is_file()

    shortcuts_bytes = SHORTCUTS_VENDOR.read_bytes()
    assert hashlib.md5(shortcuts_bytes).hexdigest() == SHORTCUTS_MD5, "Skin Shortcuts upstream MD5"
    assert hashlib.sha256(shortcuts_bytes).hexdigest() == SHORTCUTS_SHA256, "Skin Shortcuts original SHA256"
    actual_blob = hashlib.sha1(
        b"blob " + str(len(shortcuts_bytes)).encode("ascii") + b"\0" + shortcuts_bytes
    ).hexdigest()
    assert actual_blob == SHORTCUTS_BLOB_SHA1, "Skin Shortcuts original Git blob changed"
    shortcuts_xml = _bytes_in_zip(SHORTCUTS_VENDOR, "script.skinshortcuts")
    assert shortcuts_xml.get("id") == "script.skinshortcuts"
    assert shortcuts_xml.get("version") == "2.1.0"
    assert shortcuts_xml.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-2.0-only"
    assert (ROOT / "vendor/bingie-skinshortcuts-210/SOURCE.txt").is_file()

    # Build a tiny native Kodi addon whose required dependency forces Kodi's
    # official dependency resolver to choose a >=2.1.0 Skin Shortcuts package
    # from this same GS Media test repository (not InstallAddon of installed id).
    bridge_dir = ROOT / "tools/gsmedia_053_shortcuts_bridge"
    bridge_version = "0.1.0"
    bridge_id = "script.gsmedia.skinshortcuts.bridge"
    bridge_target = destination / bridge_id / (
        bridge_id + "-" + bridge_version + ".zip")
    bridge_target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bridge_target, "w", compression=zipfile.ZIP_DEFLATED) as out:
        out.write(bridge_dir / "addon.xml", bridge_id + "/addon.xml")
        out.write(bridge_dir / "default.py", bridge_id + "/default.py")
        out.write(bridge_dir / "README.md", bridge_id + "/README.md")
    bridge_xml = _bytes_in_zip(bridge_target, bridge_id)
    assert bridge_xml.get("id") == bridge_id and bridge_xml.get("version") == bridge_version
    imports = bridge_xml.findall("./requires/import")
    assert ("script.skinshortcuts", "2.1.0") in [
        (x.get("addon"), x.get("version")) for x in imports]
    assert bridge_xml.findtext("./extension[@point='xbmc.addon.metadata']/license") == "MIT"
    (destination / bridge_id / "SOURCE.txt").write_text(
        "First-party GS Media Kodi-native dependency bridge. Source: " +
        "https://github.com/artattakk-creator/kodi-noodleprivate/" +
        "tree/fix/gsmedia-wizard-053-native-shortcuts-dependency-20261103/" +
        "tools/gsmedia_053_shortcuts_bridge\n",
        encoding="utf-8")

    jurial_bytes = JURIAL_VENDOR.read_bytes()
    git_blob = hashlib.sha1(
        b"blob " + str(len(jurial_bytes)).encode("ascii") + b"\0" + jurial_bytes
    ).hexdigest()
    assert git_blob == JURIAL_BLOB_SHA1, "Jurialmunkey upstream Git blob changed"
    original_jurial = _bytes_in_zip(JURIAL_VENDOR, "script.module.jurialmunkey")
    assert original_jurial.get("id") == "script.module.jurialmunkey"
    assert original_jurial.get("version") == "0.2.35"
    assert original_jurial.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-3.0-or-later"
    assert (ROOT / "vendor/jurialmunkey-common-0235/SOURCE.txt").is_file()

    all_addons = [bridge_xml]
    for addon_id, version, package in [
        ("plugin.video.xtreammate", "0.1.29.70",
         ROOT / "plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.70.zip"),
        ("plugin.video.noodleprivate", "0.4.2",
         ROOT / "plugin.video.noodleprivate/plugin.video.noodleprivate-0.4.2.zip"),
        ("script.gsmedia.setup", "0.5.4",
         ROOT / ".build/gsmedia-054/script.gsmedia.setup-0.5.4.zip"),
        ("repository.titan.bingie.mod", "2.0.1", VENDOR),
        ("script.skinshortcuts", "2.1.0", SHORTCUTS_VENDOR),
        ("script.module.jurialmunkey", "0.2.35", JURIAL_VENDOR),
    ]:
        root = _bytes_in_zip(package, addon_id)
        assert root.get("id") == addon_id and root.get("version") == version
        all_addons.append(root)
        target = destination / addon_id / (addon_id + "-" + version + ".zip")
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(package, target)
        if addon_id == "script.module.jurialmunkey":
            shutil.copyfile(ROOT/"vendor/jurialmunkey-common-0235/SOURCE.txt",
                            destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    source = addon_id + "/" + name
                    if source in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(source))
        if addon_id == "script.skinshortcuts":
            shutil.copyfile(ROOT/"vendor/bingie-skinshortcuts-210/SOURCE.txt",
                            destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    source = addon_id + "/" + name
                    if source in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(source))
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
    pilot.set("name", "GS Media Online-Test 1.8.7")
    dir_ = pilot.find("extension[@point='xbmc.addon.repository']/dir")
    assert dir_ is not None
    dir_.find("info").text = TEST_URL + "addons.xml"
    dir_.find("checksum").text = TEST_URL + "addons.xml.md5"
    dir_.find("datadir").text = TEST_URL
    for node in pilot.findall("extension[@point='xbmc.addon.metadata']/summary"):
        node.text = "GS Media Online-Test 1.8.7, nicht produktiv"
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
    print("VENDOR_SHORTCUTS_SHA256", hashlib.sha256(shortcuts_bytes).hexdigest())
    print("VENDOR_JURIAL_SHA256", hashlib.sha256(jurial_bytes).hexdigest())
    print("TEST_ONLY", destination, "CATALOG", len(all_addons))
    print("NO_PUBLICATION_NO_ANDROID_PASS")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv)>1 else ROOT/".build/gsmedia-054-pilot")
