"""Real router menu reachability, approval boundaries and source preservation."""
import importlib,unittest
from urllib.parse import urlsplit,parse_qsl
from unittest import mock
from xcmate050_fixture import Fixture50

class Menu61(Fixture50,unittest.TestCase):
 def follow(self,action,**params):
  self.added.clear();self.ends.clear();self.router._directory_done=False;params.setdefault('pid','p');self.router._params=dict(action=action,**params);self.routes.dispatch(self.router)
  self.assertEqual(len(self.ends),1)
 def test_visible_path_reaches_manager_and_plain_ok_layout_and_restore_actions(self):
  self.follow('settings_home')
  url=next(u for u,i,f in self.added if i.label=='Aussehen und Darstellung')
  self.follow(**dict(parse_qsl(urlsplit(url).query)))
  url=next(u for u,i,f in self.added if i.label=='BINGIE-Startseiten-Widgets einrichten')
  self.follow(**dict(parse_qsl(urlsplit(url).query)))
  self.assertEqual([i.label for u,i,f in self.added[:3]],['Live-TV','Filme','Serien'])
  for label,action in [('BINGIE-Home-Layout prüfen/vorbereiten','widget_skin50'),('Widget-Verknüpfung oder Layout wiederherstellen','widget_restore50')]:
   matches=[(u,f) for u,i,f in self.added if 'action='+action in u]
   self.assertEqual(len(matches),1);self.assertFalse(matches[0][1])
  self.assertFalse(self.builtins)
 def test_existing_adapter_never_rebuilds_without_explicit_confirmation(self):
  import widget_manager50 as ui
  self.skinmod.apply(self.skinmod.prepare(self.skin)['id'],self.skin,confirmed=True)
  before=self.skin_bytes();saved=self.prop.read_bytes()
  with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):
   self.dialog.yesno.return_value=False;ui.skin_setup();self.assertFalse(self.builtins)
   self.dialog.yesno.return_value=True;ui.skin_setup()
  self.assertEqual(len(self.builtins),1);self.assertIn('type=buildxml',self.builtins[0])
  self.assertEqual(self.skin_bytes(),before);self.assertEqual(self.prop.read_bytes(),saved)
 def test_approval_revalidates_profile_before_rebuild(self):
  import widget_manager50 as ui
  self.skinmod.apply(self.skinmod.prepare(self.skin)['id'],self.skin,confirmed=True)
  self.dialog.yesno.return_value=True
  with mock.patch.object(ui,'runtime',side_effect=[(self.profile,self.skin),(self.folder/'other',self.skin)]):ui.skin_setup()
  self.assertFalse(self.builtins);self.dialog.ok.assert_called()
