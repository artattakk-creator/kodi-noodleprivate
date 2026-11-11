"""Published .86 and installer are immutable; .87 is a distinct review ZIP."""
import hashlib,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BASE='c5b7c18ab2f8a9f6be740f3b8cd2f0d1814ec467'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
 raw=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if committed else (ROOT/path).read_bytes()
 if raw==approved(path):return True
 if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_87_CHANNEL_CHANGE '+path)
 # Only historical repository-builder tests may stage an uncommitted index.
 data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)};old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
 assert set(nodes)==set(old)
 assert nodes['plugin.video.xtreammate'].get('version')==E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
 for ident in set(nodes)-{'plugin.video.xtreammate'}:assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
 assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
 return True
