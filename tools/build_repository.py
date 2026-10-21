#!/usr/bin/env python3
"""Build Kodi repository metadata and installable ZIPs; seed initial source once."""
import base64, hashlib, io, lzma, os, re, struct, tarfile, zipfile, zlib
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
IDS = tuple(d.name for d in sorted(SRC.iterdir()) if d.is_dir() and (d / "addon.xml").is_file())
# The former repository.noodleprivate is retired. Refuse to republish competing
# Kodi repositories, so Noodle Private has exactly one managed update source.
if "repository.gsmedia" not in IDS:
    raise RuntimeError("Missing central GS Media repository")
if any(name.startswith("repository.") and name != "repository.gsmedia" for name in IDS):
    raise RuntimeError("Only repository.gsmedia may be published (legacy repo must be removed)")

def apply_pending_release():
    """One-time, path-checked import of v0.3.0 sources; keeps Kodi user data untouched."""
    pending = ROOT / ".release" / "v0.3.0.tar.xz.b64"
    if not pending.exists():
        return
    data = base64.b64decode(pending.read_text(encoding="ascii"), validate=True)
    payload = lzma.decompress(data)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                raise ValueError("Only regular source files are allowed")
            rel = Path(member.name)
            allowed = (str(rel).startswith("src/plugin.video.noodleprivate/")
                       or str(rel).startswith("tests/"))
            if not allowed or rel.is_absolute() or ".." in rel.parts:
                raise ValueError("Invalid release path: " + member.name)
            target = (ROOT / rel).resolve()
            if not target.is_relative_to(ROOT.resolve()):
                raise ValueError("Archive escapes repository root")
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".release-tmp")
            with open(tmp, "wb") as f:
                f.write(archive.extractfile(member).read())
            os.replace(tmp, target)
    pending.unlink()

def seed():
    if not (SRC / "plugin.video.noodleprivate" / "default.py").exists():
        raise RuntimeError("Missing Kodi add-on sources under src/")
    # Original add-on assets refer to jpg, initial repository provides PNG placeholders.
    for addon in IDS:
        xml = SRC / addon / "addon.xml"
        data = xml.read_text(encoding="utf-8")
        # Keep a real packaged JPEG (XCMate); PNG fallback is for addons
        # whose original JPEG was absent and is generated below.
        if "fanart.jpg" in data and not (SRC / addon / "fanart.jpg").is_file():
            xml.write_text(data.replace("fanart.jpg", "fanart.png"), encoding="utf-8")
    entry = SRC/"plugin.video.noodleprivate"/"default.py"
    content = entry.read_text(encoding="utf-8")
    if "resources', 'fanart.jpg'" in content:
        entry.write_text(content.replace("resources', 'fanart.jpg'", "resources', 'fanart.png'"), encoding="utf-8")


def render_noodle_artwork():
    """Generate self-contained branded Kodi PNG assets from versioned renderer."""
    path = ROOT / ".artwork" / "noodle_0.4.1_renderer.py.xz.b64"
    if not path.exists():
        raise FileNotFoundError("Missing Noodle Private 0.4.1 artwork renderer")
    src = lzma.decompress(base64.b64decode(path.read_text(encoding="ascii"), validate=True))
    script_name = SRC / "plugin.video.noodleprivate" / "artwork-renderer.py"
    namespace = {"__file__": str(script_name), "__name__": "__main__"}
    exec(compile(src, str(script_name), "exec"), namespace)

def image(path, w, h):
    if path.exists(): return
    path.parent.mkdir(parents=True, exist_ok=True)
    def c(t,d): return len(d).to_bytes(4,"big")+t+d+(zlib.crc32(t+d)&0xffffffff).to_bytes(4,"big")
    scan = bytearray()
    for y in range(h):
        scan.append(0)
        for x in range(w): scan.extend((20+x*30//w,30+y*60//h,70+x*100//w,255))
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+c(b"IHDR",struct.pack("!2I5B",w,h,8,6,0,0,0))+c(b"IDAT",zlib.compress(bytes(scan),7))+c(b"IEND",b""))

def package_file(archive, addon, filename, member):
    """One canonical XCMate RC across local/CI builds; other addons unchanged."""
    if addon != 'plugin.video.xtreammate':
        archive.write(filename, member)
        return
    info=zipfile.ZipInfo(member, date_time=(1980,1,1,0,0,0))
    info.create_system=3
    info.external_attr=0o100644 << 16
    archive.writestr(info, filename.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=8)


def main():
    apply_pending_release()
    seed()
    render_noodle_artwork()
    image(SRC/"plugin.video.noodleprivate/resources/icon.png",256,256)
    image(SRC/"plugin.video.noodleprivate/resources/fanart.png",1280,720)
    for addon in IDS:
        if addon.startswith("repository."):
            image(SRC/addon/"icon.png",256,256)
            image(SRC/addon/"fanart.png",1280,720)
    entries = []
    for addon in IDS:
        xmlfile = SRC/addon/"addon.xml"
        xmlroot = ET.parse(xmlfile).getroot()
        assert xmlroot.tag=="addon" and xmlroot.attrib["id"]==addon
        version=xmlroot.attrib["version"]
        assert re.fullmatch(r"\d+(?:\.\d+){2,3}",version)
        content=xmlfile.read_text(encoding="utf-8").strip()
        entries.append(re.sub(r"^<\?xml[^>]*\?>\s*","",content))
        dest=ROOT/addon/f"{addon}-{version}.zip"
        dest.parent.mkdir(exist_ok=True, parents=True)
        with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as zf:
            for f in sorted((SRC/addon).rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":
                    package_file(zf,addon,f,(Path(addon)/f.relative_to(SRC/addon)).as_posix())
        with zipfile.ZipFile(dest) as zf:
            assert zf.testzip() is None and f"{addon}/addon.xml" in zf.namelist()
        if addon == 'plugin.video.xtreammate':
            # CI repacks ZIP timestamps: always hash this exact output archive.
            dest.with_name(dest.name+'.sha256').write_text(
                hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n')
        if addon.startswith("repository."):
            (ROOT/dest.name).write_bytes(dest.read_bytes())
            if addon == "repository.gsmedia":
                direct = ROOT / "repository-programme" / dest.name
                direct.parent.mkdir(parents=True, exist_ok=True)
                direct.write_bytes(dest.read_bytes())
    # Third-party music release; pinned, validated and packaged on build hosts only.
    # A download or hash error aborts the build instead of publishing a broken index.
    from import_mp3_streams import add_to_repository
    entries.append(add_to_repository(ROOT))
    from import_kodi_omega_selected import import_selected
    entries.extend(import_selected(ROOT))
    idx='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'+"\n".join(entries)+"\n</addons>\n"
    ET.fromstring(idx)
    (ROOT/"addons.xml").write_text(idx,encoding="utf-8")
    (ROOT/"addons.xml.md5").write_text(hashlib.md5(idx.encode("utf-8")).hexdigest()+"\n",encoding="ascii")
    print("Kodi index and installable ZIP packages built successfully")

if __name__=="__main__":
    main()
