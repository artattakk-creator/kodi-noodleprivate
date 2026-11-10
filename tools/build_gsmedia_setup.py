"""Package the read-only GS Media Setup preview for a Kodi test device.

No addons.xml publishing, installer execution or profile changes.
"""
from pathlib import Path
import hashlib
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "script.gsmedia.setup"
FILES = ("addon.xml", "default.py", "service.py", "README.md",
         "resources/lib/setup_plan.py", "resources/lib/setup_inventory.py",
         "resources/lib/setup_gate.py", "resources/lib/setup_layout.py",
         "resources/lib/setup_handoff.py",
         "resources/lib/setup_tmdb_player.py",
         "resources/lib/setup_install_pilot.py",
         "resources/lib/setup_install_ui.py",
         "resources/lib/setup_full.py", "resources/lib/setup_full_ui.py",
         "resources/lib/setup_bingie_apply.py", "resources/lib/setup_tmdb_apply.py",
         "resources/lib/setup_patch.py",
         "resources/skinpatch/manifest.json",
         "resources/skinpatch/LICENSE.BINGIE",
         "resources/skinpatch/xml/IncludesHomeWidgets.xml",
         "resources/skinpatch/xml/IncludesHomeBingie.xml",
         "resources/skinpatch/shortcuts/overrides.xml",
         "resources/skinpatch/shortcuts/template.xml")

def build(target):
    metadata = ET.parse(SOURCE / "addon.xml").getroot()
    if metadata.get("id") != "script.gsmedia.setup" or metadata.get("version") != "0.4.0":
        raise ValueError("Unexpected or unreviewed wizard version")
    if any(not (SOURCE / relative).is_file() for relative in FILES):
        raise FileNotFoundError("Missing required GS Media wizard source file")
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    filename = "script.gsmedia.setup-0.4.0.zip"
    output = target / filename
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in FILES:
            entry = zipfile.ZipInfo("script.gsmedia.setup/" + relative, date_time=(2020, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, (SOURCE / relative).read_bytes())
    with zipfile.ZipFile(output, "r") as archive:
        if archive.testzip() or len(archive.namelist()) != len(FILES):
            raise ValueError("Broken or incomplete wizard ZIP")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    (target / (filename + ".sha256")).write_text(digest + "  " + filename + "\n", encoding="ascii")
    print(str(output))
    print("SHA256 " + digest)

if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".build" / "gsmedia-setup")
