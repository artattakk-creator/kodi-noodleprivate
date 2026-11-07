"""Exact #385 release: regular + Pilot + NeoDark3, no installer execution.

Staging is reviewable and changes only XCMate's blocks and new artifacts.
Public verification reads actual main URLs and compares canonical source bytes.
"""
import argparse,hashlib,io,json,re,subprocess,urllib.request,zipfile
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
ADDON='plugin.video.xtreammate';VERSION='0.1.29.78'
NAME=ADDON+'-'+VERSION+'.zip';REL=ADDON+'/'+NAME
BASE='https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/'
PATHS=(REL,'online-test/'+REL,'online-test/'+NAME)
INSTALLER='5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inspect(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        names=archive.namelist();assert len(names)==len(set(names))
        source=ROOT/'src'/ADDON
        expected={ADDON+'/'+p.relative_to(source).as_posix():p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo') and p.name!='.DS_Store'}
        assert set(names)==set(expected),'SOURCE_ZIP_FILE_SET'
        for name in names:
            assert '..' not in Path(name).parts and not name.startswith('/')
            assert not name.endswith(('.db','.sqlite','.log','.pyc'))
            assert archive.read(name)==expected[name].read_bytes(),name
        manifest=archive.read(ADDON+'/addon.xml');node=E.fromstring(manifest)
        assert node.get('id')==ADDON and node.get('version')==VERSION
        return manifest

def replace_index(before,manifest):
    block=re.sub(r'^\s*<\?xml[^>]*\?>\s*','',manifest.decode()).strip()
    text,count=re.subn(r'<addon\b(?=[^>]*\bid="plugin\.video\.xtreammate")[^>]*>.*?</addon>',lambda _:block,before.decode(),flags=re.S)
    assert count==1
    after=text.encode();old={n.get('id'):n for n in E.fromstring(before)};new={n.get('id'):n for n in E.fromstring(after)}
    assert old.keys()==new.keys()
    for key in old.keys()-{ADDON}:assert E.tostring(old[key])==E.tostring(new[key]),key
    return after

def stage():
    from release_channel75 import regular_allowed
    assert regular_allowed(),'EXPLICIT_78_RELEASE_AUTHORIZATION_REQUIRED'
    raw=(ROOT/'docs/XCMate/test-builds/02978'/NAME).read_bytes();manifest=inspect(raw)
    # Immutable old/published versions; never replace a different released .78.
    for path in PATHS:
        published=subprocess.run(['git','show','origin/main:'+path],cwd=ROOT,capture_output=True)
        assert published.returncode!=0 or published.stdout==raw,'PUBLISHED_VERSION_CONFLICT'
    for prefix in ('','online-test/'):
        channel=ROOT/prefix;after=replace_index((channel/'addons.xml').read_bytes(),manifest)
        (channel/'addons.xml').write_bytes(after);(channel/'addons.xml.md5').write_text(hashlib.md5(after).hexdigest()+'\n')
    for path in PATHS:
        target=ROOT/path;target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw);target.with_suffix('.zip.sha256').write_text(sha(raw)+'  '+NAME+'\n')
    metadata=json.loads((ROOT/'online-test/manifest.json').read_text());metadata['zip_sha256'][ADDON]=sha(raw)
    (ROOT/'online-test/manifest.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    return verify(lambda p:(ROOT/p).read_bytes())

def verify(fetch):
    expected=(ROOT/'docs/XCMate/test-builds/02978'/NAME).read_bytes();manifest=inspect(expected)
    releases=[]
    for prefix,repoid in (('','repository.gsmedia'),('online-test/','repository.gsmedia.pilot')):
        index=fetch(prefix+'addons.xml');assert fetch(prefix+'addons.xml.md5').decode().strip()==hashlib.md5(index).hexdigest()
        nodes=E.fromstring(index);node=next(n for n in nodes if n.get('id')==ADDON)
        assert E.tostring(node).strip()==E.tostring(E.fromstring(manifest)).strip()
        repository=next(n for n in nodes if n.get('id')==repoid)
        assert repository.findtext('./extension/dir/info')==BASE+prefix+'addons.xml'
        assert repository.findtext('./extension/dir/checksum')==BASE+prefix+'addons.xml.md5'
        installer=next(n for n in nodes if n.get('id')=='script.gsmedia.setup');assert installer.get('version')=='0.5.26'
    metadata=json.loads(fetch('online-test/manifest.json'));assert metadata['zip_sha256'][ADDON]==sha(expected)
    for path in PATHS:
        raw=fetch(path);assert raw==expected,'CHANNEL_BYTES_DIFFER'
        assert fetch(path+'.sha256').decode().split()==[sha(expected),NAME]
        releases.append(dict(url=BASE+path,sha256=sha(raw),bytes=len(raw)))
    # The NeoDark3 source directory must expose its flat direct download.
    assert NAME in fetch('online-test/index.html').decode()
    installer=fetch('online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip');assert sha(installer)==INSTALLER
    return dict(version=VERSION,status='RELEASED',channels=releases,index_md5='PASS',source_bytes='PASS',crc='PASS',installer='0.5.26 UNCHANGED / NOT RUN',android='ANDROID_NOT_TESTED')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--public',action='store_true');args=parser.parse_args()
    if args.stage:result=stage()
    elif args.public:
        def fetch(path):
            with urllib.request.urlopen(BASE+path,timeout=40) as response:
                assert response.status==200
                return response.read(32*1024*1024)
        result=verify(fetch)
    else:result=verify(lambda p:(ROOT/p).read_bytes())
    print(json.dumps(result,indent=2))
