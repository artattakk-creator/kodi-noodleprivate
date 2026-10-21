#!/usr/bin/env python3
"""Mirror two selected, official Kodi Omega addons into the GS Media catalogue.

Build-host only: Kodi devices use resulting GS Media ZIPs, not additional repo
addons. Version pins change only after an explicit source/license/QA review.
"""
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import re
import stat
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

BASE = "https://mirrors.kodi.tv/addons/omega"
APPROVED = (
    ("plugin.video.plutotv", "1.6.2"),
    ("plugin.audio.shoutcast", "2.5.2+matrix.1"),
)
MAX_DOWNLOAD = 8 * 1024 * 1024
MAX_FILE = 7 * 1024 * 1024
MAX_TOTAL = 40 * 1024 * 1024
MAX_ITEMS = 400


def upstream_url(addon_id, version):
    if (addon_id, version) not in APPROVED:
        raise ValueError("Unapproved Kodi add-on or version")
    return f"{BASE}/{addon_id}/{addon_id}-{version}.zip"


def download(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "GS-Media-Kodi-Repository/1.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Unencrypted Kodi mirror transport")
        payload = response.read(MAX_DOWNLOAD + 1)
    if len(payload) > MAX_DOWNLOAD:
        raise ValueError("Kodi source archive exceeds download budget")
    return payload


def validate(payload, addon_id, version):
    if (addon_id, version) not in APPROVED:
        raise ValueError("Unapproved Kodi add-on or version")
    if not isinstance(payload, bytes) or len(payload) > MAX_DOWNLOAD:
        raise ValueError("Kodi source archive exceeds download budget")
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError("Invalid upstream ZIP") from exc
    with archive:
        members = archive.infolist()
        if len(members) > MAX_ITEMS:
            raise ValueError("Too many ZIP entries")
        files, total = set(), 0
        for item in members:
            path = PurePosixPath(item.filename)
            if (path.is_absolute() or ".." in path.parts or
                    "\\" in item.filename or ":" in item.filename or
                    not path.parts or path.parts[0] != addon_id or
                    "\x00" in item.filename):
                raise ValueError("Unsafe or foreign add-on ZIP path")
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("Symlinks are forbidden")
            if item.is_dir():
                continue
            if item.filename in files:
                raise ValueError("Duplicate add-on path")
            files.add(item.filename)
            if item.file_size > MAX_FILE:
                raise ValueError("Oversized add-on file")
            total += item.file_size
            if total > MAX_TOTAL:
                raise ValueError("Oversized unpacked package")
        manifest_path = addon_id + "/addon.xml"
        if manifest_path not in files:
            raise ValueError("Missing add-on manifest")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC failure")
        manifest = ET.fromstring(archive.read(manifest_path))
    if (manifest.tag != "addon" or manifest.get("id") != addon_id or
            manifest.get("version") != version):
        raise ValueError("Upstream add-on/version mismatch")
    dependencies = {
        e.get("addon"): e.get("version")
        for e in manifest.findall("./requires/import")
    }
    if not dependencies.get("xbmc.python", "").startswith("3."):
        raise ValueError("Kodi Python 3 requirement missing")
    if manifest.find("./extension[@point='xbmc.addon.metadata']") is None:
        raise ValueError("Add-on license/metadata missing")
    return ET.tostring(manifest, encoding="unicode")


def import_selected(root, provider=download):
    root = Path(root)
    entries, pending = [], []
    for addon_id, version in APPROVED:
        payload = provider(upstream_url(addon_id, version))
        manifest = validate(payload, addon_id, version)
        target = root / addon_id / f"{addon_id}-{version}.zip"
        pending.append((target, payload))
        entries.append(manifest)
    # All inputs validated before any files/index are written.
    for target, payload in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".zip.pending")
        try:
            temporary.write_bytes(payload)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        target.with_name(target.name + ".sha256").write_text(
            hashlib.sha256(payload).hexdigest() + "  " + target.name + "\n",
            encoding="ascii")
    return entries


if __name__ == "__main__":
    from pathlib import Path
    home = Path(__file__).resolve().parents[1]
    result = import_selected(home)
    print("Added to local GS Media test index:", len(result), "official Kodi addons")
