"""Companion update from main's exact .5.19 ZIP; no old branch or repo publish."""
import ast
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.19.zip'
SHA='92756415de0f09cc0f2094f2f5fc1226a64d5bc573c3f5f6103029062da81f60'


def build(output):
    if hashlib.sha256(BASE.read_bytes()).hexdigest()!=SHA:raise ValueError('SETUP352_BASE_CHANGED')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    prefix='script.gsmedia.setup/'
    with zipfile.ZipFile(BASE) as source:
        if source.testzip():raise ValueError('SETUP352_BASE_CRC')
        files={name:source.read(name) for name in source.namelist() if not name.endswith('/')}
    # The reported .5.16 omission is already repaired in main's .5.19 package.
    if prefix+'resources/lib/setup_catalog_0516.py' not in files:raise ValueError('SETUP352_MODULE_MISSING')
    old=dict(files)
    files[prefix+'addon.xml']=files[prefix+'addon.xml'].replace(b'version="0.5.19"',b'version="0.5.20"',1)
    if files[prefix+'addon.xml']==old[prefix+'addon.xml']:raise ValueError('SETUP352_VERSION')
    files[prefix+'service.py']=(ROOT/'tools/gsmedia_setup352/service.py').read_bytes()
    files[prefix+'resources/lib/setup_postboot71.py']=(ROOT/'tools/gsmedia_setup352/setup_postboot71.py').read_bytes()
    allowed={prefix+'addon.xml',prefix+'service.py',prefix+'resources/lib/setup_postboot71.py'}
    if any(files[name]!=data for name,data in old.items() if name not in allowed):raise ValueError('SETUP352_UNRELATED_DELTA')
    missing=[]
    for name,data in files.items():
        if not name.endswith('.py'):continue
        tree=ast.parse(data)
        for node in ast.walk(tree):
            imports=([a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else [])
            for module in imports:
                if module.startswith('setup_') and prefix+'resources/lib/'+module+'.py' not in files:missing.append(module)
    if missing:raise ValueError('SETUP352_IMPORT_CLOSURE')
    path=output/'script.gsmedia.setup-0.5.20.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,3,0,0,0));info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data)
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix('.zip.sha256').write_text(sha+'  '+path.name+'\n')
    report=dict(base_sha256=SHA,sha256=sha,files=len(files),version='0.5.20',import_closure='PASS',
                unchanged_files=len(old)-2,android='NOT_TESTED',auto_install=False,production_publish=False)
    (output/'setup352-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    import sys
    print(json.dumps(build(sys.argv[1]),sort_keys=True))
