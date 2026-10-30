"""Direct-update contract: original icon, persisted data, and player/EPG handoff.

Real filesystem/SQLite and simulated Kodi events; Android remains NOT_TESTED.
"""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from PIL import Image
from xcmate027_fixture import Fixture,QueuedPool,ADDON

ICON_SHA='81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135'


class IconContractTests(unittest.TestCase):
    def test_original_icon_bytes_dimensions_and_kodi_asset_reference(self):
        icon=ADDON/'icon.png';self.assertEqual(hashlib.sha256(icon.read_bytes()).hexdigest(),ICON_SHA)
        with Image.open(icon) as image:self.assertEqual(image.size,(512,512));image.verify()
        addon=ET.parse(ADDON/'addon.xml').getroot()
        self.assertEqual(addon.get('id'),'plugin.video.xtreammate')
        self.assertEqual(addon.get('version'),'0.1.29.61')
        self.assertEqual(addon.findtext("extension[@point='xbmc.addon.metadata']/assets/icon"),'icon-81da1003a2753ec6.png')


class CumulativeUpdateTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('guide_grid_window','guide_grid_data','guide_playback','media_autoplay','media_intent','playback_exit'):
            sys.modules.pop(name,None)
        self.grid=importlib.import_module('guide_grid_window');self.auto=importlib.import_module('media_autoplay')
        patch=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);patch.start();self.addCleanup(patch.stop)

    def window(self):
        window=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p')
        window.configure(self.router,self.portal);window.doModal();self.settle(window);self.addCleanup(window.close)
        return window

    def test_existing_resume_favourites_images_settings_survive_guide_theme_roundtrip(self):
        episode=dict(pid='p',kind='episode',sid='11',series_id='1',season='1',episode='1')
        self.state.save_progress(episode,120,600);self.state.mark_episode('p',dict(sid='12',series_id='1',season=1),True)
        self.state.toggle('p','vod','7');before=self.state.read()
        settings=self.folder/'settings.xml';settings.write_text('<settings><setting id="media_art_budget_mb">0</setting></settings>')
        art=self.folder/'media_art_v1';art.mkdir();picture=art/'existing-cover.img';picture.write_bytes((ADDON/'icon.png').read_bytes())
        saved={str(p):p.read_bytes() for p in (settings,picture)};portal=dict(self.portal)
        window=self.window();window._show_groups();window._group_back_after=0;window.native(92);self.settle(window)
        appearance=importlib.import_module('appearance')
        appearance.save(dict(appearance.DEFAULT,text='000000',focus='FFFFFF'))
        appearance.window_source('XCMateGuideGrid.xml');appearance.save(appearance.DEFAULT)
        self.assertEqual(self.state.read(),before);self.assertEqual(self.portal,portal)
        for p,data in saved.items():self.assertEqual(Path(p).read_bytes(),data)
        self.assertEqual(hashlib.sha256((ADDON/'icon.png').read_bytes()).hexdigest(),ICON_SHA)
        # Reload state as after a new interpreter: original bookmark/seen remain.
        state=importlib.reload(self.state)
        self.assertEqual(state.resume_position(state.progress('p','episode','11','1','1')),120)
        self.assertTrue(state.progress('p','episode','12','1','1')['watched']);self.assertTrue(state.favourite('p','vod','7'))

    def test_stopped_autoplay_chain_cannot_restart_after_epg_live_handoff(self):
        intent=importlib.import_module('media_intent');progress=importlib.import_module('media_progress')
        playing=[True];nonce=['episode-one']
        player=mock.Mock();player.isPlayingVideo.side_effect=lambda:playing[0];player.isPlaying.side_effect=lambda:playing[0]
        player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda key:nonce[0] if key=='xcmate_media' else ''
        player.getTime.return_value=300;player.getTotalTime.return_value=600;player.getPlayingFile.return_value='owned-media'
        sys.modules['xbmc'].Player=lambda:player
        session=dict(pid='p',kind='episode',series_id='1',season='1',episode='1',sid='11',nonce=nonce[0],at=time.time(),autoplay=True,autoplay_chain='root')
        self.properties[progress.PROPERTY]=json.dumps(session)
        from media_sequence import records
        episodes=records(self.details['get_series_info'],'p','1');events=self.auto.Events();pool=QueuedPool()
        coordinator=self.auto.Coordinator(player,events,pool,loader=lambda session:episodes,launch=self.builtins.append)
        self.addCleanup(coordinator.shutdown)
        events.av_started(player);coordinator.tick();pool.drain();coordinator.tick()
        playing[0]=False;events.terminal('ended',player);coordinator.tick();coordinator.tick()
        self.assertEqual(len(self.builtins),1);self.assertIn('kind=episode',self.builtins[0]);self.assertIn('sid=12',self.builtins[0])
        pending=coordinator.session['nonce'];self.auto.request_cancel('root','p');coordinator.tick()
        self.assertFalse(intent.allowed(pending,'p','episode','12'))
        window=self.window();self.dialog.select.return_value=1;window.native(7)
        self.assertTrue(window._leaving);window._leave_after=0;window._owner_tick()
        play=importlib.import_module('guide_playback')
        self.assertTrue(play.handoff(self.router,self.portal,window._play_request))
        self.assertFalse(play.handoff(self.router,self.portal,window._play_request))
        for _ in range(5):coordinator.tick()
        self.assertEqual(len(self.builtins),2);self.assertIn('action=play_live',self.builtins[-1])
        self.assertEqual(coordinator.phase,'CANCELLED');player.stop.assert_not_called()
        self.assertTrue(self.state.progress('p','episode','11','1','1')['watched'])
