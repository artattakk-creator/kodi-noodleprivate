"""Regression for Kodi 21 import crash in Setup 0.5.16.

2026-11-03 log (19:02:00): ModuleNotFoundError: setup_catalog_0516.
The source existed on GitHub but build_gsmedia_setup.py's explicit FILES
omitted it. Check source and actual packaged ZIP.
"""
import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_gsmedia_setup.py"
spec = importlib.util.spec_from_file_location("setup_packager", BUILDER)
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class KodiModulePackagingTests(unittest.TestCase):
    def test_builder_declares_entire_local_setup_dependency_closure(self):
        self.assertIn("resources/lib/setup_catalog_0516.py", packager.FILES)
        self.assertTrue(packager.validate_bundled_imports())

    def test_missing_import_causes_build_to_fail_not_publish(self):
        files = tuple(name for name in packager.FILES
                      if name != "resources/lib/setup_catalog_0516.py")
        with self.assertRaisesRegex(ValueError, "setup_catalog_0516"):
            packager.validate_bundled_imports(packager.SOURCE, files)

    def test_actual_zip_contains_kodi_catalog_module_and_resolves_local_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            packager.build(tmp)
            path = Path(tmp) / "script.gsmedia.setup-0.5.19.zip"
            self.assertTrue(path.is_file())
            with zipfile.ZipFile(path) as z:
                self.assertIsNone(z.testzip())
                names = z.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertIn("script.gsmedia.setup/resources/lib/setup_catalog_0516.py", names)
                import_names = {Path(n).stem
                                for n in names
                                if n.startswith("script.gsmedia.setup/resources/lib/")
                                and n.endswith(".py")}
                for entry in names:
                    if not entry.endswith(".py"):
                        continue
                    tree = ast.parse(z.read(entry).decode("utf-8"), filename=entry)
                    for node in ast.walk(tree):
                        local = []
                        if isinstance(node, ast.ImportFrom):
                            local = [(node.module or "").split(".")[0]]
                        elif isinstance(node, ast.Import):
                            local = [a.name.split(".")[0] for a in node.names]
                        for dependency in local:
                            if dependency.startswith("setup_"):
                                self.assertIn(dependency, import_names, (entry, dependency))


if __name__ == "__main__":
    unittest.main()
