"""Build a review artifact from an unpacked official skin; never patch input."""
from pathlib import Path
import argparse,difflib,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/plugin.video.xtreammate/resources/lib'))
from widget_skin50 import FILES,guard,patch,reference


def build(skin,output):
    skin=Path(skin).resolve();output=Path(output).resolve()
    if output==skin or skin in output.parents:raise ValueError('OUTPUT_MUST_NOT_BE_IN_SKIN')
    guard(skin);output.mkdir(parents=True,exist_ok=True);manifest=dict(version='0.1.29.50',status='REVIEW_ONLY_NOT_APPLIED',automatic_apply=False,reference=reference(),files={});diff=[]
    for name in FILES:
        original=(skin/name).read_bytes();candidate=patch(name,original)
        target=output/'candidate'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(candidate)
        manifest['files'][name]=dict(before=hashlib.sha256(original).hexdigest(),after=hashlib.sha256(candidate).hexdigest(),bytes=len(candidate))
        diff+=difflib.unified_diff(original.decode().splitlines(keepends=True),candidate.decode().splitlines(keepends=True),fromfile='before/'+name,tofile='candidate/'+name)
        assert (skin/name).read_bytes()==original
    (output/'REVIEW.patch').write_text(''.join(diff));(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    license=skin/'LICENSE'
    if license.is_file():(output/'LICENSE.BINGIE').write_bytes(license.read_bytes())
    archive=output/'XCMate_BINGIE_02950_REVIEW.zip'
    members=sorted(p for p in output.rglob('*') if p.is_file() and p!=archive and p.suffix!='.sha256')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in members:
            e=zipfile.ZipInfo(str(p.relative_to(output)),(1980,1,1,0,0,0));e.create_system=3;e.external_attr=0o100644<<16
            z.writestr(e,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest();archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n')
    return manifest,digest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--skin-root',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    result,digest=build(args.skin_root,args.output);print(json.dumps(dict(status=result['status'],files=len(result['files']),sha256=digest)))
