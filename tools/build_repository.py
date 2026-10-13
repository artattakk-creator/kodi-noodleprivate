#!/usr/bin/env python3
"""Build Kodi repository metadata and installable ZIPs; seed initial source once."""
import base64, hashlib, io, lzma, re, struct, tarfile, zipfile, zlib
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
IDS = ("plugin.video.noodleprivate", "repository.noodleprivate")

def seed():
    archive = ROOT / "bootstrap.xz.b64"
    if not (SRC / "plugin.video.noodleprivate" / "default.py").exists():
        if not archive.is_file():
            raise RuntimeError("Missing initial source archive")
        payload = lzma.decompress(base64.b64decode(archive.read_text(encoding="ascii")))
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as tf:
            for member in tf:
                if not member.isfile():
                    continue
                path = (SRC / member.name).resolve()
                if not path.is_relative_to(SRC.resolve()):
                    raise ValueError("Invalid archive path")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(tf.extractfile(member).read())
    # Original add-on assets refer to jpg, initial repository provides PNG placeholders.
    for addon in IDS:
        xml = SRC / addon / "addon.xml"
        data = xml.read_text(encoding="utf-8")
        if "fanart.jpg" in data:
            xml.write_text(data.replace("fanart.jpg", "fanart.png"), encoding="utf-8")
    entry = SRC/"plugin.video.noodleprivate"/"default.py"
    content = entry.read_text(encoding="utf-8")
    if "resources', 'fanart.jpg'" in content:
        entry.write_text(content.replace("resources', 'fanart.jpg'", "resources', 'fanart.png'"), encoding="utf-8")

def image(path, w, h):
    if path.exists(): return
    path.parent.mkdir(parents=True, exist_ok=True)
    def c(t,d): return len(d).to_bytes(4,"big")+t+d+(zlib.crc32(t+d)&0xffffffff).to_bytes(4,"big")
    scan = bytearray()
    for y in range(h):
        scan.append(0)
        for x in range(w): scan.extend((20+x*30//w,30+y*60//h,70+x*100//w,255))
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+c(b"IHDR",struct.pack("!2I5B",w,h,8,6,0,0,0))+c(b"IDAT",zlib.compress(bytes(scan),7))+c(b"IEND",b""))

def main():
    seed()
    image(SRC/"plugin.video.noodleprivate/resources/icon.png",256,256)
    image(SRC/"plugin.video.noodleprivate/resources/fanart.png",1280,720)
    image(SRC/"repository.noodleprivate/icon.png",256,256)
    image(SRC/"repository.noodleprivate/fanart.png",1280,720)
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
                    zf.write(f,(Path(addon)/f.relative_to(SRC/addon)).as_posix())
        with zipfile.ZipFile(dest) as zf:
            assert zf.testzip() is None and f"{addon}/addon.xml" in zf.namelist()
        if addon.startswith("repository."):
            (ROOT/dest.name).write_bytes(dest.read_bytes())
    idx='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'+"\n".join(entries)+"\n</addons>\n"
    ET.fromstring(idx)
    (ROOT/"addons.xml").write_text(idx,encoding="utf-8")
    (ROOT/"addons.xml.md5").write_text(hashlib.md5(idx.encode("utf-8")).hexdigest()+"\n",encoding="ascii")
    print("Kodi index and installable ZIP packages built successfully")

if __name__=="__main__":
    main()
