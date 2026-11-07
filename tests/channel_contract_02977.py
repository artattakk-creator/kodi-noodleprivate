"""Approved .76 release baseline; only an exact .77 Pilot package may differ."""
import hashlib,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='27104311012252f8c6382a392807b88290dc833c'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path):
    from channel_contract_02978 import verify as verify78
    if verify78(path):return True
    current=(ROOT/path).read_bytes()
    if current==approved(path):return True
    if path not in ('online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):return False
    # User #380 permits .77 in Pilot only, with installer/inventory untouched.
    package=ROOT/'docs/XCMate/test-builds/02977/plugin.video.xtreammate-0.1.29.77.zip'
    if not package.is_file():return False
    old={n.get('id'):n for n in E.fromstring(approved('online-test/addons.xml'))}
    new={n.get('id'):n for n in E.parse(ROOT/'online-test/addons.xml').getroot()}
    assert old.keys()==new.keys()
    for key in old.keys()-{'plugin.video.xtreammate'}:assert E.tostring(old[key])==E.tostring(new[key]),key
    assert E.tostring(new['plugin.video.xtreammate']).strip()==E.tostring(E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()).strip()
    assert new['plugin.video.xtreammate'].get('version')=='0.1.29.77'
    raw=package.read_bytes();assert (ROOT/'online-test/plugin.video.xtreammate'/package.name).read_bytes()==raw
    assert (ROOT/'online-test/addons.xml.md5').read_text().strip()==hashlib.md5((ROOT/'online-test/addons.xml').read_bytes()).hexdigest()
    before=json.loads(approved('online-test/manifest.json'));after=json.loads((ROOT/'online-test/manifest.json').read_bytes())
    expected=json.loads(json.dumps(before));expected['zip_sha256']['plugin.video.xtreammate']=hashlib.sha256(raw).hexdigest();assert after==expected
    return True
