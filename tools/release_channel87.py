"""Version-scoped, fail-closed authorization for XCMate 0.1.29.87 releases only."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.29.87'
HASH='e78f28fdb1f1537d42acbef55f5539d6670f4b306d07b92e9e7795cc51dff843'
MERGE='3a8c374fa752d99b97a101178868b86d80435fad'
def regular_allowed87():
    try:
        src=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()
        if (src.get('id'),src.get('version'))!=('plugin.video.xtreammate',VERSION):return False
        data=json.loads((ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.87.json').read_text())
        expected={
            'addon_id':'plugin.video.xtreammate','version':VERSION,
            'exception_applies_only_to_version':VERSION,
            'user_approved_regular_release':True,'user_approved_pilot_release':True,
            'user_approved_all_channels':True,'android_status':'NOT_TESTED',
            'android_pass_claimed':False,'installer_0_5_26_unchanged':True,
            'authorization_issue':419,'source_merge_pr':416,'source_merge_sha':MERGE,'sha256':HASH
        }
        if any(data.get(key)!=value for key,value in expected.items()):return False
        pkg=ROOT/'docs/XCMate/test-builds/02987/plugin.video.xtreammate-0.1.29.87.zip'
        return hashlib.sha256(pkg.read_bytes()).hexdigest()==HASH
    except (OSError,ValueError,KeyError,E.ParseError):return False
if __name__=='__main__':
    if not regular_allowed87():raise SystemExit('XCMATE_02987_ALL_CHANNEL_RELEASE_BLOCKED')
    print('XCMATE_02987_EXPLICIT_APPROVAL_PINNED_ANDROID_NOT_TESTED')
