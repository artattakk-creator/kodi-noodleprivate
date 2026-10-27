"""Actual validated thumbnail textures, explicit Save and cancellation guards."""
import importlib,sys,threading,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_media_picker_02943 as old
from test_xcmate_media_choices_02943 import image


class PickerMaster46(unittest.TestCase):
 def setUp(self):
  self.m=old.Picker43(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  self.p=self.m.p;self.thumbs=self.p._thumbs46;self.source=importlib.import_module('media_sources43')
 def candidates(self):
  return [dict(self.m.candidate,url='https://image.invalid/'+str(i)+'.png',name='Actual choice '+str(i),role='poster' if i%2==0 else 'fanart') for i in range(4)]
 def load(self,rows=None):
  self.p._results(rows if rows is not None else self.candidates());self.thumbs.pump()
  if self.thumbs.thread:self.thumbs.thread.join(3)
  self.thumbs.pump()
 def test_four_real_candidates_have_local_validated_thumbnail_textures(self):
  owner=threading.get_ident();calls=[]
  def get(*a,**kw):calls.append(threading.get_ident());return image()
  with mock.patch.object(self.source,'get',side_effect=get):self.load()
  self.assertEqual(len(calls),4);self.assertTrue(all(i!=owner for i in calls));self.assertEqual(len(self.thumbs.paths),4)
  for li in self.p.getControl(200).items:
   path=li.art['thumb'];self.assertTrue(Path(path).is_file());self.assertEqual(li.props['XCMate.Preview46'],'READY');self.assertNotIn('https://',path)
  self.assertFalse((self.m.folder/'media_choices43').exists());self.assertFalse(self.p.changed)
 def test_panel_has_large_graphical_tiles_and_visible_role_filters(self):
  c=self.p.getControl(200);self.assertEqual(c.kind,'panel')
  self.assertGreaterEqual(int(c.node.find('itemlayout').get('height')),200)
  self.assertTrue(all(self.p.getControl(i).visible for i in (406,407,408)))
  self.p.setFocusId(401);self.p.native(4);self.assertEqual(self.p.getFocusId(),406)
  self.p.native(2);self.assertEqual(self.p.getFocusId(),407)
 def test_poster_and_backdrop_filters_preserve_source_candidates_and_thumbnails(self):
  with mock.patch.object(self.source,'get',return_value=image()):self.load()
  paths=dict(self.thumbs.paths);self.p.onClick(407);self.assertEqual({r['role'] for r in self.p.rows},{'poster'})
  self.p.onClick(408);self.assertEqual({r['role'] for r in self.p.rows},{'fanart'})
  self.p.onClick(406);self.assertEqual(len(self.p.rows),4);self.assertEqual(self.thumbs.paths,paths)
 def test_http_failure_stays_failure_without_placeholder_or_profile_write(self):
  with mock.patch.object(self.source,'get',side_effect=self.source.SourceError('HTTP_AUTH')):self.load()
  self.assertFalse(self.thumbs.paths);self.assertEqual(set(self.thumbs.codes.values()),{'HTTP_AUTH'})
  self.assertTrue(all(not li.art for li in self.p.getControl(200).items));self.assertFalse(self.p.changed)
 def test_empty_or_metadata_only_candidates_create_no_image_job(self):
  with mock.patch.object(self.source,'get',side_effect=AssertionError('no remote image')) as get:
   self.load([]);self.assertEqual(self.p.rows,[])
   self.load([self.m.candidate]);get.assert_not_called()
  self.assertEqual(self.p.getControl(200).items[0].props['XCMate.Preview46'],'NO_IMAGE')
 def test_stale_source_results_cannot_apply_to_new_candidates(self):
  self.p._results(self.candidates());oldgen=self.thumbs.generation
  self.p._results([self.m.candidate]);self.thumbs.results.put((oldgen,'wrong','/old.png','READY'))
  self.thumbs.pump();self.assertFalse(self.p.getControl(200).items[0].art);self.assertFalse(self.thumbs.paths)
 def test_large_preview_is_downloaded_separately_and_persists_only_after_save(self):
  with mock.patch.object(self.source,'get',return_value=image()):self.load()
  self.p._preview();self.assertIsNone(self.p.image)
  with mock.patch.object(self.source,'get',return_value=image()):self.m.drain()
  self.assertEqual(self.p.image,image());self.assertTrue(Path(self.p.getControl(300).image).is_file())
  self.assertFalse(self.p.changed);self.p.onClick(501);self.assertFalse(self.p.changed);self.p.onClick(503);self.m.drain()
  self.assertTrue(self.p.changed)
  overrides=importlib.import_module('media_overrides43');record=overrides.apply_many('p',[self.p.record])[0]
  self.assertTrue(overrides.cached_art(record)['poster']);self.assertTrue(Path(overrides.cached_art(record)['poster']).is_file())
 def test_closed_owner_never_applies_thumbnail_or_recreates_temp_folder(self):
  self.p._results(self.candidates());gen=self.thumbs.generation;self.p.close()
  self.thumbs.results.put((gen,'wrong','/late.png','READY'));self.p.pump();self.assertFalse(self.thumbs.paths)
