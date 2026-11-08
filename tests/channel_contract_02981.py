""".81 is a review build: published .80 channels and installer are immutable.

CI may build a temporary three-source regular index without publishing it.
Committed catalogues and all Pilot paths must retain exact main bytes.
"""
import hashlib,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BASE='9f5e5da705dc7be4044171debd273927998a4f27'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
 from channel_contract_02982 import verify as current82
 if current82(path,committed):return True
 raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if committed else (ROOT/path).read_bytes()
 if raw==approved(path):return True
 if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_81_CHANNEL_CHANGE '+path)
 data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)};old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
 assert set(nodes)=={'plugin.video.xtreammate','plugin.video.noodleprivate','repository.gsmedia'}
 assert nodes['plugin.video.xtreammate'].get('version')=='0.1.29.81'
 for ident in set(nodes)-{'plugin.video.xtreammate'}:assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
 assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
 package=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.81.zip'
 assert package.read_bytes()==(ROOT/'docs/XCMate/test-builds/02981'/package.name).read_bytes()
 return True
