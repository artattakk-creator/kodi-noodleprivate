"""Only user-authorized .78 may replace current feeds; all other addons frozen."""
import hashlib,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BASE='80932cc20502dc267018bfded4f2a8cc0ce77e24';ADDON='plugin.video.xtreammate'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
    from channel_contract_02979 import verify as verify79
    if verify79(path,committed=committed):return True
    def current(name):return subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT) if committed else (ROOT/name).read_bytes()
    raw=current(path)
    if raw==approved(path):return True
    allowed=('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json')
    if path not in allowed:return False
    prefix='online-test/' if path.startswith('online-test/') else ''
    index=current(prefix+'addons.xml');old={n.get('id'):n for n in E.fromstring(approved(prefix+'addons.xml'))};new={n.get('id'):n for n in E.fromstring(index)}
    assert old.keys()==new.keys()
    for key in old.keys()-{ADDON}:assert E.tostring(old[key])==E.tostring(new[key]),key
    assert new[ADDON].get('version')=='0.1.29.78'
    assert E.tostring(new[ADDON]).strip()==E.tostring(E.parse(ROOT/'src'/ADDON/'addon.xml').getroot()).strip()
    assert current(prefix+'addons.xml.md5').decode().strip()==hashlib.md5(index).hexdigest()
    package=ROOT/'docs/XCMate/test-builds/02978/plugin.video.xtreammate-0.1.29.78.zip';payload=package.read_bytes()
    destination=ROOT/prefix/ADDON/package.name
    assert destination.read_bytes()==payload
    if prefix or committed:assert destination.with_suffix('.zip.sha256').read_text().split()==[hashlib.sha256(payload).hexdigest(),package.name]
    if path.endswith('manifest.json'):
        expected=json.loads(approved(path));expected['zip_sha256'][ADDON]=hashlib.sha256(payload).hexdigest();assert json.loads(raw)==expected
    return True
