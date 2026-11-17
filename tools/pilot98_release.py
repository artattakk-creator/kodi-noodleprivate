"""Publish the exact CI-verified XCMate .98 RC to GS Media Pilot ONLY.

Never merge the full source branch or touch regular/NeoDark3/installer.
All writes are staged in a separate worktree on the *current* main.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION = "0.1.29.98"
ADDON = "plugin.video.xtreammate"
NAME = f"{ADDON}-{VERSION}.zip"
PACKAGE_SHA = "d37d34fbb5be5e46154b912d3ce960f6e248431fcf7d0a9651fa9785b20a12c3"
PILOT97_SHA = "f2853e4432b59f3ba81f3aec630401492fe8d1d8f17de3d9612999b5cf13b6ad"
SOURCE_SHA = "c5ecd2ea69bb84e648cae9433d250613dceff46e"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = SOURCE_ROOT / "docs/XCMate/test-builds/02998" / NAME

ALLOWED = {
    "online-test/addons.xml",
    "online-test/addons.xml.md5",
    "online-test/manifest.json",
    "online-test/index.html",
    f"online-test/{ADDON}/{NAME}",
    f"online-test/{ADDON}/{NAME}.sha256",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect():
    raw = ARCHIVE.read_bytes()
    assert digest(raw) == PACKAGE_SHA, "REVIEW_ZIP_SHA_MISMATCH"
    assert len(raw) == 4772893, "REVIEW_ZIP_SIZE"
    src = SOURCE_ROOT / "src" / ADDON
    members = {
        f"{ADDON}/{p.relative_to(src).as_posix()}": digest(p.read_bytes())
        for p in src.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store"
    }
    with zipfile.ZipFile(ARCHIVE) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) == 901, "ZIP_MEMBER_COUNT_DUPLICATES"
        assert set(names) == set(members), "ZIP_MEMBER_SET_MISMATCH"
        assert z.testzip() is None, "ZIP_CRC"
        assert not any(
            n.startswith("/") or ".." in Path(n).parts
            or n.endswith((".sqlite", ".db", ".log", ".pyc", ".pyo"))
            for n in names
        ), "ZIP_UNSAFE_PATH"
        assert all(digest(z.read(n)) == members[n] for n in names), "ZIP_SOURCE_BYTES"
        addon_xml = z.read(ADDON + "/addon.xml").decode("utf-8")
        node = ET.fromstring(addon_xml)
        assert (node.get("id"), node.get("version")) == (ADDON, VERSION), "ZIP_ADDON_VERSION"
    sidecar = ARCHIVE.with_name(NAME + ".sha256")
    assert sidecar.read_text().split() == [PACKAGE_SHA, NAME], "REVIEW_SIDECAR"
    return addon_xml


def assert_pilot_before(root):
    root = root.resolve()
    pilot = root / "online-test"
    assert ET.parse(root / "addons.xml").getroot().find(
        "./addon[@id='plugin.video.xtreammate']").get("version") == "0.1.29.91", "REGULAR_CHANGED"
    assert ET.parse(root / "src" / ADDON / "addon.xml").getroot().get("version") == "0.1.29.92", "MAIN_PRODUCT_CHANGED"
    raw = (pilot / "addons.xml").read_bytes()
    assert (pilot / "addons.xml.md5").read_text().strip() == hashlib.md5(raw).hexdigest(), "PILOT_MD5_INVALID"
    catalog = ET.fromstring(raw)
    assert catalog.find("./addon[@id='plugin.video.xtreammate']").get("version") == "0.1.29.97", "PILOT_PREVIOUS_VERSION_CHANGED"
    old = pilot / ADDON / f"{ADDON}-0.1.29.97.zip"
    assert digest(old.read_bytes()) == PILOT97_SHA, "PILOT97_ARCHIVE_CHANGED"
    assert (pilot / ADDON / (old.name + ".sha256")).read_text().split() == [PILOT97_SHA, old.name], "PILOT97_SIDECAR_CHANGED"
    manifest = json.loads((pilot / "manifest.json").read_text())
    assert manifest["xcmate97"]["sha256"] == PILOT97_SHA, "PILOT97_MANIFEST_CHANGED"
    assert "xcmate98" not in manifest, "PILOT98_ALREADY_PRESENT"
    assert not (pilot / ADDON / NAME).exists(), "PILOT98_ZIP_ALREADY_EXISTS"
    assert not (pilot / ADDON / (NAME + ".sha256")).exists(), "PILOT98_SHA_ALREADY_EXISTS"
    status = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"], text=True
    )
    assert not status, ("MAIN_WORKTREE_DIRTY", status[:200])
    return manifest


def stage(root):
    addon_xml = inspect()
    root = Path(root).resolve()
    manifest = assert_pilot_before(root)
    pilot = root / "online-test"
    catalog_path = pilot / "addons.xml"
    raw = catalog_path.read_text()
    start = raw.index('<addon id="plugin.video.xtreammate"')
    end = raw.index("</addon>", start) + len("</addon>")
    replacement = re.sub(r"^<\?xml[^>]*\?>\s*", "", addon_xml).strip()
    result = raw[:start] + replacement + raw[end:]
    parsed = ET.fromstring(result)
    hits = [a for a in parsed.findall("addon") if a.get("id") == ADDON]
    assert len(hits) == 1 and hits[0].get("version") == VERSION, "INVALID_PILOT_CATALOG"
    catalog_path.write_text(result)
    (pilot / "addons.xml.md5").write_text(hashlib.md5(result.encode()).hexdigest() + "\n")

    manifest["xcmate98"] = dict(
        addon_id=ADDON,
        version=VERSION,
        source_pr=487,
        source_commit=SOURCE_SHA,
        sha256=PACKAGE_SHA,
        bytes=4772893,
        files=901,
        channels=["pilot"],
        android_status="ANDROID_NOT_TESTED",
        user_approved_pilot_release=True,
        user_approved_regular_release=False,
        regular_channel_unchanged=True,
        neodark3_direct_unchanged=True,
        installer_version_unchanged="0.5.26",
        status="PILOT_ONLY_FULL_CI_NATIVE_PASS_ANDROID_NOT_TESTED",
        pilot_zip=f"online-test/{ADDON}/{NAME}",
    )
    (pilot / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    page = pilot / "index.html"
    html = page.read_text()
    a = html.index("<p><strong>Pilot-Update:</strong>")
    b = html.index("</p>", a) + len("</p>")
    html = (html[:a] +
        "<p><strong>Pilot-Update:</strong> XCMate 0.1.29.98 ist im GS Media "
        "Pilot-Repository 1.9.12 zur Android-Abnahme der Bildanzeige und "
        "manuellen EPG-Zuordnung (#482/#484/#487) verfuegbar. "
        "Vollstaendige Host-CI, native Linux-Kodi-Tests 720p/1080p und "
        "ZIP-Integritaet bestanden; physischer Android-Test offen. "
        "Regulaer/NeoDark3 bleiben unveraendert bei 0.1.29.91.</p>" + html[b:])
    page.write_text(html)
    dest = pilot / ADDON / NAME
    shutil.copyfile(ARCHIVE, dest)
    (pilot / ADDON / (NAME + ".sha256")).write_text(PACKAGE_SHA + "  " + NAME + "\n")
    found = {
        line[3:] for line in subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            text=True,
        ).splitlines()
    }
    assert found == ALLOWED, ("UNEXPECTED_RELEASE_SCOPE", sorted(found ^ ALLOWED))
    assert digest(dest.read_bytes()) == PACKAGE_SHA, "STAGED_ZIP_HASH_MISMATCH"
    assert hashlib.md5(catalog_path.read_bytes()).hexdigest() == (
        pilot / "addons.xml.md5").read_text().strip(), "STAGED_PILOT_MD5_INVALID"
    assert (pilot / ADDON / f"{ADDON}-0.1.29.97.zip").exists(), "PILOT97_MUST_REMAIN"
    print("PILOT98_EXACT_SIX_FILES_READY " + PACKAGE_SHA)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect", "stage"))
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.mode == "inspect":
        inspect()
        print("REVIEW98_EXACT_SOURCE_901_CRC_SHA_PASS " + PACKAGE_SHA)
    else:
        if args.root is None:
            parser.error("--root required to stage Pilot")
        stage(args.root)
