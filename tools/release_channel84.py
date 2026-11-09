"""Version-scoped, fail-closed authorization for XCMate 0.1.29.84 releases only."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.29.84'
HASH='25dc865c5fcb261e5e2bdad037d5bdae5b557b5f94902f8f84932fdf6a304e58'
MERGE='8e57fefb4f1b102d6b394649ff97cfa24d22aa04'
def regular_allowed84():
    try:
        src=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()
        if (src.get('id'),src.get('version'))!=('plugin.video.xtreammate',VERSION):return False
        data=json.loads((ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.84.json').read_text())
        expected={
            'addon_id':'plugin.video.xtreammate','version':VERSION,
            'exception_applies_only_to_version':VERSION,
            'user_approved_regular_release':True,'user_approved_pilot_release':True,
            'user_approved_all_channels':True,'android_status':'NOT_TESTED',
            'android_pass_claimed':False,'installer_0_5_26_unchanged':True,
            'authorization_issue':403,'source_merge_pr':405,'source_merge_sha':MERGE,'sha256':HASH
        }
        if any(data.get(key)!=value for key,value in expected.items()):return False
        pkg=ROOT/'docs/XCMate/test-builds/02984/plugin.video.xtreammate-0.1.29.84.zip'
        return hashlib.sha256(pkg.read_bytes()).hexdigest()==HASH
    except (OSError,ValueError,KeyError,E.ParseError):return False
if __name__=='__main__':
    if not regular_allowed84():raise SystemExit('XCMATE_02984_ALL_CHANNEL_RELEASE_BLOCKED')
    print('XCMATE_02984_EXPLICIT_APPROVAL_PINNED_ANDROID_NOT_TESTED')
