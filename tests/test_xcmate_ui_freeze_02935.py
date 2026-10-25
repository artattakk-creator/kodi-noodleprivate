"""User-approved .34 UI/assets and guide/player lifecycle remain exact sources."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class SearchFreeze35(unittest.TestCase):
    def test_search_ui_artwork_and_existing_handoff_are_byte_identical_to_main_034(self):
        reference=json.loads((ROOT/'tests/fixtures/xcmate_02934_search_ui_freeze.json').read_text())
        self.assertGreater(len(reference['files']),100)
        from stabilization_contract_02937 import without_stabilization37
        for path,digest in reference['files'].items():
            with self.subTest(path=path):self.assertEqual(hashlib.sha256(without_stabilization37((ROOT/path).read_bytes(),path)).hexdigest(),digest)
