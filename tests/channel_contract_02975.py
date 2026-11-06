"""Account for explicitly approved historical releases, never arbitrary changes.

Old release assertions retain their original inventory. Current main .74 is
the approved baseline; .75 may replace only XCMate in Pilot, never setup/regular.
"""
import hashlib,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='ad5c337c0ca9ea6f85e458c17383fb32c19e3fc2'
def baseline(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path):
    from channel_contract_02977 import verify as verify77
    if verify77(path):return
    current=(ROOT/path).read_bytes();old=baseline(path)
    # Published Pilot .75 remains immutable while the next candidate is reviewed.
    released=subprocess.check_output(['git','show','b3024e9620e8924e880a70fc92ca70e4b5a5658b:'+path],cwd=ROOT)
    if current==released:return
    if current==old:return
    if path=='online-test/addons.xml':
        a=E.fromstring(old);b=E.fromstring(current);aa={n.get('id'):n for n in a};bb={n.get('id'):n for n in b}
        assert aa.keys()==bb.keys(),path
        for key in aa.keys()-{'plugin.video.xtreammate'}:assert E.tostring(aa[key])==E.tostring(bb[key]),key
        assert bb['plugin.video.xtreammate'].get('version')=='0.1.29.75'
        package=ROOT/'online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.75.zip'
        reviewed=ROOT/'docs/XCMate/test-builds/02975'/package.name
        assert package.read_bytes()==reviewed.read_bytes()
        assert E.tostring(bb['plugin.video.xtreammate']).strip()==E.tostring(E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()).strip()
        return
    if path=='online-test/addons.xml.md5':
        verify('online-test/addons.xml');assert current.decode().strip()==hashlib.md5((ROOT/'online-test/addons.xml').read_bytes()).hexdigest();return
    if path=='online-test/manifest.json':
        before=json.loads(old);after=json.loads(current)
        for key in before.keys()-{'zip_sha256'}:assert after[key]==before[key],key
        assert after['zip_sha256'].keys()==before['zip_sha256'].keys()
        for key in before['zip_sha256'].keys()-{'plugin.video.xtreammate'}:assert after['zip_sha256'][key]==before['zip_sha256'][key],key
        assert after['zip_sha256']['plugin.video.xtreammate']==hashlib.sha256((ROOT/'docs/XCMate/test-builds/02975/plugin.video.xtreammate-0.1.29.75.zip').read_bytes()).hexdigest()
        return
    raise AssertionError('UNAPPROVED_CHANNEL_CHANGE '+path)
