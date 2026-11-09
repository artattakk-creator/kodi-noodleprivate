""".84 is review-only. All committed .83 channels remain byte-exact main."""
import hashlib
import subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='ee42712655cb9adcdcb11b09d591a1737d899844'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
    raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if committed else (ROOT/path).read_bytes()
    if raw==approved(path):return True
    if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_84_CHANNEL_CHANGE '+path)
    # Legacy repository-builder tests stage a disposable local index. This
    # allowance never permits a committed index or Pilot/NeoDark3 publication.
    data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)}
    old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
    assert set(nodes)=={'plugin.video.xtreammate','plugin.video.noodleprivate','repository.gsmedia'}
    assert nodes['plugin.video.xtreammate'].get('version')=='0.1.29.84'
    for ident in set(nodes)-{'plugin.video.xtreammate'}:
        assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
    assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
    package=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.84.zip'
    assert package.read_bytes()==(ROOT/'docs/XCMate/test-builds/02984'/package.name).read_bytes()
    return True
