"""Cumulative EPG/preview/wizard source and retained-test protection."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02954 import without_stabilization54
ROOT=Path(__file__).resolve().parents[1]

class Scope54(unittest.TestCase):
    def test_all_590_existing_files_retained_with_only_reviewed_epg_preview_wizard_deltas(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02954_protection.json').read_text())
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02954_reviewed_hooks.json').read_text())['modules']
        self.assertEqual(baseline['base'],'e8d14039fd989bd952c8fdf36cdccb8c966da434')
        self.assertEqual(len(baseline['source_sha256']),590);self.assertEqual(len(hooks),20)
        self.assertEqual({Path(p).name for p in hooks},set(['XCMateSetup.xml', 'addon.xml', 'changelog.txt', 'epg_manager53.py', 'epg_report53.py', 'epg_schedule53.py', 'main.py', 'setup_draft.py', 'setup_navigation.py', 'setup_window.py', 'setup_wizard.py', 'stream_epg.py', 'strings.po', 'update_notes53.py', 'update_notice41.py', 'wizard_deadline48.py', 'wizard_flow53.py', 'wizard_resume53.py', 'xmltv_stream.py']))
        for path,digest in baseline['source_sha256'].items():
            raw=__import__('stabilization_contract_02955').without_stabilization55((ROOT/path).read_bytes(),path)
            self.assertEqual(hashlib.sha256(without_stabilization54(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2240_old_methods_retained_without_new_skips(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02954_protection.json').read_text());count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2240)
