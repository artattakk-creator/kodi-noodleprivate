#!/usr/bin/env python3
"""Build and verify Installer 0.5.25: cumulative overlays over verified 0.5.21 baseline.

Default: local artifact build only. --stage-all updates both Kodi catalogs and NeoDark3 index.
Existing ZIPs and Kodi user profiles remain untouched.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.21.zip"
BASE_BLOB = "c202f1dba406ec981b27d64ba9ba6de78c777e8a"
PREFIX = "script.gsmedia.setup/"
SOURCE = ROOT / "tools/gsmedia_setup0522/base"
VERSION = "0.5.25"
ARTIFACT = "script.gsmedia.setup-0.5.25.zip"
OVERLAYS = (
    "addon.xml",
    "resources/lib/setup_auto50.py",
    "resources/lib/setup_auto_ui50.py",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def manifest_map(root: ET.Element) -> dict:
    rows = root.findall("addon")
    values = {item.get("id"): item for item in rows}
    if len(values) != len(rows):
        raise ValueError("DUPLICATE_KODI_ADDON_IDS")
    return values


def load_base():
    data = BASE.read_bytes()
    if git_blob(data) != BASE_BLOB:
        raise ValueError("0521_BASE_GIT_BLOB_CHANGED")
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        if package.testzip() is not None:
            raise ValueError("0521_ZIP_CRC_FAILURE")
        paths = package.namelist()
        if len(paths) != 32 or len(set(paths)) != len(paths):
            raise ValueError("0521_UNEXPECTED_ENTRY_COUNT")
        if any(
            not n.startswith(PREFIX) or ".." in Path(n).parts or
            Path(n).is_absolute() or "\\" in n
            for n in paths
        ):
            raise ValueError("0521_ZIP_TRAVERSAL")
        files = {name: package.read(name) for name in paths if not name.endswith("/")}
    original = ET.fromstring(files[PREFIX + "addon.xml"])
    if original.get("id") != "script.gsmedia.setup" or original.get("version") != "0.5.21":
        raise ValueError("0521_IDENTITY_MISMATCH")
    return files, sha256(data)


def source_layers(files):
    """Verify extracted audit sources before allowing only three targeted replacements."""
    for path in SOURCE.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        rel = path.relative_to(SOURCE).as_posix()
        name = PREFIX + rel
        if name not in files:
            raise ValueError("0522_BASE_FILE_NOT_IN_ZIP: " + rel)
        if rel not in OVERLAYS and path.read_bytes() != files[name]:
            raise ValueError("0522_UNRELATED_SOURCE_CHANGED: " + rel)
    updated = dict(files)
    for rel in OVERLAYS:
        data = (SOURCE / rel).read_bytes()
        if data == files[PREFIX + rel]:
            raise ValueError("0522_EXPECTED_PATCH_MISSING: " + rel)
        updated[PREFIX + rel] = data
    # Cumulative overlay: first retain every .22 fix, then apply only .23.
    # Never rebuild .23 from the older .21 UI alone.
    for rel in ("addon.xml", "resources/lib/setup_auto_ui50.py"):
        content = (ROOT / "tools/gsmedia_setup0523/overlays" / rel).read_bytes()
        if content == updated[PREFIX + rel]:
            raise ValueError("0523_EXPECTED_DELTA_MISSING:" + rel)
        updated[PREFIX + rel] = content
    ui23 = updated[PREFIX + "resources/lib/setup_auto_ui50.py"]
    for required in (
        b'code in ("INSTALL_ADDON", "INSTALL_UPGRADE")',
        b'expected = ("" if native_shortcuts',
        b'PREINSTALLED_COMPONENT_PRESERVED',
        b'ALREADY_INSTALLED_VERIFIED',
        b'OPTIONAL_EXISTING_ADDON_PRESERVED',
        b'_player_result_reusable(player_result)',
    ):
        if required not in ui23:
            raise ValueError("0523_REGRESSION_FIX_MISSING: " + str(required))
    # Preserve the cumulative 0.5.22 and 0.5.23 source layers, then apply
    # four narrowly scoped 0.5.24 files without dropping prior fixes.
    for rel in ("addon.xml", "resources/lib/setup_auto50.py",
                "resources/lib/setup_auto_ui50.py",
                "resources/lib/setup_origin_guard52.py"):
        content = (ROOT / "tools/gsmedia_setup0524/overlays" / rel).read_bytes()
        if content == updated[PREFIX + rel]:
            raise ValueError("0524_EXPECTED_DELTA_MISSING:" + rel)
        updated[PREFIX + rel] = content
    ui24 = updated[PREFIX + "resources/lib/setup_auto_ui50.py"]
    logic24 = updated[PREFIX + "resources/lib/setup_auto50.py"]
    origin24 = updated[PREFIX + "resources/lib/setup_origin_guard52.py"]
    for phrase in (
        b"native_skinicons = (",
        b"script.gsmedia.upgrade.resource.images.skinicons.wide",
        b"SKINICONS_BRIDGE_PRESENT_DEPENDENCY_UNMET",
        b'expected = ("0.1.0" if native_upgrade',
    ):
        if phrase not in ui24:
            raise ValueError("0524_RESOURCE_PATH_MISSING: " + str(phrase))
    if (b'repo=TEST_CHANNEL, minimum="1.0.5"' not in logic24 or
            b'"resource.images.skinicons.wide"' not in origin24):
        raise ValueError("0524_PINNED_PILOT_SOURCE_NOT_CONFIGURED")
    # 0.5.25 is cumulative: only the audited installer UI, policy guard and
    # manifest override 0.5.24. Never remove the BINGIE resource source fix.
    for rel in ("addon.xml", "resources/lib/setup_auto_ui50.py",
                "resources/lib/setup_origin_guard52.py"):
        content = (ROOT / "tools/gsmedia_setup0525/overlays" / rel).read_bytes()
        if content == updated[PREFIX + rel]:
            raise ValueError("0525_EXPECTED_DELTA_MISSING:" + rel)
        updated[PREFIX + rel] = content
    ui25 = updated[PREFIX + "resources/lib/setup_auto_ui50.py"]
    guard25 = updated[PREFIX + "resources/lib/setup_origin_guard52.py"]
    for needed in (
        b"_native_pilot_bridge(code, step, bridge_lookup)",
        b"native_pilot_bridge = _native_pilot_bridge(",
        b"PILOT_BRIDGE_PRESENT_DEPENDENCY_UNMET:",
        b"else ident if native_pilot_bridge",
        b"SKINICONS_BRIDGE_PRESENT_DEPENDENCY_UNMET",
        b"ALREADY_INSTALLED_VERIFIED",
    ):
        if needed not in ui25:
            raise ValueError("0525_CUMULATIVE_FIX_MISSING: " + str(needed))
    if b'"script.module.jurialmunkey"' not in guard25:
        raise ValueError("0525_GUARD_PILOT_JURIALMUNKEY_MISSING")
    if sorted(updated) != sorted(files):
        raise ValueError("0522_FILESET_CHANGED")
    manifest = ET.fromstring(updated[PREFIX + "addon.xml"])
    if manifest.get("id") != "script.gsmedia.setup" or manifest.get("version") != VERSION:
        raise ValueError("0522_ADDON_ID_VERSION")
    ui = updated[PREFIX + "resources/lib/setup_auto_ui50.py"]
    logic = updated[PREFIX + "resources/lib/setup_auto50.py"]
    if b'install_id = "script.gsmedia.bingie.bootstrap"' in ui:
        raise ValueError("0522_LEGACY_BINGIE_PARENT_RETAINED")
    if b'install_id = "script.module.slyguy"' not in ui:
        raise ValueError("0522_SLYGUY_ORIGIN_FIX_MISSING")
    for phrase in (
        b"BINGIE_REPOSITORY_TOO_OLD",
        b"SIMPLEJSON_3_17_OFFICIAL_NOT_VERIFIED",
        b'"minimum": "2.0.1"',
    ):
        if phrase not in logic:
            raise ValueError("0522_STAGED_PREFLIGHT_MISSING")
    for name, content in updated.items():
        if name.endswith(".py"):
            ast.parse(content, filename=name)
    return updated


def run_logic_contract(files):
    """Real module import and simulated Kodi inventory; never touches a Kodi profile."""
    with tempfile.TemporaryDirectory(prefix="gsmedia0522-test-") as folder:
        target = Path(folder)
        for name, data in files.items():
            if not name.endswith(".py"):
                continue
            p = target / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        sys.path.insert(0, str(target / PREFIX / "resources/lib"))
        try:
            import setup_auto50 as mod
            rows = mod.rows()
            if len(rows) != 48:
                raise ValueError("0522_EXPECTED_48_COMPONENTS_GOT_" + str(len(rows)))
            if len([r for r in rows if r["id"] == "script.module.simplejson"]) != 1:
                raise ValueError("0522_MISSING_SIMPLEJSON_PLAN")
            # All 48 components installed except the BINGIE helper. The
            # repo is a separate, non-counted stage and must be resolved first.
            data = {r["id"]: {"version": r["minimum"] or "99.0.0", "enabled": True}
                    for r in rows}
            data["repository.gsmedia.pilot"] = {"version": "1.9.12", "enabled": True}
            data.pop("script.bingie.helper", None)
            inv = lambda: {"code": "READY", "addons": dict(data)}
            state = mod.new_state()
            assert state["schema"] == 2
            no_repo = mod.next_step(state, inv())
            assert no_repo["code"] == "INSTALL_REPOSITORY", no_repo
            assert no_repo["id"] == "repository.titan.bingie.mod"
            assert no_repo["minimum"] == "2.0.1"
            # Real Kodi confirmations, not an optimistic queue insertion.
            staged = mod.after_request(state, no_repo["id"])
            assert mod.next_step(staged, inv())["code"] == "WAITING"
            data["repository.titan.bingie.mod"] = {"version": "2.0.1", "enabled": True}
            assert mod.next_step(staged, inv())["code"] == "CONFIRM"
            staged = mod.after_confirm(staged, inv())
            assert mod.next_step(staged, inv())["code"] == "INSTALL_ADDON"
            assert mod.next_step(staged, inv())["id"] == "script.bingie.helper"
            data.pop("script.module.simplejson")
            assert mod.next_step(staged, inv())["id"] == "script.module.simplejson"
            data["script.module.simplejson"] = {"version": "3.17.0", "enabled": True}
            data["repository.titan.bingie.mod"] = {"version": "2.0.0", "enabled": True}
            assert mod.next_step(staged, inv())["reason"] == "BINGIE_REPOSITORY_TOO_OLD"
            data["repository.titan.bingie.mod"] = {"version": "2.0.1", "enabled": False}
            assert mod.next_step(staged, inv())["code"] == "ENABLE_ADDON"
            data["repository.titan.bingie.mod"]["enabled"] = True
            data.pop("repository.gsmedia.pilot")
            assert mod.next_step(staged, inv())["reason"] == "PILOT_CATALOG_NOT_INSTALLED"
            # Journal identity and 48-item counting must be stable.
            assert set(staged) == set(state)
            assert mod.count_done(inv())[1] == 48
        finally:
            sys.path.remove(str(target / PREFIX / "resources/lib"))
            for key in list(sys.modules):
                if key.startswith("setup_"):
                    sys.modules.pop(key, None)
    return 12


def package(files, output):
    output.mkdir(parents=True, exist_ok=True)
    result = output / ARTIFACT
    with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 6, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[name])
    with zipfile.ZipFile(result) as archive:
        assert archive.testzip() is None
        assert archive.namelist() == sorted(files)
        assert ET.fromstring(archive.read(PREFIX + "addon.xml")).get("version") == VERSION
        assert len(archive.namelist()) == 32
    result.with_suffix(".zip.sha256").write_text(
        sha256(result.read_bytes()) + "  " + ARTIFACT + "\n", encoding="ascii")
    return result


def stage_pilot(result: Path, digest: str):
    root = ROOT / "online-test"
    catalog = root / "addons.xml"
    old_xml = catalog.read_bytes()
    prior = ET.fromstring(old_xml)
    before = manifest_map(prior)
    assert before["script.gsmedia.setup"].get("version") in ("0.5.24", "0.5.25")
    with zipfile.ZipFile(result) as archive:
        xml = archive.read(PREFIX + "addon.xml").decode("utf-8")
    xml = re.sub(r"^\s*<\?xml[^>]+>\s*", "", xml).strip()
    source = old_xml.decode("utf-8")
    pattern = r'<addon\b(?=[^>]*\bid="script\.gsmedia\.setup")[^>]*>.*?</addon>'
    updated, count = re.subn(pattern, lambda _: xml, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError("0522_PILOT_CATALOG_ENTRY_MISSING")
    next_xml = updated.encode("utf-8")
    after = manifest_map(ET.fromstring(next_xml))
    if before.keys() != after.keys() or any(
        ET.tostring(before[ident]) != ET.tostring(after[ident])
        for ident in before if ident != "script.gsmedia.setup"
    ):
        raise ValueError("0522_UNRELATED_PILOT_ENTRY_CHANGED")
    if after["script.gsmedia.setup"].get("version") != VERSION:
        raise ValueError("0522_CATALOG_WRONG_VERSION")
    target = root / "script.gsmedia.setup" / ARTIFACT
    target.parent.mkdir(parents=True, exist_ok=True)
    top = root / ARTIFACT
    if any(p.exists() and p.read_bytes() != result.read_bytes() for p in (target, top)):
        raise ValueError("0522_EXISTING_ZIP_DIFFERENT")
    target.write_bytes(result.read_bytes())
    top.write_bytes(result.read_bytes())
    (target.parent / (ARTIFACT + ".sha256")).write_text(
        digest + "  " + ARTIFACT + "\n", encoding="ascii")
    catalog.write_bytes(next_xml)
    (root / "addons.xml.md5").write_text(hashlib.md5(next_xml).hexdigest()+"\n", encoding="ascii")
    mfpath = root / "manifest.json"
    manifest = json.loads(mfpath.read_text(encoding="utf-8"))
    manifest["wizard"].update(
        version=VERSION,
        status="PILOT_0525_NATIVE_PILOT_BRIDGES_ANDROID_NOT_TESTED",
        fix="Separate Kodi-native BINGIE repository install before Helper; verified simplejson minimum. No legacy dual-dependency bootstrap.",
        main_installer_url="https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"+ARTIFACT,
    )
    manifest.setdefault("zip_sha256", {})["script.gsmedia.setup"] = digest
    manifest["installer_0525"] = {
        "version": VERSION,
        "channel": "PILOT_ONLY",
        "zip_sha256": digest,
        "android": "NOT_TESTED",
        "legacy_journal_preserved": True,
        "regular_catalog_unchanged": False,
        "auto_pilot_bootstrap": False,
        "note": "If pilot is missing, fail safely and prompt NeoDark3 repository ZIP installation",
    }
    mfpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    html_path = root / "index.html"
    html = html_path.read_text(encoding="utf-8")
    oldname = "script.gsmedia.setup-0.5.24.zip"
    assert html.count(oldname) == 2 or html.count(ARTIFACT) == 2, "0523_KODI_INDEX_UNEXPECTED"
    html = html.replace(oldname, ARTIFACT)
    # Filename in href must equal exact visible link text for Kodi's directory parser.
    kb = (result.stat().st_size + 1023) // 1024
    html = re.sub(r'(<a href="' + re.escape(ARTIFACT) + r'">' + re.escape(ARTIFACT) +
                  r'</a>)\s*\d+K', lambda m: m.group(1) + " " + str(kb) + "K", html)
    html = html.replace("Installer 0.5.24", "Installer 0.5.25")
    assert '<a href="' + ARTIFACT + '">' + ARTIFACT + '</a>' in html
    html_path.write_text(html, encoding="utf-8")
    assert hashlib.md5(catalog.read_bytes()).hexdigest() == (root / "addons.xml.md5").read_text().strip()
    assert (root / "script.gsmedia.setup" / ARTIFACT).read_bytes() == top.read_bytes()
    assert (root / "repository.gsmedia.pilot/repository.gsmedia.pilot-1.9.12.zip").is_file()
    return {"catalog_version": VERSION, "pilot_only": False, "direct_zip": str(top.relative_to(ROOT))}




RESOURCE_ID = "resource.images.skinicons.wide"
RESOURCE_VERSION = "1.0.5"
RESOURCE_FILENAME = RESOURCE_ID + "-" + RESOURCE_VERSION + ".zip"
RESOURCE_URL = (
    "https://raw.githubusercontent.com/AchillesPunks/"
    "repository.titan.bingie.mod/master/omega/"
    + RESOURCE_ID + "/" + RESOURCE_FILENAME
)
# Exact source Git blob SHA verified in upstream repository (not a ZIP SHA).
RESOURCE_BLOB = "cf9edf81fe32b2262f6fe296e0db04361697b7c2"
MAX_RESOURCE_BYTES = 40 * 1024 * 1024


def fetch_verified_skinicons():
    """Read original resource package; never substitute lower official 1.0.3."""
    request = urllib.request.Request(
        RESOURCE_URL, headers={"User-Agent": "GS-Media-Installer/0.5.24"})
    with urllib.request.urlopen(request, timeout=45) as resp:
        if resp.geturl() != RESOURCE_URL:
            raise ValueError("SKINICONS_UNEXPECTED_REDIRECT")
        contents = resp.read(MAX_RESOURCE_BYTES + 1)
    if not contents or len(contents) > MAX_RESOURCE_BYTES:
        raise ValueError("SKINICONS_UPSTREAM_SIZE_INVALID")
    if git_blob(contents) != RESOURCE_BLOB:
        raise ValueError("SKINICONS_UPSTREAM_BLOB_CHANGED")
    with zipfile.ZipFile(io.BytesIO(contents)) as package:
        if package.testzip() is not None:
            raise ValueError("SKINICONS_UPSTREAM_ZIP_CRC_FAILURE")
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError("SKINICONS_DUPLICATE_PATH")
        if any(not name.startswith(RESOURCE_ID + "/") or
               ".." in Path(name).parts or "\\" in name
               for name in names):
            raise ValueError("SKINICONS_UNSAFE_ZIP_PATH")
        target = RESOURCE_ID + "/addon.xml"
        if target not in names:
            raise ValueError("SKINICONS_MISSING_ADDON_XML")
        metadata = ET.fromstring(package.read(target))
        if (metadata.get("id"), metadata.get("version")) != (
                RESOURCE_ID, RESOURCE_VERSION):
            raise ValueError("SKINICONS_WRONG_ID_VERSION")
        if not any(ext.get("point") == "kodi.resource.images"
                   for ext in metadata.findall("extension")):
            raise ValueError("SKINICONS_RESOURCE_TYPE_MISMATCH")
    return contents, metadata


def stage_skinicons_pilot():
    """Mirror source-verified *unmodified* BINGIE 1.0.5 to the Pilot repo."""
    content, metadata = fetch_verified_skinicons()
    digest = sha256(content)
    root = ROOT / "online-test"
    target = root / RESOURCE_ID / RESOURCE_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != content:
        raise ValueError("SKINICONS_PILOT_DIFFERENT_ZIP_EXISTS")
    target.write_bytes(content)
    checksum_file = target.with_suffix(".zip.sha256")
    checksum_file.write_text(digest + "  " + RESOURCE_FILENAME + "\n",
                             encoding="ascii")
    catalog = root / "addons.xml"
    source = catalog.read_text(encoding="utf-8")
    prior = manifest_map(ET.fromstring(source))
    if RESOURCE_ID in prior:
        existing = prior[RESOURCE_ID]
        if existing.get("version") != RESOURCE_VERSION:
            raise ValueError("SKINICONS_PILOT_UNEXPECTED_RESOURCE_VERSION")
    else:
        if not source.rstrip().endswith("</addons>"):
            raise ValueError("SKINICONS_PILOT_CATALOG_MALFORMED")
        desc = ET.tostring(metadata, encoding="unicode")
        source = source.rsplit("</addons>", 1)[0] + desc + "\n</addons>\n"
    updated = source.encode("utf-8")
    after = manifest_map(ET.fromstring(updated))
    if set(after) - set(prior) not in (set(), {RESOURCE_ID}):
        raise ValueError("SKINICONS_UNRELATED_CATALOG_CHANGED")
    if after[RESOURCE_ID].get("version") != RESOURCE_VERSION:
        raise ValueError("SKINICONS_CATALOG_VERSION_INVALID")
    catalog.write_bytes(updated)
    (root / "addons.xml.md5").write_text(
        hashlib.md5(updated).hexdigest() + "\n", encoding="ascii")
    mfpath = root / "manifest.json"
    manifest = json.loads(mfpath.read_text(encoding="utf-8"))
    manifest["skinicons_wide_105"] = {
        "id": RESOURCE_ID,
        "version": RESOURCE_VERSION,
        "source": RESOURCE_URL,
        "upstream_git_blob": RESOURCE_BLOB,
        "sha256": digest,
        "channel": "GS_MEDIA_PILOT",
        "unmodified_original_zip": True,
        "device_test": "NOT_TESTED",
    }
    mfpath.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return {"id": RESOURCE_ID, "version": RESOURCE_VERSION,
            "sha256": digest, "source_blob": RESOURCE_BLOB,
            "zip": str(target.relative_to(ROOT))}

def stage_regular(result: Path, digest: str):
    """Update only normal GS Media Installer metadata and immutable ZIP."""
    root = ROOT
    catalog = root / "addons.xml"
    old_xml = catalog.read_bytes()
    before = manifest_map(ET.fromstring(old_xml))
    if before["script.gsmedia.setup"].get("version") not in ("0.5.24", "0.5.25"):
        raise ValueError("0523_UNEXPECTED_ROOT_BASE")
    with zipfile.ZipFile(result) as z:
        entry = z.read(PREFIX + "addon.xml").decode("utf-8")
    entry = re.sub(r"^\s*<\?xml[^>]+>\s*", "", entry).strip()
    old = old_xml.decode("utf-8")
    pattern = r'<addon\b(?=[^>]*\bid="script\.gsmedia\.setup")[^>]*>.*?</addon>'
    replaced, count = re.subn(pattern, lambda _: entry, old, count=1, flags=re.S)
    if count != 1:
        raise ValueError("0523_ROOT_ENTRY_NOT_FOUND")
    data = replaced.encode("utf-8")
    after = manifest_map(ET.fromstring(data))
    if before.keys() != after.keys() or any(
        ET.tostring(before[ident]) != ET.tostring(after[ident])
        for ident in before if ident != "script.gsmedia.setup"
    ):
        raise ValueError("0523_UNRELATED_ROOT_CATALOG_CHANGED")
    if after["script.gsmedia.setup"].get("version") != VERSION:
        raise ValueError("0523_ROOT_VERSION_WRONG")
    target = root / PREFIX / ARTIFACT
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and sha256(target.read_bytes()) != digest:
        raise ValueError("0523_EXISTING_ROOT_ZIP_DIFFERENT")
    target.write_bytes(result.read_bytes())
    catalog.write_bytes(data)
    (root / "addons.xml.md5").write_text(hashlib.md5(data).hexdigest()+"\n", encoding="ascii")
    htmlpath = root / "index.html"
    html = htmlpath.read_text(encoding="utf-8")
    oldlink = "script.gsmedia.setup/script.gsmedia.setup-0.5.24.zip"
    newlink = "script.gsmedia.setup/" + ARTIFACT
    if oldlink not in html and newlink not in html:
        raise ValueError("0523_ROOT_INDEX_LINK_MISSING")
    html = html.replace(oldlink, newlink).replace("Installer 0.5.24", "Installer 0.5.25")
    htmlpath.write_text(html, encoding="utf-8")
    if hashlib.md5(catalog.read_bytes()).hexdigest() != (root / "addons.xml.md5").read_text().strip():
        raise ValueError("0523_ROOT_MD5_MISMATCH")
    return {"catalog_version": VERSION, "sha256": digest, "path": str(target.relative_to(ROOT))}


def run_0523_regressions(files):
    """Extra fail-safe tests on compiled real 48-step logic and UI branch."""
    ui = files[PREFIX + "resources/lib/setup_auto_ui50.py"].decode("utf-8")
    parsed = ast.parse(ui)
    fn = next(node for node in parsed.body
              if isinstance(node, ast.FunctionDef) and node.name == "_player_result_reusable")
    namespace = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<player-reuse>", "exec"), namespace)
    reusable = namespace["_player_result_reusable"]
    for code in ("OK", "TMDB_PLAYER_EXISTING_DEFAULTS_PRESERVED",
                 "TMDB_PLAYER_EXISTING_PLAYER_PRESERVED"):
        assert reusable(code), code
    for code in ("MISSING_PLAYER", "INVALID_PROFILE", "TMDB_PLAYER_FAILED"):
        assert not reusable(code), code
    # Check both calls: player-stage and final stage must accept preservation.
    assert ui.count("not _player_result_reusable(") == 2
    assert "PREINSTALLED_COMPONENT_PRESERVED" in ui
    assert "ALREADY_INSTALLED_VERIFIED" in ui
    assert "OPTIONAL_EXISTING_ADDON_PRESERVED" in ui
    assert 'expected = ("0.1.0" if native_upgrade' in ui
    assert 'native_upgrade = (code == "INSTALL_UPGRADE" or' in ui
    assert "SHORTCUTS_BRIDGE_PRESENT_DEPENDENCY_UNMET" in ui
    with tempfile.TemporaryDirectory(prefix="gsmedia0523-regression-") as folder:
        root = Path(folder)
        for name, data in files.items():
            if name.endswith(".py"):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        lib = str(root / PREFIX / "resources/lib")
        sys.path.insert(0, lib)
        try:
            import setup_auto50 as mod
            rows = mod.rows()
            assert len(rows) == 48
            data = {r["id"]: {"version": r["minimum"] or "99.0.0", "enabled": True}
                    for r in rows}
            data["repository.gsmedia.pilot"] = {"version": "1.9.12", "enabled": True}
            data["repository.xvault"] = {"version": "1.0.0", "enabled": True}
            data["repository.titan.bingie.mod"] = {"version": "2.0.1", "enabled": True}
            def decision():
                return mod.next_step(mod.new_state(), {"code": "READY", "addons": data})
            assert decision()["code"] == "APPS_PRESENT"
            data.pop("script.skinshortcuts")
            step = decision()
            assert (step["code"], step["id"]) == ("INSTALL_ADDON", "script.skinshortcuts"), step
            data["script.skinshortcuts"] = {"version": "2.0.3", "enabled": True}
            step = decision()
            assert (step["code"], step["id"]) == ("INSTALL_UPGRADE", "script.skinshortcuts"), step
            data["script.skinshortcuts"] = {"version": "2.1.0", "enabled": True}
            assert decision()["code"] == "APPS_PRESENT"
            # Resource images: absent or official 1.0.3 must use Pilot's
            # pinned 1.0.5 package and 0.1.0 dependency bridge.
            data.pop("resource.images.skinicons.wide")
            step = decision()
            assert (step["code"], step["id"]) == (
                "INSTALL_ADDON", "resource.images.skinicons.wide"), step
            data["resource.images.skinicons.wide"] = {
                "version": "1.0.3", "enabled": True}
            step = decision()
            assert (step["code"], step["id"], step["bridge"]) == (
                "INSTALL_UPGRADE", "resource.images.skinicons.wide",
                "script.gsmedia.upgrade.resource.images.skinicons.wide"), step
            data["resource.images.skinicons.wide"] = {
                "version": "1.0.5", "enabled": True}
            assert decision()["code"] == "APPS_PRESENT"
            # Preinstalled xVAULT (and any optional image add-on) must not
            # make the real mandatory package plan stop.
            data["plugin.video.xvault"] = {"version": "99.0.0", "enabled": True}
            data["plugin.image.ximage"] = {"version": "1.0.0", "enabled": True}
            assert decision()["code"] == "APPS_PRESENT"
        finally:
            sys.path.remove(lib)
            for name in list(sys.modules):
                if name.startswith("setup_"):
                    sys.modules.pop(name, None)
    return 24


PILOT_NATIVE_TARGETS = (
    "script.bingie.helper",
    "script.module.jurialmunkey",
    "script.module.resolveurl",
    "script.module.resolveurl.xxx",
    "plugin.audio.m3sr2019",
    "script.ezmaintenanceplus",
    "plugin.video.cumination",
)


def run_0525_regressions(files):
    """Exercise the real 7-target native resolver and all 48 graph entries."""
    source = files[PREFIX + "resources/lib/setup_auto_ui50.py"].decode("utf-8")
    parsed = ast.parse(source)
    lookup = {node.name: node for node in parsed.body
              if isinstance(node, ast.FunctionDef)}
    assignments = [node for node in parsed.body
                   if isinstance(node, ast.Assign) and any(
                       isinstance(t, ast.Name) and t.id == "PILOT_BRIDGE_TARGETS"
                       for t in node.targets)]
    assert len(assignments) == 1 and "_native_pilot_bridge" in lookup
    assert source.count("PILOT_BRIDGE_PRESENT_DEPENDENCY_UNMET") == 1
    assert "else ident if native_pilot_bridge" in source
    assert "bool(native_pilot_bridge)" in source
    ns = {}
    exec(compile(ast.Module(
        body=assignments + [lookup["_native_pilot_bridge"]],
        type_ignores=[]), "<pilot-bridge>", "exec"), ns)
    select = ns["_native_pilot_bridge"]
    assert set(ns["PILOT_BRIDGE_TARGETS"]) == set(PILOT_NATIVE_TARGETS)
    fake_lookup = lambda ident, source, minimum: "script.gsmedia.upgrade." + ident
    rejected_lookup = lambda ident, source, minimum: "script.gsmedia.upgrade.OTHER"
    assert not select("INSTALL_ADDON", {
        "id": "script.module.jurialmunkey", "source": "repository.xbmc.org",
        "minimum": "0.2.35"}, fake_lookup)
    assert not select("INSTALL_ADDON", {
        "id": "plugin.video.untrusted", "source": "repository.gsmedia.pilot",
        "minimum": "999"}, fake_lookup)
    for target in PILOT_NATIVE_TARGETS:
        for code in ("INSTALL_ADDON", "INSTALL_UPGRADE"):
            step = {"id": target, "source": "repository.gsmedia.pilot",
                    "minimum": "1.0.0"}
            assert select(code, step, fake_lookup) == (
                "script.gsmedia.upgrade." + target)
            assert select(code, step, rejected_lookup) == ""
            assert select("SOURCE_BLOCKED", step, fake_lookup) == ""
    # The Pilot catalog really exposes each native parent and its original
    # target, with the required minimum and two installable ZIP files.
    index = manifest_map(ET.fromstring(
        (ROOT / "online-test/addons.xml").read_bytes()))
    with tempfile.TemporaryDirectory(prefix="gsmedia0525-test-") as folder:
        target = Path(folder)
        for name, data in files.items():
            if name.endswith(".py"):
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        lib = str(target / PREFIX / "resources/lib")
        sys.path.insert(0, lib)
        try:
            import setup_auto50 as mod
            rows = mod.rows()
            assert len(rows) == 48
            by_id = {r["id"]: r for r in rows}
            data = {r["id"]: {"version": r["minimum"] or "99.0.0",
                              "enabled": True} for r in rows}
            data["repository.gsmedia.pilot"] = {
                "version": "1.9.12", "enabled": True}
            data["repository.titan.bingie.mod"] = {
                "version": "2.0.1", "enabled": True}
            data["repository.xvault"] = {"version": "1.0", "enabled": True}
            def next_action():
                return mod.next_step(mod.new_state(),
                                     {"code": "READY", "addons": data})
            assert next_action()["code"] == "APPS_PRESENT"
            for name in PILOT_NATIVE_TARGETS:
                row = by_id[name]
                assert row["repo"] == "repository.gsmedia.pilot"
                assert row["minimum"]
                bridge = mod.upgrade_bridge_for(
                    name, row["repo"], row["minimum"])
                assert bridge == "script.gsmedia.upgrade." + name
                assert name in index and bridge in index
                version = index[name].get("version")
                assert mod.installed(
                    {"code": "READY", "addons": {
                        name: {"version": version, "enabled": True}
                    }}, name, row["minimum"])
                assert index[bridge].get("version") == "0.1.0"
                for addon_id, vers in ((name, version),
                                       (bridge, "0.1.0")):
                    file = (ROOT / "online-test" / addon_id /
                            (addon_id + "-" + vers + ".zip"))
                    if not file.is_file():
                        raise ValueError("0525_PILOT_SOURCE_ZIP_MISSING:" + addon_id)
                present = data.pop(name)
                step = next_action()
                assert (step["code"], step["id"]) == (
                    "INSTALL_ADDON", name), step
                assert select(step["code"], step, mod.upgrade_bridge_for) == bridge
                data[name] = {"version": "0.0.1", "enabled": True}
                step = next_action()
                assert (step["code"], step["id"]) == (
                    "INSTALL_UPGRADE", name), step
                assert select(step["code"], step, mod.upgrade_bridge_for) == bridge
                data[name] = present
                assert next_action()["code"] == "APPS_PRESENT"
            assert "script.skinshortcuts" not in ns["PILOT_BRIDGE_TARGETS"]
            assert "resource.images.skinicons.wide" not in ns["PILOT_BRIDGE_TARGETS"]
        finally:
            sys.path.remove(lib)
            for name in list(sys.modules):
                if name.startswith("setup_"):
                    sys.modules.pop(name, None)
    return 42


def build(out: Path, release: bool = False):
    files, base_sha = load_base()
    changed = source_layers(files)
    tests = (run_logic_contract(changed) + run_0523_regressions(changed) +
             run_0525_regressions(changed))
    artifact = package(changed, out)
    digest = sha256(artifact.read_bytes())
    result = {
        "package": ARTIFACT,
        "sha256": digest,
        "bytes": artifact.stat().st_size,
        "files": len(changed),
        "base_0521_sha256": base_sha,
        "changed_files": list(OVERLAYS) + [
            "0525/addon.xml", "0525/resources/lib/setup_auto_ui50.py",
            "0525/resources/lib/setup_origin_guard52.py",
            "0523/addon.xml", "0523/resources/lib/setup_auto_ui50.py",
            "0524/addon.xml", "0524/resources/lib/setup_auto50.py",
            "0524/resources/lib/setup_auto_ui50.py",
            "0524/resources/lib/setup_origin_guard52.py"],
        "host_contract_checks": tests,
        "zip_crc": "PASS",
        "dependency_staging": "BINGIE_REPO_2_0_1_THEN_HELPER_1_1_2",
        "simplejson_minimum": "3.17.0",
        "journal_schema": 2,
        "android": "NOT_TESTED",
        "regular_channel": "PUBLISH_WITH_PILOT_WHEN_STAGED",
        "known_limit": "Pilot repository must be installed beforehand; Kodi-specific dependency outcomes need on-device testing",
    }
    if release:
        result["pilot"] = stage_pilot(artifact, digest)
        result["skinicons_upstream"] = stage_skinicons_pilot()
        result["regular"] = stage_regular(artifact, digest)
    (out / "installer0525-verification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--stage-all", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args.out, args.stage_all), indent=2, sort_keys=True))
