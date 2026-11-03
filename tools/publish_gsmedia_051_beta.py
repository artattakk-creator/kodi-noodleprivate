#!/usr/bin/env python3
"""Publish pinned GS Media 0.5.1 Kodi beta without touching production catalog.

Existing XCMate/Noodle package bytes and XML metadata are retained unchanged.
"""
from pathlib import Path
from shutil import copy2
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "online-test"
SOURCE_RUN = 41597546159
SOURCE_HEAD = "a4ed664723f247ce5566b5d786791d736c1c0a65"
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"
SAME = {
    "plugin.video.xtreammate": ("0.1.29.70", "90b90042b02d8b0e27a7b7c014d993b1dfb6f7a0dae493bf6bf80b0f4eaee07f"),
    "plugin.video.noodleprivate": ("0.4.2", "b9d0afe06d6fc956bc0191fd51f4646ae9f54c6272009e7a8819255de7460364"),
    "repository.titan.bingie.mod": ("2.0.1", "dba0a2e670e2d93158cb030ea52fe3e237bb19177e0a165d99c8f72a8492ef46"),
}
NEW = {
    "repository.gsmedia.pilot": ("1.8.4", "7cbe8a35076e4524e89c844c7ece2f2da843384ab6b90d926d5d685b3215c8e8"),
    "script.gsmedia.setup": ("0.5.1", "0dfa6d2b9f17b11a59eea35b9561eb48bbfeaafbeb66a8ca304deeead25f8942"),
    "script.skinshortcuts": ("2.1.0", "865ee5ea5bf0accee27b82539caabce1c8a9fbb8f94b2900fe5ace4f82c80b23"),
}
EXPECTED = SAME | NEW


def sha(data):
    return hashlib.sha256(data).hexdigest()


def manifest_zip(root, identity, version):
    path = root / identity / (identity + "-" + version + ".zip")
    assert path.is_file(), path
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, path
        node = ET.fromstring(z.read(identity + "/addon.xml"))
        assert node.get("id") == identity and node.get("version") == version, path
    return path


