"""Mini mapping shares the grid controller and keeps previews out of storage."""
from contextlib import contextmanager
import importlib
import io
import time
from pathlib import Path
import types
import unittest
from unittest import mock

from xcmate027_fixture import ADDON
import test_xcmate_epg_binding_02948 as old


class MiniMapping96(unittest.TestCase):
    def setUp(self):
        self.fixture = old.Binding48(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.mapping = importlib.import_module('guide_mapping48')
        self.context = importlib.import_module('mapping_context96')
        self.snapshot = importlib.import_module('tv_data').GuideSnapshot(self.fixture.portal, self.fixture.client)
        self.channel = types.SimpleNamespace(name='Selected station', tvg_id='xml', logo='', extra={'stream_id': '1', 'category_id': 'a'})
        self.control = types.SimpleNamespace(getId=lambda: 501, getSelectedPosition=lambda: 0)
        self.parent = types.SimpleNamespace(portal=self.fixture.portal, _guide=self.snapshot,
            _closed=False, mode='channels', category_id='a', visible_channels=[self.channel],
            _page_start=0, _row_offset=0, control=self.control, _highlight={'channels': 0},
            _mini=types.SimpleNamespace(focused=False, signature='original'),
            getFocusId=lambda: 501, setFocusId=mock.Mock(), _render=mock.Mock(), sid='playing-other')
        self.dialog = self.mapping.MappingWindow48('XCMateMapping48.xml', str(ADDON), 'Default', '720p')
        self.dialog.configure(self.parent, self.context.MiniAdapter(self.parent, self.channel))
        self.dialog.onInit()
        self.addCleanup(self.dialog.close)
        self.dialog.source={'id': self.fixture.bid, 'name': 'Second XMLTV'}
        self.dialog.candidate={'id': 'xml', 'name': 'Station'}
        patch = mock.patch.object(self.dialog, '_submit', side_effect=lambda load, ready: ready(load()))
        patch.start(); self.addCleanup(patch.stop)

    def bytes(self):
        return Path(self.fixture.sources._file_path()).read_bytes(), Path(self.fixture.store.path()).read_bytes()

    def finish(self):
        with mock.patch.object(self.dialog, 'show', side_effect=self.dialog.close):
            self.dialog.run()

    def test_mini_preview_contains_actual_programmes_times_description_and_writes_nothing(self):
        before=self.bytes()
        self.dialog._preview()
        info=self.snapshot.get('1', self.fixture.now)
        self.assertEqual(info['now'], 'Source 2')
        self.assertEqual(info['description'], 'Exact description 2')
        self.assertEqual(info['epg_id'], 'xml')
        self.assertEqual(info['start'], self.fixture.now-60)
        self.assertEqual(info['stop'], self.fixture.now+600)
        self.assertEqual(info['events'][0]['source_key46'], self.fixture.bid)
        self.assertIn('Exact description 2', self.dialog.getControl(301).text)
        self.assertIn('Source 2', self.dialog.getControl(301).text)
        self.assertEqual(self.bytes(), before)
        self.assertFalse(hasattr(self.parent, 'origin'))
        self.parent._render.assert_called_with(focus=False)
        self.assertEqual(self.parent.sid, 'playing-other')

    def test_cancel_removes_preview_restores_focus_and_preserves_original_snapshot(self):
        original={'now': 'Original', 'start': self.fixture.now-60, 'stop': self.fixture.now+300, 'events': []}
        self.snapshot._values['1']=original
        before=self.bytes()
        self.dialog._preview(); self.finish()
        self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'Original')
        self.assertEqual(self.bytes(), before)
        self.parent.setFocusId.assert_called_with(501)
        self.assertEqual(self.parent.mode, 'channels')
        self.assertEqual(self.parent._highlight, {'channels': 0})

    def test_save_commits_one_exact_source_and_channel_then_clears_preview(self):
        self.dialog._preview(); self.dialog.onClick(405)
        self.assertTrue(self.dialog.saved)
        self.finish()
        state=self.fixture.sources.configuration('p')
        self.assertEqual(state['mappings'], {'1': 'xml', '2': 'xml'})
        self.assertEqual(state['source_mappings48']['1'], {'channel': 'xml', 'source': self.fixture.bid})
        self.assertEqual(state['sources'], [self.fixture.a, self.fixture.b])
        self.assertFalse(self.snapshot._preview96)
        self.assertTrue(self.snapshot._wake.is_set())

    def test_success_requires_independent_persisted_readback(self):
        self.dialog._preview()
        with mock.patch.object(self.fixture.binding, 'save', return_value=True):
            self.dialog.onClick(405)
        self.assertFalse(self.dialog.saved)
        self.assertFalse(self.dialog._closed)
        self.assertIn('nicht gespeichert', self.dialog.getControl(103).text)

    def test_same_channel_id_from_two_sources_can_be_compared_without_write(self):
        before=self.bytes(); self.dialog._preview()
        self.dialog.source={'id': self.fixture.aid, 'name': 'First XMLTV'}
        self.dialog._preview()
        self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'Source 1')
        self.assertEqual(self.bytes(), before)

    def test_request_uses_native_sender_focus_and_rejects_programme_and_page_rows(self):
        self.assertTrue(self.mapping.request_mini(self.parent))
        self.assertEqual(self.parent._mapping_request96['sid'], '1')
        self.parent.getFocusId=lambda: 999
        self.assertFalse(self.mapping.request_mini(self.parent))
        self.parent.getFocusId=lambda: 501
        self.parent._mini.focused=True
        self.assertFalse(self.mapping.request_mini(self.parent))
        self.parent._mini.focused=False
        self.parent._row_offset=1
        self.assertFalse(self.mapping.request_mini(self.parent))
        self.parent._row_offset=0
        self.channel.extra['stream_id']=''
        self.assertFalse(self.mapping.request_mini(self.parent))

    def test_snapshot_preview_epoch_rejects_late_results_and_worker_overwrites(self):
        epoch=self.snapshot.begin_preview96('1')
        value={'now':'Preview', 'start':self.fixture.now-60, 'stop':self.fixture.now+60, 'events':[]}
        self.assertTrue(self.snapshot.set_preview96('1', epoch, value))
        self.snapshot._values['1']=dict(value, now='Worker')
        self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'Preview')
        self.snapshot.clear_preview96('1', epoch)
        self.assertFalse(self.snapshot.set_preview96('1', epoch, value))
        self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'Worker')

    def test_cold_xmltv_preview_is_ram_only_until_save_and_survives_offline_reload(self):
        fmt=lambda stamp: time.strftime('%Y%m%d%H%M%S +0000', time.gmtime(stamp))
        xml=('<tv><channel id="new96"><display-name>Unmatched station</display-name></channel>'
             '<programme channel="new96" start="'+fmt(self.fixture.now-60)+'" stop="'+fmt(self.fixture.now+600)+'">'
             '<title>Cold programme</title><desc>Actual cold description</desc>'
             '<icon src="https://image.invalid/cold96.png"/></programme></tv>').encode()
        @contextmanager
        def source_stream(*args, **kwargs):
            yield io.BytesIO(xml)
        self.dialog.candidate={'id': 'new96', 'name': 'Unmatched station'}
        # SQLite mode=ro may create only empty WAL/SHM coordination files.
        def payloads():
            return {str(p):p.read_bytes() for p in self.fixture.folder.rglob('*') if p.is_file() and not str(p).endswith(('-wal','-shm'))}
        before=payloads()
        with mock.patch('stream_epg.source_stream', side_effect=source_stream):
            self.dialog._preview()
            self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'Cold programme')
            self.assertEqual(payloads(), before)
            for wal in self.fixture.folder.rglob('*-wal'):
                self.assertEqual(wal.stat().st_size, 0)
            self.dialog.onClick(405)
        self.assertTrue(self.dialog.saved)
        self.finish()
        with mock.patch('stream_epg.source_stream', side_effect=AssertionError('offline')):
            reloaded=importlib.import_module('tv_data').GuideSnapshot(self.fixture.portal, self.fixture.client)
            reloaded.request([self.channel]);reloaded.refresh()
            self.assertEqual(reloaded.get('1', self.fixture.now)['now'], 'Cold programme')
            self.assertEqual(reloaded.get('1', self.fixture.now)['description'], 'Actual cold description')

    def test_pending_mini_request_opens_shared_dialog_without_grid_fields(self):
        self.assertTrue(self.mapping.request_mini(self.parent))
        with mock.patch.object(self.mapping.MappingWindow48, 'run', autospec=True) as run:
            self.mapping.open_pending(self.parent)
        opened=run.call_args.args[0]
        self.assertIsInstance(opened.adapter96, self.context.MiniAdapter)
        self.assertEqual(opened.channel['sid'], '1')
        self.assertIsNone(self.parent._mapping_request96)
        opened.adapter96.finish(False)

    def test_pending_request_is_discarded_if_actual_sender_focus_changes(self):
        self.assertTrue(self.mapping.request_mini(self.parent))
        self.parent.getFocusId=lambda: 999
        with mock.patch.object(self.mapping.MappingWindow48, 'run') as run:
            self.mapping.open_pending(self.parent)
        run.assert_not_called()

    def test_ram_preview_rollover_and_new_epoch_preserve_source_and_reject_old_dialog(self):
        self.dialog._preview()
        info=self.snapshot.get('1', self.fixture.now+700)
        self.assertEqual(info['mapping'], 'PREVIEW_RAM96')
        self.assertFalse(info['now'])
        epoch=self.snapshot.begin_preview96('1')
        self.assertFalse(self.snapshot.set_preview96('1', self.dialog.adapter96.epoch, {}))
        self.assertFalse(self.snapshot.clear_preview96('1', self.dialog.adapter96.epoch))
        self.assertTrue(self.snapshot.set_preview96('1', epoch, {'now': 'New owner', 'start': self.fixture.now-60, 'stop': self.fixture.now+60, 'events': []}))
        self.assertEqual(self.snapshot.get('1', self.fixture.now)['now'], 'New owner')
        self.snapshot.clear_preview96('1', epoch)

    def test_failed_channel_reload_cannot_save_a_preview_from_previous_source(self):
        self.dialog._preview()
        self.dialog.source={'id': self.fixture.aid, 'name': 'First XMLTV'}
        with mock.patch.object(self.fixture.binding, 'channels', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):
                self.dialog._channels()
        self.assertFalse(self.dialog.previewed)
        self.assertIsNone(self.dialog.candidate)
        self.assertFalse(self.dialog.getControl(405).enabled)
        before=self.bytes();self.dialog.onClick(405)
        self.assertFalse(self.dialog.saved)
        self.assertEqual(self.bytes(), before)

    def test_search_supports_later_pages_and_duplicate_source_ids(self):
        rows=[('id%04d'%n, 'Name %04d'%n) for n in range(1101)]
        self.fixture.binding.stage_channels('p', 'many96', self.fixture.bid, rows)
        self.fixture.binding.finish_channels('p', 'many96', True)
        self.dialog.offset=1000; self.dialog._channels()
        self.assertEqual(self.dialog.rows[0]['id'], 'id1000')
        self.dialog.onClick(403)
        self.assertEqual(self.dialog.rows[0]['id'], 'id1100')
        self.dialog.query='Name 0420'; self.dialog.offset=0; self.dialog._channels()
        self.assertEqual([r['id'] for r in self.dialog.rows], ['id0420'])


if __name__ == '__main__':
    unittest.main()
