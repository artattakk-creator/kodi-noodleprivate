"""End-to-end deadlines, API previews, real atomic mapping and cold recovery."""
import importlib,json,threading,unittest
from unittest import mock
from types import SimpleNamespace
from xcmate027_fixture import Fixture
class Manual89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.q=importlib.import_module('work_requests86');self.m=importlib.import_module('programme_mapping85');self.event=dict(pid='p',sid='1',title='Monk',canonical='xml',start=self.now,stop=self.now+3600)
  self.candidate=dict(source='tmdb',id=1695,title='Monk',year=2002,media_type86='tv',verified85=True,url='https://image.tmdb.org/t/p/w1280/monk.png',poster='https://image.tmdb.org/t/p/w500/monk.png',role='backdrop')
  self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC_89_NOT_TOKEN',programme_tvmaze67=True)
 def test_authoritative_uses_actual_reader_interface_and_harmless_revision_refresh(self):
  from library_index import Reader
  self.assertFalse(hasattr(Reader,'close'))
  class ActualInterface:
   def __init__(self,pid):pass
   def get(self,kind,sid):return dict(sid=sid,name='Station')
  current=dict(self.event,code='LOCAL_EVENT',revision='harmless-new')
  with mock.patch('portals.get_by_id',return_value=self.portal),mock.patch('library_index.Reader',ActualInterface),mock.patch('programme_events46.load',return_value=current):
   self.assertEqual(self.q.authoritative(self.event,self.q.binding(self.event))['revision'],'harmless-new')
   with self.assertRaisesRegex(Exception,'EPG_REVISION_CHANGED'):self.q.authoritative(dict(self.event,title='Other work'),self.q.binding(self.event))
 def test_one_search_api_call_eight_previews_no_detail_or_image_fetch_before_selection(self):
  row=dict(id=1,name='Monk',first_air_date='2002-01-01',poster_path='/poster.png',backdrop_path='/backdrop.png')
  with mock.patch('tmdb_connection60.request',return_value=dict(results=[dict(row,id=i) for i in range(1,9)],page=1,total_pages=1)) as request,mock.patch('work_search86.details',side_effect=AssertionError('unselected details')),mock.patch('programme_urls55.probe',side_effect=AssertionError('unselected image')),mock.patch('programme_urls55.safe',return_value=True):
   result=__import__('work_search86').search('Monk')
  request.assert_called_once();self.assertEqual(len(result['rows']),8);self.assertTrue(all(not r['verified85'] and r['preview89'] and r['thumb86'] for r in result['rows']))
  with self.assertRaisesRegex(ValueError,'MANUAL_UNVERIFIED'):self.m.set_mapping(self.event,result['rows'][0])
 def test_tvmaze_preview_is_one_request_but_save_reverifies_selected_work(self):
  row=dict(id=1,name='Monk',premiered='2002-01-01',image=dict(original='https://static.tvmaze.com/uploads/images/original_untouched/1/1.jpg'),summary='<b>Series</b>')
  with mock.patch('media_sources43.get',return_value=[dict(show=row)]) as request,mock.patch('programme_urls55.safe',return_value=True):
   result=__import__('work_search86').search('Monk',source='tvmaze')
  request.assert_called_once();self.assertEqual(result['rows'][0]['overview'],'Series');self.assertFalse(result['rows'][0]['verified85'])
 def test_queued_time_consumes_same_thirty_second_budget_for_10_25_40_seconds(self):
  for seconds,expected in ((10,'READY'),(25,'READY'),(40,'NETWORK_TIMEOUT')):
   nonce=self.q.request(self.event,query='Monk');data=json.loads(self.properties[self.q.KEY]);origin=data['deadline89']-30
   self.properties[self.q.KEY]=json.dumps(dict(data,at=data['at']-2,deadline89=origin+30))
   def search(*args):
    # This stands for an API returning at actual end-to-end time, not a new
    # worker-only allowance. No forty-second wallclock sleep is needed.
    clock[0]=origin+seconds
    if args[-1]():raise __import__('media_sources43').SourceError('CANCELLED')
    return dict(code='READY',rows=[])
   clock=[origin+2]
   with mock.patch('work_requests86.time',SimpleNamespace(time=__import__('time').time,monotonic=lambda:clock[0])),mock.patch('work_search86.search',side_effect=search):self.q.drain()
   self.assertEqual(self.q.result(nonce)['code'],expected)
   self.q.cancel(nonce)
 def test_verified_commit_receipt_survives_lost_result_and_cold_reload(self):
  with mock.patch.object(self.q,'authoritative',return_value=self.event),mock.patch('work_search86.details',return_value=self.candidate):
   nonce=self.q.request(self.event,'save',candidate=self.candidate);self.q.drain()
  self.assertEqual(self.q.result(nonce)['code'],'SAVED');before=self.m.path().read_bytes();self.properties.clear();self.m._loaded.clear()
  self.assertTrue(self.m.reload());self.assertTrue(self.m.committed89(self.event,nonce));self.assertEqual(self.m.path().read_bytes(),before)
  self.assertEqual(self.m.current(self.event)['work87']['url'],self.candidate['url'])
 def test_worker_exception_is_reported_instead_of_leaving_request_until_ui_timeout(self):
  nonce=self.q.request(self.event,query='Monk')
  with mock.patch('work_search86.search',side_effect=AttributeError('no such reader method')):self.q.drain()
  self.assertEqual(self.q.result(nonce)['code'],'CANDIDATES_REJECTED')
 def test_second_drainer_does_not_start_parallel_work(self):
  self.q.request(self.event,query='Monk')
  self.q._drain_lock89.acquire()
  try:
   with mock.patch('work_search86.search',side_effect=AssertionError('concurrent worker')):self.q.drain()
  finally:self.q._drain_lock89.release()