def release(src):
    assert CATALOG.is_dir()
    assert src.is_dir()
    old_idx = ET.parse(CATALOG / "addons.xml").getroot()
    old_map = {x.get("id"): x for x in old_idx.findall("addon")}
    assert old_map["repository.gsmedia.pilot"].get("version") in ("1.8.3", "1.8.4")
    assert old_map["script.gsmedia.setup"].get("version") in ("0.5.0", "0.5.1")
    new_idx = ET.parse(src / "addons.xml").getroot()
    new_map = {x.get("id"): x for x in new_idx.findall("addon")}
    assert set(new_map) == set(EXPECTED), set(new_map)
    assert (src / "addons.xml.md5").read_text().strip() == hashlib.md5(
        (src / "addons.xml").read_bytes()).hexdigest()

    # Ensure all currently published source packages are exact known bytes.
    for ident, (version, digest) in SAME.items():
        present = manifest_zip(CATALOG, ident, version)
        assert sha(present.read_bytes()) == digest, "Changed pre-existing ZIP " + ident
        assert old_map[ident].get("version") == version

    for ident, (version, digest) in NEW.items():
        packaged = manifest_zip(src, ident, version)
        assert sha(packaged.read_bytes()) == digest, "Unpinned release ZIP " + ident
    pilot_node = ET.fromstring(zipfile.ZipFile(
        src / "repository.gsmedia.pilot/repository.gsmedia.pilot-1.8.4.zip"
    ).read("repository.gsmedia.pilot/addon.xml"))
    repo = pilot_node.find("extension[@point='xbmc.addon.repository']/dir")
    assert repo.findtext("info") == BASE + "addons.xml"
    assert repo.findtext("checksum") == BASE + "addons.xml.md5"
    assert repo.findtext("datadir") == BASE

    # This is a byte-identical GPL-2.0-only package supplied by its author repo.
    shortcut = new_map["script.skinshortcuts"]
    assert shortcut.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-2.0-only"
    assert (src / "script.skinshortcuts/SOURCE.txt").is_file()

    # Copy only newly released packages: do not repackage or silently alter prior.
    for ident, (version, digest) in NEW.items():
        packaged = manifest_zip(src, ident, version)
        target = CATALOG / ident / packaged.name
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(packaged, target)
        assert sha(target.read_bytes()) == digest

    for name in ("SOURCE.txt", "icon.png", "fanart.jpg"):
        source = src / "script.skinshortcuts" / name
        if source.is_file():
            copy2(source, CATALOG / "script.skinshortcuts" / name)

    copy2(src / "repository.gsmedia.pilot-1.8.4.zip",
          CATALOG / "repository.gsmedia.pilot-1.8.4.zip")
    copy2(src / "script.gsmedia.setup/script.gsmedia.setup-0.5.1.zip",
          CATALOG / "script.gsmedia.setup-0.5.1.zip")

    # Keep the *published* XCMate and Noodle manifests; only selected
    # upgrades and shortcut package metadata may change in test index.
    target_idx = ET.Element("addons")
    for ident in ("plugin.video.xtreammate", "plugin.video.noodleprivate",
                  "repository.titan.bingie.mod", "script.skinshortcuts",
                  "script.gsmedia.setup", "repository.gsmedia.pilot"):
        target_idx.append(old_map[ident] if ident in SAME else new_map[ident])
    index_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    index_bytes += ET.tostring(target_idx, encoding="utf-8") + b'\n'
    assert len(ET.fromstring(index_bytes).findall("addon")) == 6
    (CATALOG / "addons.xml").write_bytes(index_bytes)
    (CATALOG / "addons.xml.md5").write_text(
        hashlib.md5(index_bytes).hexdigest() + "\n", encoding="ascii")

    info = {
        "channel": "GS_MEDIA_ONLINE_BETA_ONLY",
        "repository": {"id": "repository.gsmedia.pilot", "version": "1.8.4"},
        "wizard": {"id": "script.gsmedia.setup", "version": "0.5.1",
                   "status": "BETA_ANDROID_INSTALL_NOT_VERIFIED"},
        "source_run_id": SOURCE_RUN, "source_head": SOURCE_HEAD,
        "skin_shortcuts": {
            "version": "2.1.0",
            "original_source": "AchillesPunks BINGIE MOD Omega",
            "license": "GPL-2.0-only",
            "sha256": NEW["script.skinshortcuts"][1]
        },
        "limitations": [
            "Kodi official-origin add-ons may require explicit Versionen selection",
            "Full eleven-app one-click install not yet complete",
            "XCMate .70 EPG/storage/artwork bugs remain"
        ],
        "zip_sha256": {k: v[1] for k, v in EXPECTED.items()}
    }
    (CATALOG / "manifest.json").write_text(
        json.dumps(info, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CATALOG / "index.html").write_text(
        '''<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>GS Media Online Test 1.8.4</title></head><body>
<h1>GS Media Online-Test 1.8.4 / Wizard 0.5.1</h1>
<p>ENTWICKLUNGS-BETA: Skin Shortcuts 2.1.0 kompatibel mit BINGIE MOD 2.2.3.
Kein vollstaendiger elf-Apps-Installer.</p>
<p>Kodi &gt; Add-ons &gt; Aktualisierungen pruefen.</p>
<p><a href="repository.gsmedia.pilot-1.8.4.zip">Test-Repository 1.8.4 ZIP</a></p>
<p><a href="script.gsmedia.setup-0.5.1.zip">Setup 0.5.1 ZIP</a></p>
<p>Original Skin Shortcuts:
<a href="script.skinshortcuts/script.skinshortcuts-2.1.0.zip">script.skinshortcuts-2.1.0.zip</a></p>
<p>Kodi kann die offizielle Version 2.0.3 wegen Quellenbindung beibehalten.
Dann in Kodi bei Skin Shortcuts &gt; Versionen die 2.1.0 des
GS-Media-Online-Tests einmalig gezielt waehlen. Niemals Profil loeschen.</p>
<p>Rollback:
<a href="repository.gsmedia.pilot-1.8.3.zip">Repo 1.8.3</a>,
<a href="script.gsmedia.setup-0.5.0.zip">Wizard 0.5.0</a>.</p>
</body></html>''', encoding="utf-8")
    for name in ("repository.gsmedia.pilot-1.8.3.zip",
                 "repository.gsmedia.pilot-1.8.2.zip",
                 "script.gsmedia.setup-0.5.0.zip",
                 "script.gsmedia.setup-0.4.0.zip"):
        assert (CATALOG / name).is_file(), "Rollback package missing " + name
    print("ONLINE_BETA_051_READY: 6 packages, retained XCMate+Noodle, verified provenance")


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Pass exact CI artifact candidate directory"
    release(Path(sys.argv[1]))
