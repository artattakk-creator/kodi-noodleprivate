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

def describe(portal,channel,event=None,canonical='',revision=None,guide=None,*,local_read=True):
 event=dict(event or {});pid=str(portal['id']);sid=str(channel.get('sid',channel.get('stream_id','')))
 value=dict(pid=pid,sid=sid,channel=str(channel.get('name','')),start=int(event.get('start',0)),stop=int(event.get('stop',0)),title=str(event.get('title') or event.get('name') or '')[:512],description=str(event.get('description') or event.get('descr') or '')[:8192],source=int(event.get('source',event.get('_source_index',0))),canonical=str(canonical),revision=revision)
 for name in ('source_key46','fact_revision46','_agent_generation103','_agent_event104','_agent_images104',
              '_agent_channel104','_agent_start104','_agent_stop104'):
  if event.get(name):value[name]=event[name]
 value['key']=key(pid,sid,value)
 if value['start']>0 and value['stop']>value['start'] and value['title']:
  from programme_flow48 import source_metadata
  prepared46=None
  if local_read and not (event.get('_agent_event104') and event.get('_metadata_verified48')):
   from programme_index46 import event as prepared_event46,metadata as prepared_metadata46
   prepared46=prepared_event46(value) if guide is None else None
  if prepared46:value.update(prepared46)
  else:
   value.update(source_metadata(event))
   if local_read and not event.get('_metadata_verified48'):
    from programme_store46 import read
    value.update(prepared_metadata46(pid,canonical,value,guide) or read(pid,canonical,value,guide,verify_source=revision is not None))
  if local_read and not value.get('metadata_code46') and not event.get('_metadata_verified48') and not any(value.get(k) for k in ('xmltv_image','provider_image','subtitle','season','agent_art')):value.update(legacy_metadata(pid,sid,canonical,value))
  if not value.get('epg_source46'):
   origin=value.get('source_key46')
   if origin or value['source']==0:value['epg_source46']=origin or 'provider'
  value['code']='LOCAL_EVENT'
 else:value.update(start=0,stop=0,title='',code='NO_EPG')
 from programme_flow48 import trace
 trace('LOCAL_EVENT',value,value.get('code','NO_EPG'))
 trace('MATCH',value,'READY' if value.get('epg_source46') else 'NO_SOURCE_FACTS')
 from agent_programme100 import source_status
 value['art_source_code104']=source_status(value)
 trace('SOURCE',value,value['art_source_code104'])
 value['key']=key(pid,sid,value);value['placeholder']=placeholder(value)
 value['details_url']='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='programme_details46',pid=pid,sid=sid,start=value['start'],stop=value['stop'],event=value['key'],source=value.get('source_key46','')))
 return value

def from_info(portal,channel,info,*,local_read=True):
 event=next((v for v in info.get('events',[]) if v['start']==info.get('start') and v['stop']==info.get('stop') and v['title']==info.get('now')),None)
 # A missing published event never turns a next-show or stale image into NOW.
 canonical=(event or {}).get('canonical46') or info.get('canonical46') or (event or {}).get('_canonical') or info.get('epg_id','')
 return describe(portal,channel,event,canonical,info.get('snapshot_revision'),local_read=local_read)

def visible(portal,channel,info):
 """Build the same event from published Now/Next facts without local storage reads."""
 return from_info(portal,channel,info,local_read=False)

