"""Build and independently inspect the installable XCMate candidate ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from package_xcmate71 import ROOT, build, inspect_package

ADDON = "plugin.video.xtreammate"
VERSIONS = {"0.1.29.102", "0.1.29.103", "0.1.29.104"}
SOURCE = ROOT / "src" / ADDON
DATA_SUFFIXES = (".sqlite", ".db", ".xml.gz", ".sqlite-wal", ".db-wal", ".db-shm",
                 ".log", ".pyo", ".zip")
SENSITIVE = re.compile(
    rb"(?:github_pat_[A-Za-z0-9_]{22,}|gh[pousr]_[A-Za-z0-9]{24,}"
    rb"|https?://[^\s\"'<>/]+:[^\s\"'<>/]+@[^\s\"'<>/]+"
    rb"|https?://[^\s\"'<>]+[?&](?:username|password|token|api_key|access_token)=[A-Za-z0-9_%.-]+)",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".py", ".xml", ".json", ".txt", ".md", ".po", ".html", ".css",
                 ".yaml", ".yml", ".js", ".m3u", ".m3u8"}


def source_hashes(source):
    hashes = {}
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if ("__pycache__" in relative.parts or path.name == ".DS_Store"):
            continue
        if path.is_symlink() or "private" in relative.parts or path.name.startswith("."):
            raise ValueError("UNSAFE_PUBLIC_SOURCE_PATH")
        if path.is_dir():
            continue
        if not path.is_file() or path.name.endswith(DATA_SUFFIXES):
            raise ValueError("UNSAFE_PUBLIC_SOURCE_MEMBER")
        raw = path.read_bytes()
        if path.suffix.lower() in TEXT_SUFFIXES and SENSITIVE.search(raw):
            raise ValueError("POSSIBLE_CREDENTIAL_IN_PUBLIC_SOURCE " + relative.as_posix())
        hashes[f"{ADDON}/{relative.as_posix()}"] = hashlib.sha256(raw).hexdigest()
    return hashes


def build_public(output, source=SOURCE, *, version=None):
    source, output = Path(source), Path(output)
    node = ET.parse(source / "addon.xml").getroot()
    version = version or node.get("version")
    if version not in VERSIONS or (node.get("id"), node.get("version")) != (ADDON, version):
        raise ValueError("UNEXPECTED_PUBLIC_VERSION")
    expected = source_hashes(source)
    entries = [item.get("library") for item in node.findall("extension") if item.get("library")]
    assets = [item.text for item in node.findall("extension/assets/*") if item.text]
    if (not {"default.py", "service.py"}.issubset(entries)
            or not all(f"{ADDON}/{item}" in expected for item in entries + assets)
            or node.find("requires/import[@addon='xbmc.python']") is None):
        raise ValueError("PACKAGE_ENTRYPOINT_OR_ASSET_MISSING")

    output.mkdir(parents=True, exist_ok=True)
    filename = f"{ADDON}-{version}.zip"
    with TemporaryDirectory(prefix=".xcmate-public-", dir=output) as temp:
        temp = Path(temp)
        build(temp, source=source)
        result = inspect_package(temp / filename, expected, version, "PUBLIC_PACKAGE")
        for name in (filename, filename + ".sha256"):
            (temp / name).replace(output / name)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--version", choices=sorted(VERSIONS))
    args = parser.parse_args()
    print(json.dumps(build_public(args.output, version=args.version), sort_keys=True))
