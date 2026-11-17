"""Host regressions for conservative widget50 plan retention."""
import hashlib
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src' / 'plugin.video.xtreammate' / 'resources' / 'lib'))
import widget_plan_retention as retention
import widget_transaction50 as transaction


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'widget50_plans'
        self.root.mkdir()
        self.targets = Path(self.tmp.name) / 'skin'
        self.targets.mkdir()

    def plan(self, ident, before, after, state='APPLIED', date=None, target='Home.xml', valid=True):
        path = self.root / ident
        path.mkdir()
        targetfile = self.targets / target
        if not targetfile.exists():
            targetfile.write_bytes(after)
        data = {'id': ident, 'kind': 'skin', 'entries': [
            {'target': str(targetfile), 'before': hashlib.sha256(before).hexdigest(),
             'after': hashlib.sha256(after).hexdigest(), 'mode': 0o600}],
            'metadata': {}, 'at': time.time() if date is None else date}
        (path / 'plan.json').write_text(json.dumps(data))
        (path / 'state.json').write_text(json.dumps({'state': state}))
        (path / 'original.0').write_bytes(before)
        (path / 'candidate.0').write_bytes(after if valid else b'CORRUPT')
        (path / 'restore-check.0').write_bytes(before)
        return path

    def test_keeps_one_live_plan_and_prunes_old(self):
        now = time.time()
        a, b, c = 'a'*32, 'b'*32, 'c'*32
        p1 = self.plan(a, b'0', b'1', date=now-500000)
        self.plan(b, b'1', b'2', date=now-360000)
        p3 = self.plan(c, b'2', b'3', date=now-5000)
        (self.targets / 'Home.xml').write_bytes(b'3')
        dry = retention.prune(directory=self.root, now=now)
        self.assertEqual(dry['deletable'], [a, b])
        self.assertTrue(p1.exists())
        real = retention.prune(directory=self.root, now=now, commit=True)
        self.assertEqual(real['removed'], [a, b])
        self.assertEqual(real['retained'], [c])
        self.assertTrue(p3.exists())

    def test_stale_prepared_removable_but_recent_safe(self):
        now = time.time()
        a, b, c = 'a'*32, 'b'*32, 'c'*32
        self.plan(a, b'0', b'1', date=now-400000)
        stale = self.plan(b, b'0', b'1', state='PREPARED', date=now-400000)
        recent = self.plan(c, b'0', b'1', state='PREPARED', date=now-900)
        result = retention.prune(directory=self.root, commit=True, now=now)
        self.assertEqual(result['removed'], [b])
        self.assertTrue(recent.exists())
        self.assertFalse(stale.exists())

    def test_no_live_match_fails_closed(self):
        now = time.time()
        a, b = 'a'*32, 'b'*32
        self.plan(a, b'0', b'1', date=now-700000)
        self.plan(b, b'1', b'2', date=now-500000)
        (self.targets / 'Home.xml').write_bytes(b'foreign')
        result = retention.prune(directory=self.root, commit=True, now=now)
        self.assertEqual(result['removed'], [])
        self.assertEqual(len(result['retained']), 2)

    def test_corrupt_file_blocks_all_prune(self):
        now = time.time()
        a, b = 'a'*32, 'b'*32
        self.plan(a, b'0', b'1', date=now-700000)
        self.plan(b, b'1', b'2', date=now-500000, valid=False)
        (self.targets / 'Home.xml').write_bytes(b'1')
        result = retention.prune(directory=self.root, commit=True, now=now)
        self.assertEqual(result['removed'], [])
        self.assertTrue(result['blocked'])

    def test_other_folders_untouched(self):
        now = time.time()
        a, b = 'a'*32, 'b'*32
        self.plan(a, b'0', b'1', date=now-700000)
        self.plan(b, b'1', b'2', date=now-500000)
        (self.targets / 'Home.xml').write_bytes(b'2')
        keep = self.targets / 'USER_SETTINGS.txt'
        keep.write_text('untouched')
        retention.prune(directory=self.root, commit=True, now=now)
        self.assertEqual(keep.read_text(), 'untouched')

    def test_symlink_is_not_followed(self):
        now = time.time()
        a, b = 'a'*32, 'b'*32
        self.plan(a, b'0', b'1', date=now-700000)
        self.plan(b, b'1', b'2', date=now-500000)
        (self.targets / 'Home.xml').write_bytes(b'2')
        victim = self.targets / 'do-not-delete'
        victim.write_text('safe')
        os.symlink(victim, self.root / 'unexpected')
        result = retention.prune(directory=self.root, commit=True, now=now)
        self.assertEqual(result['removed'], [])
        self.assertTrue(victim.exists())

    def test_cleanup_after_successful_transaction(self):
        now = time.time()
        self.plan('a'*32, b'0', b'1', date=now-600000)
        target = self.targets / 'Home.xml'
        target.write_bytes(b'1')
        utils = types.ModuleType('utils')
        utils.addon_data_dir = lambda: str(Path(self.tmp.name))
        with patch.dict(sys.modules, {'utils': utils}):
            created = transaction.prepare('skin', [(target, b'2')])
            answer = transaction.apply(created['id'], 'skin', [target], confirmed=True)
        self.assertEqual(answer['code'], 'SAVED')
        self.assertEqual(target.read_bytes(), b'2')
        self.assertFalse((self.root / ('a'*32)).exists())
        self.assertTrue((self.root / created['id']).exists())

    def test_bad_prune_does_not_uncommit_applied_change(self):
        target = self.targets / 'Home.xml'
        target.write_bytes(b'0')
        utils = types.ModuleType('utils')
        utils.addon_data_dir = lambda: str(Path(self.tmp.name))
        with patch.dict(sys.modules, {'utils': utils}):
            created = transaction.prepare('skin', [(target, b'2')])
            with patch('widget_plan_retention.prune', side_effect=OSError('read failure')):
                answer = transaction.apply(created['id'], 'skin', [target], confirmed=True)
        self.assertEqual(answer['code'], 'SAVED')
        self.assertEqual(target.read_bytes(), b'2')
        self.assertTrue((self.root / created['id']).exists())

    def test_stale_quarantine_recovered(self):
        now = time.time()
        path = self.plan('a'*32, b'0', b'1', date=now-700000)
        self.plan('b'*32, b'1', b'2', date=now-500000)
        (self.targets / 'Home.xml').write_bytes(b'2')
        quarantine = self.root / ('.pruning-'+'a'*32)
        path.rename(quarantine)
        (quarantine / 'original.0').unlink()
        result = retention.prune(directory=self.root, commit=True, now=now)
        self.assertFalse(quarantine.exists())
        self.assertEqual(result['recovered'], [quarantine.name])


if __name__ == '__main__':
    unittest.main()
