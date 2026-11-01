"""Provider-only series diagnosis; URI approval never claims decoded pixels."""
import os,time
_seen={}
CODES=frozenset(('SERIES_PROVIDER_ART_MISSING','SERIES_ART_URI_REJECTED','SERIES_ASSET_CACHE_MISS','SERIES_TEXTURE_DECODE_FAIL','SERIES_WIDGET_BINDING_MISMATCH','SERIES_ART_URI_READY'))
def inspect(row,image,expected='series',decoded=None):
 if expected!='series' or row.get('kind') in ('live','vod'):return 'SERIES_WIDGET_BINDING_MISMATCH'
 from media_art import sources
 from artwork_visible import syntactic
 raw=[row.get(k) for k in ('cover','stream_icon','movie_image','cover_big') if row.get(k)]
 if not raw:return 'SERIES_PROVIDER_ART_MISSING'
 source=sources(row)[0]
 if not source or not syntactic(source):return 'SERIES_ART_URI_REJECTED'
 if decoded is False:return 'SERIES_TEXTURE_DECODE_FAIL'  # Only explicit confirmed decode evidence.
 selected=image.get('poster','')
 if not selected or os.path.basename(selected)=='series.png':return 'SERIES_ASSET_CACHE_MISS'
 return 'SERIES_ART_URI_READY'
def note(code):
 if code not in CODES:return
 now=time.monotonic()
 if now-_seen.get(code,-100)<60:return
 _seen[code]=now
 try:
  import xbmc
  xbmc.log('[XCMate][SERIES64] code='+code+' decode=NOT_VERIFIED',xbmc.LOGINFO)
 except (ImportError,AttributeError,RuntimeError):pass
