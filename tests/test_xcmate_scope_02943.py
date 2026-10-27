"""Cumulative .42 bytes, explicit reviewed media deltas and unchanged P0 exit."""
import ast,hashlib,json,unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from stabilization_contract_02943 import without_stabilization43
ROOT=Path(__file__).resolve().parents[1]
BASE='451f4cf0995cc09ada4b9eb4090906320d36a9fb'

class Scope43(unittest.TestCase):
    def test_every_previous_source_file_retained_only_exact_authorized_hooks_differ(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02943_protection.json').read_text())
        self.assertEqual(baseline['base'],BASE)
        for path,digest in baseline['source_sha256'].items():
            from stabilization_contract_02944 import without_stabilization44
            actual=without_stabilization44((ROOT/path).read_bytes(),path)
            if path in baseline['allowed_source_changes']:actual=without_stabilization43(actual,path)
            self.assertEqual(hashlib.sha256(actual).hexdigest(),digest,path)
    def test_all_1514_existing_test_methods_still_run(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02943_protection.json').read_text());count=0
        for path,cases in baseline['test_methods'].items():
            current={(c.name,n.name) for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            self.assertLessEqual(set(map(tuple,cases)),current,path);count+=len(cases)
        self.assertEqual(count,1514)
    def test_four_exit_sources_exactly_frozen_and_compatibility_default_false_no_keymap_changes(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02943_protection.json').read_text())
        for name in ('live_stop42','native_stop41','live_exit','exit_jobs'):
            path='src/plugin.video.xtreammate/resources/lib/'+name+'.py'
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),baseline['source_sha256'][path])
        settings=ET.parse(ROOT/'src/plugin.video.xtreammate/resources/settings.xml')
        option=settings.find(".//setting[@id='live_exit_fullscreen42']");self.assertEqual(option.get('default'),'false')
    def test_approved_search_layout_and_icon_remain_byte_identical(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02943_protection.json').read_text())
        for name in ('resources/skins/Default/720p/XCMateMedia.xml','icon.png'):
            path='src/plugin.video.xtreammate/'+name
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),baseline['source_sha256'][path])
