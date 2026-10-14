"""Validate photograph-derived XCMate settings contract (no Kodi runtime).

These tests assert the documented *reference* and privacy discipline; they
are not Android validation or evidence of an implemented settings UI.
"""
import json
from pathlib import Path
import unittest

CONTRACT = (Path(__file__).resolve().parents[1] /
            "docs/XCMate/TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json")
DETAIL = (Path(__file__).resolve().parents[1] /
          "docs/XCMate/TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md")


class TiviMatePhotoContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CONTRACT.read_text(encoding="utf-8")
        cls.data = json.loads(cls.raw)
        cls.detail = DETAIL.read_text(encoding="utf-8")

    @staticmethod
    def by_id(fields):
        return {row["id"]: row for row in fields}

    def test_root_navigation_keeps_photographed_order(self):
        self.assertEqual([entry["label"] for entry in self.data["root"]], [
            "Allgemein", "Wiedergabelisten", "EPG", "Optik",
            "Wiedergabe", "Fernbedienung", "Kindersicherung",
            "Sonstiges", "Über",
        ])
        self.assertEqual(self.data["implementation_status"],
                         "specification_only")
        self.assertEqual(self.data["addon_id"], "plugin.video.xtreammate")
        self.assertEqual(self.data["release_at_observation"], "0.1.10")

    def test_playback_matches_photo_and_system_limits(self):
        found = self.by_id(self.data["playback"])
        self.assertEqual(found["buffer_size"]["observed_value"], "Klein")
        for key in ("audio_decoder", "video_decoder"):
            self.assertEqual(found[key]["observed_value"], "Hardware")
            self.assertEqual(found[key]["capability"], "kodi_system_dependent")
        self.assertEqual(found["auto_frame_rate"]["observed_value"], "Aus")
        self.assertFalse(found["surround_audio_default"]["observed_value"])
        self.assertFalse(found["audio_passthrough"]["observed_value"])
        self.assertEqual(found["external_player"]["observed_value"], "Nein")
        self.assertEqual(found["skip_steps"]["kind"], "submenu")

    def test_misc_nested_sections_and_unknown_switches(self):
        misc = self.data["misc"]
        self.assertEqual([r["id"] for r in misc["root"]], [
            "search_settings", "reminders_settings", "recording_settings",
            "vod_settings",
        ])
        search = self.by_id(misc["search"])
        self.assertIsNone(search["prefer_voice_search"]["observed_value"])
        self.assertTrue(search["show_search_history"]["observed_value"])
        self.assertTrue(search["favourite_channels_first"]["observed_value"])
        self.assertFalse(search["show_past_programs_in_search"]["observed_value"])
        reminder = self.by_id(misc["reminders"])
        self.assertEqual(reminder["reminder_before_program_minutes"]["observed_value"], 0)
        self.assertEqual(reminder["reminder_popup_timeout_seconds"]["observed_value"], 10)
        self.assertEqual(reminder["reminder_default_action"]["observed_value"], "Anschauen")
        self.assertFalse(reminder["reminder_wake_from_sleep"]["observed_value"])
        recording = self.by_id(misc["recording"])
        self.assertEqual(recording["record_before_minutes"]["observed_value"], 0)
        self.assertEqual(recording["record_after_minutes"]["observed_value"], 0)
        self.assertIsNone(recording["recordings_directory"]["observed_value"])
        self.assertIsNone(misc["vod"][0]["observed_value"])

    def test_parental_requires_real_security_not_cosmetic_ui(self):
        parent = self.by_id(self.data["parental"])
        self.assertFalse(parent["parental_enabled"]["observed_value"])
        self.assertEqual(parent["parental_pin_input_method"]["observed_value"], "Sammler")
        for key in ("parental_gate_settings", "parental_gate_playlists",
                    "parental_gate_epg", "parental_gate_channel_options",
                    "parental_gate_group_options"):
            self.assertFalse(parent[key]["observed_value"])
            self.assertEqual(parent[key]["capability"],
                             "security_implementation_required")

    def test_about_keeps_unknown_statistics_and_redacts_identity(self):
        about = self.by_id(self.data["about"])
        self.assertIsNone(about["anonymous_statistics"]["observed_value"])
        self.assertTrue(about["automatic_updates"]["observed_value"])
        self.assertFalse(about["beta_program"]["observed_value"])
        self.assertEqual(about["reference_app_version"]["observed_value"],
                         "5.3.3 (Premium)")
        for key in ("account", "device_name"):
            self.assertIsNone(about[key]["observed_value"])
            self.assertEqual(about[key]["kind"], "redacted_private_value")

    def test_sanitized_docs_contain_no_identifiers_or_secrets(self):
        for source in (self.raw, self.detail):
            with self.subTest(source=source[:40]):
                self.assertNotIn("username=", source.lower())
                self.assertNotIn("password=", source.lower())
                self.assertNotIn("/storage/emulated/", source.lower())
                self.assertNotIn("artattakk@", source.lower())
                self.assertNotIn("magican" + "tv.org", source.lower())
        self.assertIn("1000118393.jpg", self.detail)
        self.assertIn("1000118384.jpg", self.detail)

    def test_photo_file_references_only_and_no_duplicate_section_ids(self):
        from_sections = [
            self.data["playback"], self.data["parental"], self.data["about"],
            *[self.data["misc"][k] for k in
              ("root", "search", "reminders", "recording", "vod")],
        ]
        for entries in from_sections:
            self.assertEqual(len(entries), len({e["id"] for e in entries}))
            for entry in entries:
                self.assertTrue(entry["source_photo"].startswith("10001183"))
                self.assertTrue(entry["source_photo"].endswith(".jpg"))
                self.assertIn("capability", entry)


if __name__ == "__main__":
    unittest.main()
