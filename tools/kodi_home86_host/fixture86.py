""".85 synthetic source-side proposal flag; never part of the shipped addon."""
from pathlib import Path
base85=Path('/base_fixture84.py').read_text().replace("if __name__=='__main__':run()",'')
base85=base85.replace("icon=BASE+'event84-'+str(i)+'.png'","icon='' if i==3 else BASE+'event84-'+str(i)+'.png'")
exec(compile(base85,'/base_fixture84.py','exec'),globals())
install84=install
def install():
 install84()
 # Metadata identity is synthetic; image transport, Kodi decode and pixels are real.
 import programme_match46,download_redirect
 def addresses86(url):
  from urllib.parse import urlsplit
  parts=urlsplit(url)
  if parts.scheme=='https' and parts.hostname=='image.tmdb.org' and parts.port in (None,443) and parts.path.startswith(('/t/p/w500/','/t/p/w1280/','/t/p/original/')):return ['127.0.0.1']
  raise AssertionError('UNEXPECTED_SYNTHETIC86_ORIGIN')
 download_redirect.addresses=addresses86
 def candidate86(event,cancel=lambda:False):
  ident=str(event.get('sid',''))
  if not ident.isdigit():return None
  return dict(url=BASE+('official86-' if ident=='3' else 'event84-')+ident+'.png',source='tmdb_movie',role81='poster' if ident=='3' else 'backdrop',match='EXACT_TITLE_YEAR',remote_id=860000+int(ident),matched_year56=2024,attribution='TMDB · synthetic metadata identity / NOT Android')
 programme_match46.candidate=candidate86
 addon=xbmcaddon.Addon();addon.setSetting('programme_tmdb46','true');addon.setSetting('tmdb_research43','true')

# P0-F instrumentation is restricted to the disposable navigation fixture.
# Production default.py, Router, WindowXML, owner pump and Back remain real.
run86=run
def run():
 from urllib.parse import parse_qs
 import sys,time,json
 sequence=parse_qs(sys.argv[2].lstrip('?')).get('nav86',[''])[0]
 if not sequence:return run86()
 assert sequence.isdigit() and 0<=int(sequence)<100
 install()
 from utils import cache_set
 from xtream import XtreamClient
 from portals import get_active
 portal=get_active()[0];client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
 for action,extra,value in (
  ('get_vod_info',{'vod_id':'0'},{'info':{'plot':'Synthetic cached detail','duration_secs':2700}}),
  ('get_series_info',{'series_id':'0'},{'info':{'plot':'Synthetic cached series'},'episodes':{'1':[{'id':'101','episode_num':1,'title':'Synthetic episode'}]}})):
  cache_set(client._cache_key(action,extra),value)
 from media_window import MediaView
 original_pump=MediaView.pump
 def pump86(view):
  result=original_pump(view)
  xbmcgui.Window(10000).setProperty('XCMate.Nav86.State',json.dumps(dict(sequence=sequence,mode=view.mode,kind=view.kind,closed=view._closed,generation=view._generation,actions=len(getattr(view,'actions',[])),rows=len(view.rows),focus=view.getFocusId())))
  return result
 MediaView.pump=pump86
 started=time.monotonic()
 try:return run86()
 finally:Path('/root/nav86-route-'+sequence+'.json').write_text(json.dumps(dict(sequence=sequence,returned=True,elapsed_ms=int((time.monotonic()-started)*1000))))

if __name__=='__main__':run()
