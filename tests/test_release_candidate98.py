"""Frozen .98 review contract, independently frozen .96/.97 evidence."""
import hashlib,importlib,importlib.util,json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

class Release98(unittest.TestCase):
    def contract(self):
        self.assertIsNotNone(importlib.util.find_spec('release_candidate98'),'Missing explicit .98 release contract')
        return importlib.import_module('release_candidate98')
    def test_explicit98_version_and_only_authorized_runtime_metadata_change(self):
        c=self.contract();self.assertEqual(c.VERSION,'0.1.29.98')
        base='eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a'
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'--','src/plugin.video.xtreammate'],cwd=ROOT,text=True).splitlines()
        current={'src/'+name:raw for name,raw in c.source98().items()}
        self.assertEqual(set(current),set(paths))
        for name in paths:
            old=subprocess.check_output(['git','show',base+':'+name],cwd=ROOT)
            actual=current[name]
            if name.endswith('/addon.xml'):
                old=E.fromstring(old);actual=E.fromstring(actual)
                self.assertEqual(actual.get('version'),'0.1.29.98');self.assertEqual(old.get('version'),'0.1.29.97')
                actual.set('version',old.get('version'))
                actual.find('.//news').text=old.find('.//news').text
                self.assertEqual(E.tostring(actual),E.tostring(old))
            else:self.assertEqual(actual,old,name)
    def test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes(self):
        """Rebuild the .98 candidate from its original source in later checkouts."""
        c=self.contract()
        original=ROOT/'docs/XCMate/test-builds/02998'/c.NAME
        with tempfile.TemporaryDirectory() as folder:
            proof=c.build_historical(folder);self.assertEqual(proof,c.inspect_package(original))
            self.assertEqual((Path(folder)/c.NAME).read_bytes(),original.read_bytes())
    def test_review_package_never_stages_or_authorizes_any_channel(self):
        c=self.contract();before=c.frozen()
        with tempfile.TemporaryDirectory() as folder:
            proof=c.stage(folder)
            self.assertFalse(proof['repository_released']);self.assertFalse(proof['merge_or_publish_authorized'])
            self.assertEqual(proof['repository_staged'],'NONE');self.assertEqual(proof['android'],'ANDROID_NOT_TESTED')
            self.assertEqual(c.verify(folder),proof);self.assertEqual(c.frozen(),before)
            self.assertEqual({p.name for p in Path(folder).iterdir()},{c.NAME,c.NAME+'.sha256','review-plan98.json'})
            plan=Path(folder)/'review-plan98.json';data=json.loads(plan.read_text());data['merge_or_publish_authorized']=True;plan.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'RC98_PLAN_OR_BASELINE_CHANGED'):c.verify(folder)
    def test_inspector_rejects_extra_missing_duplicate_changed_and_wrong_version(self):
        c=self.contract();original=ROOT/'docs/XCMate/test-builds/02998'/c.NAME
        with zipfile.ZipFile(original) as z:contents={n:z.read(n) for n in z.namelist()}
        for mode in ('extra','missing','duplicate','changed','version'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as folder:
                changed=dict(contents)
                if mode=='extra':changed['plugin.video.xtreammate/UNREVIEWED.txt']=b'extra'
                elif mode=='missing':changed.pop(next(iter(changed)))
                elif mode=='changed':changed[next(iter(changed))]+=b'changed'
                elif mode=='version':changed['plugin.video.xtreammate/addon.xml']=changed['plugin.video.xtreammate/addon.xml'].replace(b'0.1.29.98',b'0.1.29.97')
                path=Path(folder)/c.NAME
                with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
                    for n,raw in changed.items():z.writestr(n,raw)
                    if mode=='duplicate':
                        import warnings
                        with warnings.catch_warnings():warnings.simplefilter('ignore',UserWarning);z.writestr(next(iter(changed)),b'duplicate')
                with self.assertRaisesRegex(ValueError,'RC98_FILE_SET|RC98_SOURCE_BYTES|RC98_MANIFEST'):c.inspect_package(path)
    def test_sha_sidecar_and_output_guards_fail_closed(self):
        c=self.contract()
        for path in (ROOT,ROOT/'online-test',ROOT/'src',ROOT/'plugin.video.xtreammate',ROOT.parent):
            with self.subTest(path=path),mock.patch('package_xcmate71.build') as build:
                with self.assertRaisesRegex(ValueError,'RC98_OUTPUT'):c.stage(path)
                build.assert_not_called()
        with tempfile.TemporaryDirectory() as folder:
            c.stage(folder);(Path(folder)/(c.NAME+'.sha256')).write_text('0'*64+'  '+c.NAME+'\n')
            with self.assertRaisesRegex(ValueError,'RC98_SHA256'):c.verify(folder)
    def test_retained96_and97_bytes_and_current_publication_namespaces_are_frozen(self):
        c=self.contract();self.assertEqual(c.frozen(),c.baseline_frozen())
        old=ROOT/'docs/XCMate/test-builds/issue482/plugin.video.xtreammate-0.1.29.97.zip'
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),'16c81e587cfe1739ae463ec69ba6d142ab75146e47c8273ae6a779ec750a1042')
        self.assertIsNotNone(importlib.util.find_spec('historical_release96'),'Missing immutable historical context')
        history=importlib.import_module('historical_release96');history.verify_retained96()
        with tempfile.TemporaryDirectory() as folder:
            bad=Path(folder)/'historical96.zip';bad.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'HISTORICAL96_PACKAGE'):history.verify_retained96(package=bad)
            side=Path(folder)/'historical96.sha256';side.write_text('0'*64+'  wrong.zip\n')
            with self.assertRaisesRegex(ValueError,'HISTORICAL96_SIDECAR'):history.verify_retained96(sidecar=side)

if __name__=='__main__':unittest.main()
