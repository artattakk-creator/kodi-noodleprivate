"""Stage/verify XCMate .75 in the existing Pilot channel only; no installer."""
import argparse,hashlib,io,json,re,urllib.request,zipfile,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
ADDON='plugin.video.xtreammate';VERSION='0.1.29.75'
REL=ADDON+'/'+ADDON+'-'+VERSION+'.zip'
BASE='https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inspect(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        assert all(n.startswith(ADDON+'/') and '..' not in Path(n).parts for n in z.namelist())
        manifest=z.read(ADDON+'/addon.xml');node=E.fromstring(manifest)
        assert node.get('id')==ADDON and node.get('version')==VERSION
        return manifest
def stage():
    package=ROOT/'docs/XCMate/test-builds/02975'/Path(REL).name;raw=package.read_bytes();manifest=inspect(raw)
    channel=ROOT/'online-test';before=(channel/'addons.xml').read_bytes();old=E.fromstring(before)
    block=re.sub(r'^\s*<\?xml[^>]*\?>\s*','',manifest.decode()).strip()
    pattern=r'<addon\b(?=[^>]*\bid="plugin\.video\.xtreammate")[^>]*>.*?</addon>'
    text,count=re.subn(pattern,lambda _:block,before.decode(),flags=re.S);assert count==1
    after=text.encode();new=E.fromstring(after)
    a={n.get('id'):n for n in old};b={n.get('id'):n for n in new};assert a.keys()==b.keys()
    for key in a.keys()-{ADDON}:assert E.tostring(a[key])==E.tostring(b[key]),key
    target=channel/REL;target.parent.mkdir(exist_ok=True)
    published=subprocess.run(['git','show','origin/main:online-test/'+REL],cwd=ROOT,capture_output=True)
    assert published.returncode!=0 or published.stdout==raw,'IMMUTABLE_PUBLISHED_VERSION_ALREADY_EXISTS'
    target.write_bytes(raw);target.with_suffix('.zip.sha256').write_text(sha(raw)+'  '+target.name+'\n')
    (channel/'addons.xml').write_bytes(after);(channel/'addons.xml.md5').write_text(hashlib.md5(after).hexdigest()+'\n')
    metadata=json.loads((channel/'manifest.json').read_text());metadata['zip_sha256'][ADDON]=sha(raw)
    (channel/'manifest.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    return verify(lambda p:(ROOT/p).read_bytes())
def verify(fetch):
    regular=E.fromstring(fetch('addons.xml'));assert next(n for n in regular if n.get('id')==ADDON).get('version')=='0.1.29.74','REGULAR_CHANGED_BEFORE_ANDROID_APPROVAL'
    index=fetch('online-test/addons.xml');assert fetch('online-test/addons.xml.md5').decode().strip()==hashlib.md5(index).hexdigest()
    nodes=E.fromstring(index);node=next(n for n in nodes if n.get('id')==ADDON);assert node.get('version')==VERSION
    raw=fetch('online-test/'+REL);manifest=inspect(raw)
    assert E.tostring(node).strip()==E.tostring(E.fromstring(manifest)).strip()
    checksum=fetch('online-test/'+REL+'.sha256').decode().split();assert checksum==[sha(raw),Path(REL).name]
    metadata=json.loads(fetch('online-test/manifest.json'));assert metadata['zip_sha256'][ADDON]==sha(raw)
    repo=next(n for n in nodes if n.get('id')=='repository.gsmedia.pilot')
    assert repo.findtext('./extension/dir/info')==BASE+'online-test/addons.xml'
    assert repo.findtext('./extension/dir/checksum')==BASE+'online-test/addons.xml.md5'
    return dict(version=VERSION,channel='GS Media Pilot',sha256=sha(raw),bytes=len(raw),crc='PASS',index='PASS',update_version_comparison='0.1.29.75 > 0.1.29.74',regular_version='0.1.29.74',installer_executed=False,android='ANDROID_NOT_TESTED',url=BASE+'online-test/'+REL)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--public',action='store_true');args=parser.parse_args()
    if args.stage:result=stage()
    elif args.public:
        def fetch(path):
            with urllib.request.urlopen(BASE+path,timeout=30) as response:
                assert response.status==200
                return response.read(20*1024*1024)
        result=verify(fetch)
    else:result=verify(lambda p:(ROOT/p).read_bytes())
    print(json.dumps(result,indent=2))
