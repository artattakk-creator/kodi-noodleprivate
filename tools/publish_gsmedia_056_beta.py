#!/usr/bin/env python3
"""Publish pinned GS Media 0.5.6 Kodi beta without touching production catalog.

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
SOURCE_RUN = 41608807153
SOURCE_HEAD = "1b24019976d179c3c9319726bdb56021fb69e343"
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"
SAME = {
    "plugin.video.xtreammate": ("0.1.29.70", "90b90042b02d8b0e27a7b7c014d993b1dfb6f7a0dae493bf6bf80b0f4eaee07f"),
    "plugin.video.noodleprivate": ("0.4.2", "b9d0afe06d6fc956bc0191fd51f4646ae9f54c6272009e7a8819255de7460364"),
    "repository.titan.bingie.mod": ("2.0.1", "dba0a2e670e2d93158cb030ea52fe3e237bb19177e0a165d99c8f72a8492ef46"),
    "script.skinshortcuts": ("2.1.0", "865ee5ea5bf0accee27b82539caabce1c8a9fbb8f94b2900fe5ace4f82c80b23"),
    "script.gsmedia.skinshortcuts.bridge": ("0.1.0", "f84da5931a4159bbf82b78ecf6a05c0b2ce8a6e0c08ebf109d1554eb84d4f72c"),
    "script.module.jurialmunkey": ("0.2.35", "80302314cdbc5a75611b0c2866eb1c7b4e93ccadaf20208ef7eb79b79c1fb749"),
    "script.module.resolveurl": ("5.1.212", "28fb6b2340eccfb1337ba4421b6429aa1c8f2978834853d1229b42b2a947bc59"),
    "script.module.resolveurl.xxx": ("2.1.44", "d8bceeae5d492cfa111843cdf71f8681f0c9050fbc0fdd2952f77afe49ea30d5"),
    "plugin.video.cumination": ("1.1.206", "539073d804d6381105698eff054ea77ae1359b658e0f226c3807a7365a0d674c"),
}
NEW = {
    "repository.gsmedia.pilot": ("1.8.9", "b364fe7f996078c3794c7e6e3dfd69cffc9afa5a017d484ac34375722e03a949"),
    "script.gsmedia.setup": ("0.5.6", "27eb48845f2fab4940be271256d6b8f9e4ab7f0f7454c9e47bae732a6a2d2de5"),
    "repository.xvault": ("1.0.3", "df6fd9f40c12c9e0f13f7cb04589286307550cd43376c734eb127aa4e1de27ab"),
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
    assert old_map["repository.gsmedia.pilot"].get("version") in ("1.8.8", "1.8.9")
    assert old_map["script.gsmedia.setup"].get("version") in ("0.5.5", "0.5.6")
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
        src / "repository.gsmedia.pilot/repository.gsmedia.pilot-1.8.9.zip"
    ).read("repository.gsmedia.pilot/addon.xml"))
    repo = pilot_node.find("extension[@point='xbmc.addon.repository']/dir")
    assert repo.findtext("info") == BASE + "addons.xml"
    assert repo.findtext("checksum") == BASE + "addons.xml.md5"
    assert repo.findtext("datadir") == BASE

    # This is a byte-identical GPL-2.0-only package supplied by its author repo.
    shortcut = new_map["script.skinshortcuts"]
    assert shortcut.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-2.0-only"
    assert (src / "script.skinshortcuts/SOURCE.txt").is_file()

    bridge = new_map["script.gsmedia.skinshortcuts.bridge"]
    assert bridge.findtext("./extension[@point='xbmc.addon.metadata']/license") == "MIT"
    assert ("script.skinshortcuts", "2.1.0") in [
        (x.get("addon"), x.get("version"))
        for x in bridge.findall("./requires/import")]
    assert (src / "script.gsmedia.skinshortcuts.bridge/SOURCE.txt").is_file()

    jurial = new_map["script.module.jurialmunkey"]
    assert jurial.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL-3.0-or-later"
    assert jurial.get("version") == "0.2.35"
    assert (CATALOG / "script.module.jurialmunkey/SOURCE.txt").is_file()
    for ident in ("script.module.resolveurl", "script.module.resolveurl.xxx", "plugin.video.cumination"):
        assert (src / ident / "SOURCE.txt").is_file(), "Missing original maintainer provenance: " + ident
    assert new_map["plugin.video.cumination"].findtext(
        "./extension[@point='xbmc.addon.metadata']/license") == "GPL 2.0"
    assert new_map["script.module.resolveurl"].get("version") == "5.1.212"
    assert new_map["script.module.resolveurl.xxx"].get("version") == "2.1.44"

    # xVAULT's own feed and original repository remain the authoritative
    # source: only its small GPLv3 repository bootstrap is mirrored in pilot.
    official = new_map["repository.xvault"]
    official_dir = official.find("./extension[@point='xbmc.addon.repository']/dir")
    assert official.get("version") == "1.0.3"
    assert official_dir is not None
    assert official_dir.findtext("info") == "https://xvault.repowork.de/addons.xml"
    assert official_dir.findtext("checksum") == "https://xvault.repowork.de/addons.xml.md5"
    assert official_dir.findtext("datadir") == "https://xvault.repowork.de/"
    assert "plugin.video.xvault" not in new_map
    assert (src / "repository.xvault/SOURCE.txt").is_file()

    # Copy only newly released packages: do not repackage or silently alter prior.
    for ident, (version, digest) in NEW.items():
        packaged = manifest_zip(src, ident, version)
        target = CATALOG / ident / packaged.name
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(packaged, target)
        assert sha(target.read_bytes()) == digest

    for name in ("SOURCE.txt", "icon.png", "fanart.jpg"):
        source = src / "repository.xvault" / name
        if source.is_file():
            copy2(source, CATALOG / "repository.xvault" / name)

    copy2(src / "repository.gsmedia.pilot-1.8.9.zip",
          CATALOG / "repository.gsmedia.pilot-1.8.9.zip")
    copy2(src / "script.gsmedia.setup/script.gsmedia.setup-0.5.6.zip",
          CATALOG / "script.gsmedia.setup-0.5.6.zip")

    # Keep the *published* XCMate and Noodle manifests; only selected
    # upgrades and shortcut package metadata may change in test index.
    target_idx = ET.Element("addons")
    for ident in ("plugin.video.xtreammate", "plugin.video.noodleprivate",
                  "repository.titan.bingie.mod", "script.skinshortcuts",
                  "script.gsmedia.skinshortcuts.bridge", "script.module.jurialmunkey",
                  "script.module.resolveurl", "script.module.resolveurl.xxx",
                  "plugin.video.cumination", "repository.xvault",
                  "script.gsmedia.setup", "repository.gsmedia.pilot"):
        target_idx.append(old_map[ident] if ident in SAME else new_map[ident])
    index_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    index_bytes += ET.tostring(target_idx, encoding="utf-8") + b'\n'
    assert len(ET.fromstring(index_bytes).findall("addon")) == 12
    (CATALOG / "addons.xml").write_bytes(index_bytes)
    (CATALOG / "addons.xml.md5").write_text(
        hashlib.md5(index_bytes).hexdigest() + "\n", encoding="ascii")

    info = {
        "channel": "GS_MEDIA_ONLINE_BETA_ONLY",
        "repository": {"id": "repository.gsmedia.pilot", "version": "1.8.9"},
        "wizard": {"id": "script.gsmedia.setup", "version": "0.5.6",
                   "status": "BETA_XVAULT_OFFICIAL_REPO_ANDROID_NOT_VERIFIED"},
        "source_run_id": SOURCE_RUN, "source_head": SOURCE_HEAD,
        "skin_shortcuts": {
            "version": "2.1.0",
            "original_source": "AchillesPunks BINGIE MOD Omega",
            "license": "GPL-2.0-only",
            "sha256": SAME["script.skinshortcuts"][1]
        },
        "native_upgrade": {"bridge_addon": "script.gsmedia.skinshortcuts.bridge",
                           "minimum_skinshortcuts": "2.1.0",
                           "uses_kodi_dependency_manager": True,
                           "requires_temporary_user_consented_origin_setting": True},
        "jurialmunkey": {"id": "script.module.jurialmunkey", "version": "0.2.35", "license": "GPL-3.0-or-later", "sha256": SAME["script.module.jurialmunkey"][1], "source": "jurialmunkey/repository.jurialmunkey"},
        "original_resolver_batch": {
            "script.module.resolveurl": "5.1.212",
            "script.module.resolveurl.xxx": "2.1.44",
            "plugin.video.cumination": "1.1.206",
            "android_test": "NOT_TESTED"
        },
        "xvault": {
            "repo_id": "repository.xvault", "version": "1.0.3",
            "original_source": "mojomedia1812/xVAULT",
            "authoritative_plugin_feed": "https://xvault.repowork.de/addons.xml",
            "sha256": NEW["repository.xvault"][1],
            "android_test": "NOT_TESTED",
            "plugin_zip_mirrored": False
        },
        "limitations": [
            "Original xVAULT repository bootstrap and Kodi installed plugin NOT_TESTED on Android",
            "Full eleven-app one-click install not yet complete",
            "XCMate .70 EPG/storage/artwork bugs remain"
        ],
        "zip_sha256": {k: v[1] for k, v in EXPECTED.items()}
    }
    (CATALOG / "manifest.json").write_text(
        json.dumps(info, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CATALOG / "index.html").write_text(
        '''<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>GS Media Online Test 1.8.9</title></head><body>
<h1>GS Media Online-Test 1.8.9 / Wizard 0.5.6</h1>
<p>ENTWICKLUNGS-BETA: Skin Shortcuts 2.1.0 kompatibel mit BINGIE MOD 2.2.3.
Kodi-native Abhaengigkeitsinstallation via GS Media Bridge 0.1.0.\nJURIALMUNKEY common 0.2.35 als Original-GPL-Testpaket.\nKein vollstaendiger elf-Apps-Installer.</p>
<p>Kodi &gt; Add-ons &gt; Aktualisierungen pruefen.</p>
<p><a href="repository.gsmedia.pilot-1.8.9.zip">Test-Repository 1.8.9 ZIP</a></p>
<p><a href="script.gsmedia.setup-0.5.6.zip">Setup 0.5.6 ZIP</a></p>
<p><a href="script.gsmedia.skinshortcuts.bridge/script.gsmedia.skinshortcuts.bridge-0.1.0.zip">GS Media Bridge 0.1.0</a></p>\n<p><a href="script.module.jurialmunkey/script.module.jurialmunkey-0.2.35.zip">Original jurialmunkey common 0.2.35</a></p>\n<p>Batch 0.5.6: original ResolveURL 5.1.212, ResolveURL XXX 2.1.44,
Cumination 1.1.206 mit SHA-Verifikation.</p>
<p>xVAULT 1.0.3 Originalrepository: Download und Updates direkt vom offiziellen xVAULT Entwickler.</p>
<p>Original Skin Shortcuts:
<a href="script.skinshortcuts/script.skinshortcuts-2.1.0.zip">script.skinshortcuts-2.1.0.zip</a></p>
<p>Bei Skin Shortcuts 2.0.3 bittet der Assistent einmal um Zustimmung zur
voruebergehenden Kodi-Quellenfreigabe und stellt die urspruengliche Einstellung
anschliessend wieder her. Bei Misserfolg stoppt er sicher.</p>
<p>Rollback:
<a href="repository.gsmedia.pilot-1.8.3.zip">Repo 1.8.3</a>,
<a href="script.gsmedia.setup-0.5.0.zip">Wizard 0.5.0</a>.</p>
</body></html>''', encoding="utf-8")
    for name in ("repository.gsmedia.pilot-1.8.8.zip",
                 "repository.gsmedia.pilot-1.8.2.zip",
                 "script.gsmedia.setup-0.5.5.zip",
                 "script.gsmedia.setup-0.4.0.zip"):
        assert (CATALOG / name).is_file(), "Rollback package missing " + name
    print("ONLINE_BETA_056_READY: 12 packages, xVAULT official repo bootstrap, XCMate unchanged")


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Pass exact CI artifact candidate directory"
    release(Path(sys.argv[1]))
