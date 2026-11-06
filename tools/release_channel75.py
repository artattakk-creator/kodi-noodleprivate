"""Fail closed for regular publication while .75 is a Pilot-only candidate."""
import json,os
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def regular_allowed():
    version=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
    if tuple(int(n) for n in version.split('.'))<(0,1,29,75):return True
    # One tightly scoped user-approved pre-Android release: .76 only.
    # This is NOT an Android PASS: the explicit authorization records
    # android_status=NOT_TESTED and pins the existing Pilot ZIP hash.
    if version=='0.1.29.76':
        approval=ROOT/'docs/XCMate/releases/user-approved-untested-0.1.29.76.json'
        try:
            data=json.loads(approval.read_text(encoding='utf-8'))
            expected='c6b3813a6b2e9289251d3e14ea8425e0fe3fb35ee9a01dda457aa81a27e081cc'
            fields_ok=(data.get('addon_id')=='plugin.video.xtreammate'
              and data.get('version')==version
              and data.get('exception_applies_only_to_version')==version
              and data.get('user_approved_regular_release') is True
              and data.get('user_approved_all_channels') is True
              and data.get('android_status')=='NOT_TESTED'
              and data.get('android_pass_claimed') is False
              and data.get('sha256')==expected)
            if fields_ok:return True
        except (OSError,ValueError):pass
    # All other releases still require genuine Android PASS and user consent.
    path=ROOT/'docs/XCMate/releases'/('android-approved-'+version+'.json')
    try:
        value=json.loads(path.read_text())
        return value.get('version')==version and value.get('android_status')=='PASS' and value.get('user_approved_regular_release') is True
    except (OSError,ValueError):return False
if __name__=='__main__':
    allowed=regular_allowed()
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as stream:stream.write('regular='+str(allowed).lower()+'\n')
    print('REGULAR_ALLOWED' if allowed else 'PILOT_ONLY_REGULAR_PUBLICATION_BLOCKED')
