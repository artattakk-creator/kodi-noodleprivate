"""Build the review ZIP only, with the repository builder's canonical bytes."""
import hashlib,json,sys,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from build_repository import package_file
ROOT=Path(__file__).resolve().parents[1]
def build(output):
    source=ROOT/'src/plugin.video.xtreammate';version=ET.parse(source/'addon.xml').getroot().get('version')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    target=output/('plugin.video.xtreammate-'+version+'.zip')
    files=[p for p in sorted(source.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store']
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
        for path in files:package_file(archive,'plugin.video.xtreammate',path,('plugin.video.xtreammate/'+path.relative_to(source).as_posix()))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for path in files:assert archive.read('plugin.video.xtreammate/'+path.relative_to(source).as_posix())==path.read_bytes()
        assert not any(n.endswith(('.db','.sqlite','.log','.pyc')) for n in archive.namelist())
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    (output/(target.name+'.sha256')).write_text(digest+'  '+target.name+'\n')
    return dict(version=version,sha256=digest,bytes=target.stat().st_size,files=len(files),crc='PASS',source_bytes='PASS')
if __name__=='__main__':print(json.dumps(build(sys.argv[1]),sort_keys=True))
