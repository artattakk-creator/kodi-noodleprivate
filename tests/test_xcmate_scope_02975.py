"""All cumulative sources/tests retained; regular release remains blocked."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02975 import without_stabilization75
ROOT=Path(__file__).resolve().parents[1]
class Scope75(unittest.TestCase):
    def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02975_protection.json').read_text())
    def test_every_released_source_file_retained_with_exact_reviewed_delta(self):
        for path,digest in self.data()['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization75((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_previous_test_methods_and_skip_contracts_all_retained(self):
        data=self.data()
        for path,cases in data['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for c,n in cases:
                self.assertIn((c,n),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[c,n].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+c+'|'+n])
    def test_regular_catalog_committed_bytes_remain_at_approved_74(self):
        # Historical method name retained; explicit .76 all-channel approval
        # superseded the .74 regular baseline before this .77 cycle.
        base='27104311012252f8c6382a392807b88290dc833c'
        for path in ('addons.xml','addons.xml.md5'):
            current=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
            approved=subprocess.check_output(['git','show',base+':'+path],cwd=ROOT)
            self.assertEqual(current,approved,path)
    def test_regular_auto_publish_requires_explicit_separate_android_release(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('release75',ROOT/'tools/release_channel75.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertFalse(module.regular_allowed())
        self.assertIn("steps.channel75.outputs.regular == 'true'",(ROOT/'.github/workflows/publish.yml').read_text())
    def test_pilot_changes_are_limited_to_approved_xcmate_package(self):
        from channel_contract_02975 import verify
        for path in ('online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):verify(path)
