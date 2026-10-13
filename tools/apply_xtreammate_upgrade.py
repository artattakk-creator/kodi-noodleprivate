#!/usr/bin/env python3
"""Apply the one-time XtreamMate v0.1.1 source fix before the normal Kodi build.

This step is repeatable: it exits immediately after the pending patch is consumed.
"""
import base64
import lzma
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PENDING = ROOT / ".release" / "xtreammate_0.1.1.patch.xz.b64"

def main():
    if not PENDING.exists():
        return
    payload = lzma.decompress(base64.b64decode(
        PENDING.read_text(encoding="ascii").strip(), validate=True))
    text = payload.decode("utf-8")
    for line in text.splitlines():
        if line.startswith(("--- ", "+++ ")):
            name = line[4:].split("\t", 1)[0].strip()
            if name == "/dev/null":
                continue
            if not ((name.startswith("a/src/plugin.video.xtreammate/") or
                     name.startswith("b/src/plugin.video.xtreammate/") or
                     name in ("a/tests/test_xtreammate_persistence.py",
                              "b/tests/test_xtreammate_persistence.py")) and
                    ".." not in Path(name).parts):
                raise ValueError("Unexpected patch destination: " + name)
    with tempfile.TemporaryDirectory() as tmp:
        temp_patch = Path(tmp) / "xtreammate_fix.patch"
        temp_patch.write_bytes(payload)
        subprocess.run(["patch", "--batch", "--forward", "--fuzz=0",
                        "-p1", "-i", str(temp_patch)], cwd=ROOT, check=True)
    PENDING.unlink()
    print("Applied XtreamMate 0.1.1 portal persistence and group controls")

if __name__ == "__main__":
    main()
