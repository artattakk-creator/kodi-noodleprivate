#!/usr/bin/env python3
"""One-time, fail-closed XCMate .100 Pilot/NeoDark3 publication of the exact verified ZIP."""
from __future__ import annotations
import base64
import hashlib
import io
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ONLINE = ROOT / "online-test"
ADDON = "plugin.video.xtreammate"
VERSION = "0.1.29.100"
NAME = f"{ADDON}-{VERSION}.zip"
EXPECTED_SHA = "9fbea224f9417193b85f8b57a390653eb4d77aeff85196973f3520d51acb26de"
EXPECTED_SIZE = 6055446
EXPECTED_ENTRIES = 915
STAGING = ROOT / ".release-staging" / "xcmate100" / "chunks"

def ensure(condition, why):
    if not condition:
        raise RuntimeError("XCMATE100_RELEASE_BLOCKED: " + why)

def main():
    paths = sorted(STAGING.glob("*.b64"))
    ensure([x.name for x in paths] == [f"{x:02d}.b64" for x in range(16)], "shard_inventory")
    encoded = b"".join(x.read_bytes() for x in paths)
    ensure(len(encoded) == 8073928, "shard_length")
    data = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(data).hexdigest()
    ensure(len(data) == EXPECTED_SIZE and digest == EXPECTED_SHA, "original_sha256_or_size")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        ensure(len(names) == EXPECTED_ENTRIES and z.testzip() is None, "zip_integrity")
        ensure(len(names) == len(set(names)), "zip_duplicate_entries")
        ensure(not any(x.startswith("/") or ".." in Path(x).parts or "\\" in x for x in names), "zip_paths")
        xml = z.read(f"{ADDON}/addon.xml")
        pkg = ET.fromstring(xml)
        ensure(pkg.attrib.get("id") == ADDON and pkg.attrib.get("version") == VERSION, "addon_manifest")
    source_xml = ET.parse(ROOT / "src" / ADDON / "addon.xml").getroot()
    ensure(source_xml.attrib.get("version") == VERSION, "merged_main_source_version")

    catalog_path = ONLINE / "addons.xml"
    raw = catalog_path.read_bytes()
    pattern = rb'<addon id="plugin\.video\.xtreammate"[\s\S]*?</addon>'
    old = re.findall(pattern, raw)
    ensure(len(old) == 1 and b'version="0.1.29.99"' in old[0], "pilot_catalog_expected_99")
    source_bytes = (ROOT / "src" / ADDON / "addon.xml").read_bytes()
    source_node = re.findall(pattern, source_bytes)
    ensure(len(source_node) == 1 and b'version="0.1.29.100"' in source_node[0], "source_addon_node")
    new_catalog = re.sub(pattern, lambda m: source_node[0], raw, count=1)
    parsed = ET.fromstring(new_catalog)
    ensure(len([x for x in parsed.findall("addon") if x.get("id") == ADDON and x.get("version") == VERSION]) == 1, "pilot_xml")
    ensure(len([x for x in parsed.findall("addon") if x.get("id") == "script.gsmedia.setup" and x.get("version") == "0.5.27"]) == 1, "installer_catalog_unchanged")

    index_path = ONLINE / "index.html"
    index = index_path.read_text(encoding="utf-8")
    old_row = re.compile(r'<tr><td><a href="plugin\.video\.xtreammate-0\.1\.29\.91\.zip">.*?</tr>', re.S)
    ensure(len(old_row.findall(index)) == 1, "neodark3_old_row")
    new_row = ('<tr><td><a href="' + NAME + '">' + NAME + '</a></td>'
               '<td><strong>XCMate 0.1.29.100 – Pilot/NeoDark3 TEST</strong>'
               '<br>EPG Agent, XMLTV-Bildrollen und neue Designs. '
               '<strong>Android-/LG-Geräteabnahme sowie BINGIE-Navigation noch offen.</strong> '
               'Vor dem Update Benutzerprofil sichern. '
               '<a href="' + NAME + '.sha256">SHA256-Prüfsumme</a>.</td></tr>')
    index = old_row.sub(lambda m: new_row, index, count=1)
    description = ('<p><strong>Pilot-Update:</strong> XCMate 0.1.29.100 ist im GS Media Pilot '
                   'Repository 1.9.12 als nicht geraeteabgenommene Testversion verfuegbar. '
                   'Dieselbe gepruefte ZIP ist in NeoDark3 direkt installierbar. '
                   'Android/BINGIE- und LG/webOS-Abnahme offen, sechs Widgetreihen/Fernbedienung '
                   'weiter zu pruefen. Der private EPG-Agent-Publisher steht auf PRIVATE_PENDING. '
                   'Der regulaere Repository-Kanal bleibt unveraendert.</p>')
    par = re.compile(r'<p><strong>Pilot-Update:</strong>.*?</p>', re.S)
    ensure(len(par.findall(index)) == 1, "pilot_index_paragraph")
    index = par.sub(lambda m: description, index, count=1)
    ensure('script.gsmedia.setup-0.5.28.zip' in index, "installer28_preserved")

    manifest_path = ONLINE / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ensure("xcmate100" not in manifest, "release_previously_recorded")
    manifest["zip_sha256"][ADDON] = EXPECTED_SHA
    manifest["xcmate100"] = {
        "addon_id": ADDON, "version": VERSION, "sha256": EXPECTED_SHA,
        "bytes": EXPECTED_SIZE, "files": EXPECTED_ENTRIES,
        "channels": ["pilot", "neodark3"],
        "pilot_zip": f"online-test/{ADDON}/{NAME}",
        "neodark3_zip": f"online-test/{NAME}",
        "source_merge_sha": "d55567b25689670b623813159010162d3a7b0213",
        "status": "PILOT_NEODARK3_TEST_ONLY_PHYSICAL_ACCEPTANCE_PENDING",
        "user_approved_pilot_release": True,
        "user_approved_neodark3_direct_release": True,
        "user_approved_regular_release": False,
        "repository_released": True,
        "android_status": "NOT_TESTED", "lg_webos_status": "NOT_TESTED",
        "bingie_nav_timeout": "OPEN", "bingie_six_rows_native_pass": False,
        "epg_agent_private_manifest": "PRIVATE_PENDING",
        "regular_catalog_unchanged": True,
    }
    checksum = f"{EXPECTED_SHA}  {NAME}\n".encode("ascii")
    pilot_dir = ONLINE / ADDON
    ensure(pilot_dir.is_dir(), "missing_pilot_directory")
    ensure(not (pilot_dir / NAME).exists() and not (ONLINE / NAME).exists(), "target_package_already_exists")

    # Write only after all prerequisite and digest checks.
    for target in (pilot_dir / NAME, ONLINE / NAME):
        target.write_bytes(data)
        target.with_name(NAME + ".sha256").write_bytes(checksum)
    old_direct = ONLINE / f"{ADDON}-0.1.29.91.zip"
    old_sha = ONLINE / f"{ADDON}-0.1.29.91.zip.sha256"
    ensure(old_direct.is_file() and old_sha.is_file(), "old_direct_missing")
    old_direct.unlink()
    old_sha.unlink()
    catalog_path.write_bytes(new_catalog)
    (ONLINE / "addons.xml.md5").write_text(hashlib.md5(new_catalog).hexdigest() + "\n", encoding="ascii")
    index_path.write_text(index, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "TEST_PUBLISHED_IN_WORKTREE", "version": VERSION,
                      "bytes": len(data), "sha256": digest, "channels": ["pilot", "neodark3"]}, sort_keys=True))

if __name__ == "__main__":
    main()
