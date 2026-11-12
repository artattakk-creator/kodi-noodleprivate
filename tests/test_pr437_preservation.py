"""Review candidate bytes, historical delta and current .90 channel protection."""
import hashlib
import subprocess
import unittest
import zipfile
from pathlib import Path
from clock50_contract437 import delta437, without_clock437

ROOT = Path(__file__).resolve().parents[1]
BASE = '4336dd56a707f80b3784fa11f179d2a427cd5727'

class Preservation437(unittest.TestCase):
    def test_delta_matches_both_reviewed_full_file_hashes(self):
        d = delta437()
        for version in ('old', 'new'):
            self.assertEqual(hashlib.sha256(d[version].encode()).hexdigest(), d[version+'_sha256'])
        self.assertEqual(d['old'].encode(), subprocess.check_output(['git','show',BASE+':'+d['path']], cwd=ROOT))
        self.assertEqual((ROOT/d['path']).read_text(), d['new'])
        self.assertEqual(without_clock437(d['new'], d['path']), d['old'])

    def test_unreviewed_change_is_never_normalized(self):
        d = delta437()
        changed = d['new'] + '\nUNREVIEWED = True\n'
        self.assertEqual(without_clock437(changed, d['path']), changed)
        self.assertEqual(without_clock437(d['new'], 'foreign_module.py'), d['new'])

    def test_every_published_channel_and_installer_file_stays_at_main(self):
        paths = subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,
            'addons.xml','addons.xml.md5','index.html','online-test',
            'plugin.video.xtreammate','script.gsmedia.setup','src/script.gsmedia.setup'], cwd=ROOT).decode().splitlines()
        for name in paths:
            self.assertEqual((ROOT/name).read_bytes(), subprocess.check_output(['git','show',BASE+':'+name], cwd=ROOT), name)

    def test_candidate_zip_matches_every_current_source_byte(self):
        archive = ROOT/'docs/XCMate/test-builds/pr437/plugin.video.xtreammate-0.1.29.90.zip'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), Path(str(archive)+'.sha256').read_text().split()[0])
        source = ROOT/'src/plugin.video.xtreammate'
        files = [p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and p.name!='.DS_Store']
        with zipfile.ZipFile(archive) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()), {'plugin.video.xtreammate/'+p.relative_to(source).as_posix() for p in files})
            self.assertFalse(any(n.endswith(('.db','.sqlite','.log','.pyc')) for n in z.namelist()))
            for p in files:
                self.assertEqual(z.read('plugin.video.xtreammate/'+p.relative_to(source).as_posix()), p.read_bytes())
