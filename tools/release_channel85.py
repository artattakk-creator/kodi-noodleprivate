"""Version-scoped, fail-closed authorization for XCMate 0.1.29.85 releases only."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.29.85'
HASH='9efd5fe6c4078a9fe32af67d582c256a7a22de5033ed491bd5b8662904fe752a'
MERGE='21e26dd1fe2d2075eac5f87ed5da6f08a835c9c1'
def regular_allowed85():
    try:
        src=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()
        if (src.get('id'),src.get('version'))!=('plugin.video.xtreammate',VERSION):return False
        data=json.loads((ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.85.json').read_text())
        expected={
            'addon_id':'plugin.video.xtreammate','version':VERSION,
            'exception_applies_only_to_version':VERSION,
            'user_approved_regular_release':True,'user_approved_pilot_release':True,
            'user_approved_all_channels':True,'android_status':'NOT_TESTED',
            'android_pass_claimed':False,'installer_0_5_26_unchanged':True,
            'authorization_issue':406,'source_merge_pr':408,'source_merge_sha':MERGE,'sha256':HASH
        }
        if any(data.get(key)!=value for key,value in expected.items()):return False
        pkg=ROOT/'docs/XCMate/test-builds/02985/plugin.video.xtreammate-0.1.29.85.zip'
        return hashlib.sha256(pkg.read_bytes()).hexdigest()==HASH
    except (OSError,ValueError,KeyError,E.ParseError):return False
if __name__=='__main__':
    if not regular_allowed85():raise SystemExit('XCMATE_02985_ALL_CHANNEL_RELEASE_BLOCKED')
    print('XCMATE_02985_EXPLICIT_APPROVAL_PINNED_ANDROID_NOT_TESTED')
