"""Strict native .98 inspector injection; historical validator stays immutable."""
import importlib,importlib.util,inspect,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

class Native98(unittest.TestCase):
    def test_existing_native_engines_allow_explicit_inspector_without_changing_default(self):
        for name in ('run_kodi_epg96_contract','run_kodi_home88_contract'):
            module=importlib.import_module(name)
            self.assertIn('package_inspector',inspect.signature(module.main).parameters)
            self.assertIsNone(inspect.signature(module.main).parameters['package_inspector'].default)
    def test_wrapper_passes_strict98_inspector_to_each_engine_and_preserves96_globals(self):
        self.assertIsNotNone(importlib.util.find_spec('run_xcmate98_native'))
        wrapper=importlib.import_module('run_xcmate98_native')
        import release_candidate96 as old
        import release_candidate98 as current
        before=(old.VERSION,old.NAME)
        for kind,engine,flag in [('mapping','run_kodi_epg96_contract','--mapping482'),('artwork','run_kodi_home88_contract','--qa482')]:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                seen={}
                def native_main(package_inspector=None):
                    seen.update(inspector=package_inspector,argv=list(sys.argv))
                fake=types.SimpleNamespace(__file__=engine+'.py',main=native_main)
                argv=['run_xcmate98_native.py','--kind',kind,'--report-dir',folder,'--addon-zip',str(ROOT/'docs/XCMate/test-builds/02998'/current.NAME),'--resolution','1280x720']
                with mock.patch.object(sys,'argv',argv),mock.patch.dict(sys.modules,{engine:fake}):wrapper.main()
                self.assertIs(seen['inspector'],current.inspect_package)
                self.assertIn(flag,seen['argv']);self.assertIn('1280x720',seen['argv'])
                self.assertEqual(json.loads((Path(folder)/'exact-package98.json').read_text())['version'],'0.1.29.98')
                self.assertEqual((old.VERSION,old.NAME),before)

if __name__=='__main__':unittest.main()
