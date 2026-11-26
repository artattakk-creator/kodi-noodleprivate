#!/usr/bin/env python3
"""NeoDark3 exactly-one-XCMate ZIP and Pilot catalog/sidecar release contract."""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ONLINE = ROOT / "online-test"
ADDON = "plugin.video.xtreammate"
NAME = "plugin.video.xtreammate-0.1.29.100.zip"
SHA = "9fbea224f9417193b85f8b57a390653eb4d77aeff85196973f3520d51acb26de"
SINGLE = re.compile(r"plugin\.video\.xtreammate-\d+\.\d+\.\d+\.\d+\.zip$")
PACKAGE = re.compile(SINGLE.pattern.removesuffix("$") + r"(?:\.sha256)?")
PRIVATE_BOOTSTRAP = ("https://github.com/artattakk-creator/xcmate-epg-private/"
                     "actions/workflows/build-xcmate-private-pilot.yml")


def verify():
    raw = (ONLINE / "addons.xml").read_bytes()
    assert hashlib.md5(raw).hexdigest() == (ONLINE / "addons.xml.md5").read_text().strip(), "CATALOG_MD5"
    root = ET.fromstring(raw)
    addons = [x for x in root.findall("addon") if x.get("id") == "plugin.video.xtreammate"]
    assert len(addons) == 1 and addons[0].get("version") == "0.1.29.100", "PILOT_VERSION"
    installer = [x for x in root.findall("addon") if x.get("id") == "script.gsmedia.setup"]
    assert len(installer) == 1 and installer[0].get("version") == "0.5.27", "INSTALLER_CATALOG_NOT_CHANGED"
    direct = [p.name for p in ONLINE.iterdir() if p.is_file() and SINGLE.fullmatch(p.name)]
    assert direct == [NAME], "NEODARK3_LATEST_ONLY"
    for folder in (ONLINE, ONLINE / "plugin.video.xtreammate"):
        data = (folder / NAME).read_bytes()
        assert len(data) == 6055446 and hashlib.sha256(data).hexdigest() == SHA, "ZIP_SHA256"
        assert (folder / (NAME + ".sha256")).read_text().strip() == SHA + "  " + NAME, "CHECKSUM_FILE"
    manifest = json.loads((ONLINE / "manifest.json").read_text())
    entry = manifest.get("xcmate100", {})
    assert entry.get("channels") == ["pilot", "neodark3"] and entry.get("sha256") == SHA, "MANIFEST_RECORD"
    assert manifest["zip_sha256"]["plugin.video.xtreammate"] == SHA, "MANIFEST_CURRENT_SHA"
    index = (ONLINE / "index.html").read_text(encoding="utf-8")
    links = re.findall(r'<a\s+href="([^"]+)"', index)
    required = [
        NAME, NAME + ".sha256", "repository.gsmedia.pilot-1.9.12.zip",
        "repository.gsmedia-1.8.1.zip", "script.gsmedia.setup-0.5.26.zip",
        "script.gsmedia.setup-0.5.27.zip", "script.gsmedia.setup-0.5.27.zip.sha256",
        "script.gsmedia.setup-0.5.28.zip", "script.gsmedia.setup-0.5.28.zip.sha256",
    ]
    assert set(links) == set(required) and len(links) == len(required), "NEODARK3_LINKS"
    assert all((ONLINE / link).exists() for link in required), "NEODARK3_LINK_TARGETS"
    assert "0.1.29.100" in index and "PRIVATE_PENDING" in index, "USER_NOTICE"
    assert entry.get("user_approved_regular_release") is False, "RELEASE_SCOPE"
    regular = ET.fromstring((ROOT / "addons.xml").read_bytes())
    assert not any(x.get("version") == "0.1.29.100" for x in regular.findall("addon") if x.get("id") == "plugin.video.xtreammate"), "REGULAR_UNCHANGED"
    print("PASS XCMate .100 Pilot and NeoDark3 | 6055446 bytes | SHA256 " + SHA)


class IndexLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = Counter()
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attributes):
        if tag == "a":
            self.links.update(value for name, value in attributes if name == "href" and value)


def require(condition, code):
    if not condition:
        raise ValueError(code)


def canonical(node):
    return ET.canonicalize(ET.tostring(node), strip_text=True)


def version_tuple(version):
    return tuple(int(part) for part in version.split("."))


