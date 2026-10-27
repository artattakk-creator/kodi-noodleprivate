"""Published .45 remains reproducible after exact reviewed additive .46 hooks."""
import ast,hashlib,json,re,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from stabilization_contract_02946 import without_stabilization46
ROOT=Path(__file__).resolve().parents[1];BASE='a2f83c49e8f756f1379b68e462eb6304c924bee1'
class Scope46(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02946_protection.json').read_text())
 def test_all_510_published_source_files_remain_after_exact_reviewed_hooks(self):
  b=self.baseline();self.assertEqual(b['base'],BASE);self.assertEqual(len(b['source_sha256']),510)
  for path,digest in b['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization46((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_1725_existing_test_methods_are_retained_without_skips(self):
  total=0
  for path,cases in self.baseline()['test_methods'].items():
   present={(c.name,n.name) for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   self.assertTrue(set(map(tuple,cases))<=present,path);total+=len(cases)
  self.assertEqual(total,1725)
 def test_critical_stop_player_autoplay_resume_epg_backup_and_infobar_files_are_byte_identical(self):
  names=('live_stop42','native_stop41','live_exit','exit_jobs','playback_exit','media_progress','media_autoplay','media_state','media_sequence','stream_details','guide_publish44','guide_backup44','epg_merge44','epg_sources','epg','portals','infobar45','tv_data','nav_rail')
  b=self.baseline()
  for name in names:
   path='src/plugin.video.xtreammate/resources/lib/'+name+'.py'
   raw=(ROOT/path).read_bytes()
   if name in ('live_exit','media_progress','epg'):raw=without_stabilization46(raw,path)
   elif name=='tv_data':raw=__import__('stabilization_contract_02947').without_stabilization47(raw,path)
   self.assertEqual(hashlib.sha256(raw).hexdigest(),b['source_sha256'][path],name)
 def test_original_application_icons_search_xml_and_keymaps_have_exact_bytes(self):
  b=self.baseline()
  for p,digest in b['source_sha256'].items():
   if '/keymaps/' in p or p.endswith('/icon.png') or p.endswith('/icon-81da1003a2753ec6.png') or p.endswith('/XCMateMedia.xml'):self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest,p)
 def test_every_existing_native_setting_id_type_default_and_action_is_preserved(self):
  old=json.loads((ROOT/'tests/fixtures/xcmate_02946_settings_baseline.json').read_text());current={n.get('id'):dict(n.attrib) for n in ET.parse(ROOT/'src/plugin.video.xtreammate/resources/settings.xml').iter('setting') if n.get('id')}
  self.assertTrue(old.keys()<=current.keys());self.assertEqual(current['programme_tmdb46']['default'],'false')
  for key,value in old.items():
   for attribute in ('type','default','values','range','option','action'):self.assertEqual(current[key].get(attribute),value.get(attribute),(key,attribute))
 def test_new_event_reader_is_readonly_and_does_not_start_imports_or_player(self):
  source=(ROOT/'src/plugin.video.xtreammate/resources/lib/programme_events46.py').read_text()
  for token in ('request_refresh','import_cache','PlayMedia','Container.Update','set_mapping','DELETE FROM','ALTER TABLE'):self.assertNotIn(token,source)
  self.assertIn('mode=ro',(ROOT/'src/plugin.video.xtreammate/resources/lib/programme_store46.py').read_text())
