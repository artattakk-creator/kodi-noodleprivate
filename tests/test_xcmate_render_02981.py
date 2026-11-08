"""A1/A2/A3/A8: real files, expiry, profile/role isolation and source hysteresis."""
import importlib,io,json,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Render81(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.cache=importlib.import_module('render_cache81')
 def png(self,rgb=(20,80,130)):
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(160,90),rgb).save(out,'PNG');return out.getvalue()
 def test_88_logos_and_two_24_cover_rails_survive_expiry_three_cycles_and_restart(self):
  rows={kind:[dict(kind=kind,sid=str(i),cover=f'https://images.example/{kind}{i}.png') for i in range(88 if kind=='live' else 24)] for kind in ('live','vod','series')}
  with mock.patch('programme_art46.space'):
   for kind,items in rows.items():
    for row in items:self.cache.store(self.cache.identity(self.portal,kind,row,'poster',row['cover']),self.png())
  now=time.time()
  for delta in (330,660,990):
   with mock.patch('time.time',return_value=now+delta):
    for kind,items in rows.items():
     self.assertEqual(len(self.cache.references(self.portal,kind,items)),len(items))
  importlib.reload(self.cache)
  self.assertEqual(len(self.cache.references(self.portal,'live',rows['live'])),88)
 def test_scope_role_source_account_and_corruption_are_not_reused(self):
  row=dict(kind='vod',sid='1',cover='https://images.example/a.png');key=self.cache.identity(self.portal,'vod',row,'poster',row['cover'])
  with mock.patch('programme_art46.space'):value=self.cache.store(key,self.png())
  self.assertTrue(self.cache.read(key))
  self.assertFalse(self.cache.references(dict(self.portal,xc_user='different'),'vod',[row]))
  self.assertFalse(self.cache.references(self.portal,'series',[row]))
  self.assertFalse(self.cache.references(self.portal,'vod',[dict(row,cover='https://images.example/b.png')]))
  from pathlib import Path
  Path(value['file']).write_bytes(b'broken');self.assertIsNone(self.cache.read(key))
 def test_group_file_touch_and_unrelated_group_change_do_not_change_context(self):
  from widget_policy74 import signature
  from group_selection import save
  before=signature(self.portal,'vod');save('unrelated',['x'],'series')
  self.assertEqual(signature(self.portal,'vod'),before)
  save(self.portal['id'],['a'],'vod');self.assertNotEqual(signature(self.portal,'vod'),before)
 def test_same_event_lower_quality_never_replaces_tmdb_and_retry_does_not_write_image(self):
  import event_art81 as event
  e=dict(pid='p',sid='1',key='k',title='Synthetic movie',start=1,stop=time.time()+600,canonical='xml')
  base=dict(key='k',source='tmdb_movie',code='READY',until=time.time()+300,image='https://example.invalid/a')
  self.options.update(programme_tmdb46=True,tmdb_research43=True)
  with mock.patch('programme_art46.space'):first=event.commit(e,base,self.png())
  from pathlib import Path
  stamp=Path(first['image']).stat().st_mtime_ns
  for i in range(3):self.assertEqual(event.commit(e,dict(base,source='xmltv_event'),self.png((120,50,90)))['image'],first['image'])
  self.assertEqual(Path(first['image']).stat().st_mtime_ns,stamp)
  self.assertIsNone(event.prior(dict(e,start=2)))
  self.options['programme_tmdb_optout77']=True;self.assertIsNone(event.prior(e))
 def test_transport_only_keeps_body_when_explicit_worker_requests_it(self):
  import programme_transport77 as transport
  data=self.png()
  for keep in (False,True):
   body=io.BytesIO(data);response=mock.Mock(status=200,headers={'Content-Type':'image/png'},read=body.read)
   with mock.patch('image_redirect48.open_image',return_value=response):value=transport.verified('https://image.tmdb.org/t/p/w500/synthetic81.jpg',keep_data81=keep)
   self.assertEqual(value['width'],160);self.assertEqual(value['height'],90)
   if keep:self.assertEqual(value['_body81'],data)
   else:self.assertNotIn('_body81',value)
   response.close.assert_called_once()

 def test_android_storage_root_alias_is_allowed_but_links_below_texture_root_are_not(self):
  from pathlib import Path
  import widget_cache79 as cache,xbmcvfs
  actual=self.folder/'storage';actual.mkdir();textures=actual/'Thumbnails';textures.mkdir();image=textures/'image.jpg';image.write_bytes(self.png())
  alias=self.folder/'android_alias';alias.symlink_to(actual,target_is_directory=True)
  with mock.patch.object(xbmcvfs,'translatePath',return_value=str(alias/'Thumbnails')):
   self.assertTrue(cache.permitted(str(alias/'Thumbnails'/'image.jpg')))
   linked=textures/'linked';linked.symlink_to(textures,target_is_directory=True)
   self.assertFalse(cache.permitted(str(linked/'image.jpg')))
 def test_reserve_budget_and_real_capacity_remain_distinct_and_backed_off(self):
  from pathlib import Path
  from art_storage import ArtworkFailure
  from programme_art46 import CacheBudget
  source=self.folder/'input81.png';source.write_bytes(self.png());row=dict(sid='1',kind='vod',name='Synthetic',cover='https://image.tmdb.org/t/p/w500/input81.png')
  for error,code in ((CacheBudget('PROGRAMME_CACHE_BUDGET'),'PROGRAMME_CACHE_BUDGET'),(ArtworkFailure('DISK_FULL','RESERVE_BLOCKED',dict(free=500,reserve=1024)),'RESERVE_BLOCKED'),(ArtworkFailure('DISK_FULL','BLOCKED_REAL_DISK'),'BLOCKED_REAL_DISK')):
   self.cache._due.clear()
   with mock.patch.object(self.cache,'store',side_effect=error) as store,mock.patch('media_art.cached',return_value=str(source)),mock.patch('art_trace81.note') as trace:
    self.cache.prepare(self.portal,'vod',[row]);self.cache.prepare(self.portal,'vod',[row])
   self.assertEqual(store.call_count,1);self.assertEqual(trace.call_args.args[2],code);self.assertTrue(source.exists())
 def test_legacy_event_without_source_key_is_invalidated_by_real_source_or_subtitle_change(self):
  import event_art81 as event
  self.options.update(programme_tmdb46=True,tmdb_research43=True)
  e=dict(pid='p',sid='1',key='legacy',title='Synthetic series',subtitle='Episode A',epg_source46='xml-source-a',start=1,stop=time.time()+600,canonical='cid')
  value=dict(key='legacy',source='tmdb_series',code='READY',until=time.time()+300)
  with mock.patch('programme_art46.space'):event.commit(e,value,self.png())
  self.assertIsNotNone(event.prior(e));self.assertIsNone(event.prior(dict(e,epg_source46='xml-source-b')));self.assertIsNone(event.prior(dict(e,subtitle='Episode B')))
