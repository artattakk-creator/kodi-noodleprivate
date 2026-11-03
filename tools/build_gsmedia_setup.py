"""Package the read-only GS Media Setup preview for a Kodi test device.

No addons.xml publishing, installer execution or profile changes.
"""
from pathlib import Path
import hashlib
import ast
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
         "resources/lib/setup_auto50.py",
         "resources/lib/setup_auto_ui50.py",
         "resources/lib/setup_catalog_0516.py",
         "resources/lib/setup_auto_store50.py",
         "resources/lib/setup_origin_guard52.py",
         "resources/lib/setup_bingie_apply.py", "resources/lib/setup_tmdb_apply.py",
         "resources/lib/setup_skin_activate_0511.py",
         "resources/lib/setup_finish_0512.py",
         "resources/lib/setup_bingie_merge_0513.py",
         "resources/lib/setup_patch.py",
         "resources/skinpatch/manifest.json",
         "resources/skinpatch/LICENSE.BINGIE",
         "resources/skinpatch/xml/IncludesHomeWidgets.xml",
         "resources/skinpatch/xml/IncludesHomeBingie.xml",
         "resources/skinpatch/shortcuts/overrides.xml",
         "resources/skinpatch/shortcuts/template.xml")

def validate_bundled_imports(source=SOURCE, files=FILES):
    """Fail release if any bundled Python imports a missing local setup_*.py.

    Source compilation alone cannot detect missing modules in the actual ZIP.
    This scans the same exact packaged files and their local Python imports.
    """
    source = Path(source)
    local_modules = {path.stem for path in
                     (source / "resources/lib").glob("setup_*.py")}
    shipped_modules = {
        Path(name).stem for name in files
        if name.startswith("resources/lib/") and name.endswith(".py")
    }
    missing = []
    for relative in files:
        if not relative.endswith(".py"):
            continue
        tree = ast.parse((source / relative).read_text(encoding="utf-8"),
                         filename=relative)
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[:1][0]]
            elif isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            for name in names:
                if name in local_modules and name not in shipped_modules:
                    missing.append((relative, name))
    if missing:
        raise ValueError("Unshipped local Python imports: " + repr(missing))
    return True


def build(target):
    metadata = ET.parse(SOURCE / "addon.xml").getroot()
    if metadata.get("id") != "script.gsmedia.setup" or metadata.get("version") != "0.5.17":
        raise ValueError("Unexpected or unreviewed wizard version")
    if any(not (SOURCE / relative).is_file() for relative in FILES):
        raise FileNotFoundError("Missing required GS Media wizard source file")
    validate_bundled_imports()
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    filename = "script.gsmedia.setup-0.5.17.zip"
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
        expected = {"script.gsmedia.setup/" + name for name in FILES}
        if set(archive.namelist()) != expected:
            raise ValueError("ZIP contains missing, unexpected or duplicate files")
        if "script.gsmedia.setup/resources/lib/setup_catalog_0516.py" not in expected:
            raise ValueError("Required Kodi catalog module absent from ZIP")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    (target / (filename + ".sha256")).write_text(digest + "  " + filename + "\n", encoding="ascii")
    print(str(output))
    print("SHA256 " + digest)

if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".build" / "gsmedia-setup")
