"""Local XMLTV source/event identity, explicit manual commit and fallback."""
import importlib,json,unittest
from types import SimpleNamespace
from contextlib import closing
from unittest import mock
from xcmate027_fixture import Fixture

class XMLTV96(Fixture,unittest.TestCase):
 def xmltv_only_selection(self):
  self.options.update(programme_xmltv96=True,programme_tmdb46=False,tmdb_research43=False,programme_tvmaze67=False,programme_helper57=False,programme_catalog57=False)
  event=dict(self.event,source_key46='provider',epg_source46='provider',code='LOCAL_EVENT',_detail93=True)
  candidate=self.module.search(event)['rows'][0]
  __import__('programme_mapping85').set_mapping(event,candidate)
  return event,candidate
 def test_manual_xmltv_alternative_is_ready_with_all_remote_lookups_disabled(self):
  event,candidate=self.xmltv_only_selection()
  with mock.patch('utils.http_get',side_effect=AssertionError('no metadata request')):
   value=__import__('programme_urls55').resolve(event,allow_lookup=False,check=mock.Mock())
  self.assertEqual(value['source'],'xmltv_event')
  self.assertEqual(value['xmltv96'],candidate['xmltv96'])
  self.assertEqual(value['code'],'READY')
 def test_service_admits_manual_xmltv_alternative_without_enabling_remote_lookup(self):
  event,candidate=self.xmltv_only_selection()
  requests=__import__('programme_requests68');self.assertTrue(requests.request(event,priority=True))
  reader=SimpleNamespace(get=lambda *a:dict(sid='1'),close=lambda:None)
  with mock.patch('series_requests85.drain'),mock.patch('programme_reference84.tick'),mock.patch('programme_events46.load',return_value=event),mock.patch('library_index.Reader',return_value=reader),mock.patch('programme_urls55.enqueue',return_value=True) as enqueue:
   self.assertEqual(requests.drain(),1)
  enqueue.assert_called_once()
  self.assertFalse(enqueue.call_args.kwargs['allow_lookup'])
  self.assertEqual(enqueue.call_args.args[0]['sid'],'1')
  self.assertEqual(__import__('programme_mapping85').current(event)['xmltv96'],candidate['xmltv96'])
 def test_service_respects_xmltv_optout_even_with_saved_alternative(self):
  event,candidate=self.xmltv_only_selection();self.options['programme_xmltv96']=False
  requests=__import__('programme_requests68');self.assertTrue(requests.request(event,priority=True))
  reader=SimpleNamespace(get=lambda *a:dict(sid='1'),close=lambda:None)
  with mock.patch('series_requests85.drain'),mock.patch('programme_reference84.tick'),mock.patch('programme_events46.load',return_value=event),mock.patch('library_index.Reader',return_value=reader),mock.patch('programme_urls55.enqueue') as enqueue:
   self.assertEqual(requests.drain(),0)
  enqueue.assert_not_called()
  self.assertEqual(__import__('programme_mapping85').current(event)['xmltv96'],candidate['xmltv96'])
 def resolved_manual(self,local=False):
  import io
  from PIL import Image
  body=io.BytesIO();Image.new('RGB',(1280,720)).save(body,'PNG')
  candidate=self.module.search(self.event)['rows'][0]
  __import__('programme_mapping85').set_mapping(self.event,candidate)
  with mock.patch('media_sources43.get',return_value=body.getvalue()):
   value=__import__('programme_urls55').resolve(dict(self.event,_detail93=True),allow_lookup=True,local_image63=local,url_mode69=not local,check=lambda *a,**k:dict(decoded77=True,width=1280,height=720))
  self.assertEqual(value['code'],'READY')
  return value,candidate
 def test_manual_xmltv_proof_survives_worker_status_and_revokes_display(self):
  value,candidate=self.resolved_manual()
  requests=__import__('programme_requests68');requests.completed(self.event,value)
  delivered=requests.result(self.event)
  self.assertEqual(delivered.get('xmltv96'),candidate['xmltv96'])
  self.module.invalidate(candidate['xmltv96'])
  self.assertFalse(__import__('programme_image69').eligible(delivered,self.event))
  self.assertNotEqual(requests.result(self.event).get('source'),'xmltv_event')
 def test_local_manual_xmltv_keeps_proof_and_is_not_a_disposable_asset(self):
  value,candidate=self.resolved_manual(local=True)
  self.assertEqual(value.get('xmltv96'),candidate['xmltv96'])
  self.assertTrue(value.get('manual85'))
  self.assertTrue(__import__('artwork_temp85').durable(value))
  self.module.invalidate(candidate['xmltv96'])
  self.assertFalse(__import__('programme_image69').eligible(value,self.event))
 def test_xmltv_proof_for_different_event_cannot_be_displayed(self):
  value,candidate=self.resolved_manual()
  other=dict(value,xmltv96=dict(candidate['xmltv96'],event=self.module.identity(dict(self.event,sid='other'))))
  self.assertFalse(__import__('programme_image69').eligible(other,self.event))
  self.assertIsNone(__import__('programme_urls55').display(self.event,other))
 def test_rolling_cache_context_keeps_xmltv_revocation_proof(self):
  import io
  from PIL import Image
  body=io.BytesIO();Image.new('RGB',(1280,720)).save(body,'PNG')
  value,candidate=self.resolved_manual()
  value.pop('manual85',None) # Exercise the automatic rolling lane with proof.
  cache=__import__('artwork_temp85');cache._due=0
  with mock.patch('home_schedule75.applicable',return_value=True):
   promoted=cache.promote(self.event,value,body.getvalue())
  self.assertTrue(promoted.get('temp85'))
  restored=cache.lookup(self.event)
  self.assertEqual(restored.get('xmltv96'),candidate['xmltv96'])
  self.module.invalidate(candidate['xmltv96'])
  self.assertIsNone(cache.lookup(self.event))
 def setUp(self):
  super().setUp();self.options['programme_image_hosts55']='images.example.test'
  self.event=dict(pid='p',sid='1',canonical='xml',start=self.now-30,stop=self.now+3600,title='Verified show',source_key46='source-a',epg_source46='source-a',key='exact-event',placeholder='')
  self.index46=importlib.import_module('programme_index46')
  with closing(self.index46.connect(True)) as db,db:
   for source in ('source-a','source-b'):
    fact=dict(xmltv_image='https://images.example.test/'+source+'.jpg',epg_source46=source,source_key46=source,title='Verified show',year=2026,description='Exact source programme')
    db.execute('INSERT INTO facts VALUES(?,?,?,?,?,?,?,?,?)',('p','xml',self.event['start'],self.event['stop'],source,__import__('programme_store46').title_hash(self.event['title']),'rev-'+source,json.dumps(fact),self.now))
  self.module=importlib.import_module('xmltv_art96')
  patch=mock.patch('epg_binding48.sources',return_value=[dict(id='source-a'),dict(id='source-b')]);patch.start();self.addCleanup(patch.stop)
 def test_local_search_returns_source_qualified_exact_event_candidates_without_http(self):
  with mock.patch('utils.http_get',side_effect=AssertionError('no XMLTV download')):
   answer=self.module.search(self.event)
  self.assertEqual(len(answer['rows']),2);a,b=answer['rows'];self.assertNotEqual(a['id'],b['id']);self.assertNotEqual(a['xmltv96']['source'],b['xmltv96']['source'])
 def test_save_and_reload_are_event_specific_and_do_not_collide_same_title(self):
  candidate=self.module.search(self.event)['rows'][0];mapping=importlib.import_module('programme_mapping85')
  mapping.set_mapping(self.event,candidate)
  mapping.reload();saved=mapping.current(self.event);self.assertEqual(saved['source'],'xmltv_event')
  self.assertIsNone(mapping.current(dict(self.event,start=self.event['start']+3600,stop=self.event['stop']+3600)))
  with mock.patch.object(mapping,'window',wraps=mapping.window):self.assertEqual(mapping.read()['records'][self.module.key(self.event)]['xmltv96'],candidate['xmltv96'])
 def test_changed_source_revision_invalidates_candidate_before_commit(self):
  candidate=self.module.search(self.event)['rows'][0]
  with closing(self.index46.connect(True)) as db,db:db.execute('UPDATE facts SET fingerprint=?',('different',))
  with self.assertRaisesRegex(__import__('media_sources43').SourceError,'EPG_REVISION_CHANGED'):self.module.details(self.event,candidate)
 def test_unapproved_xmltv_image_host_is_not_a_candidate(self):
  self.options['programme_image_hosts55']=''
  self.assertEqual(self.module.search(self.event)['rows'],[])
 def test_disabled_manual_tmdb_does_not_remove_verified_xmltv_fallback(self):
  e=dict(self.event,xmltv_image='https://images.example.test/source-a.jpg',_detail93=True)
  urls=importlib.import_module('programme_urls55')
  with mock.patch('programme_mapping85.current',return_value=dict(source='tmdb',id=10,hidden=False)),mock.patch('programme_candidates85.enabled',return_value=False),mock.patch('programme_lock89.current',return_value=None),mock.patch('external_art89.recover_programme',return_value=None),mock.patch('event_art81.prior',return_value=None):
   result=urls.resolve(e,allow_lookup=True,check=mock.Mock())
  self.assertEqual(result['source'],'xmltv_event');self.assertEqual(result['code'],'READY')

 def test_retired_or_disabled_source_is_not_returned_from_retained_facts(self):
  with mock.patch('epg_binding48.sources',return_value=[dict(id='source-a')]):
   rows=self.module.search(self.event)['rows']
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['xmltv96']['source'],'source-a')
 def test_enriched_optional_metadata_does_not_change_exact_event_mapping_key(self):
  self.assertEqual(self.module.key(self.event),self.module.key(dict(self.event,year=2026,genre='series')))
 def test_confirmed_tmdb_choice_replaces_xmltv_override_for_this_event(self):
  mapping=importlib.import_module('programme_mapping85');candidate=self.module.search(self.event)['rows'][0]
  mapping.set_mapping(self.event,candidate)
  mapping.set_mapping(self.event,dict(source='tmdb',id=42,title='Verified show',year=2026,verified85=True,url='https://image.tmdb.org/t/p/w780/a.jpg'))
  self.assertEqual(mapping.current(self.event)['source'],'tmdb')
 def test_hidden_xmltv_event_can_return_to_automatic_without_stale_hidden_record(self):
  mapping=importlib.import_module('programme_mapping85');candidate=self.module.search(self.event)['rows'][0]
  mapping.set_mapping(self.event,candidate);mapping.set_mapping(self.event,hidden=True)
  self.assertTrue(mapping.current(self.event)['hidden']);mapping.set_mapping(self.event,automatic=True)
  self.assertIsNone(mapping.current(self.event))
 def test_xmltv_off_revokes_display_admission_without_deleting_mapping_or_facts(self):
  urls=importlib.import_module('programme_urls55');e=dict(self.event,xmltv_image='https://images.example.test/source-a.jpg',_detail93=True)
  value=urls.resolve(e,check=mock.Mock());self.assertEqual(value['source'],'xmltv_event')
  with closing(self.index46.connect(False)) as db:before=db.execute('SELECT * FROM facts ORDER BY source_id').fetchall()
  self.options['programme_xmltv96']=False
  self.assertFalse(__import__('event_art81').allowed(value));self.assertIsNone(urls.display(e,value))
  self.assertNotEqual(urls.resolve(e,check=mock.Mock())['source'],'xmltv_event')
  with closing(self.index46.connect(False)) as db:self.assertEqual(db.execute('SELECT * FROM facts ORDER BY source_id').fetchall(),before)
 def test_cached_manual_xmltv_is_revalidated_after_fact_revision_change(self):
  mapping=importlib.import_module('programme_mapping85');candidate=self.module.search(self.event)['rows'][0];mapping.set_mapping(self.event,candidate)
  urls=importlib.import_module('programme_urls55');e=dict(self.event,_detail93=True)
  first=urls.resolve(e,check=mock.Mock());self.assertEqual(first['source'],'xmltv_event')
  with closing(self.index46.connect(True)) as db,db:db.execute('UPDATE facts SET fingerprint=?',('new-revision',))
  check=mock.Mock()
  second=urls.resolve(e,check=check)
  self.assertEqual(check.call_count,1) # A new independent decode/reference check.
  self.assertNotEqual(first.get('xmltv96'),second.get('xmltv96'))
  self.assertFalse(self.module.display_allowed(first))
