"""Synthetic foreign-layout copy: explicit reversible adapter, never a device."""
import importlib,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,LIB
NAMES=('widget_layout_poster','widget_layout_landscape_not_vertical_layout','widget_layout_landscapelarge','widget_layout_highlight')
TEXT=('<includes><!-- existing comment unchanged -->'+''.join('<include name="'+n+'"><itemlayout width="364" height="212"><control type="image"><texture>$INFO[ListItem.Art(thumb)]</texture></control></itemlayout><focusedlayout width="364" height="212" condition="Control.HasFocus($PARAM[widgetid])"><control type="image"><texture>original.png</texture></control></focusedlayout><focusedlayout width="364" height="212" condition="!Control.HasFocus($PARAM[widgetid])"><control type="label"><label>Original</label></control></focusedlayout></include>' for n in NAMES)+'<include name="Unrelated"><label>Untouched other source</label></include></includes>').encode()
class ProgrammeAdapter46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.a=importlib.import_module('widget_adapter46');self.c=importlib.import_module('widget_capabilities46');self.root=self.folder/'synthetic_bingie';(self.root/'xml').mkdir(parents=True)
  (self.root/'addon.xml').write_text('<addon id="skin.titan.bingie.mod" version="2.2.3"/>');(self.root/'xml/Font.xml').write_text('<fonts><fontset><font><name>Reg18</name></font><font><name>Bold22</name></font></fontset></fonts>')
  self.target=self.root/'xml/IncludesHomeWidgets.xml';self.target.write_bytes(TEXT)
 def plan(self):return self.a.prepare(self.target,self.root,'2.2.3')
 def test_prepare_never_modifies_skin_or_stored_widget_urls(self):
  plan=self.plan();self.assertEqual(plan['code'],'PREPARED_NOT_APPLIED');self.assertEqual(self.target.read_bytes(),TEXT);self.assertTrue((self.a.folder()/plan['backup']).is_file())
 def test_conditional_logo_overlay_title_time_progress_focus_description_added_to_all_layouts(self):
  new,count=self.a.patch(TEXT);tree=ET.fromstring(new);groups=tree.findall('.//control[@xcmate-programme46="true"]')
  self.assertEqual(count,12);self.assertEqual(len(groups),12)
  for group in groups:
   self.assertIn('XCMate.WidgetKind41',group.findtext('visible'));self.assertIn('XCMate.ProgrammeLogo46',ET.tostring(group).decode());self.assertFalse(any(n.get('id') for n in group.iter('control')))
  self.assertEqual(self.c.inspect_file(self.target,'2.2.3')['code'],'BLOCKED_NO_OVERLAY_FOCUS_BINDING')
 def test_every_original_xml_byte_is_preserved_outside_insertions(self):
  new,count=self.a.patch(TEXT)
  for w,h,focused in [(364,212,False),(364,212,True)]:new=new.replace(self.a.card(w,h,focused),b'')
  self.assertEqual(new,TEXT)
 def test_separate_explicit_confirmation_is_mandatory_even_after_pin(self):
  plan=self.plan()
  for value in (False,None,'true',1):
   with self.assertRaises(PermissionError):self.a.apply(plan,confirmed=value)
  self.assertEqual(self.target.read_bytes(),TEXT)
 def test_single_file_atomic_apply_and_exact_hash_guarded_restore(self):
  plan=self.plan();self.assertEqual(self.a.apply(plan,confirmed=True)['code'],'APPLIED');self.assertTrue(self.c.inspect_file(self.target,'2.2.3')['overlay']);self.assertTrue(self.c.inspect_file(self.target,'2.2.3')['focus'])
  self.assertEqual(self.a.apply(plan,confirmed=True,restore=True)['code'],'RESTORED');self.assertEqual(self.target.read_bytes(),TEXT)
 def test_external_skin_changes_are_never_overwritten(self):
  plan=self.plan();self.target.write_bytes(TEXT+b'<!-- unrelated update -->');before=self.target.read_bytes()
  with self.assertRaisesRegex(ValueError,'TARGET_CHANGED'):self.a.apply(plan,confirmed=True)
  self.assertEqual(self.target.read_bytes(),before)
 def test_unknown_skin_version_fonts_or_layout_shapes_block_before_write(self):
  with self.assertRaisesRegex(ValueError,'UNVERIFIED_SKIN'):self.a.prepare(self.target,self.root,'2.2.2')
  (self.root/'xml/Font.xml').write_text('<fonts/>')
  with self.assertRaisesRegex(ValueError,'FONT'):self.plan()
  with self.assertRaisesRegex(ValueError,'UNVERIFIED_LAYOUT'):self.a.patch(b'<includes/>')
 def test_entity_and_symlink_targets_are_rejected(self):
  with self.assertRaises(ValueError):self.a.patch(b'<!DOCTYPE x [<!ENTITY bad SYSTEM "file:///etc/passwd">]><includes/>')
  other=self.folder/'outside.xml';other.write_bytes(TEXT);self.target.unlink();self.target.symlink_to(other)
  with self.assertRaisesRegex(ValueError,'UNSAFE_TARGET'):self.plan()
 def test_tampered_backup_or_candidate_cannot_be_applied(self):
  plan=self.plan();(self.a.folder()/plan['candidate']).write_bytes(b'not approved')
  with self.assertRaisesRegex(ValueError,'BACKUP_VERIFY'):self.a.apply(plan,confirmed=True)
  self.assertEqual(self.target.read_bytes(),TEXT)
 def test_patch_is_idempotent_and_never_changes_click_or_remote_actions(self):
  new,count=self.a.patch(TEXT);self.assertEqual(self.a.patch(new),(new,0));self.assertNotIn(b'<onclick>',new);self.assertNotIn(b'<oninfo>',new);self.assertNotIn(b'PlayMedia',new)
 def test_adapter_entry_is_pin_protected_and_never_auto_applied_by_workers(self):
  import experimental45
  self.assertTrue(experimental45.protected(dict(action='widget_adapter46')))
  for module in ('app_services.py','programme_widgets46.py','programme_events46.py','programme_art46.py','widget_refresh45.py'):
   self.assertNotIn('widget_adapter46',(LIB/module).read_text())
 def test_overlay_alone_never_claims_missing_reload_hook_is_fixed(self):
  self.a.apply(self.plan(),confirmed=True)
  self.assertNotIn('Reload.live',self.target.read_text());self.assertIn('ANDROID_NOT_TESTED',self.c.inspect_file(self.target,'2.2.3')['code'])