def load(portal,channel,selected=None,now=None):
 from local_epg import window,channel_keys
 from epg_sources import configuration
 now=time.time() if now is None else now;mappings=configuration(portal['id']).get('mappings',{})
 moment=selected.get('start',now) if selected else now
 view=window(portal['id'],[channel],mappings,moment,moment+2*86400,limit=48,budget=.15)
 sid,ids=channel_keys(channel,mappings);event=None;canonical='';following=[];preceding=None
 if view is not None:
  for ident in ids:
   rows=view.get(ident,[])
   if not rows:continue
   canonical=view.canonical.get(ident,ident)
   for raw in rows:
    candidate=dict(raw,title=raw['name'],description=raw['descr'],start=raw['start_timestamp'],stop=raw['stop_timestamp'],source=raw.get('source',raw.get('_source_index',0)))
    if selected:
     if selected.get('source_key46') and selected['source_key46']!=candidate.get('source_key46'):continue
     if candidate['start']==int(selected.get('start',0)) and candidate['stop']==int(selected.get('stop',0)) and (not selected.get('title') or candidate['title']==selected['title']):event=candidate;break
    elif candidate['start']<=now<candidate['stop']:event=candidate;break
   if event is not None:
    canonical=event.get('canonical46') or event.get('_canonical') or canonical
    source=event.get('source_key46')
    def same_source(row):
     if source:return row.get('source_key46')==source
     return row.get('source',row.get('_source_index',0))==event['source']
    def schedule_row(row):
     return dict(start=row['start_timestamp'],stop=row['stop_timestamp'],title=row['name'])
    following=[schedule_row(row) for row in rows if row['start_timestamp']>=event['stop']
               and same_source(row) and row.get('name')][:3]
    prior=None if selected and selected.get('_art_view499') else window(portal['id'],[channel],mappings,event['start']-3*3600,event['start'],limit=48,budget=.08)
    if prior is not None and getattr(prior,'revision',None)==getattr(view,'revision',None):
     previous=[row for row in prior.get(ident,[]) if row['stop_timestamp']<=event['start']
               and same_source(row) and row.get('name')]
     if previous:preceding=schedule_row(max(previous,key=lambda row:row['stop_timestamp']))
    break  # Expired/future aliases cannot mask a valid current provider row.
 # An existing source/mapping/revision-checked Now/Next snapshot is local
 # authority during a short SQLite outage, not a guessed short-cache event.
 if event is None:
  from epg_handoff63 import get as handoff85
  info85=handoff85(portal['id'],sid,now=now,mappings=mappings)
  if info85:
   saved85=next((v for v in info85.get('events',[]) if (int(v['start'])==int(selected.get('start',0)) and int(v['stop'])==int(selected.get('stop',0)) if selected else v['start']<=now<v['stop']) and (not selected or not selected.get('title') or v['title']==selected['title'])
                 and (not selected or not selected.get('source_key46') or
                      selected['source_key46']==v.get('source_key46'))),None)
   if saved85:
    return describe(portal,channel,dict(saved85,_metadata_verified48=True),info85.get('canonical46',''),info85.get('snapshot_revision'))
 # Locally supplied legacy short-cache text remains usable offline, labelled.
 if event is None and selected and selected.get('title') and int(selected.get('stop',0))>int(selected.get('start',0)):
  event=dict(selected);canonical='';view=None
 result=describe(portal,channel,event,canonical,getattr(view,'revision',None))
 if following:result['following46']=following
 if preceding:result['preceding46']=preceding
 if event and view is None:
  result['code']='CACHED_EVENT';result['read_code69']=__import__('epg_read69').last(portal['id'],sid)
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
 for name in ('genre','year','age_rating','director'):
  if event.get(name):lines.append(str(event[name]))
 if event.get('cast'):lines.append(tr(36104)+': '+', '.join(event['cast']))
 if event.get('description'):lines+=['',event['description']]
 return __import__('presentation80').text('\n'.join(lines))

def source_name(portal,event):
 from guide_publish44 import source_id
 from epg_sources import configuration
 from localization import tr
 if not event.get('title'):return ''
 source=event.get('source_key46') or event.get('epg_source46')
 if source=='agent':return __import__('epg_agent100').SOURCE_NAME
 if source=='provider':return tr(32555)
 if isinstance(source,str) and source.startswith('external:'):
  for rank,row in enumerate(configuration(portal['id']).get('sources',()),1):
   if source_id(row,rank)==source:return str(row.get('name') or 'XMLTV')[:96]
  return 'XMLTV'
 rank=event.get('source')
 if rank==-1 or rank==0 and event.get('canonical'):return tr(32555)
 return 'XMLTV' if isinstance(rank,int) and rank>0 else ''


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
