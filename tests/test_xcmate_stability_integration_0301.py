"""Keep tested hotfix, owner lifecycle and live methods across theme merges."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'src/plugin.video.xtreammate/resources/lib'


class StabilityIntegrationTests(unittest.TestCase):
    def test_hotfix_and_live_modules_remain_byte_identical(self):
        reference=json.loads((ROOT/'tests/fixtures/xcmate_0297_integration.json').read_text())
        for name,digest in reference['files'].items():
            self.assertEqual(hashlib.sha256((LIB/name).read_bytes()).hexdigest(),digest,name)

    def test_owner_loop_and_native_player_methods_remain_identical(self):
        reference=json.loads((ROOT/'tests/fixtures/xcmate_0297_integration.json').read_text())
        for identity,digest in reference['methods'].items():
            filename,cls,name=identity.split(':')
            tree=ast.parse((LIB/filename).read_text())
            node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
            method=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name==name)
            actual=hashlib.sha256(ast.dump(method,include_attributes=False).encode()).hexdigest()
            self.assertEqual(actual,digest,identity)


if __name__=='__main__':unittest.main()
