"""Execute native wrapper composition on the host before remote Kodi dispatch."""
import ast,builtins,types,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
class NativeHarness90(unittest.TestCase):
 def test_original_picker_parent_is_not_counted_as_only_addon(self):
  source=ast.parse((ROOT/'tools/kodi_home90_host/picker90.py').read_text())
  node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='entries')
  for labels in (['..','XCMate  >'],['None','Add-On  >'],[]):
   def label(key):
    if key.endswith('.NumItems'):return str(len(labels)-(1 if labels and labels[0]=='..' else 0))
    index=int(key.split('ListItemAbsolute(')[1].split(')')[0]);return labels[index] if index<len(labels) else ''
   ns={'xbmc':types.SimpleNamespace(getInfoLabel=label)}
   exec(compile(ast.Module(body=[node],type_ignores=[]),'picker90-entries','exec'),ns)
   self.assertEqual(ns['entries'](),labels)
 def test_native_wrapper_composition_keeps_pixel_gates_and_supplies_early_epg_receipt(self):
  mapping={'/base_gui89.py':'tools/kodi_home89_host/gui89.py','/base_gui88.py':'tools/kodi_home88_host/gui88.py','/base_gui86.py':'tools/kodi_home86_host/gui86.py','/base_gui84.py':'tools/kodi_home84_host/gui84.py'}
  saved_read=Path.read_text;captured={}
  def read(path,*a,**kw):return (ROOT/mapping[str(path)]).read_bytes().decode('utf-8') if str(path) in mapping else saved_read(path,*a,**kw)
  class BottomReached(Exception):pass
  def compile_source(source,filename,mode):captured[filename]=source;return builtins.compile(source,filename,mode)
  def nested(code,ns):
   if code.co_filename=='/base_gui84.py':raise BottomReached()
   return builtins.exec(code,ns)
  ns={'__name__':'native90_composition','exec':nested,'compile':compile_source}
  with mock.patch.object(Path,'read_text',read):
   with self.assertRaises(BottomReached):builtins.exec(builtins.compile((ROOT/'tools/kodi_home90_host/gui90.py').read_bytes(),'gui90.py','exec'),ns)
  bottom=captured['/base_gui84.py'];outer=captured['/base_gui88.py']
  self.assertIn("check(hero_pixels>3000",bottom);self.assertIn("check(rail_pixels>1500",bottom)
  self.assertIn('START90_OWN_LOGO_RENDER_BINDING_MISMATCH',bottom);self.assertIn('epg_case90.update',bottom)
  self.assertIn('home,logo_case84,epg_case90)',outer)