def verify_release(root, baseline, version, sha256):
    """Check a staged distribution tree against an immutable main and reviewed ZIP."""
    require(re.fullmatch(r"[0-9a-f]{40}", baseline), "BASELINE_COMMIT")
    require(re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", version), "EXPECTED_VERSION")
    require(re.fullmatch(r"[0-9a-f]{64}", sha256), "EXPECTED_SHA256")
    root = Path(root).resolve()
    online = root / "online-test"
    name = f"{ADDON}-{version}.zip"
    sidecar = name + ".sha256"

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    def previous(filename):
        return git("show", f"{baseline}:online-test/{filename}")

    metadata = {"addons.xml", "addons.xml.md5", "index.html", "manifest.json"}
    replaceable = {p for p in git("ls-tree", "--name-only", f"{baseline}:online-test").decode().splitlines()
                   if PACKAGE.fullmatch(p)}
    outputs = metadata | {name, sidecar, f"{ADDON}/{name}", f"{ADDON}/{sidecar}"}
    allowed = {"online-test/" + p for p in outputs | replaceable}
    diff = git("diff", "--no-ext-diff", "--name-only", "--no-renames", "-z", baseline, "--")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z")
    changed = set((diff + untracked).decode().split("\0")) - {""}
    require(changed <= allowed, "UNRELATED_RELEASE_CHANGES: " + ", ".join(sorted(changed - allowed)))
    require(all((online / p).is_file() and not (online / p).is_symlink() for p in outputs)
            and not (online / ADDON).is_symlink(), "NOT_A_REGULAR_RELEASE_FILE")

    raw = (online / "addons.xml").read_bytes()
    require(hashlib.md5(raw).hexdigest() == (online / "addons.xml.md5").read_text().strip(), "CATALOG_MD5")
    catalog = ET.fromstring(raw)
    before_catalog = ET.fromstring(previous("addons.xml"))
    def remove_xcmate(tree):
        matches = tree.findall(f"addon[@id='{ADDON}']")
        require(len(matches) == 1, "CATALOG_XCMATE_UNIQUE")
        tree.remove(matches[0])
        return matches[0]

    current_xcmate = remove_xcmate(catalog)
    old_xcmate = remove_xcmate(before_catalog)
    require(current_xcmate.get("version") == version, "PILOT_VERSION")
    require(version_tuple(version) > version_tuple(old_xcmate.attrib["version"]), "PILOT_VERSION_NOT_NEWER")
    require(canonical(catalog) == canonical(before_catalog), "UNRELATED_CATALOG_CHANGED")

    direct = {p.name for p in online.iterdir() if PACKAGE.fullmatch(p.name)}
    require(direct == {name, sidecar}, "NEODARK3_LATEST_ONLY")
    flat = (online / name).read_bytes()
    require(sha256 == hashlib.sha256(flat).hexdigest(), "ZIP_SHA256")
    require(flat == (online / ADDON / name).read_bytes(), "PILOT_NEODARK3_ZIP_MISMATCH")
    for folder in (online, online / ADDON):
        require((folder / sidecar).read_text().strip() == f"{sha256}  {name}", "CHECKSUM_FILE")
    with ZipFile(io.BytesIO(flat)) as package:
        names = package.namelist()
        require(len(names) == len(set(names)) and package.testzip() is None, "ZIP_INVALID")
        addon = ET.fromstring(package.read(f"{ADDON}/addon.xml"))
        require((addon.get("id"), addon.get("version")) == (ADDON, version), "ZIP_ADDON_ID_VERSION")

        def library_metadata(node):
            return [extension.attrib for extension in node.findall("extension")]

        package_requires = addon.find("requires")
        catalog_requires = current_xcmate.find("requires")
        require(addon.attrib == current_xcmate.attrib
                and package_requires is not None and catalog_requires is not None
                and canonical(package_requires) == canonical(catalog_requires)
                and library_metadata(addon) == library_metadata(current_xcmate),
                "PILOT_PACKAGE_METADATA")

    manifest = json.loads((online / "manifest.json").read_text())
    before_manifest = json.loads(previous("manifest.json"))
    key = "xcmate" + version.rsplit(".", 1)[1]
    require(key not in before_manifest, "MANIFEST_VERSION_ALREADY_PRESENT")
    entry = manifest.pop(key)
    expected = {"version": version, "sha256": sha256, "bytes": len(flat), "channels": ["pilot", "neodark3"],
                "pilot_zip": f"online-test/{ADDON}/{name}", "neodark3_zip": f"online-test/{name}",
                "user_approved_regular_release": False}
    require(all(entry.get(field) == value for field, value in expected.items()), "MANIFEST_RECORD")
    require(manifest["zip_sha256"].pop(ADDON) == sha256, "MANIFEST_CURRENT_SHA")
    before_manifest["zip_sha256"].pop(ADDON)
    require(manifest == before_manifest, "UNRELATED_MANIFEST_CHANGED")

    html = (online / "index.html").read_text(encoding="utf-8")
    links = IndexLinks(html).links
    require({p: n for p, n in links.items() if PACKAGE.fullmatch(p)} == {name: 1, sidecar: 1}, "NEODARK3_LINKS")
    before_links = IndexLinks(previous("index.html").decode()).links

    def without_xcmate(links):
        return {p: n for p, n in links.items() if not PACKAGE.fullmatch(p) and p != PRIVATE_BOOTSTRAP}

    require(without_xcmate(links) == without_xcmate(before_links), "UNRELATED_LINKS_CHANGED")
    require(PRIVATE_BOOTSTRAP not in links and version in html and "PUBLIC_READY" in html, "USER_NOTICE")
    require(all((online / p).is_file() for p in links if not urlsplit(p).scheme), "NEODARK3_LINK_TARGETS")
    print(f"PASS XCMate {version} Pilot and NeoDark3 | {len(flat)} bytes | SHA256 {sha256}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Distribution worktree to verify")
    parser.add_argument("--baseline", help="Exact main commit prior to distribution")
    parser.add_argument("--version", help="Reviewed package version")
    parser.add_argument("--sha256", help="Reviewed package SHA256")
    args = parser.parse_args()
    try:
        if args.baseline or args.version or args.sha256 or args.root != ROOT:
            if not all((args.baseline, args.version, args.sha256)):
                parser.error("--baseline, --version and --sha256 are required together")
            verify_release(args.root, args.baseline, args.version, args.sha256)
        else:
            verify()
    except (AssertionError, BadZipFile, KeyError, ValueError, OSError, ET.ParseError, subprocess.CalledProcessError) as exc:
        print("FAIL NeoDark3 release: " + str(exc), file=sys.stderr)
        sys.exit(1)
