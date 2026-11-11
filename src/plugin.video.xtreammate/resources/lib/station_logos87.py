"""Station-only sources and read-only reuse of Kodi's decoded texture cache.

Called by the existing provider worker. Reserve failure cannot revoke an
already decoded image. No image database, new thread or URL-policy bypass.
"""
import hashlib,json,os,time
PREFIX='XCMate.Logos87.'
_seen={};_cursor={};_keys=[]
def source(row):
 # Xtream/M3U logo fields precede every generic artwork field. Some legacy
 # live DTOs contain only cover; reject that fallback when movie fields exist.
 for field in ('stream_icon','logo','tvg_logo'):
  if isinstance(row.get(field),str) and row[field]:return row[field]
 if not any(row.get(k) for k in ('movie_image','cover_big','poster')):
  return row.get('cover') if isinstance(row.get('cover'),str) else ''
 return ''
def blocked_reason(portal,uri):
 from urllib.parse import urlsplit,unquote
 try:
  parts=urlsplit(uri);path=unquote(parts.path)
  if parts.username is not None or parts.password is not None or not __import__('programme_url77').public_query(parts.query):return 'AUTH_SCOPE'
  if any(value and (value in path.split('/') or len(value)>=4 and value in path) for value in (str(portal.get('xc_user') or ''),str(portal.get('xc_pass') or ''))):return 'AUTH_SCOPE'
 except (ValueError,TypeError):pass
 return 'URL_SCHEME_OR_HOST_BLOCKED'

def sources(row,provider_only=True):
 value=source(row)
 return dict(poster=value) if value else {}
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def note(portal,row,code,**facts):
 if code not in ('SOURCE_MISSING','URL_SCHEME_OR_HOST_BLOCKED','AUTH_SCOPE','LEASE_PENDING','DOWNLOAD_FAILED','IMAGE_INVALID','STORAGE_RESERVE_BLOCKED','LOCAL_READY','TEXTURE_CACHED','DECODED_RAM_READY','PERSISTED_VERIFIED'):return
 from logo_manifest86 import key
 tag=key(portal,row);now=time.monotonic();slot=(tag,code)
 if now-_seen.get(slot,-1e9)<60:return
 _seen[slot]=now
 while len(_seen)>512:_seen.pop(next(iter(_seen)))
 value=dict(station=tag,code=code,**{k:v for k,v in facts.items() if k in ('reserve','budget','free','ms') and type(v) in (int,float)})
 window().setProperty(PREFIX+'Last',json.dumps(value,separators=(',',':')))
 import xbmc
 try:xbmc.log('[XCMate][LOGO87] '+json.dumps(value,separators=(',',':')),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass
 # TEXTURE_CACHED is decode evidence, never a TEXTURE_VISIBLE/pixel claim.
def read(portal,rows):
 from logo_manifest86 import key
 result={};win=window()
 for row in rows:
  try:
   raw=win.getProperty(PREFIX+key(portal,row));data=json.loads(raw) if raw and len(raw)<2048 else {}
   file=data.get('file','')
   if not os.path.isabs(file) or os.path.islink(file):continue
   stat=os.stat(file)
   if data.get('stamp')==[stat.st_mtime_ns,stat.st_size] and data.get('source_hash')==hashlib.sha256(source(row).encode()).hexdigest():result[str(row['sid'])]=file
  except (OSError,ValueError,TypeError):continue
 return result

def recover(portal,rows,cancel=lambda:False):
 """One bounded Kodi query; fully decode only exact source-addressed files."""
 from widget_assets69 import safe
 from widget_cache82 import variants,decoded
 from logo_manifest86 import key
 import xbmc
 scope=__import__('logo_manifest86').context(portal);offset=_cursor.get(scope,5)
 ordered=rows[:5]+rows[offset:offset+5];_cursor[scope]=offset+5 if offset+5<len(rows) else 5
 while len(_cursor)>16:_cursor.pop(next(iter(_cursor)))
 selected=[r for r in ordered if source(r) and safe(portal,source(r))]
 if not selected or cancel():return
 wanted=list(dict.fromkeys(v for row in selected for v in variants(source(row))))
 try:
  raw=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=87,method='Textures.GetTextures',params=dict(filter={'or':[dict(field='url',operator='is',value=v) for v in wanted]},properties=['url','cachedurl','sizes']))))
  if not isinstance(raw,str) or len(raw)>262144:return
  records=json.loads(raw).get('result',{}).get('textures',[])
  if not isinstance(records,list):return
  for row in selected:
   if cancel():return
   uri=source(row)
   for record in records[:32]:
    if not isinstance(record,dict) or record.get('url') not in variants(uri):continue
    value=decoded(record,uri)
    if not value:continue
    stat=os.stat(value['file'])
    value=dict(file=value['file'],stamp=[stat.st_mtime_ns,stat.st_size],source_hash=hashlib.sha256(uri.encode()).hexdigest())
    slot=PREFIX+key(portal,row);window().setProperty(slot,json.dumps(value,separators=(',',':')))
    if slot not in _keys:_keys.append(slot)
    while len(_keys)>512:window().clearProperty(_keys.pop(0))
    note(portal,row,'TEXTURE_CACHED');break
 except (ValueError,TypeError,AttributeError,RuntimeError,OSError):return
