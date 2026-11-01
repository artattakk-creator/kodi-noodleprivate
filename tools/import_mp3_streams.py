#!/usr/bin/env python3
"""Safely add the pinned upstream MP3 Streams Echoed package at repository build.

This runs on a CI/build host, never on Kodi. It does not modify upstream code.
"""
import hashlib
import io
from pathlib import Path, PurePosixPath
import stat
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile

ADDON_ID = "plugin.audio.m3sr2019"
VERSION = "2026.1.0"
SOURCE = (
    "https://raw.githubusercontent.com/Echo-Storm/"
    "MP3-Streams-2026-Kodi/master/plugin_audio_m3sr2019-2026.1.0.zip"
)
# Pin of upstream GitHub release ZIP verified from the GitHub content API.
UPSTREAM_GIT_BLOB = "ebc7f51129fb24f7db0c9d85c8c5c03ec3f97929"
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_MEMBERS = 1000
MAX_UNPACKED = 256 * 1024 * 1024


def fetch_release():
    request = Request(SOURCE, headers={"User-Agent": "GS-Media-Kodi-Build/1.0"})
    with urlopen(request, timeout=25) as response:
        if response.url != SOURCE:
            raise ValueError("Unapproved upstream redirect")
        payload = response.read(MAX_DOWNLOAD + 1)
    return payload


def repackage(payload):
    if not isinstance(payload, bytes) or len(payload) > MAX_DOWNLOAD:
        raise ValueError("Upstream ZIP exceeds size budget")
    git_blob = hashlib.sha1(
        b"blob " + str(len(payload)).encode() + b"\0" + payload
    ).hexdigest()
    if git_blob != UPSTREAM_GIT_BLOB:
        raise ValueError("MP3 ZIP changed: re-review before publishing")

    with zipfile.ZipFile(io.BytesIO(payload)) as source:
        paths, unpacked = [], 0
        if len(source.infolist()) > MAX_MEMBERS:
            raise ValueError("Too many ZIP entries")
        for member in source.infolist():
            path = PurePosixPath(member.filename)
            if (path.is_absolute() or ".." in path.parts
                    or "\\" in member.filename or ":" in member.filename):
                raise ValueError("Unsafe ZIP filename")
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("ZIP symlink not allowed")
            if member.is_dir():
                continue
            if not path.parts or member.file_size > MAX_DOWNLOAD:
                raise ValueError("Unsafe entry size")
            unpacked += member.file_size
            if unpacked > MAX_UNPACKED:
                raise ValueError("Excessive ZIP uncompressed size")
            paths.append(path)

        prefixed = all(path.parts[0] == ADDON_ID for path in paths)
        files = {}
        for member in source.infolist():
            if member.is_dir():
                continue
            path = PurePosixPath(member.filename)
            normalized = path if prefixed else PurePosixPath(ADDON_ID) / path
            if normalized.parts[0] != ADDON_ID or len(normalized.parts) < 2:
                raise ValueError("Unrecognized ZIP layout")
            key = normalized.as_posix()
            if key in files:
                raise ValueError("Duplicate ZIP filename")
            files[key] = source.read(member)
        if source.testzip() is not None:
            raise ValueError("Upstream ZIP CRC failure")

    manifest_name = ADDON_ID + "/addon.xml"
    if manifest_name not in files:
        raise ValueError("Missing addon.xml")
    manifest = ET.fromstring(files[manifest_name])
    if (manifest.tag != "addon" or manifest.get("id") != ADDON_ID
            or manifest.get("version") != VERSION):
        raise ValueError("Upstream addon ID/version mismatch")
    deps = {
        (item.get("addon"), item.get("version"))
        for item in manifest.findall("./requires/import")
    }
    if not any(addon == "xbmc.python" and (version or "") >= "3.0.0"
               for addon, version in deps):
        raise ValueError("Kodi Python 3 dependency missing")
    if not any(path.endswith(".py") for path in files):
        raise ValueError("Redistributable Python source missing")
    if manifest.find("./extension[@point='xbmc.addon.metadata']") is None:
        raise ValueError("Missing addon metadata")

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for key, data in sorted(files.items()):
            item = zipfile.ZipInfo(key, date_time=(1980, 1, 1, 0, 0, 0))
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=8)
    return output.getvalue(), ET.tostring(manifest, encoding="unicode")


def add_to_repository(root, payload=None):
    original = fetch_release() if payload is None else payload
    normalized, manifest = repackage(original)
    destination = Path(root) / ADDON_ID / (ADDON_ID + "-" + VERSION + ".zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(normalized)
    destination.with_name(destination.name + ".sha256").write_text(
        hashlib.sha256(normalized).hexdigest() + "  " + destination.name + "\n",
        encoding="ascii",
    )
    return manifest
