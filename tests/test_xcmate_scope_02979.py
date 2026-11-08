"""Cumulative .76 and every existing source/test remain intact in this draft."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02979 import without_stabilization79
ROOT=Path(__file__).resolve().parents[1]
class Scope79(unittest.TestCase):
    def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02979_protection.json').read_text())
    def test_all_published_source_files_retained_with_exact_reviewed_delta(self):
        for path,digest in self.data()['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization79((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_existing_test_methods_and_skip_conditions_retained(self):
        data=self.data()
        for path,cases in data['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for c,n in cases:
                self.assertIn((c,n),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[c,n].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+c+'|'+n])
    def test_all_published_channels_and_installer_frozen(self):
        from channel_contract_02979 import verify
        for path in ('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):self.assertTrue(verify(path,committed=True))
        for path in ('script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.78.zip'):
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show','3b2a52859feda4d9413231bb4d3cf4121b1f1d67'+':'+path],cwd=ROOT))
