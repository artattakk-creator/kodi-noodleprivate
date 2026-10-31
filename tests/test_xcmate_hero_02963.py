"""Exact adapter upgrade, accepted LiveRow, overlay geometry and reversible consent."""
import importlib,json,unittest
import xml.etree.ElementTree as E
from unittest import mock
from pathlib import Path
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ADDON

class Hero63(Fixture50,unittest.TestCase):
 def test_full_bleed_text_overlay_and_live_buttons_keep_the_accepted_layout(self):
  new=E.parse(ADDON/'resources/bingie63/IncludesXCMate63.xml').getroot()
  old=E.parse(ADDON/'resources/bingie60/IncludesXCMate60.xml').getroot()
  a=new.find("include[@name='XCMate50.LiveRow']");b=old.find("include[@name='XCMate50.LiveRow']");a.tail=b.tail=None
  self.assertEqual(E.tostring(a),E.tostring(b))
  hero=new.find("include[@name='XCMate50.Hero']")
  images=[n for n in hero.iter('control') if n.get('type')=='image']
  background=next(n for n in images if n.findtext('width')=='1920')
  self.assertEqual(background.findtext('left'),'0');self.assertEqual(background.findtext('height'),'570');self.assertEqual(background.findtext('aspectratio'),'scale')
  self.assertEqual(background.find('aspectratio').get('aligny'),'top')
  labels=[n for n in hero.iter('control') if n.get('type') in ('label','textbox')]
  self.assertTrue(any(n.findtext('label')=='$VAR[XCMate63.Title]' and int(n.findtext('left'))<400 for n in labels))
  self.assertFalse(any(n.findtext('left')=='1314' for n in labels))
  self.assertEqual(len(new.findall('variable')),9)
  self.assertTrue((ADDON/'resources/media/hero63/left.png').is_file())
 def test_legacy_approved_skin_migrates_without_changing_bindings_and_both_restore_levels_work(self):
  skin63=importlib.import_module('widget_skin63')
  original=self.skin_bytes();saved=self.prop.read_bytes();menu=self.menu.read_bytes()
  paths=[self.skin/name for name in self.skinmod.FILES]
  previous=[(p,skin63.previous_candidate(name,p.read_bytes())) for name,p in zip(self.skinmod.FILES,paths)]
  meta=dict(skin=str(self.skin.resolve()),meta_sha=self.tx.sha((self.skin/'addon.xml').read_bytes()))
  old=self.tx.prepare('skin',previous,meta)
  self.tx.apply(old['id'],'skin',paths,confirmed=True)
  legacy=self.skin_bytes();self.assertTrue(skin63.previously_applied(self.skin));self.assertFalse(self.skinmod.applied(self.skin))
  plan=self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),legacy)
  with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin,confirmed=False)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True)
  self.assertTrue(self.skinmod.applied(self.skin));self.assertEqual(self.prop.read_bytes(),saved);self.assertEqual(self.menu.read_bytes(),menu)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),legacy)
  self.skinmod.apply(old['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),original)
 def test_unknown_skin_changes_are_never_forced_or_silently_overwritten(self):
  target=self.skin/'xml/IncludesHomeWidgets.xml';target.write_bytes(target.read_bytes()+b'\n<!-- user customization -->')
  original=self.skin_bytes()
  with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),original)

 def test_verified_local_catalogue_and_helper_precede_optional_own_token_lookup(self):
  sources=importlib.import_module('programme_sources57');sources._backoff.clear()
  self.options.update(programme_catalog57=True,programme_helper57=True)
  seen=[]
  def method(name):
   def run(*a,**kw):seen.append(name)
   return run
  with mock.patch('programme_catalog57.xcmate',side_effect=method('local-xcmate')),mock.patch('programme_catalog57.kodi',side_effect=method('local-kodi')),mock.patch('programme_helper57.lookup',side_effect=method('helper')),mock.patch('programme_match46.candidate',side_effect=method('own-tmdb')),mock.patch('programme_urls55.profile',return_value='fixture63'):
   for attempt in sources.attempts(dict(title='Synthetic event')):attempt()
  self.assertEqual(seen,['local-xcmate','local-kodi','helper','own-tmdb'])

 def test_pending_upgrade_is_not_reprepared_and_another_profile_never_gets_its_dialog(self):
  upgrade=importlib.import_module('skin_upgrade63');upgrade._done=False;upgrade._next=0;upgrade._pending=dict(scope='old-profile')
  try:
   with mock.patch('widget_skin50.prepare') as prepare:upgrade.prepare()
   prepare.assert_not_called()
   with mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmc.getCondVisibility',return_value=False),mock.patch('epg_handoff63.profile_scope',return_value='different-profile'):upgrade.poll()
   self.dialog.yesno.assert_not_called();self.assertNotIn('bingie_hero63_notice',self.options);self.assertFalse(upgrade._done)
  finally:upgrade._pending=None;upgrade._done=False;upgrade._next=0
