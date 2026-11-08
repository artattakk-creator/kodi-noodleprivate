"""Cross-interpreter negative receipts, writer admission, bounded UI waits."""
import importlib,json,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Pipeline80(Fixture,unittest.TestCase):
 def test_missing_channel_receipt_survives_interpreter_local_cache_loss(self):
  m=importlib.import_module('epg_poll79');row=dict(sid='1',epg_channel_id='xml');now=time.time();info=dict(now='',next='',next_start=0)
  m.remember('p',[row],{},now,True,{'1':info});m._values.clear()
  self.assertEqual(m.select('p',[row],{},now,True),({'1':info},[]))
 def test_stream_object_and_dictionary_use_same_exact_epg_key(self):
  from epg_poll77 import key
  channel=types.SimpleNamespace(tvg_id='xml',extra=dict(stream_id='1'))
  self.assertEqual(key('p',[channel],{},True),key('p',[dict(sid='1',epg_channel_id='xml')],{},True))
 def test_shared_negative_never_crosses_mapping_change(self):
  m=importlib.import_module('epg_poll79');row=dict(sid='1',epg_channel_id='xml');now=time.time()
  m.remember('p',[row],{},now,True,{'1':dict(now='',next='',next_start=0)});m._values.clear()
  self.assertEqual(m.select('p',[row],{'1':'different'},now,True)[1],[row])
 def test_own_writer_defers_then_recovers_without_sqlite_busy_or_schema_change(self):
  import programme_index46 as store
  from programme_writes69 import Deferred
  first=store.connect(True)
  try:
   with self.assertRaises(Deferred):store.connect(True)
   self.assertEqual(first.execute('PRAGMA user_version').fetchone()[0],1)
  finally:first.close()
  second=store.connect(True);self.assertEqual(second.execute('PRAGMA integrity_check').fetchone()[0],'ok');second.close()
 def test_ui_wait_has_finite_terminal_status_without_inventing_image(self):
  import programme_requests68 as requests
  event=dict(pid='p',sid='1',title='Synthetic',key='k',start=1,stop=time.time()+600)
  start=time.time()
  with mock.patch('time.time',return_value=start):requests.request(event)
  for elapsed in range(5,46,5):
   with mock.patch('time.time',return_value=start+elapsed):requests.request(event)
  with mock.patch('time.time',return_value=start+46):
   requests.request(event);self.assertEqual(requests.result(event).get('code'),'IMAGE_LOOKUP_TIMEOUT')
 def test_automatic_image_sources_never_wait_for_external_helper(self):
  import programme_sources57 as suppliers
  with mock.patch('utils.setting_bool',side_effect=lambda key,default=False: True),mock.patch('programme_helper57.lookup',side_effect=AssertionError('external helper in critical lane')):
   self.assertNotIn('helper',[getattr(fn,'source70','') for fn in suppliers.attempts(dict(title='Synthetic film',genre='Film'),critical80=True)])
 def test_description_escapes_are_normalized_and_cells_have_finite_width(self):
  import presentation80 as display
  self.assertEqual(display.text('First\\n\\nSecond'),'First\n\nSecond')
  self.assertEqual(display.clipped('Long programme title',5),'')
  self.assertLessEqual(len(display.clipped('Long programme title'*10,80)),5)
 def test_part_normalization_keeps_sequel_and_never_collapses_parts(self):
  from programme_title80 import key
  self.assertEqual(key('Die Tribute von Panem – Mockingjay (1)'),key('Die Tribute von Panem - Mockingjay Teil 1'))
  self.assertNotEqual(key('Mockingjay (1)'),key('Mockingjay (2)'))
  self.assertNotEqual(key('Film (2025)'),key('Film Teil 2025'))
 def test_independent_image_scopes_keep_all_88_logos_when_media_refreshes(self):
  import hashlib,widget_art44 as art,artwork_visible as visible
  rows={kind:[dict(kind=kind,sid=str(i),cover=f'https://images.example/{kind}-{i}.jpg') for i in range(88 if kind=='live' else 24)] for kind in ('live','vod','series')}
  def approve(url):visible._dns_cache[('images.example',443)]=(time.monotonic()+30,True);return True
  with mock.patch('artwork_config.persistent',return_value=False),mock.patch('media_art.request'),mock.patch.object(visible,'public_dns',side_effect=approve):
   for kind in rows:art.prepare('p',rows[kind])
  for kind in rows:
   self.assertEqual(len(art.read('p',kind)),len(rows[kind]))
   self.assertTrue(all(hashlib.sha256(row['cover'].encode()).hexdigest() in art.read('p',kind) for row in rows[kind]))
  self.assertEqual(len(art.read('p')),136)
 def test_explicit_retry_budget_is_consumed_once_not_reset_each_poll(self):
  import programme_deadline80 as deadline,xbmcgui
  from programme_refresh63 import KEY
  from epg_handoff63 import profile_scope
  now=time.time();previous=dict(since70=now-60);marker=dict(id='a'*32,profile=profile_scope(),at=now)
  xbmcgui.Window(10000).setProperty(KEY,json.dumps(marker))
  with mock.patch('time.time',return_value=now):deadline.retry_window(previous,{})
  self.assertEqual(previous['since70'],now)
  for elapsed in (5,30,46):
   record=dict(since70=previous['since70'])
   with mock.patch('time.time',return_value=now+elapsed):deadline.retry_window(record,previous)
   self.assertEqual(record['since70'],now);previous=record
 def test_non_posix_hosts_keep_bounded_native_sqlite_without_import_failure(self):
  import programme_write80 as writer
  with mock.patch.object(writer,'fcntl',None):
   db=writer.connect(str(self.folder/'non-posix.sqlite'))
   try:self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   finally:db.close()
