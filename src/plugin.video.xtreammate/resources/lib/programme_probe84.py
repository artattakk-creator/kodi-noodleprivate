"""Worker-only explicit exact-event probe. No credential/title/URL diagnostics."""
import time

def inspect(portal,cancel=lambda:False):
 from utils import setting_bool
 from tmdb_token61 import effective_tmdb_read_token,TokenError
 from tmdb_connection60 import test_connection
 from library_index import Reader
 from programme_events46 import load
 rows=[('CLOCK',time.strftime('%Y-%m-%d %H:%M:%S %Z'))]
 enabled=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
 rows.extend([('TMDB_ENABLED','YES' if enabled else 'NO'),('OPT_OUT','YES' if setting_bool('programme_tmdb_optout77',False) else 'NO')])
 try:present=bool(effective_tmdb_read_token())
 except TokenError:present=False
 rows.append(('TOKEN_READABLE','YES' if present else 'NO'))
 if cancel():return rows+[('PROBE','CANCELLED')]
 if not enabled or not present or setting_bool('programme_tmdb_optout77',False):return rows+[('MATCH','DISABLED_OR_NO_TOKEN')]
 rows.append(('API_CONFIGURATION',test_connection(cancel)))
 reader=Reader(portal['id'])
 try:channel=reader.get('live',str(portal.get('start_stream_id') or ''))
 finally:reader.close()
 if not channel:return rows+[('EVENT','NO_START_CHANNEL')]
 event=load(portal,channel)
 if not event.get('title'):return rows+[('EVENT','NO_LOCAL_EPG')]
 from art_trace81 import own
 from programme_match46 import candidate
 from media_sources43 import SourceError
 try:
  found=own(event,lambda:candidate(event,cancel))
  if not found:return rows+[('MATCH','NO_CONFIRMED_MATCH')]
  rows.append(('MATCH','EXACT_REFERENCE'))
  # Use the existing secure resolver and full decode; not a new URL client.
  from programme_urls55 import resolve
  result=resolve(event,allow_lookup=True,match=lambda *a,**k:found,url_mode69=True,cancel=cancel)
  rows.extend([('IMAGE_DECODE','YES' if result.get('decoded77') else 'NO'),('DISPLAY_LEASE','READY' if __import__('programme_image69').eligible(result,event) else 'BLOCKED')])
  from programme_requests68 import completed
  completed(event,result)
  rows.append(('GUI_TEXTURE','NOT_VERIFIED_OPEN_SAME_EVENT'))
 except SourceError as error:
  rows.append(('PROBE',error.code if error.code in ('TIMEOUT','HTTP_AUTH','HTTP_RATE_LIMIT','HTTP_NOT_FOUND','IMAGE_PREFLIGHT_FAILED','NO_MATCH','NO_ARTWORK','NO_MATCH_AMBIGUOUS') else 'SOURCE_ERROR'))
 return rows

def report(portal,cancel=lambda:False):
 from artwork_inventory84 import measure
 rows=inspect(portal,cancel)
 inventory=measure()
 return '\n'.join(k+': '+v for k,v in rows)+'\n\nREAD_ONLY_CACHE_BYTES\n'+'\n'.join(k+': '+str(v['bytes'])+' B / '+str(v['files'])+' / '+v['code'] for k,v in inventory.items())+'\n\nAndroid-Bildanzeige: NOT_TESTED. Cache-Inventur nur lesend; kein Datenreset.'
