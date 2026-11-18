"""Issue #488: exercise the real profile files across simulated Kodi processes."""
from contextlib import contextmanager
import errno
import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from xml.etree import ElementTree

LIBRARY = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'
BROKEN = b'<settings><setting id="new_portal_xc_pass">\xff'


@contextmanager
def import_rebuild():
    sys.path.insert(0, str(LIBRARY))
    try:
        import settings_rebuild99
        yield settings_rebuild99
    finally:
        sys.path.remove(str(LIBRARY))


class SettingsRebuild99Tests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.settings = self.root / 'settings.xml'
        try:
            with import_rebuild() as rebuild:
                self.rebuild = rebuild
        except ModuleNotFoundError as error:
            if error.name != 'settings_rebuild99':
                raise
            self.fail('No disk-backed settings-rebuild action exists')

    def backups(self):
        return list(self.root.glob('settings99.before-reset.*.xml'))

    def assert_safe_defaults(self):
        raw = self.settings.read_bytes()
        root = ElementTree.fromstring(raw)
        self.assertEqual((root.tag, root.get('version')), ('settings', '2'))
        values = {node.attrib['id']: node.text for node in root}
        self.assertRegex(values.pop('settings_rebuild_receipt99'), '^[0-9a-f]{32}$')
        self.assertEqual(values, {
            'epg_enabled': 'true', 'programme_xmltv96': 'false',
            'programme_tmdb46': 'false', 'tmdb_research43': 'false',
            'programme_tvmaze67': 'false',
        })
        self.assertNotIn(b'new_portal_xc_pass', raw)
        return raw

    def test_replaces_corrupt_xml_only_after_exit_and_verifies_after_next_exit(self):
        self.settings.write_bytes(BROKEN)
        native_check = Mock(return_value=True)
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-before', native_check), None)
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(self.rebuild.stage(self.root, 'kodi-before'), 'RESTART_REQUIRED')
        self.assertEqual(self.backups()[0].read_bytes(), BROKEN)
        self.assertEqual(self.backups()[0].stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-before', native_check), 'RESTART_REQUIRED')
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-writes', native_check), 'RESTART_REQUIRED')
        raw = self.assert_safe_defaults()
        self.assertEqual(self.settings.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-writes', native_check), 'RESTART_REQUIRED')
        native_check.assert_not_called()
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-verifies', native_check), 'POST_RESTART_OK')
        native_check.assert_called_once()
        self.assertEqual(self.settings.read_bytes(), raw)
        self.assertEqual(self.rebuild.resume(self.root, 'kodi-further', native_check), None)
        self.assertEqual(self.rebuild.stage(self.root, 'kodi-further'), 'POST_RESTART_OK')
        self.assertEqual(len(self.backups()), 1)

    def test_missing_valid_duplicate_and_large_settings_are_handled_without_lastgood(self):
        samples = (None, b'<settings><setting id="x">1</setting></settings>',
                   b'<settings><setting id="x"/><setting id="x"/></settings>',
                   b'<unexpected/>', b'x' * 262145)
        for original in samples:
            with self.subTest(size=len(original or b'')), TemporaryDirectory() as directory:
                root = Path(directory)
                if original is not None:
                    (root / 'settings.xml').write_bytes(original)
                self.assertEqual(self.rebuild.stage(root, 'original'), 'RESTART_REQUIRED')
                self.assertEqual(self.rebuild.stage(root, 'original'), 'RESTART_REQUIRED')
                copies = list(root.glob('settings99.before-reset.*.xml'))
                self.assertEqual([copy.read_bytes() for copy in copies],
                                 [] if original is None else [original])
                self.assertEqual(self.rebuild.resume(root, 'apply', lambda receipt: True), 'RESTART_REQUIRED')
                self.assertEqual(self.rebuild.resume(root, 'verify', lambda receipt: True), 'POST_RESTART_OK')

    def test_does_not_touch_private_data(self):
        stored = {name: name.encode() for name in (
            'portals.json', 'tmdb_read_access_token.txt', 'epg.db', 'guide.sqlite',
            'favorites.json', 'logo-mapping.json', 'source-mapping.json', 'settings96.lastgood.xml')}
        self.settings.write_bytes(BROKEN)
        for name, data in stored.items():
            (self.root / name).write_bytes(data)
        self.rebuild.stage(self.root, 'original')
        self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        self.rebuild.resume(self.root, 'verify', lambda receipt: True)
        for name, data in stored.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_native_cache_restoring_old_file_is_reported_and_never_overwritten(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, 'original')
        self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        self.settings.write_bytes(BROKEN)
        with self.assertRaisesRegex(self.rebuild.RebuildError, '^KODI_CACHE_CONFLICT$'):
            self.rebuild.resume(self.root, 'verify', lambda receipt: True)
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(self.backups()[0].read_bytes(), BROKEN)

    def test_a_different_interpreter_cannot_replace_settings_while_origin_is_alive(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, self.rebuild.process_identity())
        self.assertEqual(self.rebuild.resume(self.root, 'other-kodi', lambda receipt: True), 'RESTART_REQUIRED')
        self.assertEqual(self.settings.read_bytes(), BROKEN)

    def test_concurrent_resumer_cannot_bypass_the_profile_lock(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, 'original')
        with self.rebuild._directory(self.root) as directory, self.rebuild._locked(directory):
            with self.assertRaisesRegex(self.rebuild.RebuildError, '^REPAIR_BUSY$'):
                self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(len(self.backups()), 1)

    def test_keeps_changes_made_after_confirmation_by_another_writer(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, 'original')
        changed = b'<settings><setting id="epg_enabled">false</setting></settings>'
        self.settings.write_bytes(changed)
        with self.assertRaisesRegex(self.rebuild.RebuildError, '^KODI_CACHE_CONFLICT$'):
            self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        self.assertEqual(self.settings.read_bytes(), changed)

    def test_fails_if_native_settings_are_unreadable_after_restart(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, 'original')
        self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        with self.assertRaisesRegex(self.rebuild.RebuildError, '^KODI_CACHE_CONFLICT$'):
            self.rebuild.resume(self.root, 'verify', lambda receipt: False)
        self.assert_safe_defaults()

    def test_rejects_symlink_without_touching_its_target(self):
        target = self.root / 'private.xml'
        target.write_bytes(BROKEN)
        self.settings.symlink_to(target)
        with self.assertRaisesRegex(self.rebuild.RebuildError, '^BACKUP_FAILED$'):
            self.rebuild.stage(self.root, 'original')
        self.assertTrue(self.settings.is_symlink())
        self.assertEqual(target.read_bytes(), BROKEN)
        self.assertEqual(self.backups(), [])

    def test_fails_closed_when_backup_filesystem_has_no_space(self):
        self.settings.write_bytes(BROKEN)
        with patch.object(self.rebuild.os, 'fsync', side_effect=OSError(errno.ENOSPC, 'private path')):
            with self.assertRaisesRegex(self.rebuild.RebuildError, '^NO_SPACE$'):
                self.rebuild.stage(self.root, 'original')
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(self.backups(), [])
        self.assertIsNone(self.rebuild.resume(self.root, 'new-kodi', lambda receipt: True))

    def test_interrupted_phase_can_recover_after_replacement_without_a_second_write(self):
        self.settings.write_bytes(BROKEN)
        self.rebuild.stage(self.root, 'original')
        replace = self.rebuild.os.replace

        def interrupt_after_settings_replace(source, destination, **kwargs):
            replace(source, destination, **kwargs)
            if destination == 'settings.xml':
                raise KeyboardInterrupt

        with patch.object(self.rebuild.os, 'replace', side_effect=interrupt_after_settings_replace):
            with self.assertRaises(KeyboardInterrupt):
                self.rebuild.resume(self.root, 'apply', lambda receipt: True)
        original_inode = self.settings.stat().st_ino
        self.assertEqual(self.rebuild.resume(self.root, 'verify', lambda receipt: True), 'POST_RESTART_OK')
        self.assertEqual(self.settings.stat().st_ino, original_inode)
        self.assertEqual(hashlib.sha256(self.backups()[0].read_bytes()).digest(),
                         hashlib.sha256(BROKEN).digest())


class KodiSettingsRebuild99Tests(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        sys.path.insert(0, str(LIBRARY))
        self.addCleanup(sys.path.remove, str(LIBRARY))
        self.settings = self.root / 'settings.xml'
        self.settings.write_bytes(BROKEN)
        self.dialog = Mock()
        self.gui = SimpleNamespace(Dialog=lambda: self.dialog, DLG_YESNO_NO_BTN=10)
        self.addon = Mock()
        self.addon.getLocalizedString.return_value = 'XCMate repair'
        self.addon.getSettingString.side_effect = lambda key: {
            node.get('id'): node.text for node in ElementTree.parse(self.settings).getroot()
        }[key]
        self.addon.getSettingBool.side_effect = lambda key: {
            node.get('id'): node.text == 'true'
            for node in ElementTree.parse(self.settings).getroot()
        }[key]
        self.xbmc = SimpleNamespace(log=Mock(), LOGINFO=1, getCondVisibility=lambda _: False)
        self.active_process = 'first'
        modules = {
            'xbmc': self.xbmc, 'xbmcgui': self.gui,
            'xbmcaddon': SimpleNamespace(Addon=lambda: self.addon),
            'xbmcvfs': SimpleNamespace(translatePath=lambda _: str(self.settings)),
            'profile_transaction': SimpleNamespace(writing=lambda: TemporaryDirectory()),
        }
        mocks = patch.dict(sys.modules, modules)
        mocks.start()
        self.addCleanup(mocks.stop)
        try:
            with import_rebuild() as rebuild:
                import settings_rebuild99_ui
                self.ui = settings_rebuild99_ui
        except ModuleNotFoundError as error:
            if error.name != 'settings_rebuild99_ui':
                raise
            self.fail('The Kodi startup and confirmation paths are missing')
        identity = patch.object(rebuild, 'process_identity', side_effect=lambda: self.active_process)
        identity.start()
        self.addCleanup(identity.stop)

    def test_cancel_never_stages_anything_and_native_check_is_read_only(self):
        self.dialog.yesno.return_value = False
        self.assertFalse(self.ui.confirm())
        self.assertEqual(list(self.root.iterdir()), [self.settings])
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(self.dialog.yesno.call_args.kwargs['defaultbutton'], 10)
        self.dialog.yesno.return_value = True
        self.assertTrue(self.ui.confirm())
        self.assertTrue(self.ui.preflight())
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.active_process = 'second'
        self.assertTrue(self.ui.preflight())
        self.addon.getSettingBool.assert_not_called()
        self.active_process = 'third'
        self.assertFalse(self.ui.preflight())
        self.assertEqual(self.addon.getSettingBool.call_count, 5)
        self.addon.setSetting.assert_not_called()
        with import_rebuild():
            import settings_guard96
            self.assertEqual(settings_guard96.snapshot()['code'], 'READY')

    def test_native_defaults_alone_do_not_prove_kodi_loaded_user_file(self):
        self.dialog.yesno.return_value = True
        self.assertTrue(self.ui.confirm())
        self.active_process = 'second'
        self.assertTrue(self.ui.preflight())
        self.active_process = 'third'
        self.addon.getSettingString.side_effect = None
        self.addon.getSettingString.return_value = ''
        self.assertTrue(self.ui.preflight())
        self.assertEqual(self.xbmc.log.call_args.args[0], '[XCMate][SETTINGS99] KODI_CACHE_CONFLICT')

    def test_direct_kodi_route_always_requires_confirmation(self):
        self.dialog.yesno.return_value = False
        self.assertTrue(self.ui.entry(['plugin://plugin.video.xtreammate', '-1', '?action=settings_rebuild99']))
        self.dialog.yesno.assert_called_once()
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.assertEqual(list(self.root.iterdir()), [self.settings])

    def test_pending_boot_blocks_repairs_while_native_settings_dialog_is_open(self):
        self.dialog.yesno.return_value = True
        self.assertTrue(self.ui.confirm())
        self.active_process = 'second'
        self.xbmc.getCondVisibility = lambda _: True
        self.assertTrue(self.ui.preflight())
        self.assertEqual(self.settings.read_bytes(), BROKEN)
        self.xbmc.getCondVisibility = lambda _: False
        self.assertTrue(self.ui.preflight())
        self.assertEqual(ElementTree.parse(self.settings).getroot().tag, 'settings')


if __name__ == '__main__':
    unittest.main()
