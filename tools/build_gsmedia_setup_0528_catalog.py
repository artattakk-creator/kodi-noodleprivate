#!/usr/bin/env python3
"""Build the Issue #496 candidate or stage a local three-channel release plan."""
import argparse
import ast
from hashlib import md5, sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import stat
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from build_gsmedia_setup_0527 import build as build_0527

ROOT = Path(__file__).resolve().parents[1]
ADDON = "script.gsmedia.setup"
PREFIX = ADDON + "/"
VERSION = "0.5.28"
NAME = ADDON + "-" + VERSION + ".zip"
RELEASE_IDENTITY = "gsmedia-setup-0528-catalog-496"
BASE_COMMIT = "8f8569294f29a50ba99a23e2de58ecae846bcfed"
BASE_SHA256 = "1d74c566edfc20a122bb8767c17bed915d90966fb5e33e47298aa257500e2872"
LIVE_BASE_VERSION = "0.5.26"
LIVE_BASE_NAME = ADDON + "-" + LIVE_BASE_VERSION + ".zip"
LIVE_METADATA_SHA256 = {
    "addons.xml": "c094b14edc1320f22aa2ca48c67cdc06b6e4899bf160e72d50a4b1515a27427b",
    "addons.xml.md5": "f17de59cc2e0fbff7d7ad1ab55946b9e92d47aab0343ce5c70b484f625b780c7",
    "index.html": "54d62f7ecdad83994e47263a2b5244eaf25bfe0c436ae5f3b3f26cad591b15e3",
    "online-test/addons.xml": "14378bf53e93323b03dde3037f5dd78f16064f9ece2f7476ebd8286f14913db2",
    "online-test/addons.xml.md5": "606ca429c04ceb546d31b74c8d1d6e228df63a036f823c3e7fafc1d29d460ab9",
    "online-test/index.html": "199a8df9aaaa66fa3b259c5191330371803e059674f4b48e03aac7426d5671b2",
    "online-test/manifest.json": "07f39e76ef9406b2aa5feb56942eb4281f637aa224ccb0e337fc25466bdf8a18",
}
OVERLAYS = ROOT / "tools/gsmedia_setup0528/overlays"
CANDIDATE = ROOT / "docs/GS-Media/test-builds/0528"
MANIFEST = PREFIX + "addon.xml"
OVERLAY_PATHS = {
    "addon.xml", "default.py", "service.py",
    "resources/lib/setup_auto_store50.py", "resources/lib/setup_auto_ui50.py",
    "resources/lib/setup_compat27.py", "resources/lib/setup_source27.py",
}
CHANNELS = {
    "regular": {
        "catalog": "addons.xml",
        "index": "index.html",
        "href": PREFIX + NAME,
        "zip": PREFIX + NAME,
    },
    "pilot": {
        "catalog": "online-test/addons.xml",
        "zip": "online-test/" + PREFIX + NAME,
    },
    "neodark3": {
        "catalog": "online-test/addons.xml",
        "index": "online-test/index.html",
        "href": NAME,
        "zip": "online-test/" + NAME,
    },
}


def output_path(folder, *, release_plan=False):
    folder = Path(folder).absolute()
    if any(path.is_symlink() for path in (folder, *folder.parents)):
        raise ValueError("GS0528_OUTPUT_SYMLINK")
    folder = folder.resolve()
    if (folder == ROOT or folder in ROOT.parents
            or ROOT in folder.parents and (release_plan or folder != CANDIDATE)):
        raise ValueError("GS0528_OUTPUT_SCOPE")
    return folder


def package_members(raw, version):
    with ZipFile(BytesIO(raw)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if archive.testzip() is not None or len(names) != len(set(names)):
            raise ValueError("GS0528_ZIP_READBACK_FAILED")
        for entry in entries:
            name = entry.filename
            if (not name.startswith(PREFIX) or "\\" in name
                    or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", name)
                    or ".." in PurePosixPath(name).parts
                    or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG)):
                raise ValueError("GS0528_UNSAFE_ZIP_MEMBER")
        files = {name: archive.read(name) for name in names}
    manifest = ET.fromstring(files[MANIFEST])
    if (manifest.tag, manifest.get("id"), manifest.get("version")) != ("addon", ADDON, version):
        raise ValueError("GS0528_PACKAGE_IDENTITY")
    return files


