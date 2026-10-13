#!/usr/bin/env python3
"""Apply the vetted GPL XtreamMate 0.1.2 source patch once, then delete it.

The 0.1.2 delta applies to committed XtreamMate 0.1.1 sources before building.
GitHub Actions commits the resulting open-source files and output ZIP.
"""
import base64
import lzma
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PENDING = ROOT / ".release" / "xtreammate_0.1.2.patch.xz.b64"

def main():
    if not PENDING.exists():
        return
    payload = lzma.decompress(base64.b64decode(
        PENDING.read_text(encoding="ascii").strip(), validate=True))
    patch = payload.decode("utf-8")
    for line in patch.splitlines():
        if line.startswith(("--- ", "+++ ")):
            path = line[4:].split("\t", 1)[0].strip()
            if path == "/dev/null":
                continue
            if (not path.startswith(("a/src/plugin.video.xtreammate/",
                                     "b/src/plugin.video.xtreammate/"))
                    or ".." in Path(path).parts):
                raise ValueError("Unexpected source patch destination: " + path)
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "xtreammate012.patch"
        source.write_bytes(payload)
        subprocess.run(["patch", "--batch", "--forward", "--fuzz=0",
                        "-p1", "-i", str(source)], cwd=ROOT, check=True)
    PENDING.unlink()
    print("XtreamMate 0.1.2: remote zapping, OSD and startup preferences applied")

if __name__ == "__main__":
    main()
