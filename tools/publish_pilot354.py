"""Issue #354: publish exactly two tested packages in the EXISTING Pilot feed.

No Kodi execution, installer invocation, repository replacement or user data.
Use --stage before committing; --public verifies the actual unmodified Kodi URLs.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import time
import urllib.request
import zipfile
from xml.etree import ElementTree as ET

from package_xcmate71 import build as build_xcmate
from build_setup352_update import build as build_setup

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/"
PACKAGES = {
    "plugin.video.xtreammate": ("0.1.29.71", "ebebf3c9cdb00b8730da436bfb7bd8909a8a5cdfd23ee36b61afa99f775a9a4d"),
    "script.gsmedia.setup": ("0.5.20", "568a76b67d80d846ea09176d0ea1b9f6b6fed1fd86c2ace79ca865b4a8ccadbd"),
}
REPO = "repository.gsmedia.pilot/repository.gsmedia.pilot-1.9.12.zip"
REPO_SHA = "57ee7166f0caca2071e6fd36fed76e5660d9dc6f221d8c78d4e259d66a507489"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def entries(data):
    root = ET.fromstring(data)
    found = {item.get("id"): item for item in root}
    if len(found) != len(root):
        raise ValueError("DUPLICATE_ADDON_IDS")
    return found


def package_path(addon):
    return f"{addon}/{addon}-{PACKAGES[addon][0]}.zip"


def inspect_package(addon, data):
    version, digest = PACKAGES[addon]
    assert sha(data) == digest, "TESTED_PACKAGE_CHANGED"
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.testzip() is None
        assert all(name.startswith(addon + "/") and ".." not in Path(name).parts
                   for name in archive.namelist())
        manifest = archive.read(addon + "/addon.xml")
        node = ET.fromstring(manifest)
        assert node.get("id") == addon and node.get("version") == version
        return manifest, {name[len(addon) + 1:]: archive.read(name)
                          for name in archive.namelist() if not name.endswith("/")}


def stage(root=ROOT):
    channel = root / "online-test"
    before = (channel / "addons.xml").read_bytes()
    old = entries(before)
    assert sha((channel / REPO).read_bytes()) == REPO_SHA
    manifest = json.loads((channel / "manifest.json").read_text())
    updated = before.decode("utf-8")
    with tempfile.TemporaryDirectory(prefix="pilot354-") as folder:
        build_xcmate(folder)
        build_setup(folder)
        for addon, (version, digest) in PACKAGES.items():
            path = Path(folder) / Path(package_path(addon)).name
            data = path.read_bytes()
            xml, files = inspect_package(addon, data)
            block = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", xml.decode("utf-8")).strip()
            pattern = r'<addon\b(?=[^>]*\bid="' + re.escape(addon) + r'")[^>]*>.*?</addon>'
            updated, count = re.subn(pattern, lambda _: block, updated, flags=re.S)
            assert count == 1, "INDEX_ENTRY_NOT_UNIQUE"
            target = channel / package_path(addon)
            target.parent.mkdir(exist_ok=True)
            # Never silently replace an existing version with different bytes.
            assert not target.exists() or target.read_bytes() == data
            target.write_bytes(data)
            target.with_suffix(".zip.sha256").write_text(digest + "  " + target.name + "\n")
            for asset in ET.fromstring(xml).findall("./extension/assets/*"):
                if asset.text and "://" not in asset.text:
                    relative = Path(asset.text)
                    assert not relative.is_absolute() and ".." not in relative.parts
                    asset_path = channel / addon / relative
                    if not asset_path.exists():
                        asset_path.parent.mkdir(parents=True, exist_ok=True)
                        asset_path.write_bytes(files[asset.text])
            manifest["zip_sha256"][addon] = digest
    after = updated.encode("utf-8")
    current = entries(after)
    assert old.keys() == current.keys()
    assert all(ET.tostring(old[k]) == ET.tostring(current[k])
               for k in old.keys() - PACKAGES.keys()), "UNRELATED_INDEX_CHANGED"
    (channel / "addons.xml").write_bytes(after)
    (channel / "addons.xml.md5").write_text(hashlib.md5(after).hexdigest() + "\n")
    manifest["wizard"]["version"] = "0.5.20"
    manifest["wizard"]["status"] = "PILOT_INCREMENTAL_354_ANDROID_NOT_TESTED"
    manifest["incremental_update_354"] = {
        "source_merge": "f0a1bb40050e89e0220687722273e7cc859b9b5b",
        "source_ci": "https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/41723976215",
        "repository_id": "repository.gsmedia.pilot", "repository_version": "1.9.12",
        "index_url": BASE + "addons.xml", "installer_restarted": False,
        "android": "NOT_TESTED", "packages": {
            addon: {"version": version, "sha256": digest, "url": BASE + package_path(addon)}
            for addon, (version, digest) in PACKAGES.items()}}
    # Older global source_* fields describe the retained third-party baseline.
    (channel / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return verify_local(root)


def verify(fetch):
    index = fetch("addons.xml")
    assert fetch("addons.xml.md5").decode().strip() == hashlib.md5(index).hexdigest()
    nodes = entries(index)
    repository = fetch(REPO)
    assert sha(repository) == REPO_SHA
    with zipfile.ZipFile(io.BytesIO(repository)) as archive:
        repo = ET.fromstring(archive.read("repository.gsmedia.pilot/addon.xml"))
    assert repo.get("id") == "repository.gsmedia.pilot" and repo.get("version") == "1.9.12"
    assert repo.findtext("./extension/dir/info") == BASE + "addons.xml"
    assert repo.findtext("./extension/dir/checksum") == BASE + "addons.xml.md5"
    assert repo.findtext("./extension/dir/datadir") == BASE
    result = {"index_md5": hashlib.md5(index).hexdigest(), "index_entries": len(nodes),
              "repository": "repository.gsmedia.pilot 1.9.12 unchanged", "packages": {},
              "android": "NOT_TESTED", "installer_executed": False}
    for addon, (version, digest) in PACKAGES.items():
        path = package_path(addon)
        data = fetch(path)
        xml, _ = inspect_package(addon, data)
        assert ET.tostring(nodes[addon]).strip() == ET.tostring(ET.fromstring(xml)).strip()
        assert fetch(path + ".sha256").decode().split() == [digest, Path(path).name]
        for asset in ET.fromstring(xml).findall("./extension/assets/*"):
            if asset.text and "://" not in asset.text:
                assert fetch(addon + "/" + asset.text)
        result["packages"][addon] = {"version": version, "sha256": digest,
                                     "bytes": len(data), "url": BASE + path, "crc": "PASS"}
    return result


def verify_local(root=ROOT):
    return verify(lambda path: (root / "online-test" / path).read_bytes())


def verify_public():
    def fetch(path):
        with urllib.request.urlopen(BASE + path, timeout=30) as response:
            assert response.status == 200
            return response.read(16 * 1024 * 1024)
    for attempt in range(12):
        try:
            result = verify(fetch)
            result["public_channel"] = "PASS"
            return result
        except (AssertionError, OSError, ValueError, ET.ParseError):
            if attempt == 11:
                raise
            time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    print(json.dumps(stage() if args.stage else verify_public() if args.public else verify_local(), indent=2))