def candidate_bytes():
    with TemporaryDirectory(prefix="gsmedia-0528-base-") as folder:
        baseline = build_0527(Path(folder)).read_bytes()
    if sha256(baseline).hexdigest() != BASE_SHA256:
        raise ValueError("GS0528_BASE_0527_SHA256")
    files = package_members(baseline, "0.5.27")
    if OVERLAYS.is_symlink():
        raise ValueError("GS0528_OVERLAY_SYMLINK")
    found = set()
    for path in sorted(OVERLAYS.rglob("*")):
        if path.is_symlink():
            raise ValueError("GS0528_OVERLAY_SYMLINK")
        if path.is_dir():
            continue
        relative = path.relative_to(OVERLAYS).as_posix()
        if not path.is_file() or relative not in OVERLAY_PATHS:
            raise ValueError("GS0528_UNEXPECTED_OVERLAY")
        found.add(relative)
        name = PREFIX + relative
        raw = path.read_bytes()
        if name.endswith(".py"):
            ast.parse(raw, filename=name, feature_version=(3, 8))
        files[name] = raw
    if found != OVERLAY_PATHS:
        raise ValueError("GS0528_MISSING_OVERLAY")
    digestible = BytesIO()
    with ZipFile(digestible, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(files.items()):
            info = ZipInfo(name, date_time=(2026, 11, 19, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw, compress_type=ZIP_DEFLATED, compresslevel=9)
    payload = digestible.getvalue()
    if package_members(payload, VERSION) != files:
        raise ValueError("GS0528_ZIP_READBACK_FAILED")
    return payload


def checksum(payload):
    return (sha256(payload).hexdigest() + "  " + NAME + "\n").encode("ascii")


def build(folder):
    folder = output_path(folder)
    payload = candidate_bytes()
    files = {NAME: payload, NAME + ".sha256": checksum(payload)}
    for name, data in files.items():
        target = folder / name
        if target.is_symlink() or (target.exists() and
                (not target.is_file() or target.read_bytes() != data)):
            raise ValueError("GS0528_OUTPUT_COLLISION")
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = folder / name
        if not target.exists():
            with target.open("xb") as stream:
                stream.write(data)
        if target.read_bytes() != data:
            raise ValueError("GS0528_OUTPUT_READBACK")
    return folder / NAME


def updated_catalog(raw, manifest):
    root = ET.fromstring(raw)
    existing = [node for node in root if node.get("id") == ADDON]
    if (root.tag != "addons" or len(existing) != 1
            or existing[0].get("version") != LIVE_BASE_VERSION):
        raise ValueError("GS0528_CATALOG_BASE")
    manifest = re.sub(rb"^\s*<\?xml[^>]+>\s*", b"", manifest).strip()
    matcher = rb'<addon\b(?=[^>]*\bid="script\.gsmedia\.setup")[^>]*>.*?</addon>'
    new, count = re.subn(matcher, lambda _: manifest, raw, flags=re.S)
    if count != 1:
        raise ValueError("GS0528_CATALOG_ENTRY")
    updated = [node for node in ET.fromstring(new) if node.get("id") == ADDON]
    if len(updated) != 1 or ET.tostring(updated[0]).strip() != ET.tostring(ET.fromstring(manifest)):
        raise ValueError("GS0528_CATALOG_READBACK")
    return new


def updated_index(raw, href, size):
    old = href.replace(NAME, LIVE_BASE_NAME).encode("ascii")
    markers = [index for index, line in enumerate(raw.splitlines(keepends=True))
               if b'href="' + old + b'"' in line]
    if len(markers) != 1 or raw.count(b'href="' + old + b'"') != 1:
        raise ValueError("GS0528_INDEX_BASE")
    lines = raw.splitlines(keepends=True)
    index = markers[0]
    lines[index] = lines[index].replace(LIVE_BASE_NAME.encode("ascii"), NAME.encode("ascii"))
    lines[index] = lines[index].replace(b"Installer 0.5.26", b"Installer 0.5.28")
    if href == NAME:
        link = b'<a href="' + NAME.encode("ascii") + b'">' + NAME.encode("ascii") + b'</a>'
        if lines[index].count(link) != 1:
            raise ValueError("GS0528_NEODARK3_LINK")
        kb = str((size + 1023) // 1024).encode("ascii")
        lines[index] = re.sub(re.escape(link) + rb"\s+\d+K", lambda _: link + b" " + kb + b"K",
                              lines[index])
    return b"".join(lines)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def stage_release_plan(package, folder):
    """Write a sparse repository overlay outside the checkout, for review only."""
    folder = output_path(folder, release_plan=True)
    if folder.exists() and (not folder.is_dir() or any(folder.iterdir())):
        raise ValueError("GS0528_OUTPUT_COLLISION")
    package = Path(package)
    sidecar_path = package.with_suffix(".zip.sha256")
    if package.name != NAME or package.is_symlink() or sidecar_path.is_symlink():
        raise ValueError("GS0528_PACKAGE_SHA256")
    payload = package.read_bytes()
    sidecar = checksum(payload)
    if sidecar_path.read_bytes() != sidecar:
        raise ValueError("GS0528_PACKAGE_SHA256")
    entries = package_members(payload, VERSION)
    if payload != candidate_bytes():
        raise ValueError("GS0528_PACKAGE_PROVENANCE")
    digest = sha256(payload).hexdigest()
    baseline = {name: (ROOT / name).read_bytes() for name in LIVE_METADATA_SHA256}
    if {name: sha256(data).hexdigest() for name, data in baseline.items()} != LIVE_METADATA_SHA256:
        raise ValueError("GS0528_LIVE_BASE_SHA256")
    files = {}
    channels = {}
    for channel, paths in CHANNELS.items():
        catalog = paths["catalog"]
        md5_path = catalog + ".md5"
        if catalog not in files:
            raw = baseline[catalog]
            if baseline[md5_path].decode("ascii").strip() != md5(raw).hexdigest():
                raise ValueError("GS0528_CATALOG_BASE_MD5")
            update = updated_catalog(raw, entries[MANIFEST])
            files[catalog] = update
            files[md5_path] = (md5(update).hexdigest() + "\n").encode("ascii")
        sha_path = paths["zip"] + ".sha256"
        for target in (paths["zip"], sha_path):
            if (ROOT / target).exists() or (ROOT / target).is_symlink():
                raise ValueError("GS0528_LIVE_ASSET_COLLISION")
        files[paths["zip"]] = payload
        files[sha_path] = sidecar
        if "index" in paths:
            files[paths["index"]] = updated_index(baseline[paths["index"]], paths["href"], len(payload))
        channels[channel] = dict(paths, catalog_md5=md5_path, sha256_file=sha_path,
                                 catalog_version=VERSION)

    manifest_path = "online-test/manifest.json"
    manifest = json.loads(baseline[manifest_path])
    wizard = manifest["wizard"]
    if (wizard.get("version") != LIVE_BASE_VERSION
            or not wizard.get("main_installer_url", "").endswith("/" + LIVE_BASE_NAME)
            or "installer_0528" in manifest):
        raise ValueError("GS0528_UPDATE_METADATA_BASE")
    wizard.update(version=VERSION, status="REVIEW_ONLY_DEVICE_ACCEPTANCE_PENDING",
                  main_installer_url=wizard["main_installer_url"].removesuffix(LIVE_BASE_NAME) + NAME,
                  fix="Issue #496: bounded Kodi compatibility catalog retry and confirmed resume")
    manifest["zip_sha256"][ADDON] = digest
    manifest["installer_0528"] = {
        "release_identity": RELEASE_IDENTITY, "version": VERSION, "zip_sha256": digest,
        "channels": list(CHANNELS), "published": False, "device_acceptance_confirmed": False,
    }
    files[manifest_path] = json_bytes(manifest)
    plan = {
        "addon": ADDON, "version": VERSION, "release_identity": RELEASE_IDENTITY,
        "source_base": BASE_COMMIT, "base_package_sha256": BASE_SHA256,
        "live_base_version": LIVE_BASE_VERSION,
        "displaced_draft": 428, "published": False, "device_acceptance_confirmed": False,
        "package_sha256": digest, "package_bytes": len(payload), "package_members": len(entries),
        "channels": channels, "files": {path: sha256(data).hexdigest() for path, data in files.items()},
    }
    files["release-plan.json"] = json_bytes(plan)
    folder.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".gsmedia-0528-plan-", dir=folder.parent) as scratch:
        stage = Path(scratch) / "plan"
        for name, data in files.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if target.read_bytes() != data:
                raise ValueError("GS0528_OUTPUT_READBACK")
        stage.rename(folder)
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--release-plan-out", type=Path)
    args = parser.parse_args()
    result = build(args.out)
    print(result)
    if args.release_plan_out is not None:
        print(json.dumps(stage_release_plan(result, args.release_plan_out), indent=2, sort_keys=True))
