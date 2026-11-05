"""Fail closed for regular publication while .75 is a Pilot-only candidate."""
import json,os
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
def regular_allowed():
    version=E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
    if tuple(int(n) for n in version.split('.'))<(0,1,29,75):return True
    # Unlocking requires a subsequent explicit Android-approval change.
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
