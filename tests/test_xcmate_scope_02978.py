"""Cumulative .76 and every existing source/test remain intact in this draft."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02978 import without_stabilization78
ROOT=Path(__file__).resolve().parents[1]
class Scope78(unittest.TestCase):
    def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02978_protection.json').read_text())
    def test_all_published_source_files_retained_with_exact_reviewed_delta(self):
        for path,digest in self.data()['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization78((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_existing_test_methods_and_skip_conditions_retained(self):
        data=self.data()
        for path,cases in data['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for c,n in cases:
                self.assertIn((c,n),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[c,n].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+c+'|'+n])
    def test_both_published_channels_and_pilot_package_unchanged(self):
        # Published .76 is the current authorized channel baseline.
        base='80932cc20502dc267018bfded4f2a8cc0ce77e24'
        paths=['addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.76.zip','docs/XCMate/test-builds/02977/plugin.video.xtreammate-0.1.29.77.zip']
        for path in paths:
            # CI builds a temporary regular index for package validation.
            # Publication protection checks committed regular-channel bytes;
            # the Pilot files and reviewed ZIP must also stay byte-identical on disk.
            current=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT) if path in ('addons.xml','addons.xml.md5') else (ROOT/path).read_bytes()
            if path.startswith('online-test/') and path.endswith(('addons.xml','addons.xml.md5','manifest.json')):
                from channel_contract_02978 import verify
                self.assertTrue(verify(path))
            elif path in ('addons.xml','addons.xml.md5'):
                from channel_contract_02978 import verify
                self.assertTrue(verify(path,committed=True))
            else:self.assertEqual(current,subprocess.check_output(['git','show',base+':'+path],cwd=ROOT),path)
