""".96 mandatory Xtream baseline; synthetic profile files, no provider network."""
import copy,importlib,importlib.util,sys,unittest
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,LIB

class Baseline96(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  spec=importlib.util.spec_from_file_location('baseline_portals96',LIB/'portals.py')
  self.portals=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.portals)
  patch=mock.patch.dict(sys.modules,{'portals':self.portals});patch.start();self.addCleanup(patch.stop)
  self.m=importlib.import_module('provider_baseline96')
 def test_new_xtream_default_does_not_probe_or_require_extra_source(self):
  adapter=mock.Mock();adapter.get_xmltv_epg_url.side_effect=AssertionError('no setup request')
  draft=SimpleNamespace(data=dict(type='xtream'),adapter=adapter,provider_epg=False,epg_sources=[])
  __import__('epg_config94').setup_default(draft)
  self.assertTrue(draft.provider_epg);self.assertTrue(draft.data['epg_show']);adapter.get_xmltv_epg_url.assert_not_called()
 def test_legacy_optout_archived_copy_on_write_and_idempotent(self):
  original=dict(self.portal,epg_show=False,provider_epg_enabled=False,epg_opt_out94=True,provider_epg_opt_out94=True,xc_user='synthetic-user',xc_pass='synthetic-pass')
  before=copy.deepcopy(original);self.portals.save_all([original])
  with mock.patch('source_adapters.for_portal',side_effect=AssertionError('no migration network')):
   result=self.m.ensure()
  self.assertEqual(original,before)
  saved=result[0];self.assertTrue(saved['epg_show']);self.assertTrue(saved['provider_epg_enabled']);self.assertFalse(saved['epg_opt_out94']);self.assertFalse(saved['provider_epg_opt_out94'])
  self.assertEqual(saved['provider_baseline_history96'][0]['values'],{k:before[k] for k in self.m.FIELDS})
  self.assertEqual(saved['xc_user'],before['xc_user']);self.assertEqual(saved['xc_pass'],before['xc_pass'])
  raw=__import__('pathlib').Path(self.portals._db_path()).read_bytes()
  self.assertEqual(self.m.ensure(),result);self.assertEqual(__import__('pathlib').Path(self.portals._db_path()).read_bytes(),raw)
 def test_non_xtream_and_optional_source_choices_are_unchanged(self):
  portal=dict(self.portal,type='m3u',epg_show=False,provider_epg_enabled=False,epg_opt_out94=True)
  self.portals.save_all([portal]);self.assertEqual(self.m.ensure(),[portal])
  original=copy.deepcopy(portal);draft=SimpleNamespace(data=portal,provider_epg=False,epg_sources=[])
  __import__('epg_config94').setup_default(draft)
  self.assertFalse(draft.provider_epg);self.assertFalse(draft.data['epg_show'])
  self.assertEqual(self.m.normalized(original),original)
 def test_failed_write_or_failed_readback_never_reports_migration_success(self):
  portal=dict(self.portal,epg_show=False);self.portals.save_all([portal])
  with mock.patch.object(self.portals,'update',side_effect=OSError('synthetic storage')):
   with self.assertRaises(OSError):self.m.ensure()
  self.assertEqual(self.portals.get_by_id(portal['id']),portal)
  with mock.patch.object(self.portals,'update',return_value=True):
   with self.assertRaisesRegex(OSError,'PROVIDER_BASELINE_READBACK'):self.m.ensure()
 def test_portal_record_preserves_history_and_enforces_new_xtream_baseline(self):
  portal=dict(self.portal,provider_epg_enabled=False,epg_show=False)
  result=self.portals._record(portal,portal_id='synthetic-new')
  self.assertTrue(result['epg_show']);self.assertTrue(result['provider_epg_enabled']);self.assertEqual(result['provider_baseline_history96'][0]['values']['epg_show'],False)
 def test_legacy_toggle_cannot_disable_xtream_and_preserves_optout_history(self):
  self.portals.save_all([dict(self.portal,epg_show=False,provider_epg_enabled=False)])
  result=__import__('provider_epg58').toggle(self.portal)
  self.assertTrue(result['provider_epg_enabled']);self.assertFalse(result['provider_baseline_history96'][0]['values']['provider_epg_enabled'])
  again=__import__('provider_epg58').toggle(result)
  self.assertEqual(result,again)
 def test_xtream_global_setter_keeps_baseline_while_non_xtream_can_disable(self):
  self.portals.save_all([dict(self.portal,epg_show=False)])
  self.assertTrue(__import__('epg_config94').set_global(self.portal['id'],False)['epg_show'])
  other=dict(self.portal,id='other',type='m3u');self.portals.save_all([other])
  self.assertFalse(__import__('epg_config94').set_global('other',False)['epg_show'])

 def test_migration_preserves_optional_sources_and_existing_guide_backup_bytes(self):
  from pathlib import Path
  self.portals.save_all([dict(self.portal,epg_show=False)])
  records={}
  for name,body in [('epg_sources.json',b'{"optional":"unchanged"}'),('guide_v1.sqlite',b'existing guide sentinel'),('guide.backup',b'existing backup sentinel')]:
   file=Path(self.portals._db_path()).parent/name;file.write_bytes(body);records[file]=body
  self.m.ensure()
  for file,body in records.items():self.assertEqual(file.read_bytes(),body)
 def test_malformed_history_is_not_silently_discarded(self):
  portal=dict(self.portal,epg_show=False,provider_baseline_history96={'unknown':'retain'})
  self.portals.save_all([portal])
  with self.assertRaisesRegex(ValueError,'PROVIDER_BASELINE_HISTORY_INVALID'):self.m.ensure()
  self.assertEqual(self.portals.get_by_id(portal['id']),portal)

