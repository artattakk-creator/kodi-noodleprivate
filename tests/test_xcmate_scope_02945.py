"""Cumulative published .44 plus reviewed .45 menu/widget/presentation deltas."""
import ast,hashlib,json,re,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from stabilization_contract_02945 import without_stabilization45
ROOT=Path(__file__).resolve().parents[1]
BASE='aace7f0f85cea8b9d132b0090563e28c9941bc4a'
class Scope45(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02945_protection.json').read_text())
 def test_every_412_previous_source_file_retained_only_exact_reviewed_hooks_change(self):
  b=self.baseline();self.assertEqual(b['base'],BASE);self.assertEqual(len(b['source_sha256']),412)
  for path,digest in b['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization45((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_1652_previous_test_methods_retained_without_skip(self):
  count=0
  for path,cases in self.baseline()['test_methods'].items():
   current={(c.name,n.name) for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   self.assertTrue(set(map(tuple,cases))<=current,path);count+=len(cases)
  self.assertEqual(count,1652)
 def test_live_stop_media_progress_and_epg_publish_core_remain_byte_identical(self):
  names=('live_stop42','native_stop41','live_exit','exit_jobs','media_progress','media_autoplay','media_state','media_sequence','stream_details','guide_store','guide_publish44','guide_backup44','stream_epg','epg_merge44','local_epg','epg','portals')
  b=self.baseline()
  for name in names:
   path='src/plugin.video.xtreammate/resources/lib/'+name+'.py';self.assertEqual(hashlib.sha256(__import__('stabilization_contract_02946').without_stabilization46((ROOT/path).read_bytes(),path)).hexdigest(),b['source_sha256'][path],name)
 def test_original_icon_search_xml_and_existing_keymaps_have_exact_bytes(self):
  b=self.baseline()
  paths=[p for p in b['source_sha256'] if '/keymaps/' in p or p.endswith('/icon.png') or p.endswith('/XCMateMedia.xml')]
  for path in paths:self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),b['source_sha256'][path],path)
 def test_comp_mode_default_and_every_setting_id_type_default_value_preserved(self):
  original=json.loads((ROOT/'tests/fixtures/xcmate_02945_settings_baseline.json').read_text())
  current={n.get('id'):dict(n.attrib) for n in ET.fromstring(__import__('stabilization_contract_02953').without_stabilization53((ROOT/'src/plugin.video.xtreammate/resources/settings.xml').read_bytes(),'src/plugin.video.xtreammate/resources/settings.xml')).iter('setting')}
  for key,value in original.items():
   for field in ('type','default','values','range','option','action'):self.assertEqual(current[key].get(field),value.get(field),(key,field))
  self.assertEqual(current['live_exit_fullscreen42']['default'],'false')
 def test_native_relative_visibility_expressions_still_reference_same_setting_ids(self):
  original=json.loads((ROOT/'tests/fixtures/xcmate_02945_settings_baseline.json').read_text());oldkeys=list(original)
  for cat in ET.parse(ROOT/'src/plugin.video.xtreammate/resources/settings.xml').getroot():
   keys=[n.get('id') for n in cat]
   for i,n in enumerate(cat):
    for offset in re.findall(r'(?:eq|gt|lt|gte|lte)\((-?\d+),',n.get('visible','')+' '+n.get('enable','')):
     key=n.get('id');delta=int(offset);self.assertEqual(keys[i+delta],oldkeys[oldkeys.index(key)+delta],key)
