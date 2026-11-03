#!/usr/bin/env python3
"""Publish isolated xcMate Repository 1.9.5 / XCMate Media Center Setup 0.5.12 with mandatory xVAULT and active BINGIE.

Only repository and wizard ZIP bytes may change, all other 13 packages
retained byte-for-byte from already published main/online-test 1.9.4.
"""
from pathlib import Path
from shutil import copy2
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

OLD = {"repository.gsmedia.pilot": "1.9.4", "script.gsmedia.setup": "0.5.11"}
NEW = {"repository.gsmedia.pilot": "1.9.5", "script.gsmedia.setup": "0.5.12"}
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def zip_path(directory, ident, version):
    path = directory / ident / (ident + "-" + version + ".zip")
    assert path.is_file(), "Package missing: " + str(path)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        xml = ET.fromstring(archive.read(ident + "/addon.xml"))
        assert xml.get("id") == ident and xml.get("version") == version
    return path, xml


def release(source, target):
    source, target = Path(source), Path(target)
    old_root, new_root = ET.parse(target / "addons.xml").getroot(), ET.parse(source / "addons.xml").getroot()
    old = {x.get("id"): x for x in old_root.findall("addon")}
    new = {x.get("id"): x for x in new_root.findall("addon")}
    assert len(old) == 15 and len(new) == 15 and set(old) == set(new)
    for ident, v in OLD.items():
        assert old[ident].get("version") == v
        assert new[ident].get("version") == NEW[ident]
    info = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    assert info["repository"]["version"] == "1.9.4"
    assert info["wizard"]["version"] == "0.5.11"
    assert (source / "addons.xml.md5").read_text().strip() == hashlib.md5((source / "addons.xml").read_bytes()).hexdigest()

    # All old Kodi packages and public metadata stay byte-identical, even if
    # older source builds in candidate differ at the same version.
    for ident, node in old.items():
        v = node.get("version")
        archive, _ = zip_path(target, ident, v)
        assert digest(archive.read_bytes()) == info["zip_sha256"][ident], ident
        if ident not in NEW:
            assert new[ident].get("version") == v, ident

    new_packs = {}
    for ident, version in NEW.items():
        new_packs[ident], xml = zip_path(source, ident, version)
        if ident == "repository.gsmedia.pilot":
            directory = xml.find("./extension[@point='xbmc.addon.repository']/dir")
            assert directory is not None
            assert directory.findtext("info") == BASE + "addons.xml"
            assert directory.findtext("checksum") == BASE + "addons.xml.md5"
            assert directory.findtext("datadir") == BASE
            assert xml.get("name") == "xcMate Repository – Test v1.9.5 – Kodi 21.3 Omega"
            assert xml.get("provider-name") == "xcMate"
        else:
            with zipfile.ZipFile(new_packs[ident]) as a:
                ui = a.read("script.gsmedia.setup/resources/lib/setup_auto_ui50.py").decode("utf-8")
                patch = a.read("script.gsmedia.setup/resources/lib/setup_patch.py").decode("utf-8")
                assert 'backup_root = os.path.join(profile, "skinpatch-060")' in ui
                assert 'backup_root = os.path.join(profile, "skinpatch-050")' not in ui
                assert 'dest.name != "skinpatch-060"' in patch
                assert 'SKIN_PATCH_FAILED:' in ui
                assert "script.gsmedia.setup/resources/skinpatch/manifest.json" in a.namelist()
                tmdb = a.read("script.gsmedia.setup/resources/lib/setup_tmdb_apply.py").decode("utf-8")
                assert 'ALT_PLAYER_FILE = "xcmate_xvault_verified.json"' in tmdb
                assert "EXISTING_DEFAULTS_PRESERVED" in tmdb
                assert "def verify(" in tmdb
                assert ui.count("dialog.yesno(") == 3
                assert "TMDB_XVAULT_MANDATORY_UNMET:" in ui
                assert "BINGIE_NOT_ACTIVE:" in ui
                activation = a.read("script.gsmedia.setup/resources/lib/setup_skin_activate_0511.py").decode("utf-8")
                assert 'SETTING = "lookandfeel.skin"' in activation
                assert "Settings.SetSettingValue" in activation
                assert "GUI.GetProperties" in activation
                fin = a.read("script.gsmedia.setup/resources/lib/setup_finish_0512.py").decode("utf-8")
                assert "mark_restart_pending" in fin and "def finish(" in fin
                ui_main = a.read("script.gsmedia.setup/default.py").decode("utf-8")
                assert 'choices = ["Installation starten"]' in ui_main
                assert 'choices.append("Fehlerprotokoll anzeigen")' in ui_main
                assert 'xbmc.executebuiltin("Quit")' in ui
                skinlayout = a.read("script.gsmedia.setup/resources/lib/setup_bingie_apply.py").decode("utf-8")
                assert "OWNED_UPGRADE_READY" in skinlayout and "_semantic_match" in skinlayout
                boot = a.read("script.gsmedia.setup/service.py").decode("utf-8")
                assert "ActivateWindow(Home)" in boot and "POSTBOOT_WIDGETS_" in boot
                meta = ET.fromstring(a.read("script.gsmedia.setup/addon.xml"))
                assert meta.get("name") == "XCMate Media Center Setup – v0.5.12 – Kodi 21.3 Omega"
                assert meta.get("provider-name") == "XCMate"

    # Stop if there is anything unusual before the public index is changed.
    for ident, src in new_packs.items():
        dest = target / ident / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(src, dest)
        assert digest(src.read_bytes()) == digest(dest.read_bytes())
    for ident, src in new_packs.items():
        if ident == "repository.gsmedia.pilot":
            copy2(src, target / src.name)
        elif ident == "script.gsmedia.setup":
            copy2(src, target / src.name)

    final = ET.Element("addons")
    for element in old_root.findall("addon"):
        ident = element.get("id")
        final.append(new[ident] if ident in NEW else element)
    raw = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    raw += ET.tostring(final, encoding="utf-8") + b"\n"
    assert len(ET.fromstring(raw).findall("addon")) == 15
    (target / "addons.xml").write_bytes(raw)
    (target / "addons.xml.md5").write_text(hashlib.md5(raw).hexdigest() + "\n", encoding="ascii")

    info["repository"]["version"] = "1.9.5"
    info["wizard"]["version"] = "0.5.12"
    info["wizard"]["status"] = "BETA_XCMATE_WIDGET_RECOVERY_POSTRESTART_ANDROID_NOT_VERIFIED"
    info["wizard"]["fix"] = ("On-demand 0.5.11-owned widget/SHOUTcast migration, "
                              "semantic SkinShortcuts verification, single "
                              "Installation starten action, error-only local "
                              "diagnostics, verified restart handoff and "
                              "BINGIE home on next Kodi Android launch; all "
                              "43/43 component installations preserved")
    for ident, pack in new_packs.items():
        info["zip_sha256"][ident] = digest(pack.read_bytes())
    (target / "manifest.json").write_text(json.dumps(info, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / "index.html").write_text(
        '<!doctype html><html lang="de"><meta charset="utf-8">'
        '<title>xcMate Repository – Test v1.9.5 – Kodi 21.3 Omega</title>'
        '<h1>xcMate Repository – Test v1.9.5 – Kodi 21.3 Omega / Setup 0.5.12</h1>'
        '<p>Exakter BINGIE 2.2.3 Hashschutz bleibt aktiv. Sicherungspfad '
        'skinpatch-060 abgeglichen. Bestehende Daten und 43 gepruefte '
        'Add-ons bleiben erhalten. Fortsetzung nach Update.</p>'
        '<p><a href="repository.gsmedia.pilot-1.9.5.zip">Repo 1.9.5</a></p>'
        '<p><a href="script.gsmedia.setup-0.5.12.zip">Wizard 0.5.12</a></p>'
        '<p>Android-Box-B-Integration und Player-Abnahme stehen aus.</p></html>\n',
        encoding="utf-8")
    for ident, version in OLD.items():
        assert zip_path(target, ident, version)[0].is_file()
    print("XCMATE_0512_PUBLICATION_READY", len(ET.fromstring(raw).findall("addon")))


if __name__ == "__main__":
    assert len(sys.argv) == 3
    release(sys.argv[1], sys.argv[2])
