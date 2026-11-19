"""Apply earlier release contracts to the exact .99 inputs behind this draft."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "b1e4cfb8e3b4812e866c8ac340feeb22c17030f6"
FIXTURE = Path(__file__).with_name("fixtures") / "stabilization_029100_hashes.json"
_temp = None


@lru_cache(maxsize=1)
def hashes():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@lru_cache(maxsize=128)
def original(name):
    return subprocess.check_output(["git", "show", BASE + ":" + name], cwd=ROOT)


def without100(source, module):
    binary = isinstance(source, bytes)
    data = source if binary else source.encode("utf-8")
    digest = sha256(data).hexdigest()
    for name, expected in hashes()["changed"].items():
        if module in (name, Path(name).name, Path(name).stem) and digest == expected:
            before = original(name)
            return before if binary else before.decode("utf-8")
    return source


def runtime_without100(source):
    added = hashes()["added"]
    for name in source.keys() & added.keys():
        if sha256(source[name]).hexdigest() != added[name]:
            raise ValueError("UNREVIEWED100_ADDED_BYTES: " + name)
    return {name: without100(raw, name) for name, raw in source.items() if name not in added}


@lru_cache(maxsize=1)
def snapshot99():
    global _temp
    _temp = tempfile.TemporaryDirectory(prefix="xcmate-historical99-")
    repo = Path(_temp.name) / "repo"
    subprocess.run(["git", "clone", "--shared", "--quiet", "--no-checkout", str(ROOT), str(repo)], check=True)
    subprocess.run(["git", "checkout", "--quiet", "--detach", BASE], cwd=repo, check=True)
    return repo