class WizardBaseline96(unittest.TestCase):
 def setUp(self):
  import test_xcmate_setup_02971 as setup71
  setup71.Setup71.setUp(self)
  self.m.dialog.multiselect=mock.Mock()
 def test_xtream_source_picker_offers_only_optional_feeds_and_keeps_baseline(self):
  self.m.dialog.multiselect.return_value=[0]
  window=SimpleNamespace(draft=self.d,status=mock.Mock())
  self.ui.SetupWindow.choose_epg(window)
  heading,choices=self.m.dialog.multiselect.call_args.args
  self.assertIn('Anbieter-Grundversorgung',heading);self.assertNotIn('Anbieter-EPG',choices)
  self.assertTrue(self.d.provider_epg);self.assertEqual(len(self.d.epg_sources),1)
  self.assertEqual(self.d.epg_sources[0]['uri'],sys.modules['epg_sources'].PRESET_FEEDS[0][2])
 def test_cancelled_optional_picker_preserves_draft_and_existing_choices(self):
  self.d.epg_sources=[dict(id='optional',uri='https://synthetic.invalid/epg.xml',enabled=False)]
  before=copy.deepcopy(self.d.data);sources=copy.deepcopy(self.d.epg_sources)
  self.m.dialog.multiselect.return_value=None
  self.ui.SetupWindow.choose_epg(SimpleNamespace(draft=self.d,status=mock.Mock()))
  self.assertEqual(self.d.data,before);self.assertEqual(self.d.epg_sources,sources);self.assertTrue(self.d.provider_epg)
 def test_cold_legacy_draft_resume_enforces_baseline_and_retains_original_history(self):
  self.d.data.pop('provider_baseline96',None);self.d.data.pop('provider_baseline_history96',None)
  self.d.data.update(epg_show=False,provider_epg_enabled=False,epg_opt_out94=True,provider_epg_opt_out94=True)
  self.d.provider_epg=False;self.d.epg_sources=[dict(id='optional',name='Optional',uri='https://synthetic.invalid/epg.xml',local=False,enabled=False)]
  self.assertTrue(self.s.checkpoint(self.d,'groups',categories=True))
  cold=self.resume.Session.load();restored=cold.restore(dict(cold.data,xc_pass='SECRET'));self.addCleanup(restored.dispose)
  self.assertTrue(restored.provider_epg);self.assertTrue(restored.data['epg_show'])
  self.assertEqual(restored.epg_sources,self.d.epg_sources)
  history=restored.data['provider_baseline_history96']
  self.assertTrue(any(row['values'].get('epg_show') is False for row in history))
  self.assertTrue(any(row['values'].get('provider_epg_enabled') is False for row in history))
  self.assertTrue(self.resume.safe_data(restored.data)['provider_baseline_history96'])
