#!/usr/bin/env python3
"""Reproducibly bootstrap XtreamMate GPL source from a pinned upstream ZIP.

A compact versioned patch is applied once, and resulting sources are committed
by the regular Kodi release workflow. No credentials or playlist data included.
"""
import base64
import hashlib
import io
import lzma
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / 'src' / 'plugin.video.xtreammate'
PATCH = ROOT / '.release' / 'xtreammate_0.1.0.patch.xz.b64'
UPSTREAM = ('https://raw.githubusercontent.com/mr-evil1/kodi-media-repo/main/'
            'plugin.video.iptvmaster/plugin.video.iptvmaster-2026.06.12.1.zip')
ORIGINAL_SHA256 = 'ef0c922b8095da164556a8745747797dceba4de59a3abb3cd03aab926c077148'


def artwork(destination):
    from PIL import Image, ImageDraw, ImageFont
    def font(size):
        for loc in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
            if os.path.isfile(loc):
                return ImageFont.truetype(loc,size)
        return ImageFont.load_default()
    art = [(600,600,'icon.png'),(1920,1080,'fanart.jpg')]
    for w,h,name in art:
        im = Image.new('RGB',(w,h))
        d = ImageDraw.Draw(im)
        for y in range(h):
            s = y / h
            d.line((0,y,w,y), fill=(int(18+26*s), int(22+6*s), int(50+26*s)))
        d.ellipse((int(w*.36),int(h*.1),int(w*.90),int(h*.88)),
                  outline=(218,100,246),width=max(4,w//95))
        d.text((int(w*.1),int(h*.40)), 'XM' if name=='icon.png' else 'XtreamMate',
               font=font(int(min(w,h)*(.26 if name=='icon.png' else .12))),
               fill=(245,240,255),stroke_width=max(1,w//650),stroke_fill=(115,59,182))
        if name=='icon.png': im.save(destination/name,optimize=True)
        else:im.save(destination/name,quality=83,optimize=True)
    bg = Image.new('RGBA',(820,1080),(11,16,30,218))
    bg.save(destination/'resources/media/tv_overlay_bg.png',optimize=True)


def bootstrap():
    if (TARGET / 'addon.xml').exists():
        return
    if not PATCH.exists():
        raise FileNotFoundError('Missing pinned XtreamMate source patch')
    override=os.environ.get('XTREAMMATE_ORIGINAL_ZIP')
    if override:
        binary=Path(override).read_bytes()
    else:
        with urllib.request.urlopen(UPSTREAM,timeout=60) as resp:
            binary=resp.read(15*1024*1024)
    if hashlib.sha256(binary).hexdigest()!=ORIGINAL_SHA256:
        raise RuntimeError('Unexpected upstream TiViMate ZIP checksum. Aborting bootstrap.')
    payload=lzma.decompress(base64.b64decode(PATCH.read_text(encoding='ascii').strip(),validate=True))
    with tempfile.TemporaryDirectory() as tmp:
        temp=Path(tmp) / 'unpacked'
        temp.mkdir()
        with zipfile.ZipFile(io.BytesIO(binary)) as archive:
            for item in archive.infolist():
                # No trusting archive paths: all filenames must stay inside the addon.
                rel=Path(item.filename)
                if item.is_dir():continue
                if rel.parts[0] != 'plugin.video.iptvmaster' or len(rel.parts)<2 or '..' in rel.parts:
                    raise ValueError('Illegal upstream ZIP path')
                dest=temp.joinpath(*rel.parts[1:])
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(archive.read(item))
        patchfile=Path(tmp)/'_xtreammate.patch'
        patchfile.write_bytes(payload)
        cmd=subprocess.run(['patch','--batch','--forward','-p1','-i',str(patchfile)],cwd=temp,
                           check=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if cmd.returncode:
            raise RuntimeError('Could not apply XtreamMate patch: '+cmd.stderr[-500:])
        patchfile.unlink()
        # Images are GS Media originals, not repackaged mr-evil1 art.
        artwork(temp)
        if b'id="plugin.video.xtreammate"' not in (temp/'addon.xml').read_bytes():
            raise RuntimeError('Invalid XtreamMate manifest')
        TARGET.parent.mkdir(parents=True,exist_ok=True)
        temp.rename(TARGET)
    print('Reconstructed XtreamMate 0.1.0 from pinned upstream and GPL patch')


if __name__ == '__main__':
    bootstrap()