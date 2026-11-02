"""Offline safety, exact patch hashes, and full-setup regression tests."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "script.gsmedia.setup"
sys.path.insert(0, str(APP / "resources" / "lib"))

import setup_full as full
import setup_patch as skinpatch
import setup_bingie_apply as bingie
import setup_tmdb_apply as player
from setup_plan import MANDATORY


def inventory_for(*ids):
    d = {"repository.xbmc.org": {"version": "3.4.0", "enabled": True},
         "repository.gsmedia": {"version": "1.8.1", "enabled": True}}
    for name in ids:
        d[name] = {"version": "999.99", "enabled": True}
    return {"code": "READY", "addons": d}


class FakeAddon:
    def __init__(self):
        self.settings = {}
    def getSetting(self, key):
        return self.settings.get(key, "")
    def setSetting(self, key, value):
        self.settings[key] = value


class FullSetupTests(unittest.TestCase):
    def test_all_eleven_and_graph(self):
        self.assertEqual(len(MANDATORY), 11)
        ids = [x["id"] for x in full.manifest()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(MANDATORY) <= set(ids))
        self.assertLess(ids.index("script.module.slyguy"), ids.index("slyguy.trailers"))
        self.assertLess(ids.index("script.skinshortcuts"), ids.index("skin.titan.bingie.mod"))

    def test_clean_session_starts_with_only_requested_missing_dependency(self):
        state = full.new_session(123)
        decision = full.decide(state, inventory_for())
        self.assertIn(decision["code"], ("INSTALL_READY", "REPOSITORY_REQUIRED"))
        self.assertEqual(state["phase"], "apps")
        self.assertFalse(state["setup_attempted"])

    def test_external_repositories_need_explicit_bootstrap(self):
        ids = [r["id"] for r in full.manifest()]
        self.assertIn("repository.slyguy", ids)
        rows = {r["id"]: r for r in full.manifest()}
        self.assertEqual(rows["plugin.audio.m3sr2019"]["repo"], "ZIP_REQUIRES_PROVENANCE")
        self.assertEqual(rows["script.ezmaintenanceplus"]["repo"], "ZIP_REQUIRES_PROVENANCE")
        self.assertTrue(full.REPO_BOOTSTRAP["repository.titan.bingie.mod"].startswith("https://"))

    def test_unknown_inventory_and_invalid_journal_fail_closed(self):
        self.assertEqual(full.decide(None, inventory_for())["code"], "INVALID_STATE")
        self.assertEqual(full.decide(full.new_session(9), {"code": "UNKNOWN"})["code"], "INVENTORY_UNAVAILABLE")

    def test_requested_then_confirmed_only_with_live_kodi_evidence(self):
        row = full.manifest()[0]
        inv = inventory_for()
        state = full.new_session(111)
        state = full.mark_requested(state, row["id"])
        self.assertEqual(full.decide(state, inv)["code"], "WAIT_FOR_KODI")
        with self.assertRaises(ValueError):
            full.mark_installed(state, row["id"], inv)
        inv["addons"][row["id"]] = {"version": "999.0", "enabled": True}
        self.assertEqual(full.decide(state, inv)["code"], "CONFIRM_INSTALLED")
        saved = full.mark_installed(state, row["id"], inv)
        self.assertEqual(saved["pending"], "")

    def test_completion_is_blocked_without_real_skin_patch_and_package_verification(self):
        inv = inventory_for(*[r["id"] for r in full.manifest()])
        state = full.new_session(22)
        self.assertEqual(full.decide(state, inv)["code"], "ALL_APPS_PRESENT")
        state = full.advance(state, "apps", inv)
        self.assertEqual(state["phase"], "bingie")
        state = full.advance(state, "bingie", inv)
        state = full.advance(state, "tmdb_xvault", inv)
        self.assertEqual(full.verify_complete(state, inv, True, True, True)["code"], "BINGIE_PATCHES_UNVERIFIED")
        state["steps"]["bingie_patches_applied"] = True
        self.assertEqual(full.verify_complete(state, inv, True, True, False)["code"], "PACKAGE_PROVENANCE_NOT_VERIFIED")
        self.assertEqual(full.verify_complete(state, inv, False, True, True)["code"], "BINGIE_NOT_VERIFIED")
        self.assertEqual(full.verify_complete(state, inv, True, False, True)["code"], "TMDB_PLAYER_NOT_VERIFIED")
        blocked = full.verify_complete(state, inv, True, True, True)
        self.assertEqual(blocked["code"], "MANDATORY_STAGES_UNVERIFIED")
        self.assertIn("postinstall_health_passed", blocked["stages"])
        self.assertIn("repositories_verified", blocked["stages"])
        # A separate audited provenance + live device health-gate can
        # explicitly supply evidence later. No fabricated success by advance().
        from setup_handoff import REQUIRED_STAGES
        state["steps"].update({key: True for key in REQUIRED_STAGES})
        self.assertEqual(full.verify_complete(state, inv, True, True, True)["code"], "READY_FOR_RESTART")

    def test_inventory_does_not_fabricate_dependency_or_repo_verification(self):
        inv = inventory_for(*[r["id"] for r in full.manifest()])
        state = full.advance(full.new_session(442), "apps", inv)
        self.assertTrue(state["steps"]["all_mandatory_apps_enabled"])
        self.assertFalse(state["steps"]["all_dependencies_installed"])
        self.assertFalse(state["steps"]["repositories_verified"])
        self.assertFalse(state["steps"]["packages_verified"])

    def test_corrupt_and_credential_bearing_journal_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "script.gsmedia.setup"
            valid = full.new_session(125)
            bad = dict(valid, token="PRIVATE-SECRET")
            with self.assertRaises(ValueError):
                full.save(profile, bad)
            for changes in (
                {"phase": "restart_pending", "setup_attempted": True},
                {"phase": "handoff_attempted", "setup_attempted": False},
                {"boot_pid": 0},
                {"steps": {"packages_verified": "yes"}},
                {"pending": ["plugin.video.xtreammate"]},
                {"pending": "plugin.video.xtreammate"},
                {"attempted": ["plugin.video.xtreammate", "plugin.video.xtreammate"]},
            ):
                with self.subTest(changes=changes):
                    with self.assertRaises(ValueError):
                        full.save(profile, dict(valid, **changes))
            full.save(profile, valid)
            (profile / full.JOURNAL).write_text(
                '{"schema":1,"origin":"GS_MEDIA_NEW_INSTALL","phase":"restart_pending"}',
                encoding="utf-8")
            with self.assertRaises(ValueError):
                full.load(profile)

    def test_restart_journal_atomic_and_credentialless(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "script.gsmedia.setup"
            state = full.new_session(8787)
            state["phase"] = "apps"
            full.save(p, state)
            again = full.load(p)
            self.assertEqual(again["boot_pid"], 8787)
            self.assertNotIn("password", (p / full.JOURNAL).read_text("utf-8"))
            with self.assertRaises(ValueError):
                full.save(Path(root) / "different.addon", state)


class BingiePatchTests(unittest.TestCase):
    def test_bundled_patch_sources_and_hashes_are_exact(self):
        root = APP / "resources" / "skinpatch"
        data = json.loads((root / "manifest.json").read_text("utf-8"))
        self.assertEqual(data["skin_version"], "2.2.3")
        self.assertEqual(set(data["files"]), set(skinpatch.FILES))
        self.assertTrue((root / "LICENSE.BINGIE").is_file())
        for relative in skinpatch.FILES:
            target = root / relative
            self.assertTrue(target.exists())
            self.assertEqual(skinpatch.digest(target), data["files"][relative]["after"])

    def _example_patch(self, workspace):
        skin = workspace / "skin.titan.bingie.mod"
        src = workspace / "payload"
        original = b"original-BINGIE-2.2.3"
        patched = b"GS-Media-patched"
        manifest = {"skin_version": "2.2.3", "files": {}}
        for rel in skinpatch.FILES:
            for folder, content in ((skin, original), (src, patched)):
                path = folder / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            manifest["files"][rel] = {
                "before": hashlib.sha256(original).hexdigest(),
                "after": hashlib.sha256(patched).hexdigest(),
            }
        (src / "manifest.json").write_text(json.dumps(manifest), "utf-8")
        (src / "LICENSE.BINGIE").write_text("GPL-v2 source attribution", "utf-8")
        return skin, src

    def test_patch_applies_only_pinned_version_and_backs_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skin, package = self._example_patch(root)
            backup = root / "script.gsmedia.setup" / "skinpatch-060"
            self.assertEqual(skinpatch.apply(package, skin, backup, "2.2.2", True)["code"], "UNSUPPORTED_SKIN_VERSION")
            self.assertEqual(skinpatch.inspect(package, skin, "2.2.3")["code"], "READY")
            self.assertEqual(skinpatch.apply(package, skin, backup, "2.2.3", True)["code"], "APPLIED_AND_VERIFIED")
            self.assertEqual(skinpatch.inspect(package, skin, "2.2.3")["pending"], ())
            self.assertEqual((backup / skinpatch.FILES[0]).read_bytes(), b"original-BINGIE-2.2.3")

    def test_modified_skin_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skin, package = self._example_patch(root)
            (skin / skinpatch.FILES[0]).write_bytes(b"someone-else-modified")
            backup = root / "script.gsmedia.setup" / "skinpatch-060"
            self.assertEqual(skinpatch.apply(package, skin, backup, "2.2.3", True)["code"], "SOURCE_HASH_MISMATCH")
            self.assertFalse(backup.exists())


class BingieLayoutTests(unittest.TestCase):
    @staticmethod
    def _installed():
        return inventory_for("skin.titan.bingie.mod", "script.skinshortcuts")

    def test_template_has_first_three_xcmate_widgets(self):
        payload = bingie.render()
        self.assertTrue(bingie.validate(payload[bingie.MENU_FILENAME], payload[bingie.PROPS_FILENAME]))
        self.assertIn(b"widget_live_start_group", payload[bingie.PROPS_FILENAME])
        self.assertIn(b"widget_recent_vod", payload[bingie.PROPS_FILENAME])
        self.assertIn(b"widget_recent_series", payload[bingie.PROPS_FILENAME])

    def test_wont_override_skinshortcuts(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "script.skinshortcuts"
            inv = self._installed()
            inv["addons"]["skin.titan.bingie.mod"]["version"] = "2.2.3"
            inv["addons"]["script.skinshortcuts"]["version"] = "2.1.0"
            self.assertEqual(bingie.inspect_new_profile(folder, inv), "READY")
            self.assertEqual(bingie.apply_new_profile(folder, inv, True), "APPLIED")
            self.assertEqual(bingie.inspect_new_profile(folder, inv), "ALREADY_APPLIED")
            self.assertEqual(bingie.apply_new_profile(folder, inv, True), "ALREADY_APPLIED")
            path = folder / bingie.MENU_FILENAME
            path.write_bytes(b"<shortcuts/>")
            self.assertEqual(bingie.inspect_new_profile(folder, inv), "EXISTING_SKIN_DATA_PRESERVED")
            self.assertEqual(bingie.apply_new_profile(folder, inv, True), "EXISTING_SKIN_DATA_PRESERVED")
            self.assertEqual(path.read_bytes(), b"<shortcuts/>")


class TmdbApplyTests(unittest.TestCase):
    def test_json_validation_and_fresh_only(self):
        src_data = {
            "name": "xVAULT", "plugin": "plugin.video.xvault",
            "play_movie": "plugin://plugin.video.xvault/?action=playTMDbHelper&tmdb_id={tmdb}&imdb={imdb}",
            "play_episode": "plugin://plugin.video.xvault/?action=playTMDbHelper&tmdb_id={tmdb}&imdb={imdb}&season={season}&episode={episode}",
        }
        with tempfile.TemporaryDirectory() as tmp:
            xvault = Path(tmp) / "plugin.video.xvault"
            tmdb = Path(tmp) / "plugin.video.themoviedb.helper"
            source = xvault / "resources" / "tmdbhelper" / "xvault.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps(src_data), encoding="utf-8")
            addon = FakeAddon()
            self.assertEqual(player.apply(xvault, tmdb, addon, fresh_profile=False, user_approved=True), "NOT_AUTHORIZED")
            self.assertEqual(player.apply(xvault, tmdb, addon, fresh_profile=True, user_approved=True), "APPLIED")
            self.assertTrue(player.verify(xvault, tmdb, addon))
            addon.setSetting("default_player_movies", "other.player")
            self.assertEqual(player.apply(xvault, tmdb, addon, fresh_profile=True, user_approved=True), "EXISTING_DEFAULTS_PRESERVED")
            # Swapping the movie/episode defaults is also a customization.
            addon.setSetting("default_player_movies", player.EPISODE_PLAYER)
            addon.setSetting("default_player_episodes", player.MOVIE_PLAYER)
            self.assertEqual(player.apply(xvault, tmdb, addon, fresh_profile=True, user_approved=True), "EXISTING_DEFAULTS_PRESERVED")


if __name__ == "__main__":
    unittest.main()
