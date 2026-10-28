import contextlib,importlib,io,json,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'tests'))
import xcmate027_fixture as fixture
fixture.ROOT=root;fixture.ADDON=root/'src/plugin.video.xtreammate';fixture.LIB=fixture.ADDON/'resources/lib'
class Model(fixture.Fixture,unittest.TestCase):pass
m=Model();m.setUp()
try:
 g=importlib.import_module('guide_store');se=importlib.import_module('stream_epg');g.connect().close()
 config=dict(mappings={},sources=[dict(id='other',uri='https://fixture.invalid/other',enabled=True)])
 sys.modules['epg_sources'].configuration=lambda pid:config
 sys.modules['epg_sources']._channel_name_key=lambda value:str(value).casefold()
 channel=dict(sid='1',name='Station',epg_channel_id='a',kind='live')
 def put(cid,days,rank=0,rich=False):
  stamp=lambda ts:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(ts))
  events=[]
  for day in days:
   start=m.now-60 if day==0 else g.day_window(day,m.now)[0]+3600
   events.append('<programme channel="'+cid+'" start="'+stamp(start)+'" stop="'+stamp(start+1800)+'"><title>Programme '+str(day)+'</title><desc>'+('Rich details' if rich else '')+'</desc></programme>')
  raw=('<tv><channel id="'+cid+'"><display-name>Station</display-name></channel>'+''.join(events)+'</tv>').encode()
  @contextlib.contextmanager
  def stream(*args,**kw):yield io.BytesIO(raw)
  with mock.patch.object(se,'source_stream',stream):se.import_source('p',dict(config['sources'][0] if rank else {},uri='https://fixture.invalid/feed'),rank,[channel],{})
 def titles():
  db=sqlite3.connect(g.path())
  try:return [r[0] for r in db.execute('SELECT title FROM programmes ORDER BY start')]
  finally:db.close()
 started=time.perf_counter();put('a',[-7,0,11,20,21]);initial=titles();put('a',[0]);short=titles();put('b',[0,1],1,True)
 from local_epg import window
 rows=window('p',[channel],{},m.now,m.now+2*86400)['a'];epg=dict(initial=initial,after_shorter=short,now_description=rows[0]['descr'],shown_events=[r['name'] for r in rows],elapsed_ms=round((time.perf_counter()-started)*1000,3))
 groups=importlib.import_module('group_selection');delta=importlib.import_module('catalog_delta')
 m.portal['include_series']=True;groups.save('p',['b'],'series',known=['a','b'])
 db=m.index.connect(write=True)
 with db:
  for table in ('titles','heads','items_v2','catalog','groups','sync_status'):db.execute('DELETE FROM '+table+" WHERE pid='p' AND kind='series'")
 db.close();calls=[]
 client=type('Client',(),{})();client.get_cached_catalog=lambda action:[];client._get_json=lambda *a,**k:[dict(category_id='b',category_name='Series B')]
 def entries(action,cid,**kw):
  calls.append(cid)
  yield from [dict(series_id='b'+str(i),name='Series '+str(i),category_id='b',cover='https://images.invalid/'+str(i)+'.png') for i in range(7)]
 client.iter_catalog=entries
 with mock.patch.object(sys.modules['xtream'],'XtreamClient',return_value=client):
  delta.request(m.portal,'series','b');delta.run_next()
 from widget_data41 import snapshot
 series,code=snapshot(m.portal,'series',background=True)
 print(json.dumps(dict(source=sys.argv[2],epg=epg,series=dict(job=delta.states('p','series')[0]['code'],catalogue=m.index.Reader('p').page('series')[1],widget=len(series),widget_code=code,provider_groups=calls))))
finally:m.doCleanups()
