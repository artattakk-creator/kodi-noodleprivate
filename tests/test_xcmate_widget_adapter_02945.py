"""Isolated synthetic skin copies only. No actual installed skin is modified."""
import importlib,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
TEXT=b'<includes><content>plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p</content><content>plugin://foreign/?action=movies</content><label>Unrelated untouched bytes</label></includes>'
class WidgetAdapter45(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.a=importlib.import_module('widget_adapter45');self.h=importlib.import_module('widget_hooks45');self.root=self.folder/'synthetic_skin';(self.root/'xml').mkdir(parents=True)
  (self.root/'addon.xml').write_text('<addon id="skin.titan.bingie.mod" version="2.2.3"/>');self.target=self.root/'xml/script-skinshortcuts-includes.xml';self.target.write_bytes(TEXT)
 def plan(self):return self.a.prepare(self.target,self.root,'2.2.3')
 def test_prepare_is_readonly_for_foreign_skin_and_stored_shortcuts(self):
  plan=self.plan();self.assertEqual(plan['code'],'PREPARED_NOT_APPLIED');self.assertEqual(self.target.read_bytes(),TEXT);self.assertTrue((self.a.folder()/plan['backup']).is_file())
 def test_patch_only_exact_own_widget_source_urls_and_preserves_other_bytes(self):
  new,count=self.a.patch(TEXT);self.assertEqual(count,1)
  suffix=b'&amp;xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.vod)]';self.assertEqual(new.replace(suffix,b''),TEXT);self.assertEqual(self.h.sources(new.decode())[0]['hooks'],['XCMate.Widget45.Reload.vod'])
 def test_apply_without_separate_explicit_confirmation_refuses_write(self):
  plan=self.plan()
  for confirmed in (False,None,'true',1):
   with self.assertRaises(PermissionError):self.a.apply(plan,confirmed=confirmed)
  self.assertEqual(self.target.read_bytes(),TEXT)
 def test_explicit_apply_and_hash_guarded_restore_are_exact(self):
  plan=self.plan();self.assertEqual(self.a.apply(plan,confirmed=True)['code'],'APPLIED');self.assertNotEqual(self.target.read_bytes(),TEXT)
  self.assertEqual(self.a.apply(plan,confirmed=True,restore=True)['code'],'RESTORED');self.assertEqual(self.target.read_bytes(),TEXT)
 def test_concurrent_changed_layout_or_skin_update_never_overwritten(self):
  plan=self.plan();self.target.write_bytes(b'<includes><label>External change</label></includes>');before=self.target.read_bytes()
  with self.assertRaisesRegex(ValueError,'TARGET_CHANGED'):self.a.apply(plan,confirmed=True)
  self.assertEqual(self.target.read_bytes(),before)
 def test_unverified_skin_version_or_metadata_blocked_before_backup(self):
  with self.assertRaisesRegex(ValueError,'UNVERIFIED'):self.a.prepare(self.target,self.root,'2.2.2')
  (self.root/'addon.xml').write_text('<addon id="other" version="2.2.3"/>')
  with self.assertRaisesRegex(ValueError,'METADATA'):self.plan()
 def test_unsafe_path_symlink_and_source_entities_rejected(self):
  wrong=self.root/'other.xml';wrong.write_bytes(TEXT)
  with self.assertRaises(ValueError):self.a.prepare(wrong,self.root,'2.2.3')
  with self.assertRaises(ValueError):self.h.sources('<!DOCTYPE a [<!ENTITY p "x">]><includes/>')
 def test_backup_tamper_blocks_apply_and_never_touches_target(self):
  plan=self.plan();(self.a.folder()/plan['backup']).write_bytes(b'altered')
  with self.assertRaisesRegex(ValueError,'BACKUP_VERIFY'):self.a.apply(plan,confirmed=True)
  self.assertEqual(self.target.read_bytes(),TEXT)
 def test_other_widget_ids_actions_and_direct_item_click_urls_are_not_patched(self):
  text=b'<includes><content>plugin://plugin.video.xtreammate/?action=media_detail&amp;pid=p&amp;sid=1</content></includes>'
  self.assertEqual(self.a.patch(text),(text,0))
 def test_existing_native_hook_does_not_need_patch_or_shortcut_rebind(self):
  data=TEXT.replace(b'pid=p',b'pid=p&amp;reload=$INFO[Window(Home).Property(widgetreload)]');self.assertEqual(self.a.patch(data),(data,0))
 def test_adapter_is_pin_protected_and_not_invoked_by_service_or_widget_render(self):
  import experimental45
  self.assertTrue(experimental45.protected({'action':'widget_adapter45'}))
  from xcmate027_fixture import LIB
  for module in ('app_services.py','widget_refresh45.py','widget_items45.py','widget_hooks45.py'):
   text=(LIB/module).read_text();self.assertNotIn('widget_adapter45',text)
 def test_private_backups_are_verified_and_permission_restricted(self):
  plan=self.plan();backup=self.a.folder()/plan['backup'];self.assertEqual(backup.stat().st_mode&0o777,0o600);self.assertEqual(self.a.sha(backup.read_bytes()),plan['before'])
