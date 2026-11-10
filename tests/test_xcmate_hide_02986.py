"""Explicit opt-out beats automatic caches without deleting any original image."""
import importlib,io,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Hide86(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('media_overrides43');self.row=dict(kind='vod',sid='1',name='Synthetic film',cover='https://example.org/provider.jpg',year=2023)
 def test_explicit_hide_is_durable_reversible_and_preserves_old_image_bytes(self):
  from PIL import Image
  image=io.BytesIO();Image.new('RGB',(120,180),'blue').save(image,'PNG')
  self.m.save('p','vod','1',image=image.getvalue(),source='synthetic')
  root,file=self.m.paths('p');original={p:p.read_bytes() for p in (root/'images').iterdir()}
  self.assertTrue(self.m.hide86('p','vod','1'));row=self.m.apply_many('p',[self.row])[0];self.assertTrue(row['_no_art86'])
  with mock.patch('media_art.sources',side_effect=AssertionError('hidden source preparation')):self.assertFalse(any(__import__('media_art').local_art(row).values()))
  self.assertEqual({p:p.read_bytes() for p in (root/'images').iterdir()},original)
  self.m._cache.clear();self.m._versions.clear();self.assertTrue(self.m.apply_many('p',[self.row])[0]['_no_art86'])
  self.assertTrue(self.m.reset('p','vod','1'));self.assertNotIn('_no_art86',self.m.apply_many('p',[self.row])[0]);self.assertEqual({p:p.read_bytes() for p in (root/'images').iterdir()},original)
 def test_blocked_hide_cannot_change_existing_choice_file(self):
  self.m.hide86('p','vod','1');root,file=self.m.paths('p');before=file.read_bytes()
  with mock.patch('import_budget.check_space',side_effect=OSError('RESERVE_BLOCKED')):
   with self.assertRaises(OSError):self.m.hide86('p','vod','other')
  self.assertEqual(file.read_bytes(),before)
 def test_last_good_merge_cannot_resurrect_explicitly_hidden_provider_cover(self):
  item=dict(label='Film',url='plugin://movie',props={'XCMate.MediaId':'1','XCMate.NoImage86':'true'},art=dict(poster=''),info={})
  old=dict(source_revision74=1,items=[dict(item,art={'poster':'/verified/old.png'})])
  with mock.patch('home_publication74.source',return_value=1),mock.patch('home_publication74.source_refs',return_value={'1':'same'}),mock.patch('home_publication80.reconcile',side_effect=AssertionError('must not retain opted-out pictures')):
   rows,_=__import__('home_publication74').merge(self.portal,'vod',[item],[dict(self.row,_no_art86=True)],old)
  self.assertFalse(any(rows[0]['art'].values()))
 def test_epg_hide_beats_decoded_cache_and_lookup_before_any_art_io(self):
  event=dict(pid='p',sid='1',title='Monk',key='hidden',start=self.now,stop=self.now+1800,placeholder='/neutral.png')
  with mock.patch('programme_mapping85.current',return_value={'hidden':True}),mock.patch('artwork_temp85.lookup',side_effect=AssertionError('cache bypass')),mock.patch('programme_display84.recover',side_effect=AssertionError('cache bypass')),mock.patch('programme_urls55.probe',side_effect=AssertionError('network')):
   result=__import__('programme_urls55').resolve(event,allow_lookup=True,url_mode69=True)
  self.assertEqual(result['source'],'placeholder');self.assertEqual(result['code'],'NO_IMAGE')
 def test_context_key_opens_the_same_detail_menu_and_back_restores_focus(self):
  w=self.media_window();w._details(w.rows[0]);self.settle(w)
  with mock.patch.object(w,'_search',side_effect=AssertionError('context must not open search')):w.native(117)
  self.assertTrue(w._detail_menu_open);self.assertEqual(w.getFocusId(),810)
  w.native(92);self.assertFalse(w._detail_menu_open);self.assertEqual(w.getFocusId(),300)
 def test_deliberately_hidden_covers_do_not_report_pending_downloads(self):
  rows=[dict(self.row,_no_art86=True)]
  record=__import__('home_loading85').update(self.portal,'vod',rows,'READY',images=0,pending=True)
  self.assertEqual(record['state'],'READY');self.assertFalse(record['busy'])
