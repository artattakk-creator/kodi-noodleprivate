""".41 source bytes and every previous test method survive the P0 candidate."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Scope42(unittest.TestCase):
    def test_041_protected_source_bytes_and_all_1479_previous_methods_retained(self):
        baseline = json.loads((ROOT/'tests/fixtures/xcmate_02942_protection.json').read_text())
        self.assertEqual(baseline['base'], '354afc1cc524ec3b01001770e6afe6aec5fea70c')
        for path, digest in baseline['source_sha256'].items():
            self.assertEqual(hashlib.sha256(__import__('stabilization_contract_02943').without_stabilization43((ROOT/path).read_bytes(),path)).hexdigest(), digest, path)
        count = 0
        for path, cases in baseline['test_methods'].items():
            current = {(c.name, n.name) for c in ast.parse((ROOT/path).read_bytes()).body
                       if isinstance(c, ast.ClassDef) for n in c.body
                       if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
            self.assertLessEqual({tuple(case) for case in cases}, current, path)
            count += len(cases)
        self.assertEqual(count, 1479)
