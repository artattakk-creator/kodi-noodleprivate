"""Version-scoped, fail-closed authorization for XCMate 0.1.29.83 releases only."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.29.83'
HASH='bdb10ae7d60c13cac38d58b7f73f89075c5b8f384e825dbc34461c4c2a82b738'
MERGE='0f7664c82269a26a804131dd62d183bbcf6f9b66'
def regular_allowed83():
    try:
        src=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()
        if (src.get('id'),src.get('version'))!=('plugin.video.xtreammate',VERSION):return False
        data=json.loads((ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.83.json').read_text())
        expected={
            'addon_id':'plugin.video.xtreammate','version':VERSION,
            'exception_applies_only_to_version':VERSION,
            'user_approved_regular_release':True,'user_approved_pilot_release':True,
            'user_approved_all_channels':True,'android_status':'NOT_TESTED',
            'android_pass_claimed':False,'installer_0_5_26_unchanged':True,
            'authorization_issue':398,'source_merge_pr':399,'source_merge_sha':MERGE,'sha256':HASH
        }
        if any(data.get(key)!=value for key,value in expected.items()):return False
        pkg=ROOT/'docs/XCMate/test-builds/02983/plugin.video.xtreammate-0.1.29.83.zip'
        return hashlib.sha256(pkg.read_bytes()).hexdigest()==HASH
    except (OSError,ValueError,KeyError,E.ParseError):return False
if __name__=='__main__':
    if not regular_allowed83():raise SystemExit('XCMATE_02983_ALL_CHANNEL_RELEASE_BLOCKED')
    print('XCMATE_02983_EXPLICIT_APPROVAL_PINNED_ANDROID_NOT_TESTED')
