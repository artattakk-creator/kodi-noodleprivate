import ast,hashlib,importlib,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50,ROOT
class Shortcuts62(Fixture50,unittest.TestCase):
 def setUp(self):
  super().setUp();self.mod=importlib.import_module('shortcuts62');self.addon=self.folder/'script.skinshortcuts';self.target=self.addon/'resources/lib/library.py';self.target.parent.mkdir(parents=True);self.raw=(ROOT/'tests/fixtures/skinshortcuts210_library62.py').read_bytes();self.target.write_bytes(self.raw)
 def test_exact_official_code_reproduces_two_python311_failures_and_both_iter_expressions_work(self):
  patched=self.mod.candidate(self.raw)
  for source,fail in ((self.raw,True),(patched,False)):
   nodes=[n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr==('getiterator' if fail else 'iter') and isinstance(n.func.value,ast.Name) and n.func.value.id=='xmldata']
   self.assertEqual(len(nodes),2)
   for node in nodes:
    expr=compile(ast.fix_missing_locations(ast.Expression(node)),'official-library.py','eval');env={'xmldata':ET.fromstring('<smartplaylist type="movies"><name>Fixture</name></smartplaylist>')}
    if fail:
     with self.assertRaises(AttributeError):eval(expr,env)
    else:self.assertEqual(len(list(eval(expr,env))),2)
 def test_prepare_apply_restore_are_explicit_hash_guarded_and_preserve_all_profile_bindings(self):
  before=self.prop.read_bytes();plan,diff=self.mod.prepare(self.addon,'2.1.0');self.assertEqual(self.target.read_bytes(),self.raw);self.assertIn('getiterator',diff)
  with self.assertRaises(PermissionError):self.mod.apply(plan['id'],self.addon,'2.1.0')
  self.mod.apply(plan['id'],self.addon,'2.1.0',confirmed=True);self.assertNotIn(b'.getiterator()',self.target.read_bytes());self.assertEqual(self.prop.read_bytes(),before)
  self.mod.apply(plan['id'],self.addon,'2.1.0',confirmed=True,restore=True);self.assertEqual(self.target.read_bytes(),self.raw)
 def test_unknown_version_modified_source_and_later_foreign_changes_are_never_overwritten(self):
  with self.assertRaises(ValueError):self.mod.prepare(self.addon,'3.0.6')
  plan,_=self.mod.prepare(self.addon,'2.1.0');self.target.write_bytes(self.raw+b'\n# foreign change\n')
  with self.assertRaises(ValueError):self.mod.apply(plan['id'],self.addon,'2.1.0',confirmed=True)
  self.assertTrue(self.target.read_bytes().endswith(b'# foreign change\n'))
 def test_declined_ui_preview_never_changes_external_addon_or_rebuilds_skin(self):
  self.dialog.yesno.return_value=False
  with mock.patch.object(self.mod,'context',return_value=(self.addon,'2.1.0')):self.mod.show()
  self.assertEqual(self.target.read_bytes(),self.raw);self.assertFalse(self.builtins)
