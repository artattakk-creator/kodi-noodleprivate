"""Shared, read-only programme identity for grid details and all Live cards."""
import hashlib,os,time
from urllib.parse import urlencode

def key(pid,sid,event):
 from programme_store46 import title_hash
 return hashlib.sha256((str(pid)+'|'+str(sid)+'|'+str(int(event.get('start',0)))+'|'+str(int(event.get('stop',0)))+'|'+title_hash(event.get('title',''))).encode()).hexdigest()

def placeholder(event):
 from programme_store46 import title_hash
 genre=str(event.get('genre','')).casefold()
 kind='news' if any(v in genre for v in ('nachricht','news')) else 'talk' if 'talk' in genre else 'series' if event.get('season') and event.get('episode') else 'movie' if any(v in genre for v in ('film','movie')) else 'neutral'
 return os.path.join(os.path.dirname(os.path.dirname(__file__)),'media','programme46',kind+'.png')

def describe(portal,channel,event=None,canonical='',revision=None,guide=None):
 from programme_store46 import read
 event=dict(event or {});pid=str(portal['id']);sid=str(channel.get('sid',channel.get('stream_id','')))
 value=dict(pid=pid,sid=sid,channel=str(channel.get('name','')),start=int(event.get('start',0)),stop=int(event.get('stop',0)),title=str(event.get('title') or event.get('name') or '')[:512],description=str(event.get('description') or event.get('descr') or '')[:8192],source=int(event.get('source',event.get('_source_index',0))),canonical=str(canonical),revision=revision)
 for name in ('source_key46','fact_revision46'):
  if event.get(name):value[name]=event[name]
 value['key']=key(pid,sid,value)
 if value['start']>0 and value['stop']>value['start'] and value['title']:
  from programme_index46 import event as prepared_event46,metadata as prepared_metadata46
  prepared46=prepared_event46(value) if guide is None else None
  value.update(prepared46 or prepared_metadata46(pid,canonical,value,guide) or read(pid,canonical,value,guide,verify_source=revision is not None))
  if not value.get('metadata_code46') and not any(value.get(k) for k in ('xmltv_image','provider_image','subtitle','season')):value.update(legacy_metadata(pid,sid,canonical,value))
  value['code']='LOCAL_EVENT'
 else:value.update(start=0,stop=0,title='',code='NO_EPG')
 value['key']=key(pid,sid,value);value['placeholder']=placeholder(value)
 value['details_url']='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='programme_details46',pid=pid,sid=sid,start=value['start'],stop=value['stop'],event=value['key']))
 return value

def from_info(portal,channel,info):
 event=next((v for v in info.get('events',[]) if v['start']==info.get('start') and v['stop']==info.get('stop') and v['title']==info.get('now')),None)
 # A missing published event never turns a next-show or stale image into NOW.
 return describe(portal,channel,event,info.get('canonical46') or info.get('epg_id',''),info.get('snapshot_revision'))

def load(portal,channel,selected=None,now=None):
 from local_epg import window,channel_keys
 from epg_sources import configuration
 now=time.time() if now is None else now;mappings=configuration(portal['id']).get('mappings',{})
 moment=selected.get('start',now) if selected else now
 view=window(portal['id'],[channel],mappings,moment,moment+2*86400,limit=48,budget=.15)
 sid,ids=channel_keys(channel,mappings);event=None;canonical=''
 if view is not None:
  for ident in ids:
   rows=view.get(ident,[])
   if not rows:continue
   canonical=view.canonical.get(ident,ident)
   for raw in rows:
    candidate=dict(raw,title=raw['name'],description=raw['descr'],start=raw['start_timestamp'],stop=raw['stop_timestamp'],source=raw.get('source',raw.get('_source_index',0)))
    if selected:
     if candidate['start']==int(selected.get('start',0)) and candidate['stop']==int(selected.get('stop',0)) and (not selected.get('title') or candidate['title']==selected['title']):event=candidate;break
    elif candidate['start']<=now<candidate['stop']:event=candidate;break
   break
 # Locally supplied legacy short-cache text remains usable offline, labelled.
 if event is None and selected and selected.get('title') and int(selected.get('stop',0))>int(selected.get('start',0)):
  event=dict(selected);canonical='';view=None
 result=describe(portal,channel,event,canonical,getattr(view,'revision',None))
 if event and view is None:result['code']='CACHED_EVENT'
 if selected and selected.get('key') and selected['key']!=result['key']:return describe(portal,channel)
 return result

def summary(event,now=None):
 from localization import tr
 now=time.time() if now is None else now
 lines=[event['channel'],event.get('title') or tr(36102)]
 if event.get('start'):
  lines.append(time.strftime('%d.%m. %H:%M',time.localtime(event['start']))+' – '+time.strftime('%H:%M',time.localtime(event['stop']))+' · '+str(max(1,(event['stop']-event['start'])//60))+' min')
 if event.get('subtitle'):lines.append(event['subtitle'])
 if event.get('season') and event.get('episode'):lines.append(tr(36103,event['season'],event['episode']))
 elif event.get('episode_label'):lines.append(event['episode_label'])
 for name in ('genre','year'):
  if event.get(name):lines.append(str(event[name]))
 if event.get('cast'):lines.append(tr(36104)+': '+', '.join(event['cast']))
 if event.get('description'):lines+=['',event['description']]
 return '\n'.join(lines)


def legacy_metadata(pid,sid,canonical,event):
 """Bounded lookup in an already loaded legacy cache, never disk/network/import."""
 try:
  from epg import _mem_get
  from programme_store46 import metadata,title_hash
  cache=_mem_get(pid)
  if not isinstance(cache,dict):return {}
  for ident in dict.fromkeys((canonical,sid)):
   rows=cache.get(ident,[])
   if not isinstance(rows,list):continue
   for raw in rows[:256]:
    if not isinstance(raw,dict):continue
    if int(raw.get('start_timestamp',0))==event['start'] and int(raw.get('stop_timestamp',0))==event['stop'] and title_hash(raw.get('name'))==title_hash(event['title']) and int(raw.get('_source_index',0))==event['source']:return metadata(raw)
 except (ImportError,ValueError,TypeError,AttributeError):pass
 return {}
