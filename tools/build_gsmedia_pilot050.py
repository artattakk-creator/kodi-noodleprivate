#!/usr/bin/env python3
"""Build a test-only GS Media 1.9.0 pilot catalog with Apache BINGIE bootstrap.

Never publishes to main. The original BINGIE ZIP is retained byte-for-byte.
"""
from pathlib import Path
import hashlib
import shutil
import sys
import zipfile
import urllib.request
import xml.etree.ElementTree as ET
from gsmedia_058_sources import echo_package, ez_package

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/bingie-repository/repository.titan.bingie.mod-2.0.1.zip"
BINGIE_HELPER_UPSTREAM_REV = "d9f334ecc33c7d0e137dd1728af18815c512e577"
BINGIE_HELPER_UPSTREAM_ZIP = (
    "https://raw.githubusercontent.com/AchillesPunks/repository.titan.bingie.mod/"
    + BINGIE_HELPER_UPSTREAM_REV
    + "/omega/script.bingie.helper/script.bingie.helper-1.1.2.zip"
)
BINGIE_HELPER_GIT_BLOB = "c209ef019b71fc7d89860966cdf1beec082e070f"
BINGIE_HELPER_LENGTH = 121147
BINGIE_BOOTSTRAP_ID = "script.gsmedia.bingie.bootstrap"
BINGIE_BOOTSTRAP_VERSION = "0.1.0"

SHORTCUTS_VENDOR = ROOT / "vendor/bingie-skinshortcuts-210/script.skinshortcuts-2.1.0.zip"
JURIAL_VENDOR = ROOT / "vendor/jurialmunkey-common-0235/script.module.jurialmunkey-0.2.35.zip"
JURIAL_BLOB_SHA1 = "98556ddadf9ea88db9809728663ddc08fe9a0990"
XVAULT_REPO_VENDOR = ROOT / "vendor/xvault-official-repository-103/repository.xvault-1.0.3.zip"
XVAULT_REPO_BLOB_SHA1 = "52f4ffdf82234aef742a38a94695e4b373acc0a1"
XVAULT_OFFICIAL_FEED = "https://xvault.repowork.de/addons.xml"
SLYGUY_REPOSITORY_REV = "42ea97aca5987db6ce3e2cdfa1a129bc8b0b0281"
SLYGUY_REPOSITORY_BLOB = "1551ecb1c2fcf1c5f951c84aa7721412c11c90cb"
SLYGUY_REPOSITORY_URL = (
    "https://raw.githubusercontent.com/matthuisman/slyguy.addons/"
    + SLYGUY_REPOSITORY_REV + "/repository.slyguy/repository.slyguy-0.0.9.zip"
)
SLYGUY_SOURCE = ROOT / "vendor/slyguy-repository-009/SOURCE.txt"
RESOLVE_VENDOR = ROOT / "vendor/gsmedia-source-batch-055/script.module.resolveurl-5.1.212.zip"
RESOLVE_XXX_VENDOR = ROOT / "vendor/gsmedia-source-batch-055/script.module.resolveurl.xxx-2.1.44.zip"
RESOLVE_BLOB = "307decca19aed7be9f51e501d736f1cd87443a07"
RESOLVE_XXX_BLOB = "2081ed1145afded501c99bb515c5c9bf91c96d77"
CUMINATION_BLOB = "1df112d1129193b53d07496d307ad0e81eafb259"
CUMINATION_REV = "d3dc0c6643bb4ed07a47fdb3c87a84f8c95bffde"
CUMINATION_URL = ("https://raw.githubusercontent.com/dobbelina/"
                  "repository.dobbelina/" + CUMINATION_REV
                  + "/plugin.video.cumination/plugin.video.cumination-1.1.206.zip")
CUMINATION_SOURCE = ROOT / "vendor/gsmedia-source-batch-055/plugin.video.cumination-SOURCE.txt"
SHORTCUTS_BLOB_SHA1 = "abb2627aef68e15c40e4a33144b1d4cc7bf4d3e6"
SHORTCUTS_MD5 = "69d497c8884da6b169b6f9727d29910f"
SHORTCUTS_SHA256 = "865ee5ea5bf0accee27b82539caabce1c8a9fbb8f94b2900fe5ace4f82c80b23"
ORIGINAL_GIT_BLOB = "da6e2b22b9bdb3baaf12da362fcbadb0b17628e6"
ORIGINAL_SHA256 = "dba0a2e670e2d93158cb030ea52fe3e237bb19177e0a165d99c8f72a8492ef46"
TEST_URL = ("https://raw.githubusercontent.com/artattakk-creator/"
            "kodi-noodleprivate/main/online-test/")
