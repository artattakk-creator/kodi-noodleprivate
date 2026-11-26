"""Regression checks for opt-in Hero installation and safe failure receipts."""

import base64
import errno
import json
import lzma
import types
import unittest
from unittest import mock

from xcmate050_fixture import Fixture50
from xcmate027_fixture import ROOT


class HeroPatch103(Fixture50, unittest.TestCase):
    def setUp(self):
        super().setUp()
        import widget_manager50
        import widget_skin78
        import xbmcvfs

        self.manager = widget_manager50
        self.graph = widget_skin78
        original_translate = xbmcvfs.translatePath
        translation = mock.patch(
            'xbmcvfs.translatePath',
            side_effect=lambda path: str(self.profile) if path == 'special://profile/' else original_translate(path),
        )
        translation.start()
        self.addCleanup(translation.stop)
        data = json.loads(lzma.decompress(base64.b64decode(
            (ROOT / 'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes()
        )))
        for name, value in data.items():
            (self.skin / name).write_text(value)
        self.before = self.graph_bytes()

    def graph_bytes(self):
        return {name: (self.skin / name).read_bytes() for name in self.graph.FILES}

    def setup_dialog(self, results):
        def choose(*args, **kwargs):
            self.assertEqual(self.graph_bytes(), self.before)
            return next(results)

        return mock.Mock(select=mock.Mock(side_effect=choose))

    def test_setup_offers_native_cancel_install_and_optional_details(self):
        self.options['xcmate_ui_language'] = 'de_de'
        dialog = self.setup_dialog(iter([2, -1, -1]))
        with mock.patch('xbmcgui.Dialog', return_value=dialog), mock.patch.object(
            self.manager, 'runtime', return_value=(self.profile, self.skin)
        ):
            self.manager.skin_setup()
        self.assertEqual(dialog.select.call_count, 3)
        first = dialog.select.call_args_list[0]
        self.assertEqual(first.kwargs, {'preselect': 0, 'useDetails': True})
        self.assertEqual([item.getLabel() for item in first.args[1]],
                         ['Abbrechen', 'Jetzt installieren', 'Technische Details'])
        self.assertIn('Senderleiste', first.args[1][1].label2)
        self.assertNotIn('IncludesHomeWidgets.xml', first.args[1][1].label2)
        technical = dialog.select.call_args_list[1]
        self.assertIn('Geprüfte Dateien', technical.args[0])
        details = technical.args[1]
        self.assertEqual(details[0], 'Zurück')
        self.assertIn('xml/IncludesHomeWidgets.xml', details)
        self.assertTrue(any(row.startswith('Vorher ') for row in details))
        self.assertTrue(any(row.startswith('Nachher ') for row in details))
        self.assertNotIn('<control', '\n'.join(details))
        self.assertEqual(self.graph_bytes(), self.before)

    def test_widget_change_during_preview_is_reported_without_writing_skin_files(self):
        dialog = self.setup_dialog(iter([1]))
        self.saved.append(['mainmenu', '10000', 'widgetPath.5', 'plugin://example.test/?demo=1'])

        def select_install(*args, **kwargs):
            self.prop.write_text(repr(self.saved))
            return 1

        dialog.select.side_effect = select_install
        with mock.patch('xbmcgui.Dialog', return_value=dialog), mock.patch.object(
            self.manager, 'runtime', return_value=(self.profile, self.skin)
        ), mock.patch('xbmc.log', create=True) as log:
            self.manager.skin_setup()
        self.assertIn('WIDGET_INVENTORY_CHANGED', dialog.ok.call_args.args[1])
        self.assertTrue(any('stage=inventory' in call.args[0] for call in log.call_args_list))
        self.assertNotIn('example.test', str(log.call_args_list))
        self.assertEqual(self.graph_bytes(), self.before)

    def test_journal_file_permissions_are_diagnosed_without_disclosing_paths(self):
        private_home = str(self.folder)
        dialog = mock.Mock()
        with mock.patch('xbmcgui.Dialog', return_value=dialog), mock.patch.object(
            self.manager, 'runtime', return_value=(self.profile, self.skin)
        ), mock.patch(
            'widget_transaction50.private', side_effect=PermissionError(errno.EACCES, 'Denied', private_home)
        ), mock.patch('xbmc.log', create=True) as log:
            self.manager.skin_setup()
        self.assertIn('PATCH_PERMISSION_DENIED', dialog.ok.call_args.args[1])
        self.assertTrue(any('stage=inventory' in call.args[0] for call in log.call_args_list))
        self.assertNotIn(private_home, str(log.call_args_list) + str(dialog.ok.call_args_list))
        self.assertEqual(self.graph_bytes(), self.before)

    def test_runtime_translates_active_skin_addon_uri_and_rejects_unresolved_profile(self):
        def addon(identifier):
            version = '2.2.3' if identifier == 'skin.titan.bingie.mod' else '2.1.0'
            return types.SimpleNamespace(
                getAddonInfo=lambda name: {'version': version, 'path': 'special://home/addons/skin.titan.bingie.mod/'}[name]
            )

        paths = {
            'special://profile/': str(self.profile),
            'special://skin/': str(self.skin),
            'special://home/addons/skin.titan.bingie.mod/': str(self.skin),
        }
        with mock.patch('xbmc.getSkinDir', return_value='skin.titan.bingie.mod', create=True), mock.patch(
            'xbmcaddon.Addon', side_effect=addon
        ), mock.patch('xbmcvfs.translatePath', side_effect=lambda path: paths.get(path, path)):
            self.assertEqual(self.manager.runtime(), (self.profile, self.skin))
            paths.pop('special://profile/')
            with self.assertRaisesRegex(ValueError, 'PROFILE_PATH_UNAVAILABLE'):
                self.manager.runtime()

    def test_explicit_restore_remains_possible_after_user_changes_saved_widgets(self):
        plan = self.skinmod.prepare(self.skin)
        self.skinmod.apply(plan['id'], self.skin, confirmed=True)
        installed = self.graph_bytes()
        self.assertNotEqual(installed, self.before)
        self.saved.append(['mainmenu', '10000', 'widgetPath.5', 'plugin://example.test/?demo=1'])
        self.prop.write_text(repr(self.saved))
        user = self.prop.read_bytes()
        self.skinmod.apply(plan['id'], self.skin, confirmed=True, restore=True)
        self.assertEqual(self.prop.read_bytes(), user)
        self.assertEqual(self.graph_bytes(), self.before)

    def test_target_permission_failure_restores_verified_files_and_records_rollback(self):
        plan = self.skinmod.prepare(self.skin)
        original = self.tx.replace
        target = self.skin / self.graph.FILES[1]

        def fail(path, *args, **kwargs):
            if path == target:
                raise PermissionError(errno.EROFS, 'Read-only', str(path))
            return original(path, *args, **kwargs)

        with mock.patch.object(self.tx, 'replace', side_effect=fail):
            with self.assertRaises(OSError) as raised:
                self.skinmod.apply(plan['id'], self.skin, confirmed=True)
        self.assertEqual(str(raised.exception), 'PATCH_READ_ONLY')
        self.assertEqual(raised.exception.stage, 'target')
        self.assertEqual(raised.exception.journal, 'ROLLED_BACK')
        self.assertEqual(self.graph_bytes(), self.before)

    def test_private_lock_refuses_symlink(self):
        plan = self.skinmod.prepare(self.skin)
        link = self.tx.folder() / '.lock'
        fake = self.folder / 'unrelated'
        fake.write_text('keep')
        link.symlink_to(fake)
        with self.assertRaisesRegex(ValueError, 'UNSAFE_BACKUP_FOLDER'):
            self.skinmod.apply(plan['id'], self.skin, confirmed=True)
        self.assertEqual(self.graph_bytes(), self.before)
        self.assertEqual(fake.read_text(), 'keep')

    def test_interrupted_journal_can_restore_after_new_invocation(self):
        plan = self.skinmod.prepare(self.skin)
        original = self.tx.replace
        target = self.skin / self.graph.FILES[1]

        def interrupt(path, *args, **kwargs):
            if path == target:
                raise SystemExit
            return original(path, *args, **kwargs)

        with mock.patch.object(self.tx, 'replace', side_effect=interrupt), self.assertRaises(SystemExit):
            self.skinmod.apply(plan['id'], self.skin, confirmed=True)
        state = self.tx.folder() / plan['id'] / 'state.json'
        self.assertNotEqual(self.graph_bytes(), self.before)
        self.assertEqual(json.loads(state.read_text())['state'], 'APPLYING')
        self.skinmod.apply(plan['id'], self.skin, confirmed=True, restore=True)
        self.assertEqual(json.loads(state.read_text())['state'], 'RESTORED')
        self.assertEqual(self.graph_bytes(), self.before)

    def test_approved_legacy_layout_requires_a_new_native_install_choice(self):
        from widget_skin75 import navigation_candidate
        from widget_skin77 import candidate
        import skin_upgrade63

        for name in self.graph.FILES[:4]:
            (self.skin / name).write_bytes(candidate(name, self.before[name]))
        name = self.graph.FILES[4]
        (self.skin / name).write_bytes(navigation_candidate(self.before[name]))
        self.before = self.graph_bytes()
        dialog = self.setup_dialog(iter([0]))
        with mock.patch.multiple(skin_upgrade63, _done=False, _pending=None, _next=0), mock.patch.object(
            self.manager, 'runtime', return_value=(self.profile, self.skin)
        ), mock.patch(
            'xbmcgui.Dialog', return_value=dialog
        ), mock.patch(
            'xbmcgui.getCurrentWindowId', return_value=10000
        ), mock.patch(
            'xbmcgui.getCurrentWindowDialogId', return_value=9999
        ):
            skin_upgrade63.prepare()
            skin_upgrade63.poll()
            skin_upgrade63.prepare()
        dialog.select.assert_called_once()
        self.assertNotIn('XCMate.Home78.Apply', self.properties)
        self.assertEqual(self.graph_bytes(), self.before)

    def test_reload_after_commit_ignores_another_kodi_profile(self):
        import home_activation78

        with mock.patch('epg_handoff63.profile_scope', return_value='first'):
            home_activation78.request('a' * 32)
        with mock.patch('epg_handoff63.profile_scope', return_value='other'), mock.patch(
            'xbmc.getSkinDir', return_value='skin.titan.bingie.mod', create=True
        ), mock.patch(
            'xbmcgui.getCurrentWindowId', return_value=10000
        ), mock.patch('xbmc.getCondVisibility', return_value=False), mock.patch.multiple(
            home_activation78, _next=0
        ):
            home_activation78.poll()
        self.assertNotIn(home_activation78.KEY, self.properties)

    def test_reviewed_102_layout_can_upgrade_and_both_backup_generations_restore(self):
        from home_inventory78 import snapshot

        legacy = self.graph.build(self.before)
        legacy_plan = self.tx.prepare(
            'skin', [(self.skin / name, legacy[name]) for name in self.graph.FILES],
            dict(skin=str(self.skin), meta_sha=self.tx.sha((self.skin / 'addon.xml').read_bytes()),
                 contract78=1, inventory78=snapshot(self.profile, self.skin)),
        )
        self.tx.apply(legacy_plan['id'], 'skin', [self.skin / name for name in self.graph.FILES], confirmed=True)
        plan = self.skinmod.prepare(self.skin)
        self.assertEqual(plan['metadata'].get('layout103'), 1)
        self.skinmod.apply(plan['id'], self.skin, confirmed=True)
        self.assertNotEqual(self.graph_bytes(), legacy)
        self.skinmod.apply(plan['id'], self.skin, confirmed=True, restore=True)
        self.assertEqual(self.graph_bytes(), legacy)
        self.skinmod.apply(legacy_plan['id'], self.skin, confirmed=True, restore=True)
        self.assertEqual(self.graph_bytes(), self.before)
