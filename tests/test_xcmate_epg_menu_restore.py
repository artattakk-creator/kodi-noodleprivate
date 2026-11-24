"""Structural regression for XCMate's EPG settings (Kodi-free)."""
import ast
from pathlib import Path
import unittest


SETTINGS = (
    Path(__file__).resolve().parents[1]
    / "src" / "plugin.video.xtreammate" / "resources"
    / "lib" / "settings_sections45.py"
)


def rows():
    tree = ast.parse(SETTINGS.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "ROWS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("ROWS not found in settings_sections45.py")


class TestEPGMenuRestore(unittest.TestCase):
    def test_epg_agent_and_all_existing_settings_accessible(self):
        actual = [entry[1] for entry in rows()["epg"]]
        expected = [
            "epg_agent100",
            "native_options45",
            "guide_browser",
            "epg_sources",
            "guide_status",
            "guide_backup44",
            "refresh_epg",
            "native_options45",
        ]
        self.assertEqual(actual, expected)
        self.assertEqual(rows()["epg"][1][2]["group"], "tmdb_access61")
        self.assertEqual(rows()["epg"][-1][2]["group"], "epg")

    def test_legacy_system_epg_options_deeplink_remains_available(self):
        sections = rows()
        self.assertEqual(
            [(name, params) for _, name, params in sections["epg_tools"]],
            [(name, params) for _, name, params in sections["epg"] if name != "epg_agent100"],
        )
        self.assertIn(
            (36017, "settings_section", {"section": "epg_tools"}),
            sections["system"],
        )


if __name__ == "__main__":
    unittest.main()
