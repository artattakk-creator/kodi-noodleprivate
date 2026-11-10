"""Cumulative source/tests and all published channels remain protected."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from stabilization_contract_02983 import without_stabilization83
ROOT=Path(__file__).resolve().parents[1]
BASE='fdbcf96823760777d0a2f153d046389c3d1f1352'
class Scope83(unittest.TestCase):
    def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02983_protection.json').read_text())
    def test_all_previous_source_files_preserved_with_exact_reviewed_storage_delta(self):
        for path,digest in self.data()['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization83((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_previous_test_methods_and_skip_conditions_retained(self):
        data=self.data()
        for path,cases in data['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for c,n in cases:
                self.assertIn((c,n),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[c,n].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+c+'|'+n])
    def test_player_and_skin_runtime_sources_not_modified(self):
        reviewed=json.loads((ROOT/'tests/fixtures/xcmate_02983_reviewed_hooks.json').read_text())['modules']
        allowed={'addon.xml','changelog.txt','artwork_ui.py','artwork_vfs.py','artwork_migration.py','strings.po'}
        self.assertTrue(all(Path(p).name in allowed for p in reviewed),list(reviewed))
    def test_all_committed_channels_and_installer_unchanged(self):
        from channel_contract_02983 import verify
        for path in ('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):self.assertTrue(verify(path,committed=True))
        paths=('script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.82.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.82.zip','online-test/plugin.video.xtreammate-0.1.29.82.zip','index.html','online-test/index.html')
        for path in paths:self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',('48cbdc2fbdb32d2f0225b8db2398b25b4fcc4d6e' if path in ('index.html','online-test/index.html') else BASE)+':'+path],cwd=ROOT),path)
    def test_regular_release_not_authorized_for_83(self):
        import sys
        sys.path.insert(0,str(ROOT/'tools'))
        try:
            from release_channel75 import regular_allowed
            self.assertFalse(regular_allowed())
        finally:sys.path.remove(str(ROOT/'tools'))
