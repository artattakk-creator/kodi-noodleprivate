"""All .54 sources/tests retained; Wizard, EPG import and .42 stop frozen."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02955 import without_stabilization55
ROOT=Path(__file__).resolve().parents[1]


class Scope55(unittest.TestCase):
    def test_all_596_sources_have_only_exact_reviewed_home_url_and_input_deltas(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02955_protection.json').read_text())
        self.assertEqual(base['base'],'2d08ff1e650505aa4d78a1128640d8baacb929c5');self.assertEqual(len(base['source_sha256']),596)
        for path,digest in base['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization55((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)

    def test_wizard_and_epg_import_freeze_is_raw_byte_exact_without_normalization(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02955_protection.json').read_text())
        found=[]
        for path,digest in base['source_sha256'].items():
            name=Path(path).name
            if name.startswith(('setup_','wizard_','XCMateSetup')) or name in ('stream_epg.py','xmltv_stream.py','epg_schedule53.py','source_adapters.py','native_stop41.py','native_stop42.py','live_exit.py','exit_jobs.py','playback_exit.py'):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path);found.append(path)
        self.assertGreater(len(found),25)

    def test_all_2294_existing_test_methods_retained_without_additional_skips(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02955_protection.json').read_text());count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2294)
