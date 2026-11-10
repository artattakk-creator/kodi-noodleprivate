"""Real-path identity guards for art-only updates; no selection/reset operations."""
import importlib,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ListItem
class Patch85(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.module=importlib.import_module('widget_patch85');self.runtime=importlib.import_module('widget_runtime79');self.profile=importlib.import_module('epg_handoff63').profile_scope();self.values=[];self.items=[]
  for i in range(24):
   props={'XCMate.PortalId':str(self.portal['id']),'XCMate.WidgetKind41':'vod','XCMate.MediaId':str(i),'XCMate.Source85':'source-'+str(i)};value=dict(label='Title '+str(i),url='plugin://plugin.video.xtreammate/?action=media_detail&kind=vod&pid='+str(self.portal['id'])+'&sid='+str(i),art={'poster':'/verified-new/'+str(i)+'.png'},props=props)
   item=ListItem(value['label'],path=value['url']);item.getPath=lambda item=item:item.path;item.props=dict(props);item.art={'poster':'/verified-old/'+str(i)+'.png'};self.items.append(item);self.values.append(value)
  self.control=mock.Mock(getListItem=lambda i:self.items[i]);self.control.getSelectedPosition.return_value=23;self.control.size.return_value=len(self.items)
  self.runtime._plans[(str(self.portal['id']),'vod')]=dict(scope=self.profile,slot=self.runtime.slot(self.portal,'vod'),ids=[2520],at=time.monotonic())
  self.module.prepare(self.portal,'vod',self.values,'a'*64)
 def apply(self):
  with mock.patch('home_runtime77.control',return_value=self.control),mock.patch('xbmc.getInfoLabel',return_value='24'),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmc.getCondVisibility',return_value=False):return self.module.apply(self.portal['id'],'vod','a'*64)
 def test_twenty_four_verified_art_changes_keep_selected_item_and_never_reset(self):
  self.assertTrue(self.apply());self.assertEqual(self.items[23].art['poster'],'/verified-new/23.png');self.control.reset.assert_not_called();self.control.selectItem.assert_not_called();self.control.setFocusId.assert_not_called();self.assertEqual(self.control.getSelectedPosition(),23)
 def test_foreign_item_url_prevents_entire_patch(self):
  self.items[23].path='plugin://foreign/';self.assertFalse(self.apply());self.assertEqual(self.items[0].art['poster'],'/verified-old/0.png')
 def test_foreign_provider_prevents_entire_patch(self):
  self.items[7].props['XCMate.PortalId']='foreign';self.assertFalse(self.apply());self.assertEqual(self.items[0].art['poster'],'/verified-old/0.png')
 def test_new_catalogue_identity_does_not_get_art_from_previous_row(self):
  self.items[5].props['XCMate.MediaId']='new';self.assertFalse(self.apply());self.assertEqual(self.items[0].art['poster'],'/verified-old/0.png')
 def test_same_source_missing_art_keeps_accepted_reference(self):
  self.values[0]['art']['poster']='';self.module.prepare(self.portal,'vod',self.values,'a'*64);self.assertTrue(self.apply());self.assertEqual(self.items[0].art['poster'],'/verified-old/0.png')
 def test_changed_source_does_not_inherit_previous_pixels(self):
  self.values[0]['art']['poster']='';self.values[0]['props']['XCMate.Source85']='new-source';self.module.prepare(self.portal,'vod',self.values,'a'*64);self.assertTrue(self.apply());self.assertEqual(self.items[0].art['poster'],'')
 def test_gui_patch_never_reads_sql_files_or_provider_data(self):
  with mock.patch('library_index.Reader',side_effect=AssertionError('GUI SQL')),mock.patch('portals.get_by_id',side_effect=AssertionError('GUI provider')),mock.patch('widget_data41.policy',side_effect=AssertionError('GUI policy file')):self.assertTrue(self.apply())
 def test_wrong_profile_and_expired_snapshot_are_rejected(self):
  with mock.patch('epg_handoff63.profile_scope',return_value='foreign'):self.assertFalse(self.apply())
  with mock.patch('widget_patch85.time.time',return_value=time.time()+31):self.assertFalse(self.apply())
 def test_identical_publication_is_deduplicated_after_sent_hook(self):
  values=[(self.portal['id'],'vod','a'*64,24)];self.module.sent('hook',values)
  with mock.patch.object(self.module,'apply',side_effect=AssertionError('same frame repaint')):self.assertTrue(self.module.publication('hook',values))
 def test_changed_live_publication_keeps_existing_native_handoff(self):
  with mock.patch.object(self.module,'apply',side_effect=AssertionError('live rewritten')):self.assertFalse(self.module.publication('hook',[(self.portal['id'],'live','b'*64,88)]))
 def test_no_verified_binding_creates_no_patch_property(self):
  self.runtime._plans.clear();self.properties.clear()
  self.assertFalse(self.module.prepare(self.portal,'vod',self.values,'a'*64));self.assertFalse(self.properties)
 def test_source_bookkeeping_alone_never_reloads_but_real_picture_change_does(self):
  import copy
  from home_publication74 import signature
  from widget_snapshot85 import semantic
  values=copy.deepcopy(self.values);prior=signature(values,'vod');plain=semantic(values[0]);values[0]['props']['XCMate.Source85']='renewed-proof-bookkeeping'
  self.assertEqual(signature(values,'vod'),prior);self.assertEqual(semantic(values[0]),plain)
  values[0]['art']['poster']='/verified-new-edition.png';self.assertNotEqual(signature(values,'vod'),prior)
