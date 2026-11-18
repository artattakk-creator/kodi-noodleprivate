""".96 native menu callbacks retain source intent, routes and cancel semantics."""
import copy
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

from xcmate027_fixture import Fixture


class WizardMenus96(unittest.TestCase):
    def setUp(self):
        import test_xcmate_setup_02971 as setup71
        setup71.Setup71.setUp(self)
        self.m.dialog.multiselect = mock.Mock()

    def click_sources(self):
        owner = SimpleNamespace(draft=self.d, busy=False, stage='groups', status=mock.Mock(), _closed=False, _initialized=False)
        owner.choose_epg = lambda: self.ui.SetupWindow.choose_epg(owner)
        self.ui.SetupWindow.onClick(owner, 15)
        return owner

    def test_xtream_optional_source_callback_decorates_real_rows_and_preserves_selection(self):
        presets = sys.modules['epg_sources'].PRESET_FEEDS
        self.d.epg_sources = [dict(id='existing', name=presets[0][1], uri=presets[0][2], enabled=True)]
        self.m.dialog.multiselect.return_value = [0]
        self.click_sources()
        heading, rows = self.m.dialog.multiselect.call_args.args
        self.assertIn('Anbieter-Grundversorgung', heading)
        self.assertTrue(all(hasattr(row, 'art') and Path(row.art.get('icon', '')).is_file() for row in rows))
        self.assertEqual([row.getLabel() for row in rows[:-1]], [title for _, title, _ in presets])
        self.assertEqual(self.m.dialog.multiselect.call_args.kwargs['preselect'], [0])
        self.assertTrue(self.m.dialog.multiselect.call_args.kwargs['useDetails'])
        self.assertTrue(self.d.provider_epg)
        self.assertEqual([row['uri'] for row in self.d.epg_sources], [presets[0][2]])

    def test_non_xtream_legacy_source_picker_stays_neutral_and_cancel_keeps_draft(self):
        self.d.data['type'] = 'm3u'
        self.d.provider_epg = False
        before = copy.deepcopy((self.d.data, self.d.epg_sources))
        self.m.dialog.multiselect.return_value = None
        self.click_sources()
        heading, rows = self.m.dialog.multiselect.call_args.args
        self.assertEqual(heading, importlib.import_module('localization').tr(32706))
        self.assertTrue(all(isinstance(row, str) for row in rows))
        self.assertNotIn('useDetails', self.m.dialog.multiselect.call_args.kwargs)
        self.assertEqual((self.d.data, self.d.epg_sources), before)
        self.assertFalse(self.d.provider_epg)


class ArtworkMenus96(Fixture, unittest.TestCase):
    def test_existing_native_route_reaches_the_single_artwork_hub(self):
        self.router._params.update(action='native_options45', group='tmdb_access61')
        with mock.patch('artwork_hub96.show') as hub:
            self.routes.dispatch(self.router)
        hub.assert_called_once_with()

    def test_every_hub_action_and_cancel_uses_its_existing_callback(self):
        hub = importlib.import_module('artwork_hub96')
        state = dict(settings='READY', xmltv=True, tmdb=True, tvmaze=True, token_valid=True, images_enabled=True)
        targets = ('artwork_sources96.choose', 'programme_diagnostic74.show', 'tmdb_connection60.launch',
                   'logo_editor96.manage', 'storage_artwork96.manage', 'settings_guard96.repair',
                   'artwork_sources96.enroll_test_profile', 'manual_image96.manage', 'settings_rebuild99_ui.confirm')
        for action in range(-1, 13):
            with self.subTest(action=action):
                actors = {}
                with mock.patch('artwork_sources96.status', return_value=state), mock.patch.object(hub, 'onboarding', return_value=True):
                    from contextlib import ExitStack
                    with ExitStack() as stack:
                        for target in targets:
                            actors[target] = stack.enter_context(mock.patch(target, return_value='TMDB_OK' if target.endswith('.launch') else None))
                        self.dialog.select.side_effect = [action, -1]
                        self.dialog.yesno.return_value = True
                        self.dialog.ok.reset_mock()
                        hub.show()
                if action in (0, 1, 2):
                    actors[targets[0]].assert_called_once_with(('xmltv', 'tmdb', 'tvmaze')[action], False)
                else:
                    actors[targets[0]].assert_not_called()
                expected = {4: targets[1], 5: targets[2], 6: targets[3], 7: targets[4], 8: targets[5],
                            9: targets[6], 10: targets[7], 11: targets[8]}
                for target in targets[1:]:
                    calls = 1 if target == expected.get(action) or action == 9 and target == targets[2] else 0
                    self.assertEqual(actors[target].call_count, calls, (action, target))
                if action == 3:
                    self.assertIn('XMLTV:', self.dialog.ok.call_args.args[1])
                    self.assertIn('TMDB:', self.dialog.ok.call_args.args[1])
                    self.assertIn('TVMaze:', self.dialog.ok.call_args.args[1])
                rows = self.dialog.select.call_args_list[-1].args[1]
                self.assertEqual(len(rows), 13)
                self.assertTrue(all(row.art.get('icon') for row in rows))
