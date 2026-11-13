"""Review-only .5.29; exact published .5.26 base. No channel staging function."""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af'
NAME='script.gsmedia.setup-0.5.29.zip'
PREFIX='script.gsmedia.setup/'

def build(output):
    raw=(ROOT/'online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASE_SHA:raise ValueError('FROZEN_0526_CHANGED')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip():raise ValueError('BASE_CRC')
        files={n:z.read(n) for n in z.namelist()}
    if any(not n.startswith(PREFIX) or '..' in Path(n).parts or Path(n).is_absolute() for n in files):raise ValueError('BASE_TRAVERSAL')
    addon=E.fromstring(files[PREFIX+'addon.xml'])
    if addon.get('version')!='0.5.26':raise ValueError('BASE_VERSION')
    addon.set('version','0.5.29');files[PREFIX+'addon.xml']=E.tostring(addon,encoding='utf-8',xml_declaration=True)
    for name in ('setup_auto_ui50.py','setup_storage92.py'):
        files[PREFIX+'resources/lib/'+name]=(ROOT/'tools/gsmedia_setup0529/overlays/resources/lib'/name).read_bytes()
        compile(files[PREFIX+'resources/lib/'+name],name,'exec')
    output=Path(output);output.mkdir(parents=True,exist_ok=True);path=output/NAME
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,data)
    with zipfile.ZipFile(path) as z:
        if z.testzip() or any(z.read(n)!=data for n,data in files.items()):raise ValueError('PACKAGE_READBACK')
    digest=hashlib.sha256(path.read_bytes()).hexdigest();(output/(NAME+'.sha256')).write_text(digest+'  '+NAME+'\n')
    return dict(version='0.5.29',sha256=digest,files=len(files),source_base='0.5.26',android='ANDROID_NOT_TESTED',released=False)
if __name__=='__main__':print(json.dumps(build(sys.argv[1]),sort_keys=True))
