""".82 is a review build: published .81 channels and installer are immutable.

CI may build a temporary three-source regular index without publishing it.
Committed catalogues and all Pilot paths must retain exact main bytes.
"""
import hashlib,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BASE='7e5a1cf588b7c1043a1849e5c48e77358812b1ef'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
 raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if committed else (ROOT/path).read_bytes()
 if raw==approved(path):return True
 if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_82_CHANNEL_CHANGE '+path)
 data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)};old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
 assert set(nodes)=={'plugin.video.xtreammate','plugin.video.noodleprivate','repository.gsmedia'}
 assert nodes['plugin.video.xtreammate'].get('version')=='0.1.29.82'
 for ident in set(nodes)-{'plugin.video.xtreammate'}:assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
 assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
 package=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.82.zip'
 assert package.read_bytes()==(ROOT/'docs/XCMate/test-builds/02982'/package.name).read_bytes()
 return True
