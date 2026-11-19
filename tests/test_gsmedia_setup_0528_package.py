"""Reproducible repair package and local-only release staging for GS Media 0.5.28."""
from hashlib import md5, sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ADDON = "script.gsmedia.setup"
NAME = ADDON + "-0.5.28.zip"
BASE_SHA = "1d74c566edfc20a122bb8767c17bed915d90966fb5e33e47298aa257500e2872"


class Setup0528Package(unittest.TestCase):
    def builder(self):
        self.assertIsNotNone(importlib.util.find_spec("build_gsmedia_setup_0528_catalog"),
                             "Missing standalone catalog-hotfix builder for Issue #496")
        import build_gsmedia_setup_0528_catalog
        return build_gsmedia_setup_0528_catalog

    def test_candidate_is_reproducible_and_retains_all_27_members(self):
        builder = self.builder()
        from build_gsmedia_setup_0527 import build as build27

        with TemporaryDirectory() as folder:
            folder = Path(folder)
            previous = build27(folder / "previous")
            first = builder.build(folder / "first")
            second = builder.build(folder / "second")
            digest = sha256(first.read_bytes()).hexdigest()
            self.assertEqual(sha256(previous.read_bytes()).hexdigest(), BASE_SHA)
            self.assertEqual(first.name, NAME)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.with_suffix(".zip.sha256").read_text().split(), [digest, NAME])
            with ZipFile(previous) as old, ZipFile(first) as new:
                names = new.namelist()
                self.assertIsNone(new.testzip())
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(set(old.namelist()).issubset(names))
                for suffix in ("setup_auto50.py", "setup_omega26.py", "setup_finish27.py"):
                    member = ADDON + "/resources/lib/" + suffix
                    self.assertEqual(old.read(member), new.read(member))
                manifest = ET.fromstring(new.read(ADDON + "/addon.xml"))
                self.assertEqual((manifest.get("id"), manifest.get("version")), (ADDON, "0.5.28"))
                self.assertIn("496", manifest.findtext(".//news"))

    def test_release_plan_stages_three_routes_and_only_updates_installer_entries(self):
        builder = self.builder()
        with TemporaryDirectory() as folder:
            folder = Path(folder)
            package = builder.build(folder / "candidate")
            baseline = {name: (ROOT / name).read_bytes() for name in (
                "addons.xml", "addons.xml.md5", "index.html", "online-test/addons.xml",
                "online-test/addons.xml.md5", "online-test/index.html", "online-test/manifest.json",
                ADDON + "/" + ADDON + "-0.5.26.zip", "online-test/" + ADDON + "-0.5.26.zip",
            )}
            release = folder / "release"
            plan = builder.stage_release_plan(package, release)
            self.assertEqual(plan, builder.stage_release_plan(package, folder / "release-again"))
            self.assertEqual(plan, json.loads((release / "release-plan.json").read_bytes()))
            self.assertEqual(plan["release_identity"], "gsmedia-setup-0528-catalog-496")
            self.assertFalse(plan["published"])
            self.assertFalse(plan["device_acceptance_confirmed"])
            self.assertEqual(set(plan["channels"]), {"regular", "pilot", "neodark3"})
            for channel in plan["channels"].values():
                target = release / channel["zip"]
                self.assertEqual(target.read_bytes(), package.read_bytes())
                self.assertEqual((release / channel["sha256_file"]).read_bytes(),
                                 package.with_suffix(".zip.sha256").read_bytes())
                catalog = channel["catalog"]
                updated = (release / catalog).read_bytes()
                self.assertEqual((release / channel["catalog_md5"]).read_text().strip(),
                                 md5(updated).hexdigest())
                old = {n.get("id"): ET.tostring(n) for n in ET.fromstring(baseline[catalog])}
                new = {n.get("id"): ET.tostring(n) for n in ET.fromstring(updated)}
                self.assertEqual(ET.fromstring(new.pop(ADDON)).get("version"), "0.5.28")
                old.pop(ADDON)
                self.assertEqual(old, new)
                if "index" in channel:
                    index = (release / channel["index"]).read_text(encoding="utf-8")
                    self.assertEqual(index.count('href="' + channel["href"] + '"'), 1)
            expected = sha256(package.read_bytes()).hexdigest()
            manifest = json.loads((release / "online-test/manifest.json").read_bytes())
            self.assertEqual(manifest["wizard"]["version"], "0.5.28")
            self.assertEqual(manifest["zip_sha256"][ADDON], expected)
            self.assertEqual(manifest["installer_0528"]["release_identity"], plan["release_identity"])
            self.assertEqual({name: (ROOT/name).read_bytes() for name in baseline}, baseline)

    def test_candidate_does_not_overwrite_collision_or_accept_live_destination(self):
        builder = self.builder()
        with TemporaryDirectory() as folder:
            path = Path(folder) / NAME
            raw = b"unrelated same-version package"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "GS0528_OUTPUT_COLLISION"):
                builder.build(path.parent)
            self.assertEqual(path.read_bytes(), raw)
            self.assertFalse(path.with_suffix(".zip.sha256").exists())
        with self.assertRaisesRegex(ValueError, "GS0528_OUTPUT_SCOPE"):
            builder.build(ROOT / "online-test")
        with self.assertRaisesRegex(ValueError, "GS0528_OUTPUT_SCOPE"):
            builder.stage_release_plan(ROOT / "unused.zip", ROOT / "online-test")

    def test_other_0528_variant_overlay_cannot_enter_candidate(self):
        builder = self.builder()
        with TemporaryDirectory() as folder:
            folder = Path(folder)
            overlays = folder / "overlays"
            library = overlays / "resources/lib"
            library.mkdir(parents=True)
            (overlays / "addon.xml").write_bytes((builder.OVERLAYS / "addon.xml").read_bytes())
            (library / "tmdb_cloud_import.py").write_bytes(b"value = None\n")
            with patch.object(builder, "OVERLAYS", overlays):
                with self.assertRaisesRegex(ValueError, "GS0528_UNEXPECTED_OVERLAY"):
                    builder.build(folder / "candidate")
            self.assertFalse((folder / "candidate").exists())

    def test_release_plan_rejects_changed_sha_and_existing_unrelated_output(self):
        builder = self.builder()
        with TemporaryDirectory() as folder:
            folder = Path(folder)
            package = builder.build(folder / "candidate")
            release = folder / "release"
            release.mkdir()
            (release / NAME).write_bytes(b"another .28 candidate")
            with self.assertRaisesRegex(ValueError, "GS0528_OUTPUT_COLLISION"):
                builder.stage_release_plan(package, release)
            self.assertEqual((release / NAME).read_bytes(), b"another .28 candidate")
            package.with_suffix(".zip.sha256").write_text("0" * 64 + "  " + NAME + "\n")
            with self.assertRaisesRegex(ValueError, "GS0528_PACKAGE_SHA256"):
                builder.stage_release_plan(package, folder / "new-release")
            self.assertFalse((folder / "new-release").exists())

    def test_release_plan_rejects_changed_live_catalog_even_with_matching_md5(self):
        builder = self.builder()
        with TemporaryDirectory() as folder:
            folder = Path(folder)
            package = builder.build(folder / "candidate")
            checkout = folder / "checkout"
            for name in ("addons.xml", "addons.xml.md5", "index.html",
                         "online-test/addons.xml", "online-test/addons.xml.md5",
                         "online-test/index.html", "online-test/manifest.json"):
                target = checkout / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            catalog = checkout / "addons.xml"
            changed = catalog.read_bytes().replace(b'name="Noodle Private"', b'name="Other"')
            self.assertNotEqual(changed, catalog.read_bytes())
            catalog.write_bytes(changed)
            catalog.with_suffix(".xml.md5").write_text(md5(changed).hexdigest() + "\n")
            with patch.object(builder, "ROOT", checkout):
                with self.assertRaisesRegex(ValueError, "GS0528_LIVE_BASE_SHA256"):
                    builder.stage_release_plan(package, folder / "release")
            self.assertFalse((folder / "release").exists())


if __name__ == "__main__":
    unittest.main()
