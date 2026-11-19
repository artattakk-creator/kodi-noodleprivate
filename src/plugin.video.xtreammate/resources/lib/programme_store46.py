"""Optional rich-event sidecar. Never alters, creates or migrates guide_v1.

Only metadata from a successfully committed source generation is published.
Readers require the exact canonical channel, interval, title and source rank.
Failures in this bounded cache cannot fail or modify the authoritative guide.
"""
import hashlib,json,os,re,sqlite3,time
from urllib.parse import quote
MAX_BYTES=32*1024*1024

def path(guide=None):
 if guide:return str(guide)+'.programme46.sqlite'
 from utils import addon_data_dir
 return os.path.join(addon_data_dir(),'programme_meta46.sqlite')

def title_hash(title):
 from epg_events import title_key
 return hashlib.sha256(title_key(title).encode()).hexdigest()

def age_rating(event):
 raw=str(event.get('age_rating') or event.get('rating') or '').strip().upper()
 system=str(event.get('rating_system') or '').strip().upper()
 fsk=re.fullmatch(r'(?:FSK[ -]*)?(0|6|12|16|18)',raw)
 if fsk and (system=='FSK' or raw.startswith('FSK')):return 'FSK '+fsk.group(1)
 if re.fullmatch(r'TV-(?:Y|Y7|Y7-FV|G|PG|14|MA)',raw):return raw
 if system in ('BBFC','MPAA','MPA') and raw in ('U','PG','12','12A','15','18','R18','G','PG-13','R','NC-17'):
  return system+' '+raw
 if re.fullmatch(r'(?:BBFC|MPAA|MPA) (?:U|PG|12|12A|15|18|R18|G|PG-13|R|NC-17)',raw):return raw
 return ''

def metadata(event):
 """Bounded source facts, no title/description replacement or network calls."""
 result={}
 if isinstance(event.get('agent_art'),dict):result['agent_art']=event['agent_art']
 rating=age_rating(event)
 if rating:result['age_rating']=rating
