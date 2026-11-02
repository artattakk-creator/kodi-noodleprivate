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
FILES = ("addon.xml", "default.py", "README.md",
         "resources/lib/setup_plan.py", "resources/lib/setup_inventory.py",
         "resources/lib/setup_gate.py", "resources/lib/setup_layout.py")

def build(target):
    metadata = ET.parse(SOURCE / "addon.xml").getroot()
    if metadata.get("id") != "script.gsmedia.setup" or metadata.get("version") != "0.2.2":
        raise ValueError("Unexpected or unreviewed wizard version")
    if any(not (SOURCE / relative).is_file() for relative in FILES):
        raise FileNotFoundError("Missing required GS Media wizard source file")
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    filename = "script.gsmedia.setup-0.2.2.zip"
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
