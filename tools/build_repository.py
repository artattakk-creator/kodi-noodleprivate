#!/usr/bin/env python3
"""Build Kodi add-on packages and index from the committed src/ directory."""
import hashlib, re, struct, zipfile, zlib
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
IDS = ("plugin.video.noodleprivate", "repository.noodleprivate")
def create_png(dest, w, h):
    if dest.exists(): return
    dest.parent.mkdir(parents=True, exist_ok=True)
    def chunk(tag, data):
        return struct.pack("!I",len(data))+tag+data+struct.pack("!I",zlib.crc32(tag+data)&0xffffffff)
    pixels=bytearray()
    for y in range(h):
        pixels.append(0)
        for x in range(w): pixels.extend((20+x*30//w,30+y*60//h,70+x*100//w,255))
    dest.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack("!2I5B",w,h,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(bytes(pixels),7))+chunk(b"IEND",b""))
def main():
    for name in IDS:
        create_png(SRC/name/("resources/icon.png" if name.startswith("plugin.") else "icon.png"),256,256)
        create_png(SRC/name/("resources/fanart.png" if name.startswith("plugin.") else "fanart.png"),1280,720)
    entries=[]
    for name in IDS:
        path=SRC/name/"addon.xml"
        node=ET.parse(path).getroot()
        assert node.tag=="addon" and node.attrib["id"]==name
        version=node.attrib["version"]
        assert re.fullmatch(r"\d+(?:\.\d+){2,3}",version)
        raw=path.read_text(encoding="utf-8").strip()
        entries.append(re.sub(r"^<\?xml[^>]*\?>\s*","",raw))
        target=ROOT/name/f"{name}-{version}.zip"
        target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
            for file in sorted((SRC/name).rglob("*")):
                if file.is_file() and "__pycache__" not in file.parts:
                    archive.write(file,(Path(name)/file.relative_to(SRC/name)).as_posix())
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
        if name.startswith("repository."):
            (ROOT/target.name).write_bytes(target.read_bytes())
    index='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'+"\n".join(entries)+"\n</addons>\n"
    ET.fromstring(index)
    (ROOT/"addons.xml").write_text(index,encoding="utf-8")
    (ROOT/"addons.xml.md5").write_text(hashlib.md5(index.encode("utf-8")).hexdigest()+"\n",encoding="ascii")
if __name__=="__main__":
    main()
