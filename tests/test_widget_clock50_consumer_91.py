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
    for kind, action, label, container in (
        ("live", "widget_live_start_group", "Live-TV", 1510),
        ("vod", "widget_recent_vod", "Filme", 1520),
        ("series", "widget_recent_series", "Serien", 1530),
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
            f'<param name="widgetid" value="{container}"/>'
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
        self.assertEqual([n.get('value') for n in tree.findall('.//param[@name="widgetid"]')],
                         ['1510', '1520', '1530'])
        # Only the two include names change. No label, path, refresh hook,
        # container or foreign consumer is rewritten.
        self.assertEqual([n.get('value') for n in tree.findall('.//param[@name="xcmateKind"]')], ['vod','series'])
        stripped=changed.replace(b'<param name="xcmateKind" value="vod" />',b'').replace(b'<param name="xcmateKind" value="series" />',b'')
        self.assertEqual(stripped.replace(b'content="XCMate80.MediaRow"', b'content="widget_base"'), original)

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

    def test_clock_must_be_a_whole_single_query_parameter(self):
        base = 'plugin://plugin.video.xtreammate/?action=widget_recent_vod&'
        for query in ('xclock50=' + CLOCK, 'other=clock50=' + CLOCK,
                      'clock50=' + CLOCK + 'suffix', 'clock50=' + CLOCK + '&clock50=' + CLOCK,
                      'clock50=$INFO[System.Time(HH:mm)]', 'clock50=$INFO[System.Time]'):
            with self.subTest(query=query), self.assertRaises(ValueError):
                directory_uri89(base + query)

    def test_unknown_token_is_not_masked_by_a_valid_clock(self):
        with self.assertRaises(ValueError):
            directory_uri89('plugin://plugin.video.xtreammate/?clock50=' + CLOCK
                            + '&action=widget_recent_vod&bad=$INFO[System.Exec(foo)]')

    def test_executable_boundary_remains_strict(self):
        from navigation_builtin78 import uri
        with self.assertRaises(ValueError):
            uri('plugin://plugin.video.xtreammate/?action=widget_recent_vod&clock50=' + CLOCK)

    def test_first_query_clock_is_preserved(self):
        url = 'plugin://plugin.video.xtreammate/?clock50=' + CLOCK + '&action=widget_recent_series'
        self.assertEqual(directory_uri89(url), url)

    def test_foreign_provider_and_unsafe_quote_rejected(self):
        with self.assertRaises(ValueError):
            directory_uri89("plugin://plugin.video.themoviedb.helper/?info=now_playing")
        with self.assertRaises(ValueError):
            directory_uri89('plugin://plugin.video.xtreammate/?action=widget_recent_vod&clock50="bad"')


if __name__ == "__main__":
    unittest.main()
