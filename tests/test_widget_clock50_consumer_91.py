"""Regression: Kodi's generated clock50 token must not suppress owned media rows."""
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/plugin.video.xtreammate/resources/lib"))
from widget_reload78 import candidate, directory_uri89

CLOCK = "$INFO[System.Time(hh:mm)]"
RELOAD = "$INFO[Window(Home).Property(XCMate.Widget45.Reload.{kind})]"


def fixture():
    rows = []
    for kind, action, label in (
        ("live", "widget_live_start_group", "Live-TV"),
        ("vod", "widget_recent_vod", "Filme"),
        ("series", "widget_recent_series", "Serien"),
    ):
        url = (
            "plugin://plugin.video.xtreammate/?action=" + action
            + "&amp;reload=" + RELOAD.format(kind=kind)
            + "&amp;clock50=" + CLOCK
        )
        rows.append(
            '<include content="widget_base" condition="true">'
            '<param name="contentStyle" value="normal"/>'
            '<param name="widgetTarget" value="videos"/>'
            f'<param name="widgetName" value="{label}"/>'
            f'<param name="widgetPath" value="{url}"/>'
            '</include>'
        )
    rows.append(
        '<include content="widget_base" condition="true">'
        '<param name="contentStyle" value="normal"/>'
        '<param name="widgetTarget" value="videos"/>'
        '<param name="widgetName" value="Im Kino"/>'
        '<param name="widgetPath" value="plugin://plugin.video.themoviedb.helper/?info=now_playing"/>'
        '</include>'
    )
    return ("<includes>" + "".join(rows) + "</includes>").encode()


class TestClock50Consumer(unittest.TestCase):
    def test_converts_only_owned_vod_series_rows(self):
        original = fixture()
        changed = candidate(original, layout80=True)
        self.assertNotEqual(changed, original)
        tree = ET.fromstring(changed)
        actual = {
            node.find('param[@name="widgetName"]').get("value"): node.get("content")
            for node in tree.findall("include")
        }
        self.assertEqual(actual, {
            "Live-TV": "widget_base",
            "Filme": "XCMate80.MediaRow",
            "Serien": "XCMate80.MediaRow",
            "Im Kino": "widget_base",
        })
        self.assertIn(CLOCK.encode(), changed)
        self.assertEqual(candidate(changed, layout80=True), changed)

    def test_non_xcmate_layout_not_modified(self):
        original = fixture()
        self.assertEqual(candidate(original, layout80=False), original)

    def test_exact_clock_token_allowed_but_not_executed(self):
        url = "plugin://plugin.video.xtreammate/?action=widget_recent_vod&clock50=" + CLOCK
        self.assertEqual(directory_uri89(url), url)

    def test_arbitrary_info_token_rejected(self):
        with self.assertRaises(ValueError):
            directory_uri89(
                "plugin://plugin.video.xtreammate/?action=widget_recent_vod"
                "&clock50=$INFO[System.Exec(foo)]"
            )

    def test_foreign_provider_and_unsafe_quote_rejected(self):
        with self.assertRaises(ValueError):
            directory_uri89("plugin://plugin.video.themoviedb.helper/?info=now_playing")
        with self.assertRaises(ValueError):
            directory_uri89('plugin://plugin.video.xtreammate/?action=widget_recent_vod&clock50="bad"')


if __name__ == "__main__":
    unittest.main()
