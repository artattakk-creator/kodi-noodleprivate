"""Exact audited .71 source preservation, channel freeze and scoped entry point."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from stabilization_contract_02972 import without_stabilization72

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f6ce8b135191c223d9cee7c0201f630acd196b75'


class Scope72(unittest.TestCase):
    def test_every_main71_file_retained_with_only_exact_reviewed_changes(self):
        data = json.loads((ROOT / 'tests/fixtures/xcmate_02972_protection.json').read_text())
        for path, digest in data['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization72((ROOT / path).read_bytes(), path)).hexdigest(), digest, path)

    def test_pilot_and_setup_packages_are_not_published_or_modified(self):
        # .72 was explicitly published after this archived .71 baseline.
        channel_base = '2e9e81c696c65b6dfdf0293efca9ed5b51c7bab8'  # separately approved installer .21 publication
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', channel_base, 'online-test'], cwd=ROOT).decode().splitlines()
        for path in paths:
            __import__('channel_contract_02975').verify(path)

    def test_no_live_catalog_or_player_or_installer_repair_path_in_new_modules(self):
        for path in (ROOT / 'src/plugin.video.xtreammate/resources/lib').glob('vodsync*72.py'):
            text = path.read_text()
            for forbidden in ('get_live_streams', 'get_live_categories', 'get_xmltv', 'Player().', 'InstallAddon(', 'RunAddon(', 'Container.Update(', 'Skin.Set', 'replace_catalog('):
                self.assertNotIn(forbidden, text, path.name)

    def test_existing_provider_context_menu_exposes_action_without_new_routing(self):
        path = ROOT / 'src/plugin.video.xtreammate/resources/lib/portal_manager.py'
        self.assertIn('Katalog aktualisieren (Filme / Serien)', path.read_text())
        for name in ('app_routes.py', 'app_entry.py'):
            path = 'src/plugin.video.xtreammate/resources/lib/' + name
            from stabilization_contract_02974 import without_stabilization74
            self.assertEqual(without_stabilization74((ROOT / path).read_bytes(),path), subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT))


if __name__ == '__main__': unittest.main(verbosity=2)
