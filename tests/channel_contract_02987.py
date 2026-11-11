"""Published .89 channels and installer are immutable; .90 is review-only."""
import hashlib,subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BASE='cb37de7103bd335a344c6738c33c4b5560ba2d4c'
from published_channels90 import retained,approved,committed as committed_bytes
def verify(path,committed=False):
 raw=committed_bytes(path) if committed else retained(path)
 if raw==approved(path):return True
 if committed or path not in ('addons.xml','addons.xml.md5'):raise AssertionError('UNAPPROVED_87_CHANNEL_CHANGE '+path)
 # Only historical repository-builder tests may stage an uncommitted index.
 data=(ROOT/'addons.xml').read_bytes();nodes={n.get('id'):n for n in E.fromstring(data)};old={n.get('id'):n for n in E.fromstring(approved('addons.xml'))}
 assert set(nodes)==set(old)
 assert nodes['plugin.video.xtreammate'].get('version')==E.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
 for ident in set(nodes)-{'plugin.video.xtreammate'}:assert E.canonicalize(E.tostring(nodes[ident],encoding='unicode'),strip_text=True)==E.canonicalize(E.tostring(old[ident],encoding='unicode'),strip_text=True)
 assert (ROOT/'addons.xml.md5').read_text().strip()==hashlib.md5(data).hexdigest()
 return True
