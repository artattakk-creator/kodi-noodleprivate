#!/usr/bin/env python3
"""Strict publication gate for GS Media isolated online-test 1.9.1 / 0.5.8.

Run only after CI assembles and validates the full 15-ID candidate index.
Copies four changed/new packages into a checkout of main/online-test. Old
binary artifacts and production addons.xml are never changed or replaced.
"""
from pathlib import Path
from shutil import copy2
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

REPO = "repository.gsmedia.pilot"
WIZARD = "script.gsmedia.setup"
MP3 = "plugin.audio.m3sr2019"
EZ = "script.ezmaintenanceplus"
UPDATES = {REPO: "1.9.1", WIZARD: "0.5.8", MP3: "2026.1.0", EZ: "2026.04.05.0"}
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def addon_zip(root, identity, version):
    p = root / identity / (identity + "-" + version + ".zip")
    assert p.is_file(), "Missing package " + str(p)
    with zipfile.ZipFile(p) as archive:
        assert archive.testzip() is None, p
        x = ET.fromstring(archive.read(identity + "/addon.xml"))
        assert x.get("id") == identity and x.get("version") == version, p
    return p, x


def release(src, dest):
    src, dest = Path(src), Path(dest)
    assert (src / "addons.xml").is_file() and (dest / "addons.xml").is_file()
    old = ET.parse(dest / "addons.xml").getroot()
    new = ET.parse(src / "addons.xml").getroot()
    old_map = {a.get("id"): a for a in old.findall("addon")}
    new_map = {a.get("id"): a for a in new.findall("addon")}
    assert len(old_map) == 13 and len(new_map) == 15
    assert set(new_map) == set(old_map) | {MP3, EZ}
    assert old_map[REPO].get("version") == "1.9.0"
    assert old_map[WIZARD].get("version") == "0.5.7"
    assert (src / "addons.xml.md5").read_text().strip() == hashlib.md5((src / "addons.xml").read_bytes()).hexdigest()
    old_info = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert old_info["repository"]["version"] == "1.9.0"
    assert old_info["wizard"]["version"] == "0.5.7"

    # Binary and index-preservation proof for the previous eleven packages.
    old_hashes = old_info["zip_sha256"]
    for ident in sorted(set(old_map) - set(UPDATES)):
        version = old_map[ident].get("version")
        assert new_map[ident].get("version") == version
        old_package, _ = addon_zip(dest, ident, version)
        new_package, _ = addon_zip(src, ident, version)
        assert digest(old_package.read_bytes()) == old_hashes[ident], ident
        if digest(new_package.read_bytes()) != old_hashes[ident]:
            # Candidate source can contain older same-version builds (e.g. Noodle).
            # Do not publish them: use the existing verified main ZIP and XML.
            print("UNCHANGED_MAIN_PACKAGE_RETAINED", ident, old_hashes[ident])

    # Check important security contracts *before* any release copy.
    mp3 = new_map[MP3]
    ez = new_map[EZ]
    assert mp3.get("version") == UPDATES[MP3]
    assert ez.get("version") == UPDATES[EZ]
    assert mp3.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-3.0"
    assert ez.findtext("./extension[@point='xbmc.addon.metadata']/license") == "The MIT License"
    assert {x.get("addon") for x in mp3.findall("./requires/import")} >= {
        "xbmc.python", "script.module.requests", "script.module.routing", "script.module.beautifulsoup4"}
    assert "script.module.requests" in {x.get("addon") for x in ez.findall("./requires/import")}
    for identity in (MP3, EZ):
        note = (src / identity / "SOURCE.txt").read_text(encoding="utf-8")
        assert len(note) > 120 and ("Git" in note or "Drive" in note), identity

    repo_zip, pilot = addon_zip(src, REPO, UPDATES[REPO])
    dr = pilot.find("./extension[@point='xbmc.addon.repository']/dir")
    assert dr is not None
    assert dr.findtext("info") == BASE + "addons.xml"
    assert dr.findtext("checksum") == BASE + "addons.xml.md5"
    assert dr.findtext("datadir") == BASE

    packages = {}
    for identity, version in UPDATES.items():
        package, _ = addon_zip(src, identity, version)
        packages[identity] = package
    for identity, p in packages.items():
        target = dest / identity / p.name
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(p, target)
        assert digest(target.read_bytes()) == digest(p.read_bytes())
    for identity in (MP3, EZ):
        for name in ("SOURCE.txt", "icon.png", "fanart.jpg"):
            f = src / identity / name
            if f.is_file():
                copy2(f, dest / identity / name)

    copy2(repo_zip, dest / repo_zip.name)
    copy2(packages[WIZARD], dest / packages[WIZARD].name)
    # Order and metadata for every old unchanged package are retained.
    target = ET.Element("addons")
    for entry in old.findall("addon"):
        identity = entry.get("id")
        target.append(new_map[identity] if identity in UPDATES else entry)
    target.append(new_map[MP3])
    target.append(new_map[EZ])
    contents = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    contents += ET.tostring(target, encoding="utf-8") + b"\n"
    assert len(ET.fromstring(contents).findall("addon")) == 15
    (dest / "addons.xml").write_bytes(contents)
    (dest / "addons.xml.md5").write_text(hashlib.md5(contents).hexdigest() + "\n", encoding="ascii")

    old_info["repository"]["version"] = UPDATES[REPO]
    old_info["wizard"]["version"] = UPDATES[WIZARD]
    old_info["wizard"]["status"] = "BETA_MP3_ECHOED_EZMAINTENANCE_ANDROID_NOT_VERIFIED"
    old_info["wizard"]["source_gate"] = "Drive source plus pinned upstream images and original MIT source"
    old_info["mp3_echoed"] = {
        "id": MP3, "version": UPDATES[MP3],
        "source": "owner-authorised Drive source with L2501 pinned legacy media",
        "license_notice": "addon.xml GPL-3.0; bundled LICENSE GPL-v2 inherited discrepancy",
        "android_test": "NOT_TESTED", "sha256": digest(packages[MP3].read_bytes())
    }
    old_info["ezmaintenanceplus"] = {
        "id": EZ, "version": UPDATES[EZ],
        "upstream_commit": "0e8a5bf26917f25ec79a67de1a896d440708c8e3",
        "license": "MIT", "android_test": "NOT_TESTED",
        "sha256": digest(packages[EZ].read_bytes())
    }
    old_info["zip_sha256"].update({
        ident: digest(p.read_bytes()) for ident, p in packages.items()})
    (dest / "manifest.json").write_text(json.dumps(old_info, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (dest / "index.html").write_text(
        '<!doctype html><html lang="de"><meta charset="utf-8">'
        '<title>GS Media Online-Test 1.9.1</title>'
        '<h1>GS Media Online-Test 1.9.1 / Wizard 0.5.8</h1>'
        '<p>Nur fuer Kodi 21.3 Testgeraet Box B. Kein produktiver Release. '
        'Fortsetzen mit vorhandenem Installationsjournal; nicht zuruecksetzen.</p>'
        '<p>Originalquellen MP3 Streams Echoed 2026.1.0 und '
        'EZ Maintenance+ 2026.04.05.0 mit Git-Hashpruefung.</p>'
        '<p><a href="repository.gsmedia.pilot-1.9.1.zip">Repository 1.9.1</a></p>'
        '<p><a href="script.gsmedia.setup-0.5.8.zip">Wizard 0.5.8</a></p>'
        '<p>Android 43/43 und BINGIE/Player/EPG-Endabnahme noch offen.</p></html>\n',
        encoding="utf-8")
    assert (dest / "repository.gsmedia.pilot-1.9.0.zip").is_file(), "Rollback repo must remain"
    assert (dest / "script.gsmedia.setup-0.5.7.zip").is_file(), "Rollback wizard must remain"
    print("READY_GSMEDIA_058:", len(ET.fromstring(contents).findall("addon")), "verified index packages")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Pass candidate directory and existing main/online-test target"
    release(sys.argv[1], sys.argv[2])
