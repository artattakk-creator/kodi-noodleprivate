"""Version-scoped, fail-closed authorization for XCMate 0.1.29.86 releases only."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.29.86'
HASH='07c7f10b0f5da873c1add538c44bf2ee4c9aa5027ad98c262ec98bd5d709c7c4'
MERGE='36b903c06daa7b7fb5903f9de568237c18b9e2a1'
def regular_allowed86():
    try:
        src=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot()
        if (src.get('id'),src.get('version'))!=('plugin.video.xtreammate',VERSION):return False
        data=json.loads((ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.86.json').read_text())
        expected={
            'addon_id':'plugin.video.xtreammate','version':VERSION,
            'exception_applies_only_to_version':VERSION,
            'user_approved_regular_release':True,'user_approved_pilot_release':True,
            'user_approved_all_channels':True,'android_status':'NOT_TESTED',
            'android_pass_claimed':False,'installer_0_5_26_unchanged':True,
            'authorization_issue':409,'source_merge_pr':410,'source_merge_sha':MERGE,'sha256':HASH
        }
        if any(data.get(key)!=value for key,value in expected.items()):return False
        pkg=ROOT/'docs/XCMate/test-builds/02986/plugin.video.xtreammate-0.1.29.86.zip'
        return hashlib.sha256(pkg.read_bytes()).hexdigest()==HASH
    except (OSError,ValueError,KeyError,E.ParseError):return False
if __name__=='__main__':
    if not regular_allowed86():raise SystemExit('XCMATE_02986_ALL_CHANNEL_RELEASE_BLOCKED')
    print('XCMATE_02986_EXPLICIT_APPROVAL_PINNED_ANDROID_NOT_TESTED')