PILOT_ID = "repository.gsmedia.pilot"
PILOT_VERSION = "1.9.8"


def _bytes_in_zip(data, prefix):
    with zipfile.ZipFile(data) as archive:
        assert archive.testzip() is None
        return ET.fromstring(archive.read(prefix + "/addon.xml"))


def _git_blob_sha(data):
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def _pin_original(path, sha, ident, version):
    data = path.read_bytes()
    assert data and _git_blob_sha(data) == sha, "Original ZIP SHA1 mismatch: " + ident
    addon = _bytes_in_zip(path, ident)
    assert addon.get("id") == ident and addon.get("version") == version, ident
    return data, addon


def _fetch_cumination(destination):
    # Upstream GPLv2 Cumination release is >7MB, so fetch immutable original
    # release directly during CI rather than store a corrupt/truncated mirror.
    dest = Path(destination) / "_vendor-cache"/"plugin.video.cumination-1.1.206.zip"
    dest.parent.mkdir(exist_ok=True, parents=True)
    request = urllib.request.Request(
        CUMINATION_URL,
        headers={"User-Agent": "GS-Media-Original-Package-Verification/0.5.7"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(8 * 1024 * 1024 + 1)
    assert len(raw) == 7239627, "Upstream Cumination package length mismatch"
    assert _git_blob_sha(raw) == CUMINATION_BLOB, "Upstream Cumination blob changed"
    dest.write_bytes(raw)
    addon = _bytes_in_zip(dest, "plugin.video.cumination")
    assert addon.get("id") == "plugin.video.cumination"
    assert addon.get("version") == "1.1.206"
    assert addon.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL 2.0"
    assert CUMINATION_SOURCE.is_file(), "Corresponding GPL source attribution missing"
    return dest, raw


def _fetch_slyguy_repo(destination):
    # Original minimal repository bootstrap from an immutable upstream
    # revision. All SlyGuy applications and modules are installed later
    # from its own official feed by Kodi (never mirrored in this build).
    target = Path(destination) / "_vendor-cache" / "repository.slyguy-0.0.9.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        SLYGUY_REPOSITORY_URL,
        headers={"User-Agent": "GS-Media-Kodi-Pilot-Original-Repo-Check/0.5.7"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        contents = response.read(100000)
    assert len(contents) == 84145, "Original SlyGuy repo length changed"
    assert _git_blob_sha(contents) == SLYGUY_REPOSITORY_BLOB, "SlyGuy upstream source changed"
    target.write_bytes(contents)
    addon = _bytes_in_zip(target, "repository.slyguy")
    assert addon.get("id") == "repository.slyguy"
    assert addon.get("version") == "0.0.9"
    remote = addon.find("./extension[@point='xbmc.addon.repository']/dir")
    assert remote is not None, "Missing original official SlyGuy feed"
    info = remote.findtext("info") or ""
    datadir = remote.findtext("datadir") or ""
    assert info.startswith("https://slyguy.uk/") or info.startswith("http://slyguy.uk/"), info
    assert datadir.startswith("https://slyguy.uk/") or datadir.startswith("http://slyguy.uk/"), datadir
    assert SLYGUY_SOURCE.is_file()
    return target, contents


def _fetch_bingie_helper(destination):
    """Fetch the *unchanged* Omega original, pinned to an upstream commit/blob."""
    target = Path(destination) / "_vendor-cache" / "script.bingie.helper-1.1.2.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        BINGIE_HELPER_UPSTREAM_ZIP,
        headers={"User-Agent": "xcMate-Verified-BINGIE-Omega-Helper/0.5.16"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        contents = response.read(BINGIE_HELPER_LENGTH + 1)
    assert len(contents) == BINGIE_HELPER_LENGTH, "Original BINGIE Helper ZIP size differs"
    assert _git_blob_sha(contents) == BINGIE_HELPER_GIT_BLOB, "Original BINGIE Helper blob differs"
    target.write_bytes(contents)
    xml = _bytes_in_zip(target, "script.bingie.helper")
    assert xml.get("version") == "1.1.2"
    assert xml.get("id") == "script.bingie.helper"
    assert xml.findtext("./extension[@point='xbmc.addon.metadata']/license") == "GPL v3.0"
    requires = {(x.get("addon"), x.get("version"))
                for x in xml.findall("./requires/import")}
    assert ("script.module.simplejson", "3.17.0") in requires
    assert ("xbmc.python", "3.0.0") in requires
    return target, xml


def _create_bingie_bootstrap(destination):
    """Inert Kodi-native dependency trigger; no custom installer or userdata edits."""
    addon = ET.Element("addon", {
        "id": BINGIE_BOOTSTRAP_ID,
        "name": "xcMate Native BINGIE Repository & Helper Bootstrap",
        "version": BINGIE_BOOTSTRAP_VERSION,
        "provider-name": "xcMate",
    })
    required = ET.SubElement(addon, "requires")
    for ident, version in (
        ("xbmc.python", "3.0.0"),
        ("repository.titan.bingie.mod", "2.0.1"),
        ("script.bingie.helper", "1.1.2"),
    ):
        ET.SubElement(required, "import", {"addon": ident, "version": version})
    ET.SubElement(addon, "extension", {
        "point": "xbmc.python.script", "library": "default.py"
    })
    metadata = ET.SubElement(addon, "extension", {"point": "xbmc.addon.metadata"})
    ET.SubElement(metadata, "summary", {"lang": "en_GB"}).text = (
        "First-party one-step original BINGIE dependency installation"
    )
    ET.SubElement(metadata, "description", {"lang": "en_GB"}).text = (
        "Inert addon whose only function is to request Kodi's native dependency "
        "resolver to install the verified, unmodified BINGIE MOD repository "
        "2.0.1 and BINGIE Helper 1.1.2 from the xcMate test catalog."
    )
    ET.SubElement(metadata, "license").text = "MIT"
    ET.SubElement(metadata, "platform").text = "all"
    ET.SubElement(metadata, "source").text = (
        "https://github.com/artattakk-creator/kodi-noodleprivate"
    )
    folder = Path(destination) / BINGIE_BOOTSTRAP_ID
    folder.mkdir(parents=True, exist_ok=True)
    zip_path = folder / (BINGIE_BOOTSTRAP_ID + "-" + BINGIE_BOOTSTRAP_VERSION + ".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(BINGIE_BOOTSTRAP_ID + "/addon.xml",
                         ET.tostring(addon, encoding="utf-8", xml_declaration=True))
        archive.writestr(BINGIE_BOOTSTRAP_ID + "/default.py",
                         "# Original BINGIE dependency bootstrap; intentionally inert.\n")
    result = _bytes_in_zip(zip_path, BINGIE_BOOTSTRAP_ID)
    assert result.get("id") == BINGIE_BOOTSTRAP_ID
    deps = {(node.get("addon"), node.get("version"))
            for node in result.findall("./requires/import")}
    assert ("repository.titan.bingie.mod", "2.0.1") in deps
    assert ("script.bingie.helper", "1.1.2") in deps
    return result


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

    resolve_bytes, resolve_meta = _pin_original(
        RESOLVE_VENDOR, RESOLVE_BLOB, "script.module.resolveurl", "5.1.212")
    adult_bytes, adult_meta = _pin_original(
        RESOLVE_XXX_VENDOR, RESOLVE_XXX_BLOB, "script.module.resolveurl.xxx", "2.1.44")
    assert (ROOT/"vendor/gsmedia-source-batch-055/script.module.resolveurl-SOURCE.txt").is_file()
    assert (ROOT/"vendor/gsmedia-source-batch-055/script.module.resolveurl.xxx-SOURCE.txt").is_file()
    cumination_package, cumination_bytes = _fetch_cumination(destination)

    # Only bootstrap the official xVAULT source. The actual 13 MB plugin
    # remains on the author's own feed for provenance and official updates.
    xvault_repo_bytes, xvault_repo = _pin_original(
        XVAULT_REPO_VENDOR, XVAULT_REPO_BLOB_SHA1, "repository.xvault", "1.0.3")
    repo_dir = xvault_repo.find("./extension[@point='xbmc.addon.repository']/dir")
    assert repo_dir is not None and repo_dir.findtext("info") == XVAULT_OFFICIAL_FEED
    assert repo_dir.findtext("checksum") == "https://xvault.repowork.de/addons.xml.md5"
    assert repo_dir.findtext("datadir") == "https://xvault.repowork.de/"
    assert (ROOT/"vendor/xvault-official-repository-103/SOURCE.txt").is_file()

    slyguy_repo_zip, slyguy_repo_bytes = _fetch_slyguy_repo(destination)
    # Verified, user-authorised modern audio source + original maintenance tool.
    echoed_zip, echoed_xml = echo_package(destination)
    ez_zip, ez_xml = ez_package(destination)

    original_bingie_helper_zip, original_bingie_helper = _fetch_bingie_helper(destination)
    original_bingie_bootstrap = _create_bingie_bootstrap(destination)
    all_addons = [bridge_xml, echoed_xml, ez_xml,
                  original_bingie_helper, original_bingie_bootstrap]
    helper_dir = destination / "script.bingie.helper"
    helper_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original_bingie_helper_zip,
                    helper_dir / "script.bingie.helper-1.1.2.zip")
    (helper_dir / "SOURCE.txt").write_text(
        "Original, unmodified BINGIE Helper 1.1.2, GPL v3.0. "
        "Source: https://github.com/matke-84/script.bingie.helper/ ; "
        "verbatim ZIP: " + BINGIE_HELPER_UPSTREAM_ZIP + "\n",
        encoding="utf-8"
    )
    with zipfile.ZipFile(original_bingie_helper_zip) as helper_archive:
        for asset in ("resources/icon.png", "resources/fanart.jpg"):
            member = "script.bingie.helper/" + asset
            if member in helper_archive.namelist():
                dest = helper_dir / asset
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(helper_archive.read(member))
    (destination / BINGIE_BOOTSTRAP_ID / "SOURCE.txt").write_text(
        "Original first-party xcMate native BINGIE dependency bridge, MIT. "
        "https://github.com/artattakk-creator/kodi-noodleprivate\n",
        encoding="utf-8"
    )
    # Source-constrained, inert native resolver bridges for EVERY eligible
    # versioned dependency in the 43-component plan (not just Skin Shortcuts).
    # Their only executable is an inert script; no user profile is accessed.
    sys.path.insert(0, str(ROOT / "src/script.gsmedia.setup/resources/lib"))
    from setup_auto50 import upgrade_bridges
    bridge_specs = upgrade_bridges()
    assert len(bridge_specs) >= 15, "Upgrade bridge registry unexpectedly incomplete"
    upgrade_addons = []
    for spec in bridge_specs:
        helper_id = spec["id"]
        addon = ET.Element("addon", {
            "id": helper_id,
            "name": "XCMate Dependency Upgrade - " + spec["target"],
            "version": "0.1.0",
            "provider-name": "XCMate"
        })
        imports = ET.SubElement(addon, "requires")
        ET.SubElement(imports, "import", {"addon": "xbmc.python", "version": "3.0.0"})
        ET.SubElement(imports, "import", {
            "addon": spec["target"], "version": spec["minimum"]
        })
        ET.SubElement(addon, "extension", {
            "point": "xbmc.python.script", "library": "default.py"
        })
        metadata = ET.SubElement(addon, "extension", {"point": "xbmc.addon.metadata"})
        ET.SubElement(metadata, "summary", {"lang": "en_GB"}).text = (
            "One-time original dependency version resolver"
        )
        ET.SubElement(metadata, "description", {"lang": "en_GB"}).text = (
            "First-party inert resolver: asks Kodi's native add-on dependency "
            "manager to select the original " + spec["target"] +
            " at minimum " + spec["minimum"] + ". No user data modified."
        )
        ET.SubElement(metadata, "platform").text = "all"
        ET.SubElement(metadata, "license").text = "MIT"
        ET.SubElement(metadata, "source").text = (
            "https://github.com/artattakk-creator/kodi-noodleprivate"
        )
        target = destination / helper_id / (helper_id + "-0.1.0.zip")
        target.parent.mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as out:
            out.writestr(helper_id + "/addon.xml",
                         ET.tostring(addon, encoding="utf-8", xml_declaration=True))
            out.writestr(helper_id + "/default.py",
                         "# First-party inert Kodi dependency resolver; no side effects.\n")
        checked = _bytes_in_zip(target, helper_id)
        assert checked.get("version") == "0.1.0"
        requested = checked.findall("./requires/import")
        assert (spec["target"], spec["minimum"]) in [
            (node.get("addon"), node.get("version")) for node in requested]
        upgrade_addons.append(checked)
    all_addons.extend(upgrade_addons)
    for addon_id, version, package in [
        ("plugin.video.xtreammate", "0.1.29.70",
         ROOT / "plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.70.zip"),
        ("plugin.video.noodleprivate", "0.4.2",
         ROOT / "plugin.video.noodleprivate/plugin.video.noodleprivate-0.4.2.zip"),
        ("script.gsmedia.setup", "0.5.15",
         ROOT / ".build/xcmate-0515/script.gsmedia.setup-0.5.15.zip"),
        ("repository.titan.bingie.mod", "2.0.1", VENDOR),
        ("script.skinshortcuts", "2.1.0", SHORTCUTS_VENDOR),
        ("repository.xvault", "1.0.3", XVAULT_REPO_VENDOR),
        ("repository.slyguy", "0.0.9", slyguy_repo_zip),
        ("script.module.jurialmunkey", "0.2.35", JURIAL_VENDOR),
        ("script.module.resolveurl", "5.1.212", RESOLVE_VENDOR),
        ("script.module.resolveurl.xxx", "2.1.44", RESOLVE_XXX_VENDOR),
        ("plugin.video.cumination", "1.1.206", cumination_package),
    ]:
        root = _bytes_in_zip(package, addon_id)
        assert root.get("id") == addon_id and root.get("version") == version
        all_addons.append(root)
        target = destination / addon_id / (addon_id + "-" + version + ".zip")
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(package, target)
        if addon_id in (
            "script.module.resolveurl",
            "script.module.resolveurl.xxx",
            "plugin.video.cumination",
        ):
            source = ROOT / "vendor/gsmedia-source-batch-055" / (addon_id + "-SOURCE.txt")
            shutil.copyfile(source, destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    key = addon_id + "/" + name
                    if key in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(key))
        if addon_id == "repository.slyguy":
            shutil.copyfile(SLYGUY_SOURCE, destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    source = addon_id + "/" + name
                    if source in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(source))
        if addon_id == "repository.xvault":
            shutil.copyfile(ROOT/"vendor/xvault-official-repository-103/SOURCE.txt",
                            destination/addon_id/"SOURCE.txt")
            with zipfile.ZipFile(package) as archive:
                for name in ("icon.png", "fanart.jpg"):
                    source = addon_id + "/" + name
                    if source in archive.namelist():
                        (destination/addon_id/name).write_bytes(archive.read(source))
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
    pilot.set("name", "xcMate Repository – Test v1.9.8 – Kodi 21.3 Omega")
    pilot.set("provider-name", "xcMate")
    dir_ = pilot.find("extension[@point='xbmc.addon.repository']/dir")
    assert dir_ is not None
    dir_.find("info").text = TEST_URL + "addons.xml"
    dir_.find("checksum").text = TEST_URL + "addons.xml.md5"
    dir_.find("datadir").text = TEST_URL
    for node in pilot.findall("extension[@point='xbmc.addon.metadata']/summary"):
        node.text = "xcMate Repository – Test v1.9.8 – Kodi 21.3 Omega (nicht produktiv)"
    for node in pilot.findall("extension[@point='xbmc.addon.metadata']/description"):
        node.text = "XC Mate – geprüfter Testkatalog für den automatischen Kodi-Installationswizard. Android-Endabnahme am Gerät."
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
    print("VENDOR_XVAULT_REPO_SHA256", hashlib.sha256(xvault_repo_bytes).hexdigest())
    print("VENDOR_SLYGUY_REPO_SHA256", hashlib.sha256(slyguy_repo_bytes).hexdigest())
    print("VENDOR_RESOLVE_SHA256", hashlib.sha256(resolve_bytes).hexdigest())
    print("VENDOR_RESOLVE_XXX_SHA256", hashlib.sha256(adult_bytes).hexdigest())
    print("VENDOR_CUMINATION_SHA256", hashlib.sha256(cumination_bytes).hexdigest())
    print("TEST_ONLY", destination, "CATALOG", len(all_addons))
    print("KODI_UPGRADE_BRIDGES", len(bridge_specs))
    print("NO_PUBLICATION_NO_ANDROID_PASS")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv)>1 else ROOT/".build/xcmate-0515-pilot")
