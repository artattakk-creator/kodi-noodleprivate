#!/usr/bin/env python3
"""Apply GPL XtreamMate 0.1.5 source changes once in repository CI.

The original TiViMate and users' Kodi addon_data are never changed.
All extra metadata, remote, EPG and widget tests run before publishing.
"""
import base64
import lzma
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PENDING = ROOT / ".release" / "xtreammate_0.1.5.patch.xz.b64"
ALLOW = ("src/plugin.video.xtreammate/", "tests/test_xtreammate_")

def update_once(path, needle, replacement):
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if replacement in text:
        return
    if needle not in text:
        raise RuntimeError("Unexpected existing source in " + str(path))
    file.write_text(text.replace(needle, replacement, 1), encoding="utf-8")

def main():
    if not PENDING.exists():
        return
    raw = base64.b64decode(PENDING.read_text(encoding="ascii").strip(), validate=True)
    patch = lzma.decompress(raw).decode("utf-8")
    for line in patch.splitlines():
        if line.startswith(("--- ", "+++ ")):
            filename = line[4:].split("\t", 1)[0].strip()
            if filename == "/dev/null":
                continue
            if not filename.startswith(("a/", "b/")):
                raise ValueError("Patch requires a/ and b/ source prefixes")
            rel = filename[2:]
            if (".." in Path(rel).parts or Path(rel).is_absolute()
                    or not rel.startswith(ALLOW)):
                raise ValueError("Unapproved XtreamMate release target: " + filename)
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "xtreammate-015.patch"
        file.write_text(patch, encoding="utf-8")
        subprocess.run(["patch", "--batch", "--forward", "--fuzz=0",
                        "-p1", "-i", str(file)], cwd=ROOT, check=True)
    update_once("src/plugin.video.xtreammate/addon.xml",
                'version="0.1.4"', 'version="0.1.5"')
    update_once("tests/test_repository_layout.py",
                'self.assertEqual(addon.get("version"), "0.1.4")',
                'self.assertEqual(addon.get("version"), "0.1.5")')
    readme = ROOT / "src/plugin.video.xtreammate/README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("# XtreamMate 0.1.4", "# XtreamMate 0.1.5", 1)
    text += """

## 0.1.5 – Player repair, newer titles, TV guide and BINGIE widgets

- Fixed Kodi on-video control creation and nonblocking on-video EPG.
- The Live-TV channel listing and overlay display cached 'Jetzt' and 'Danach'.
- Added 'Neueste Filme' and 'Neueste Serien' based on provider's added dates
  or locally observed genuinely new IDs (first scan sets baseline only).
- VOD and series posters show provider-supplied descriptions via Kodi metadata;
  use context menu 'Beschreibung und Details' for on-demand extended metadata.
- Valid provider YouTube trailer IDs offer the YouTube Kodi add-on link.
- Portal home -> BINGIE MOD Widgets -> choose an enabled channel category;
  in your BINGIE MOD skin settings use that category's folder as a widget.
  Widgets carry logos, possible EPG still images and now/next in ListItem.Plot.
  Skin hover appearance depends on BINGIE MOD widget layout; no live preview.
- Existing IPTV portal/userdata/settings are not reset or overwritten.

Kodi's on-device keymap needs enabling and restart; remote/skin behaviour
must be tested on the actual Kodi box.
"""
    readme.write_text(text, encoding="utf-8")
    # Kodi CI stores addon sources under src/, while local release testing
    # stages the addon at the root. Keep the same tests valid in both layouts.
    for testname in ("test_xtreammate_latest.py",
                     "test_xtreammate_overlay.py",
                     "test_xtreammate_widgets.py"):
        path = ROOT / "tests" / testname
        data = path.read_text(encoding="utf-8")
        data = data.replace("'plugin.video.xtreammate",
                            "'src/plugin.video.xtreammate")
        path.write_text(data, encoding="utf-8")
    PENDING.unlink()
    print("Applied XtreamMate 0.1.5 EPG, movie details, YouTube trailers and widgets")

if __name__ == "__main__":
    main()
