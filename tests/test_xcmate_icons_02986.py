"""P0-G: distinct packaged textures, no blank toggles and exact IR levels."""
import hashlib,importlib,json,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as model
ROOT=Path(__file__).resolve().parents[1]
class Icons86(unittest.TestCase):
 def setUp(self):
  fixture=model.OverlayLifecycleTests(methodName='runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
  self.fixture=fixture;self.view=fixture.overlay;self.view._switch('hidden')
 def test_seven_main_icons_are_distinct_valid_packaged_mit_textures_in_every_state(self):
  from PIL import Image
  module=importlib.import_module('nav_rail');wanted=('search','favourites','live','movies','series','settings','home')
  entries=[entry for entry in module.ENTRIES if entry[0] in wanted];self.assertEqual(tuple(e[0] for e in entries),wanted)
  folder=ROOT/'src/plugin.video.xtreammate/resources/media/navigation';manifest=json.loads((folder/'manifest.json').read_text());self.assertEqual(manifest['license'],'MIT')
  self.assertIn('MIT License',(ROOT/'src/plugin.video.xtreammate/THIRD_PARTY_TABLER.txt').read_text())
  for state in ('normal','focused','selected','disabled'):
   hashes=[]
   for entry in entries:
    path=folder/(entry[1]+'-'+state+'.png');record=manifest['icons'][entry[1]]['textures'][state]
    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['sha256'])
    with Image.open(path) as image:image.load();self.assertEqual(image.size,(96,96));self.assertEqual(image.mode,'RGBA');hashes.append(hashlib.sha256(image.getchannel('A').tobytes()).hexdigest())
   self.assertEqual(len(set(hashes)),7)
 def test_unchanged_rail_does_not_clear_or_reupload_local_icons(self):
  rail=self.view._nav_rail;rail.show(False)
  with mock.patch.object(rail.icons[0],'setImage',wraps=rail.icons[0].setImage) as change:
   for _ in range(100):rail.hide();rail.show(False)
   change.assert_not_called()
  self.assertTrue(all(image.image and '/navigation/' in image.image for image in rail.icons))
  self.fixture.player.stop.assert_not_called()
 def test_four_left_levels_and_reverse_path_preserve_focus_and_stream(self):
  for _ in range(100):
   for mode in ('channels','groups','nav_icons','nav_expanded'):self.view.handle_command('left');self.assertEqual(self.view.mode,mode)
   rail=self.view._nav_rail;rail.command('down');position=rail.position
   self.view.handle_command('back');self.assertEqual(self.view.mode,'nav_icons');self.assertEqual(rail.position,position)
   self.view.handle_command('right');self.assertEqual(self.view.mode,'groups')
   self.view.handle_command('right');self.assertEqual(self.view.mode,'channels')
   self.view.handle_command('back');self.assertEqual(self.view.mode,'hidden')
  self.fixture.player.stop.assert_not_called();self.fixture.player.play.assert_not_called()
 def test_leave_is_xcmate_home_intent_not_arbitrary_kodi_home(self):
  rail=self.view._nav_rail;entry=next(e for e in rail.items if e[0]=='home');self.assertEqual(entry[3],'xcmate_home')
  with mock.patch.object(self.view,'_request_exit') as leave:self.view._nav_activate(entry[3]);leave.assert_called_once_with('USER_HOME')
