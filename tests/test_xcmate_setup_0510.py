"""XC Mate 0.5.10 one-click, player-collision and safe brand compatibility tests."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src/script.gsmedia.setup/resources/lib"
sys.path.insert(0, str(LIB))
import setup_tmdb_apply as player


class FakeAddon:
    def __init__(self):
        self.data = {}
    def getSetting(self, key):
        return self.data.get(key, "")
    def setSetting(self, key, val):
        self.data[key] = val


def source_fixture(base):
    root = Path(base)
    xvault = root / "installed" / "plugin.video.xvault"
    tmdb = root / "userdata" / "plugin.video.themoviedb.helper"
    f = xvault / "resources" / "tmdbhelper" / "xvault.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({
        "name": "xVAULT", "plugin": "plugin.video.xvault",
        "play_movie": "plugin://plugin.video.xvault/?action=playTMDbHelper&tmdb_id={tmdb}&imdb={imdb}",
        "play_episode": "plugin://plugin.video.xvault/?action=playTMDbHelper&tmdb_id={tmdb}&imdb={imdb}&season={season}&episode={episode}",
    }), encoding="utf-8")
    return xvault, tmdb


class PlayerPreservationTests(unittest.TestCase):
    def test_primary_player_name_collision_uses_owned_alias_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            xvault, tmdb = source_fixture(tmp)
            legacy = tmdb / "players" / player.PLAYER_FILE
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_bytes(b'{"custom": "existing file"}')
            addon = FakeAddon()
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "APPLIED")
            self.assertEqual(legacy.read_bytes(), b'{"custom": "existing file"}')
            alias = tmdb / "players" / player.ALT_PLAYER_FILE
            self.assertTrue(alias.is_file())
            self.assertEqual(alias.read_bytes(), (xvault/"resources/tmdbhelper/xvault.json").read_bytes())
            self.assertEqual(addon.getSetting("default_player_movies"), player.ALT_MOVIE_PLAYER)
            self.assertEqual(addon.getSetting("default_player_episodes"), player.ALT_EPISODE_PLAYER)
            self.assertTrue(player.verify(xvault, tmdb, addon))
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "APPLIED")

    def test_existing_nonempty_custom_defaults_never_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            xvault, tmdb = source_fixture(tmp)
            orig = tmdb / "players" / player.PLAYER_FILE
            orig.parent.mkdir(parents=True, exist_ok=True)
            orig.write_bytes(b"keep user file")
            addon = FakeAddon()
            addon.setSetting("default_player_movies", "my.custom.movie")
            addon.setSetting("default_player_episodes", "my.custom.episode")
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "EXISTING_DEFAULTS_PRESERVED")
            self.assertEqual(orig.read_bytes(), b"keep user file")
            self.assertFalse((tmdb/"players"/player.ALT_PLAYER_FILE).exists())
            self.assertEqual(addon.getSetting("default_player_movies"), "my.custom.movie")

    def test_both_names_taken_with_different_bytes_never_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            xvault, tmdb = source_fixture(tmp)
            root = tmdb / "players"
            root.mkdir(parents=True)
            for filename in (player.PLAYER_FILE, player.ALT_PLAYER_FILE):
                (root / filename).write_text("custom", encoding="utf-8")
            addon = FakeAddon()
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "EXISTING_PLAYER_PRESERVED")
            for filename in (player.PLAYER_FILE, player.ALT_PLAYER_FILE):
                self.assertEqual((root / filename).read_text(), "custom")

    def test_existing_default_on_primary_collision_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            xvault, tmdb = source_fixture(tmp)
            p = tmdb/"players"/player.PLAYER_FILE
            p.parent.mkdir(parents=True)
            p.write_bytes(b"custom")
            addon = FakeAddon()
            addon.setSetting("default_player_movies", player.MOVIE_PLAYER)
            addon.setSetting("default_player_episodes", player.EPISODE_PLAYER)
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "EXISTING_DEFAULTS_PRESERVED")
            self.assertEqual(p.read_bytes(), b"custom")

    def test_fresh_install_without_collision_uses_standard_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            xvault, tmdb = source_fixture(tmp)
            addon = FakeAddon()
            self.assertEqual(player.apply(xvault, tmdb, addon, True, True), "APPLIED")
            self.assertEqual(addon.getSetting("default_player_movies"), player.MOVIE_PLAYER)
            self.assertEqual(addon.getSetting("default_player_episodes"), player.EPISODE_PLAYER)
            self.assertTrue(player.verify(xvault, tmdb, addon))


class OneClickContractTests(unittest.TestCase):
    def test_no_extra_wizard_confirmations_between_stages(self):
        ui = (LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertEqual(ui.count("dialog.yesno("), 2, "only initial consent and one explicit resume; no redundant per-package retry prompt")
        skin = ui[ui.index('if code == "STAGE_SKIN":'):ui.index('if code == "STAGE_PLAYER":')]
        self.assertNotIn("dialog.yesno", skin)
        player_stage = ui[ui.index('if code == "STAGE_PLAYER":'):ui.index('if code == "STAGE_CHECK":')]
        self.assertNotIn("dialog.yesno", player_stage)
        self.assertIn("TemporaryOfficialAddonSource", ui)
        self.assertIn("EXISTING_DEFAULTS_PRESERVED", ui)
        self.assertIn("XCMate", ui)

    def test_existing_update_ids_retained_while_visible_brand_changes(self):
        addon = ET.parse(ROOT/"src/script.gsmedia.setup/addon.xml").getroot()
        self.assertEqual(addon.get("id"), "script.gsmedia.setup")
        self.assertEqual(addon.get("version"), "0.5.16")
        self.assertEqual(addon.get("name"), "XCMate Media Center Setup – v0.5.16 – Kodi 21.3 Omega")
        self.assertEqual(addon.get("provider-name"), "XCMate")
        builder=(ROOT/"tools/build_gsmedia_pilot050.py").read_text(encoding="utf-8")
        self.assertIn('PILOT_ID = "repository.gsmedia.pilot"', builder)
        self.assertIn('PILOT_VERSION = "1.9.9"', builder)
        self.assertIn("xcMate Repository", builder)


if __name__ == "__main__":
    unittest.main()
