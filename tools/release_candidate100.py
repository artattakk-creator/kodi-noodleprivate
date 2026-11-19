"""Build a local, private XCMate test candidate from a committed source tree."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from package_xcmate71 import build, inspect_package

ROOT = Path(__file__).resolve().parents[1]
ADDON = "plugin.video.xtreammate"
VERSION = "0.1.29.100"
BASE = "b1e4cfb8e3b4812e866c8ac340feeb22c17030f6"
ASSET = "resources/media/hero88/xcmate_epg_default_hero_original.png"
ASSET_SHA = "8f836ef0eaa73d40410b5391e2661e01dcbfa33027146b03f460942a8deb820e"
PROTECTED = ("addons.xml", "addons.xml.md5", "online-test", "testversionen",
             "repository-programme", "repository.gsmedia", "src/repository.gsmedia",
             "src/script.gsmedia.setup", "script.gsmedia.setup", ".release")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def stage(output, original):
    output = Path(output).absolute()
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("CANDIDATE_OUTPUT_SYMLINK")
    target = output.resolve()
    if target == ROOT or ROOT in target.parents or target in ROOT.parents:
        raise ValueError("CANDIDATE_PRIVATE_OUTPUT_REQUIRED")
    asset = Path(original)
    if asset.is_symlink() or not asset.is_file() or asset.stat().st_size != 1_529_639:
        raise ValueError("CANDIDATE_ORIGINAL_REQUIRED")
    data = asset.read_bytes()
    if sha256(data).hexdigest() != ASSET_SHA:
        raise ValueError("CANDIDATE_ORIGINAL_HASH")
    commit = git("rev-parse", "HEAD").decode().strip()
    if (git("diff", "--name-only", BASE, "--", *PROTECTED)
            or git("diff", "--cached", "--name-only", "--", "src/" + ADDON)
            or git("diff", "--name-only", "--", "src/" + ADDON)):
        raise ValueError("CANDIDATE_SOURCE_OR_PUBLICATION_CHANGED")
    source = "src/" + ADDON
    files = git("ls-tree", "-r", "-z", commit, "--", source).split(b"\0")
    expected = {}
    name = f"{ADDON}-{VERSION}.zip"
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    for path in (target / name, target / (name + ".sha256")):
        if path.is_symlink() or path.exists():
            raise ValueError("CANDIDATE_OUTPUT_ALREADY_PRESENT")
    with tempfile.TemporaryDirectory(prefix=".xcmate-candidate-", dir=target) as folder:
        folder = Path(folder)
        tree = folder / "source"
        for item in filter(None, files):
            properties, filename = item.split(b"\t", 1)
            mode, kind, git_hash = properties.decode("ascii").split()
            rel = Path(filename.decode("utf-8")).relative_to(source)
            parts = {part.lower() for part in rel.parts}
            if (mode not in ("100644", "100755") or kind != "blob"
                    or "private" in parts or "userdata" in parts or "__pycache__" in parts
                    or rel.name.lower() in ("portals.json", "favourites.xml", "favorites.xml",
                                            "tmdb_read_access_token.txt", "reader-token.txt",
                                            "xcmate_epg_read_token.txt", "epg-agent-read-token.txt")
                    or rel.suffix.lower() in (".sqlite", ".db", ".log", ".pem", ".key", ".env")
                    or (rel.name.lower() == "settings.xml" and rel.as_posix() != "resources/settings.xml")):
                raise ValueError("CANDIDATE_UNSAFE_SOURCE")
            blob = git("cat-file", "blob", git_hash)
            file = tree / rel
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(blob)
            expected[f"{ADDON}/{rel.as_posix()}"] = sha256(blob).hexdigest()
        file = tree / ASSET
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
        expected[f"{ADDON}/{ASSET}"] = ASSET_SHA
        build(folder, source=tree)
        proof = inspect_package(folder / name, expected, VERSION, "CANDIDATE100")
        for filename in (name, name + ".sha256"):
            file = folder / filename
            file.chmod(0o600)
            file.rename(target / filename)
    return dict(proof, status="PRIVATE_DEVELOPMENT_TEST_ONLY", original_hero=ASSET_SHA,
                commit=commit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-hero", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(stage(args.output, args.original_hero), sort_keys=True))
