"""Actual HTTP/SQLite cold receipts, silent observer and semantic zero-diff."""
import importlib,unittest
from unittest import mock
class Catalog81(unittest.TestCase):
 def setUp(self):
  from test_xcmate_catalog_02973 import Catalog73
  self.h=Catalog73(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_real_full_scan_persists_per_kind_deltas_api_time_and_cold_readback(self):
  h=self.h;h.jobs.request(h.portal);h.finish();row=h.row()
  self.assertEqual(set(row['last_api_success81']),{'live','vod','series'})
  self.assertEqual(set(row['last_full_sync81']),{'live','vod','series'})
  self.assertEqual(row['delta81']['vod']['new'],1)
  for kind,counts in row['delta81'].items():self.assertEqual(counts['read'],counts['new']+counts['changed']+counts['unchanged'])
  importlib.reload(h.jobs);self.assertEqual(h.row()['delta81'],row['delta81'])
  h.jobs.request(h.portal);h.finish();again=h.row()
  self.assertEqual(again['delta81']['vod']['unchanged'],1);self.assertEqual(again['delta81']['vod']['new'],0)
  self.assertEqual(h.live_digest()[:2],(3357,53))
 def test_empty_group_retains_catalog_and_does_not_claim_full_sync(self):
  h=self.h;h.responses['get_live_streams']=[];h.jobs.request(h.portal,['live']);h.finish()
  self.assertIn('live',h.row()['last_api_success81']);self.assertNotIn('live',h.row()['last_full_sync81']);self.assertEqual(h.live_digest(),h.live_before)
 def test_failed_group_reports_failure_without_last_success_or_data_loss(self):
  h=self.h;h.responses['get_live_streams']=[dict(stream_id='bad',category_id='0')];h.jobs.request(h.portal,['live']);h.tick()
  row=h.row();self.assertEqual(row['state'],'FAILED');self.assertEqual(row['failed_groups81'][0]['code'],'SCHEMA');self.assertFalse(row.get('last_api_success81'));self.assertEqual(h.live_digest(),h.live_before)
 def test_background_group_completion_never_emits_popup_even_when_summary_enabled(self):
  import catalog_progress73 as progress,xbmcgui
  h=self.h;h.options['catalog_summary81']=True;progress._snapshot=dict(id='delta-p-vod-v',state='DONE',updated=2,processed=1);progress._last=('delta-p-vod-v','RUNNING',1)
  dialog=mock.Mock()
  with mock.patch.object(xbmcgui,'Dialog',return_value=dialog),mock.patch.object(xbmcgui,'DialogProgressBG',create=True) as bg:
   progress.poll();progress.poll();dialog.notification.assert_not_called();bg.assert_not_called()
 def test_absent_kind_cannot_claim_a_verified_full_sync(self):
  h=self.h;h.responses['get_series_categories']=[];h.jobs.request(h.portal);h.finish()
  self.assertEqual(h.row()['groups_found']['series'],0);self.assertNotIn('series',h.row()['last_api_success81']);self.assertNotIn('series',h.row()['last_full_sync81'])
