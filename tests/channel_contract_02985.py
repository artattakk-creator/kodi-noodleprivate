""".85 is review-only. All committed .84 channels remain byte-exact main."""
import hashlib
import subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='faf83b833a14ac1cc937692e10a058d6a4dd462b'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
    from channel_contract_02986 import verify as verify86
    return verify86(path,committed)

def verify_archived85(path,committed=False):
    raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if committed else (ROOT/path).read_bytes()
    if raw==approved(path):return True
    if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_85_CHANNEL_CHANGE '+path)
    # Legacy repository-builder tests stage a disposable local index. This
    # allowance never permits a committed index or Pilot/NeoDark3 publication.
    data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)}
    old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
    assert set(nodes)=={'plugin.video.xtreammate','plugin.video.noodleprivate','repository.gsmedia'}
    assert nodes['plugin.video.xtreammate'].get('version')=='0.1.29.85'
    for ident in set(nodes)-{'plugin.video.xtreammate'}:
        assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
    assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
    package=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.85.zip'
    assert package.read_bytes()==(ROOT/'docs/XCMate/test-builds/02985'/package.name).read_bytes()
    return True
