"""Offline QA for the private GitHub Hub schema-5 dynamic XMLTV reader."""
import copy
import gzip
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / "src" / "plugin.video.xtreammate" / "resources" / "lib"
sys.path.insert(0, str(LIB))

from epg_agent_github import DeliveryError, XMLTV_FILE
import epg_agent_hub5 as hub5


def manifest(profiles=("all", "de", "at", "en", "es", "pl")):
    files = []
    asset = 89001
    for p in profiles:
        for variant in ("artwork", "standard"):
            name = "epg-" + p + ("-standard" if variant == "standard" else "") + ".xml.gz"
            files.append({
                "profile": p, "variant": variant, "file": name,
                "api_url": hub5.BASE + str(asset), "asset_id": asset,
                "bytes": 210, "sha256": hashlib.sha256(name.encode()).hexdigest(),
                "channels": 1, "programmes": 1, "generated_utc": "2026-11-23T13:14:07Z",
            })
            asset += 1
    return {
        "schema_version": 5, "schema": "gsmedia-hub-github-v3",
        "status": "PRIVATE_READY", "delivery": "private-github-release-assets",
        "repo": hub5.REPO, "default_profile": "all",
        "variants": ["artwork", "standard"], "profiles": list(profiles),
        "release_id": 455446226,
        "tag": "gs-hub-20261123T131226Z-afdc85177f32",
        "fingerprint": "a" * 64, "generated_utc": "2026-11-23T13:14:07Z",
        "files": files,
    }


class TestHub5(unittest.TestCase):
    def test_manifest_all_six_profiles_and_twelve_assets(self):
        names, pairs = hub5.validate_manifest(manifest())
        self.assertEqual(len(names), 6)
        self.assertEqual(len(pairs), 12)
        self.assertEqual(pairs["es", "standard"]["file"], "epg-es-standard.xml.gz")

    def test_rejects_wrong_schema_and_unauthorized_origin(self):
        for field, value in (("schema_version", 4), ("status", "PRIVATE_PENDING"),
                             ("repo", "attacker/private"), ("delivery", "public")):
            with self.subTest(field=field):
                obj = manifest()
                obj[field] = value
                with self.assertRaises(DeliveryError):
                    hub5.validate_manifest(obj)

    def test_rejects_ssrf_filename_asset_hash_and_counts(self):
        for field, value in (
            ("api_url", "https://evil.invalid/collect"),
            ("file", "../epg-en.xml.gz"), ("asset_id", -1),
            ("sha256", "a" * 10), ("bytes", 0),
            ("programmes", 0), ("channels", 0)):
            with self.subTest(field=field):
                obj = manifest()
                obj["files"][0][field] = value
                with self.assertRaises(DeliveryError):
                    hub5.validate_manifest(obj)

    def test_rejects_duplicate_asset_id(self):
        obj = manifest()
        obj["files"][1]["asset_id"] = obj["files"][0]["asset_id"]
        obj["files"][1]["api_url"] = obj["files"][0]["api_url"]
        with self.assertRaises(DeliveryError):
            hub5.validate_manifest(obj)

    def test_rejects_missing_variant_and_pair_count_mismatch(self):
        obj = manifest()
        obj["files"].pop()
        with self.assertRaises(DeliveryError):
            hub5.validate_manifest(obj)
        obj = manifest()
        obj["files"][1]["channels"] = 2
        with self.assertRaises(DeliveryError):
            hub5.validate_manifest(obj)

    def test_rejects_duplicate_or_bad_country_codes(self):
        for profiles in (("all", "de", "de"), ("all", "de", "es/../"), ("de", "at")):
            with self.subTest(profiles=profiles):
                obj = manifest(profiles)
                with self.assertRaises(DeliveryError):
                    hub5.validate_manifest(obj)

    def test_selection_persists_dynamic_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub5.save_selection(["de", "en", "es", "pl"], directory=tmp)
            profiles, variant, _, available = hub5.selected_for(manifest(), tmp)
            self.assertEqual(profiles, ("de", "en", "es", "pl"))
            self.assertEqual(variant, "artwork")
            self.assertIn("at", available)
            hub5.save_selection(["es"], "standard", tmp)
            profiles, variant, _, _ = hub5.selected_for(manifest(), tmp)
            self.assertEqual((profiles, variant), (("es",), "standard"))

    def test_all_overrides_selected_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub5.save_selection(["de", "en", "all"], directory=tmp)
            selected, variant, _, _ = hub5.selected_for(manifest(), tmp)
            self.assertEqual(selected, ("all",))

    def test_corrupt_selection_rejected_without_reverting(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "profiles.json").write_text('{"schema_version":1,"selected":["../../evil"]}')
            with self.assertRaises(DeliveryError):
                hub5.selected_for(manifest(), tmp)

    def test_stage_synthetic_profiles_no_network_preserves_images(self):
        fixtures = {}
        for p in ("en", "es"):
            xml = ('<?xml version="1.0" encoding="UTF-8"?><tv>'
                   '<channel id="x.' + p + '"><display-name>TV ' + p +
                   '</display-name><icon src="https://image.tmdb.org/t/p/w500/channel.png"/></channel>'
                   '<programme channel="x.' + p +
                   '" start="20261123120000 +0000" stop="20261123130000 +0000">'
                   '<title lang="' + p + '">Episode</title>'
                   '<image type="poster" system="tmdb">https://image.tmdb.org/t/p/w500/poster.jpg</image>'
                   '</programme></tv>').encode()
            fixtures[p] = gzip.compress(xml)
        obj = manifest(("all", "en", "es"))
        for row in obj["files"]:
            if row["profile"] in fixtures:
                raw = fixtures[row["profile"]]
                row["bytes"] = len(raw)
                row["sha256"] = hashlib.sha256(raw).hexdigest()
        def fake_download(record, token, dest, opener, cancel):
            dest = Path(dest) / record["file"]
            dest.write_bytes(fixtures[record["profile"]])
            return dest
        with tempfile.TemporaryDirectory() as tmp:
            hub5.save_selection(["en", "es"], directory=tmp)
            with mock.patch.object(hub5, "_download", side_effect=fake_download):
                result = hub5.stage(Path(tmp), "test-never-sent", obj, "", None)
            self.assertEqual(result["status"], "STAGED_FULL_CANDIDATE")
            self.assertEqual(result["channels"], 2)
            self.assertEqual(result["programmes"], 2)
            self.assertEqual(result["image_counts"]["poster"], 2)
            self.assertEqual(result["image_counts"]["channel_logo"], 2)
            path = Path(result["path"]) / XMLTV_FILE
            self.assertEqual(gzip.decompress(path.read_bytes()).count(b"<programme"), 2)
            cached = hub5.stage(Path(tmp), "not-used", obj, "", None)
            self.assertEqual(cached["status"], "UNCHANGED")
            self.assertEqual(cached["generation"], result["generation"])

    def test_variants_different_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            obj = manifest(("all", "en"))
            hub5.save_selection(["en"], "artwork", tmp)
            a = hub5.selected_for(obj, tmp)
            hub5.save_selection(["en"], "standard", tmp)
            b = hub5.selected_for(obj, tmp)
            self.assertNotEqual(a[2][("en", a[1])]["sha256"],
                                b[2][("en", b[1])]["sha256"])


if __name__ == "__main__":
    unittest.main()
