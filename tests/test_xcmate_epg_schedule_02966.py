"""Per-source startup/daily planning, with no user/profile/network changes."""
import importlib,time,unittest
from unittest import mock
import test_xcmate_epg_02952 as data52
class Schedule66(unittest.TestCase):
 def setUp(self):
  self.m=data52.EPG52(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  self.schedule=importlib.import_module('epg_schedule53');self.report=importlib.import_module('epg_report53')
  self.portal=dict(self.m.portal,provider_epg_enabled=False)
  self.ids=[importlib.import_module('guide_publish44').source_id(s,i) for i,s in enumerate(self.m.config['sources'],1)]
 def record(self,code,started,sources=None):
  self.report.store('p',dict(started=started,finished=started+1,code=code,sources=sources or []))
 def test_catalog_wait_retries_after_sixty_seconds_instead_of_next_day(self):
  now=time.time();self.record('WAIT_ACTIVE_CATALOG',now-61)
  self.assertEqual(self.schedule.plan(self.portal,now),self.ids)
 def test_busy_import_wait_is_short_and_does_not_spend_source_retry_budget(self):
  now=time.time();self.record('IMPORT_BUSY_OR_LOCK_UNAVAILABLE',now-20)
  self.assertEqual(self.schedule.plan(self.portal,now),[])
  self.assertEqual(self.schedule.plan(self.portal,now+41),self.ids)
 def test_short_cache_freshness_does_not_claim_unimported_xmltv_sources(self):
  with mock.patch('epg._is_fresh',return_value=True):
   self.assertEqual(self.schedule.plan(self.portal),self.ids)
 def test_provider_success_does_not_date_new_external_sources(self):
  self.m.put('a',[self.m.event()],0)
  self.assertEqual(self.schedule.plan(self.portal),self.ids)
 def test_one_proven_external_source_does_not_date_the_other(self):
  self.m.put('a',[self.m.event()],1)
  self.assertEqual(self.schedule.plan(self.portal),[self.ids[1]])
 def test_explicit_long_interval_is_preserved_but_scheduling_caps_at_one_day(self):
  now=time.time();self.m.options['epg_refresh_hours']='48'
  self.record('READY',now-90001,[dict(id=i,code='READY',started=now-90001,finished=now-90000) for i in self.ids])
  self.assertEqual(self.schedule.interval(),48*3600)
  self.assertEqual(self.schedule.plan(self.portal,now),self.ids)
 def test_last_success_is_per_source_and_failure_retains_independent_retry(self):
  now=time.time()
  self.record('PARTIAL_SUCCESS',now-1001,[dict(id=self.ids[0],code='READY',started=now-1001,finished=now-1000),dict(id=self.ids[1],code='DOWNLOAD_FAILED',started=now-1001,finished=now-1000)])
  self.assertEqual(self.schedule.plan(self.portal,now),[self.ids[1]])
 def test_user_cancel_and_backup_gate_are_not_silently_restarted(self):
  for code in ('CANCELLED','BACKUP_REQUIRED'):
   with self.subTest(code=code):
    self.record(code,time.time());self.assertEqual(self.schedule.plan(self.portal),[])
 def test_disabled_external_source_is_never_fetched_or_reenabled(self):
  self.m.config['sources'][1]['enabled']=False
  self.assertEqual(self.schedule.plan(self.portal),self.ids[:1])
