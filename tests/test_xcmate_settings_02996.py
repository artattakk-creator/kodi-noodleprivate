"""Real settings bytes, corrupt-read diagnosis and non-destructive consent."""
import importlib,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Settings96(Fixture,unittest.TestCase):
 def xml(self,text):
  p=self.folder/'settings.xml';p.write_text(text,encoding='utf-8');return p
 def test_corrupt_settings_never_become_persisted_explicit_optouts(self):
  self.xml('<settings><setting id="programme_tmdb46">')
  m=importlib.import_module('programme_consent77')
  self.assertEqual(m.explicit_off(),set())
  self.assertEqual(m.ensure(force=True),'SETTINGS_XML_INVALID')
  self.assertNotIn('programme_tmdb_optout77',self.options)
 def test_healthy_read_does_not_repeat_kodi_getsetting_load_errors(self):
  self.xml('<settings version="2"><setting id="programme_tmdb46">true</setting></settings>')
  guard=importlib.import_module('settings_guard96')
  addon=mock.Mock();addon.getSetting.side_effect=RuntimeError('synthetic private details')
  for i in range(50):self.assertEqual(guard.value('programme_tmdb46',addon),'true')
  addon.getSetting.assert_not_called()
 def test_explicit_write_preserves_token_and_cold_readback(self):
  p=self.xml('<settings version="2"><setting id="tmdb_read_token43">TEST_ONLY</setting><setting id="programme_tmdb46">false</setting></settings>')
  guard=importlib.import_module('settings_guard96')
  class Native:
   def setSetting(_,key,value):
    tree=ET.parse(p);node=next((n for n in tree.getroot().iter('setting') if n.get('id')==key),None)
    if node is None:node=ET.SubElement(tree.getroot(),'setting',id=key)
    node.text=value;tree.write(p,encoding='utf-8')
  guard.write({'programme_tmdb46':'true'},Native())
  tree=ET.parse(p);values={n.get('id'):n.text for n in tree.iter('setting')}
  self.assertEqual(values['tmdb_read_token43'],'TEST_ONLY');self.assertEqual(values['programme_tmdb46'],'true')
  self.assertTrue((self.folder/'settings96.lastgood.xml').is_file())
 def test_failed_readback_never_acknowledges_source_enabled(self):
  self.xml('<settings version="2"><setting id="programme_tmdb46">false</setting></settings>')
  guard=importlib.import_module('settings_guard96')
  with self.assertRaisesRegex(guard.SettingsError,'SETTINGS_READBACK_FAILED'):guard.write({'programme_tmdb46':'true'},mock.Mock())
 def test_repair_keeps_corrupt_original_and_verified_backup(self):
  p=self.xml('<settings version="2"><setting id="tmdb_read_token43">TEST_ONLY</setting></settings>')
  guard=importlib.import_module('settings_guard96');guard.backup()
  p.write_text('<broken>',encoding='utf-8');guard.repair()
  self.assertEqual(guard.snapshot()['code'],'READY')
  self.assertEqual(ET.parse(p).findtext('setting'),'TEST_ONLY')
  self.assertEqual(len(list(self.folder.glob('settings96.corrupt.*.xml'))),1)
 def test_ordinary_user_optout_is_not_enrolled_as_test_profile(self):
  self.options.update(programme_tmdb_optout77='true',programme_tvmaze_optout77='true')
  m=importlib.import_module('programme_consent77')
  with mock.patch('tmdb_token61.effective_tmdb_read_token',return_value=''),mock.patch.object(m,'explicit_off',return_value=set()):m.ensure(force=True)
  self.assertNotEqual(self.options.get('programme_tmdb46'),'true');self.assertNotEqual(self.options.get('programme_tvmaze67'),'true')
 def test_source_health_failure_is_diagnosed_before_disabled_result(self):
  self.xml('<settings>')
  from media_sources43 import SourceError
  m=importlib.import_module('programme_candidates85')
  with self.assertRaisesRegex(SourceError,'SETTINGS_XML_INVALID'):m.enabled('tmdb')
 def test_three_source_enrollment_preserves_existing_token_and_reads_back(self):
  guard=importlib.import_module('settings_guard96')
  hub=importlib.import_module('artwork_sources96')
  with mock.patch.object(guard,'write',side_effect=lambda changes:self.options.update(changes) or 'revision') as write,mock.patch('tmdb_token61.effective_tmdb_read_token',return_value='TEST_VALID'),mock.patch('tmdb_token61.validate',return_value='TEST_VALID'),mock.patch('storage_policy92.choose') as choose,mock.patch('storage_policy92.images_enabled',return_value=True):
   result=hub.enroll_test_profile()
  self.assertEqual(result,'SOURCES_VERIFIED');self.assertEqual(write.call_count,1)
  changes=write.call_args[0][0];self.assertNotIn('tmdb_read_token43',changes)
  self.assertTrue(all(changes[k]=='true' for k in ('programme_xmltv96','programme_tmdb46','tmdb_research43','programme_tvmaze67')))
  choose.assert_called_once_with('yes')
 def test_unrelated_native_setting_loss_rolls_back_and_keeps_failed_copy(self):
  p=self.xml('<settings><setting id="tmdb_read_token43">TEST_ONLY</setting><setting id="programme_tmdb46">false</setting></settings>');before=p.read_bytes()
  guard=importlib.import_module('settings_guard96')
  class BrokenNative:
   def setSetting(_,key,value):p.write_text('<settings><setting id="'+key+'">'+value+'</setting></settings>')
  with self.assertRaisesRegex(guard.SettingsError,'SETTINGS_UNRELATED_CHANGED'):guard.write({'programme_tmdb46':'true'},BrokenNative())
  self.assertEqual(p.read_bytes(),before)
  self.assertEqual(len(list(self.folder.glob('settings96.rejected.*.xml'))),1)
 def test_fresh_ordinary_profile_never_auto_enables_external_sources(self):
  m=importlib.import_module('programme_consent77')
  with mock.patch('tmdb_token61.effective_tmdb_read_token',return_value='TEST_ONLY'),mock.patch('tmdb_token61.validate',return_value='TEST_ONLY'):
   m.ensure(force=True)
  self.assertNotEqual(self.options.get('programme_tvmaze67'),'true');self.assertNotEqual(self.options.get('programme_tmdb46'),'true')
 def test_worker_does_not_log_disabled_when_native_settings_are_invalid(self):
  self.xml('<settings>');event=dict(pid='p',sid='1',title='Show',key='e')
  from media_sources43 import SourceError
  run=mock.Mock()
  with self.assertRaisesRegex(SourceError,'SETTINGS_XML_INVALID'):__import__('art_trace81').own(event,run)
  run.assert_not_called()
  self.assertEqual(__import__('programme_match46').diagnose(event),'SETTINGS_XML_INVALID')
  with self.assertRaisesRegex(SourceError,'SETTINGS_XML_INVALID'):__import__('tmdb_epg60').candidate(event)
