"""Native origin mementos and asynchronous fullscreen Back, never root reload."""
import importlib,json,sys,time,types,unittest
from unittest import mock
import xcmate027_fixture as model
import test_xcmate_media_osd_02921 as osd_model


class Return39(model.Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.returning=importlib.import_module('media_return')
        self.player=mock.Mock();self.player.isPlayingVideo.return_value=False;self.player.isPlaying.return_value=False
        sys.modules['xbmc'].Player=lambda:self.player

    def test_twenty_grid_search_and_detail_returns_keep_exact_native_view_and_focus(self):
        w=self.media_window();w._page('grid',0);self.settle(w)
        for mode in ('grid','detail','search'):
            if mode=='detail':w._details(w.rows[0]);self.settle(w)
            if mode=='search':w._open_search('House');self.settle(w);w._search_click(701);self.settle(w);w.setFocusId(710)
            for cycle in range(20):
                focus=w.getFocusId();position=w.getControl(focus).getSelectedPosition();category=w.category;offset=w.offset
                query=getattr(w,'_search_query',None);tab=getattr(w,'_search_kind',None)
                nonce='origin-'+mode+str(cycle);self.returning.capture(w,nonce)
                token=('media',dict(pid='p',sid='1',nonce=nonce,at=time.time(),kind='vod'))
                self.assertTrue(self.returning.request(token));value=self.returning.read();value['not_before']=0
                self.properties[self.returning.KEY]=json.dumps(value)
                w.mode='landing';w.category='changed';w.offset=999
                self.assertTrue(self.returning.restore(w))
                self.assertEqual((w.mode,w.category,w.offset,w.getFocusId()),(mode,category,offset,focus))
                self.assertEqual(w.getControl(focus).getSelectedPosition(),position)
                self.assertEqual((getattr(w,'_search_query',None),getattr(w,'_search_kind',None)),(query,tab))
                self.assertFalse(any('Container.Update' in b or 'ActivateWindow' in b for b in self.builtins))

    def test_play_captures_origin_and_reentrant_oninit_does_not_reset_it(self):
        w=self.media_window();w._details(w.rows[0]);self.settle(w);w.setFocusId(300)
        w._play(w.selected,'vod');origin=w._playback_origin39
        self.assertTrue(origin);self.assertEqual(self.returning.read()['nonce'],w._play_intent)
        self.player.isPlayingVideo.return_value=True;self.player.isPlaying.return_value=True
        self.player.getVideoInfoTag.return_value.getUniqueID.return_value=w._play_intent
        w.onInit();self.assertIs(w._playback_origin39,origin);self.assertEqual(w.mode,'detail')

    def test_foreign_dialog_defers_return_and_foreign_playback_cancels_it(self):
        w=self.media_window();self.returning.capture(w,'ours')
        token=('media',dict(pid='p',sid='1',nonce='ours',at=time.time(),kind='vod'))
        self.returning.request(token);value=self.returning.read();value['not_before']=0;self.properties[self.returning.KEY]=json.dumps(value)
        life=importlib.import_module('window_lifecycle')
        with mock.patch.object(life,'state',return_value=dict(window=12005,dialog=10124,modal=True,updating=False)):
            self.assertFalse(self.returning.restore(w));self.assertIsNotNone(w._playback_origin39)
        self.player.isPlaying.return_value=True
        self.assertFalse(self.returning.restore(w));self.assertIsNone(w._playback_origin39);self.assertIsNone(self.returning.read())

    def test_wrong_portal_or_replaced_origin_cannot_request_return(self):
        w=self.media_window();self.returning.capture(w,'right')
        for pid,nonce in (('foreign','right'),('p','stale')):
            self.assertFalse(self.returning.request(('media',dict(pid=pid,sid='1',nonce=nonce,at=time.time(),kind='vod'))))
        w.close();self.assertIsNone(self.returning.read())


class FullscreenBack39(unittest.TestCase):
    def setUp(self):
        self.m=osd_model.MediaOSDTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)

    def test_visible_back_hides_then_hidden_back_queues_one_own_stop(self):
        w=self.m.window;w.show_bar();self.m.key(92);self.assertFalse(w.visible);self.m.player.stop.assert_not_called()
        self.m.key(92);self.assertTrue(w.closed);self.m.player.stop.assert_not_called()
        from exit37_fixture import drain_stop
        drain_stop();self.m.player.stop.assert_called_once()

    def test_hidden_back_in_episode_gap_cancels_chain_without_touching_foreign_player(self):
        from media_autoplay import STATE,cancelled
        self.m.session.update(kind='episode',series_id='1',autoplay_chain='chain')
        self.m.properties['XCMate.MediaSession']=json.dumps(self.m.session)
        self.m.properties[STATE]=json.dumps(dict(root='chain',nonce='next',pid='p',phase='STARTING',enabled=True,at=time.time()))
        self.m.player.isPlayingVideo.return_value=False;self.m.key(92)
        self.assertTrue(cancelled('chain','p'));self.m.player.stop.assert_not_called()
