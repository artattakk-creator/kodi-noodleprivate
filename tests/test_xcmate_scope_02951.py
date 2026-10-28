"""Cumulative wizard-only source and retained-test protection."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02951 import without_wizard51
ROOT=Path(__file__).resolve().parents[1]

class Scope51(unittest.TestCase):
    def test_all_573_existing_files_retained_with_only_nine_exact_wizard_deltas(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02951_protection.json').read_text())
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02951_reviewed_hooks.json').read_text())['modules']
        self.assertEqual(baseline['base'],'54759f965aef97b45c846042010d5ae1aa1f8ff3')
        self.assertEqual(len(baseline['source_sha256']),573);self.assertEqual(len(hooks),9)
        self.assertEqual({Path(p).name for p in hooks},{'addon.xml','changelog.txt','strings.po','setup_wizard.py','setup_window.py','setup_draft.py','setup_trace.py','XCMateSetup.xml'})
        for path,digest in baseline['source_sha256'].items():
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(without_wizard51(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2078_old_methods_retained_without_new_skips(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02951_protection.json').read_text());count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2078)
