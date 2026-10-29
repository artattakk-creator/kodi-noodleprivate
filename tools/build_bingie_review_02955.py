#!/usr/bin/env python3
"""Build an offline, review-only four-file adapter from pinned public fixtures.

Never takes a Kodi/profile path, never installs anything. Real device files
must instead pass the runtime hash, backup and explicit approval transaction.
"""
import difflib,hashlib,json,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/plugin.video.xtreammate/resources/lib'))
from widget_skin50 import FILES,patch,reference


def build():
    folder=ROOT/'integrations/titan-bingie-mod/0.1.29.55'
    folder.mkdir(exist_ok=True)
    manifest=dict(version='0.1.29.55',status='REVIEW_ONLY_NOT_APPLIED',automatic_apply=False,
        android='NOT_TESTED',reference=reference(),files={})
    diffs=[]
    with zipfile.ZipFile(ROOT/'tests/fixtures/bingie223_reference50.zip') as archive:
        for name in FILES:
            old=archive.read(name);new=patch(name,old)
            p=folder/'candidate'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new)
            manifest['files'][name]=dict(before=hashlib.sha256(old).hexdigest(),after=hashlib.sha256(new).hexdigest(),bytes=len(new))
            diffs.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (folder/'REVIEW.patch').write_text(''.join(diffs))
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (folder/'LICENSE.BINGIE').write_bytes((ROOT/'integrations/titan-bingie-mod/0.1.29.50/LICENSE.BINGIE').read_bytes())
    output=folder/'XCMate_BINGIE_02955_REVIEW.zip'
    files=[p for p in folder.rglob('*') if p.is_file() and p!=output and not p.name.endswith('.sha256')]
    with zipfile.ZipFile(output,'w') as archive:
        for path in sorted(files):
            info=zipfile.ZipInfo(str(path.relative_to(folder)),(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            archive.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.zip.sha256').write_text(digest+'  '+output.name+'\n')
    print('REVIEW_ONLY',digest)


if __name__=='__main__':build()
