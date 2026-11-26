"""Offline contract tests for the NAS -> private GitHub -> XCMate schema-4 bridge."""
import gzip
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from xml.etree import ElementTree as ET

LIB = Path(__file__).resolve().parents[1] / "src" / "plugin.video.xtreammate" / "resources" / "lib"
sys.path.insert(0, str(LIB))
import epg_agent_hub4 as hub4
from epg_agent_github import DeliveryError


def manifest():
    profiles = [
        ("all", "epg-all.xml.gz", 111, 2, 4),
        ("de", "epg-de.xml.gz", 222, 1, 2),
        ("at", "epg-at.xml.gz", 333, 1, 2),
    ]
    return {
        "schema_version": 4, "schema": "gsmedia-hub-github-v2",
        "status": "PRIVATE_READY", "delivery": "private-github-release-assets",
        "repo": "artattakk-creator/xcmate-epg-private",
        "default_profile": "all", "release_id": 1234,
        "tag": "gs-hub-20261122T150526Z-c9dade8c575f",
        "fingerprint": "a" * 64, "generated_utc": "2026-11-22T15:05:53Z",
        "files": [
            {"profile": code, "file": name, "bytes": 1234,
             "channels": chans, "programmes": shows,
             "asset_id": asset,
             "api_url": hub4.BASE + str(asset),
             "sha256": chr(97 + idx) * 64,
             "generated_utc": "2026-11-22T10:14:24Z"}
            for idx, (code, name, asset, chans, shows) in enumerate(profiles)
        ],
    }


class TestHub4(unittest.TestCase):
    def test_accepts_real_shape(self):
        obj = manifest()
        self.assertEqual(set(hub4.validate_manifest(obj)), {"de", "at", "all"})

    def test_rejects_wrong_repo(self):
        obj = manifest()
        obj["repo"] = "someone-else/public"
        with self.assertRaises(DeliveryError):
            hub4.validate_manifest(obj)

    def test_rejects_asset_redirect_or_injected_url(self):
        obj = manifest()
        obj["files"][1]["api_url"] = "https://attacker.invalid/steal"
        with self.assertRaises(DeliveryError):
            hub4.validate_manifest(obj)

    def test_rejects_missing_profile(self):
        obj = manifest()
        obj["files"].pop()
        with self.assertRaises(DeliveryError):
            hub4.validate_manifest(obj)

    def test_rejects_unsigned_sha_or_wrong_size(self):
        for field, value in (("sha256", "wrong"), ("bytes", -1), ("asset_id", 0)):
            with self.subTest(field=field):
                obj = manifest()
                obj["files"][0][field] = value
                with self.assertRaises(DeliveryError):
                    hub4.validate_manifest(obj)

    def test_rejects_bogus_country(self):
        obj = manifest()
        obj["files"][2]["profile"] = "gb"
        with self.assertRaises(DeliveryError):
            hub4.validate_manifest(obj)

    def test_regions_independent(self):
        class FakeUtils:
            @staticmethod
            def setting_bool(key, default):
                return {"epg_agent_country_all": False,
                        "epg_agent_country_de": True,
                        "epg_agent_country_at": False}.get(key, default)
        with mock.patch.dict(sys.modules, {"utils": FakeUtils}):
            self.assertEqual(hub4.selected(), ("de",))

    def test_all_overrides_country_combinations(self):
        class FakeUtils:
            @staticmethod
            def setting_bool(key, default):
                return key == "epg_agent_country_all"
        with mock.patch.dict(sys.modules, {"utils": FakeUtils}):
            self.assertEqual(hub4.selected(), ("all",))

    def test_combines_regions_without_duplicate_channel_or_same_slot(self):
        de = """<tv><channel id="de1"><display-name>ABC</display-name></channel>
        <channel id="common"><display-name>COMMON</display-name></channel>
        <programme channel="common" start="20261122080000 +0000"
        stop="20261122090000 +0000"><title>DE wins</title></programme>
        </tv>"""
        at = """<tv><channel id="at1"><display-name>AT Only</display-name></channel>
        <channel id="common"><display-name>COMMON</display-name></channel>
        <programme channel="common" start="20261122080000 +0000"
        stop="20261122090000 +0000"><title>AT duplicate</title></programme>
        <programme channel="common" start="20261122090000 +0000"
        stop="20261122100000 +0000"><title>AT extra</title></programme>
        <programme channel="at1" start="20261122090000 +0000"
        stop="20261122100000 +0000"><title>AT local</title></programme></tv>"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = []
            for country, raw in (("de", de), ("at", at)):
                file = root / (country + ".xml.gz")
                file.write_bytes(gzip.compress(raw.encode()))
                sources.append((country, file))
            target = root / "result.xml.gz"
            self.assertEqual(hub4._combine(sources, target, lambda: False), 3)
            with gzip.open(target, "rb") as output:
                node = ET.fromstring(output.read())
            self.assertEqual(len(node.findall("channel")), 3)
            titles = [row.findtext("title") for row in node.findall("programme")]
            self.assertEqual(titles, ["DE wins", "AT extra", "AT local"])

    def test_agent_menu_preserves_epg_tools_and_alias(self):
        source = (LIB / "settings_sections45.py").read_text(encoding="utf-8")
        self.assertIn("'epg':[(39100,'epg_agent100',{}),", source)
        self.assertIn("'epg_tools':", source)
        self.assertIn("'section':'epg_tools'", source)

    def test_refuses_conflicting_channel_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = []
            for region, name in (("de", "Station A"), ("at", "Station B")):
                file = root / (region + ".xml.gz")
                file.write_bytes(gzip.compress(("<tv><channel id='same'><display-name>" +
                                                name + "</display-name></channel></tv>").encode()))
                files.append((region, file))
            with self.assertRaises(DeliveryError):
                hub4._combine(files, root / "combined.gz", lambda: False)


if __name__ == "__main__":
    unittest.main()
