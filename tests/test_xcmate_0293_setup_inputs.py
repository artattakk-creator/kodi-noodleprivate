"""XCMate 0.1.29.3 Xtream server origin input tests (offline)."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

SRC = (Path(__file__).resolve().parents[1] /
       "src/plugin.video.xtreammate/resources/lib/setup_wizard.py")


class WizardServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake = types.ModuleType("xbmcgui")
        stub = types.ModuleType("utils")
        stub.warn = lambda msg: None
        loc = types.ModuleType("localization")
        loc.tr = lambda *args: "label"
        with patch.dict(sys.modules, {"xbmcgui": fake, "utils": stub,
                                      "localization": loc}):
            spec = importlib.util.spec_from_file_location("_test_setup_wizard_0293", SRC)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def test_bare_host_and_port_is_accepted(self):
        self.assertEqual(self.module.valid_server("tv.example.invalid:8080"),
                         "http://tv.example.invalid:8080")

    def test_explicit_https_kept(self):
        self.assertEqual(self.module.valid_server("https://tv.example.invalid:443/"),
                         "https://tv.example.invalid:443")

    def test_reject_embedded_credentials_or_url_query(self):
        for value in ("https://user:secret@tv.example.invalid",
                      "https://tv.example.invalid/get.php?username=abc&password=secret"):
            with self.subTest(value=value.split("@")[0]):
                with self.assertRaises(ValueError):
                    self.module.valid_server(value)

    def test_reject_invalid_port_or_protocol(self):
        for value in ("tv.example.invalid:notaport",
                      "ftp://tv.example.invalid", "http:/broken"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.module.valid_server(value)

    def test_reject_blank_and_unqualified_host(self):
        for value in ("", "  ", "http://", "http://other host"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.module.valid_server(value)


if __name__ == "__main__":
    unittest.main()
