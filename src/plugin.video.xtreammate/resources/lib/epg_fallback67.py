"""Worker-only bounded last-good fallback; never blesses a new guide revision."""
def window(pid,channels,mappings,start,stop,limit):
 from local_epg import View,channel_keys
 from epg_handoff63 import get
 view=View();view.code='RAM_LASTGOOD67'
 for channel in channels[:16]:
  sid,keys=channel_keys(channel,mappings)
  info=get(pid,sid,now=start,mappings=mappings,_previous_guide67=True)
  if not info:continue
  rows=[dict(e) for e in info.get('events',[]) if e.get('stop',0)>start and e.get('start',0)<stop][:min(256,limit)]
  for ident in keys:
   view[ident]=rows;view.canonical[ident]=info.get('canonical46') or info.get('epg_id','')
 return view if any(view.values()) else None
