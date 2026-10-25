"""Host regressions for fresh-profile Wizard preview (no Kodi required)."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / 'src' / 'plugin.video.xtreammate' / 'resources' / 'lib' / 'first_run_setup.py'
spec = importlib.util.spec_from_file_location('xcmate_first_run_preview', MODULE)
first_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(first_run)


class KodiWindow:
    values = {}

    def getProperty(self, key):
        return self.values.get(key, '')

    def setProperty(self, key, value):
        self.values[key] = value

    def clearProperty(self, key):
        self.values.pop(key, None)


class Router:
    def url(self, **kw):
        return 'plugin://plugin.video.xtreammate/?action={}&pid={}'.format(
            kw['action'], kw.get('pid', ''))


class TestFirstRunWizard(unittest.TestCase):

    def setUp(self):
        KodiWindow.values.clear()

    def test_only_readable_empty_list_prompts(self):
        self.assertTrue(first_run.should_autostart([]))
        self.assertFalse(first_run.should_autostart([{'id': 'disabled', 'enabled': False}]))
        self.assertFalse(first_run.should_autostart([{'id': 'existing'}]))
        self.assertFalse(first_run.should_autostart(None))
        self.assertFalse(first_run.should_autostart({}))

    def run_with(self, records, portal):
        commands = []
        attempts = []
        xbmcgui = types.SimpleNamespace(Window=lambda *_: KodiWindow())
        xbmc = types.SimpleNamespace(executebuiltin=commands.append)
        portals = types.SimpleNamespace(load_all=lambda: records)
        wizard = types.SimpleNamespace(setup=lambda: attempts.append('setup') or portal)
        with patch.dict(sys.modules, {'xbmc': xbmc, 'xbmcgui': xbmcgui,
                                      'portals': portals, 'setup_wizard': wizard}):
            result = first_run.launch_once(Router())
        return result, commands, attempts

    def test_cancel_leaves_profile_root_and_no_refresh_loop(self):
        done, commands, attempts = self.run_with([], None)
        self.assertTrue(done)
        self.assertEqual(['setup'], attempts)
        self.assertEqual([], commands)
        self.assertNotIn('XCMate.FirstRunWizardRunning', KodiWindow.values)

    def test_success_only_routes_to_new_portal(self):
        done, commands, attempts = self.run_with([], {'id': 'new-test-id'})
        self.assertTrue(done)
        self.assertEqual(['setup'], attempts)
        self.assertEqual(['Container.Update(plugin://plugin.video.xtreammate/?action=portal_home&pid=new-test-id,replace)'],
                         commands)
        self.assertNotIn('XCMate.FirstRunWizardRunning', KodiWindow.values)

    def test_preexisting_disabled_portal_never_prompts(self):
        done, commands, attempts = self.run_with([{'id': 'saved', 'enabled': False}], None)
        self.assertFalse(done)
        self.assertEqual([], commands)
        self.assertEqual([], attempts)

    def test_running_guard_prevents_parallel_modal_dialog(self):
        KodiWindow.values['XCMate.FirstRunWizardRunning'] = 'true'
        done, commands, attempts = self.run_with([], {'id': 'other'})
        self.assertFalse(done)
        self.assertEqual([], commands)
        self.assertEqual([], attempts)

    def test_exception_releases_running_property(self):
        xbmcgui = types.SimpleNamespace(Window=lambda *_: KodiWindow())
        portals = types.SimpleNamespace(load_all=lambda: [])
        def fail():
            raise OSError('simulated setup failure')
        wizard = types.SimpleNamespace(setup=fail)
        with patch.dict(sys.modules, {'xbmcgui': xbmcgui, 'portals': portals,
                                      'setup_wizard': wizard}):
            with self.assertRaises(OSError):
                first_run.launch_once(Router())
        self.assertNotIn('XCMate.FirstRunWizardRunning', KodiWindow.values)


if __name__ == '__main__':
    unittest.main()
