"""Actual progress polling with exact item identity and durable state."""
import importlib
import json
import os
import sys
import time
import types
import unittest
from unittest import mock

from xcmate027_fixture import Fixture


class ProgressTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.progress=importlib.import_module('media_progress')
        self.session=dict(pid='p',kind='vod',sid='1',nonce='one',at=time.time(),resume=True)
        self.properties[self.progress.PROPERTY]=json.dumps(self.session)
        self.position=0;self.duration=2700;self.playing=True;self.unique='one';self.seekable=True;self.seeks=[]
        def seek(position): self.seeks.append(position);self.position=position
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:self.playing,getTotalTime=lambda:self.duration,
            getTime=lambda:self.position,getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:self.unique),seekTime=seek)
        sys.modules['xbmc'].getCondVisibility=lambda condition:self.seekable

    def test_play_validates_movie_identity_and_tags_only_its_resolved_item(self):
        tag=types.SimpleNamespace(setUniqueIDs=mock.Mock())
        item=types.SimpleNamespace(getVideoInfoTag=lambda:tag)
        builder=mock.Mock(return_value=item)
        self.router._params.update(kind='vod',sid='1',resume='1')
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=builder)):
            self.progress.play(self.router,self.portal)
            session=json.loads(self.properties[self.progress.PROPERTY])
            self.assertEqual((session['pid'],session['sid'],session['kind'],session['resume']),('p','1','vod',True))
            tag.setUniqueIDs.assert_called_once_with({self.progress.UNIQUE_ID:session['nonce']})
            sys.modules['xbmcplugin'].setResolvedUrl.assert_called_once_with(7,True,item)
            self.router._params['sid']='not-cached'
            self.progress.play(self.router,self.portal)
            self.assertEqual(builder.call_count,1)
            self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])

    def test_episode_play_derives_season_from_cached_series_and_rejects_unknown_ids(self):
        tag=types.SimpleNamespace(setUniqueIDs=mock.Mock())
        builder=mock.Mock(return_value=types.SimpleNamespace(getVideoInfoTag=lambda:tag))
        self.router._params.update(kind='episode',sid='12',series_id='1',season='999')
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=builder)):
            self.progress.play(self.router,self.portal)
            session=json.loads(self.properties[self.progress.PROPERTY])
            self.assertEqual((session['series_id'],session['season'],session['episode']),('1','1','2'))
            for changes in ({'sid':'unknown'},{'sid':'12','series_id':'unknown'}):
                self.router._params.update(changes)
                self.progress.play(self.router,self.portal)
                self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
            self.assertEqual(builder.call_count,1)

    def test_ready_seek_once_periodic_checkpoint_and_stop_survive_restart(self):
        self.state.save_progress(self.session,1050,2700)
        self.progress.poll(self.player,now=100)
        self.assertEqual(self.seeks,[1050])
        self.position=1070;self.progress.poll(self.player,now=116)
        self.assertEqual(self.seeks,[1050])
        self.playing=False;self.progress.poll(self.player,now=117)
        self.assertIsNone(self.progress._current)
        self.assertEqual(self.state.progress('p','vod','1')['position'],1070)

    def test_foreign_video_or_stale_item_never_seeks_or_writes(self):
        self.unique='foreign'
        self.progress.poll(self.player,now=100)
        self.assertEqual(self.seeks,[])
        self.assertFalse(os.path.exists(self.state.path()))
        self.session['kind']='live';self.unique='one';self.properties[self.progress.PROPERTY]=json.dumps(self.session)
        self.progress.poll(self.player,now=101)
        self.assertIsNone(self.progress._current)

    def test_resume_waits_for_player_and_seek_capability_without_erasing_old_bookmark(self):
        self.state.save_progress(self.session,1050,2700)
        self.duration=0;self.progress.poll(self.player,now=100)
        self.assertFalse(self.seeks)
        self.duration=2700;self.seekable=False;self.progress.poll(self.player,now=101)
        self.assertFalse(self.seeks)
        self.seekable=True;self.progress.poll(self.player,now=105)
        self.assertEqual(self.seeks,[1050])

    def test_unseekable_resume_explained_once_and_early_restart_preserves_bookmark(self):
        self.state.save_progress(self.session,1050,2700)
        self.seekable=False
        for now in (100,105,112,113): self.progress.poll(self.player,now=now)
        self.assertFalse(self.seeks);self.dialog.notification.assert_called_once()
        self.playing=False;self.progress.poll(self.player,now=114)
        self.assertEqual(self.state.progress('p','vod','1')['position'],1050)

    def test_restart_updates_bookmark_only_after_plausible_position_and_no_auto_next(self):
        self.state.save_progress(self.session,1050,2700)
        self.session['resume']=False;self.properties[self.progress.PROPERTY]=json.dumps(self.session)
        self.progress.poll(self.player,now=100)
        self.assertFalse(self.seeks)
        self.position=30;self.progress.poll(self.player,now=116)
        self.assertEqual(self.state.progress('p','vod','1')['position'],1050)
        self.position=70;self.progress.poll(self.player,now=132)
        self.assertEqual(self.state.progress('p','vod','1')['position'],70)
        self.position=2600;self.progress.poll(self.player,now=150)
        self.playing=False;self.progress.poll(self.player,now=151)
        self.assertTrue(self.state.progress('p','vod','1')['watched'])
        self.assertEqual(self.builtins,[])

    def test_shutdown_keeps_last_sample_without_reassigning_it_to_new_video(self):
        self.session['resume']=False;self.properties[self.progress.PROPERTY]=json.dumps(self.session)
        self.position=500;self.progress.poll(self.player,now=100)
        self.progress.shutdown()
        self.assertEqual(self.state.progress('p','vod','1')['position'],500)
        self.unique='foreign';self.progress.poll(self.player,now=101)
        self.assertIsNone(self.progress._current)

    def test_episode_mark_seen_and_reset_are_scoped_and_keep_legacy_files(self):
        e=dict(sid='11',series_id='1',season=1)
        self.state.mark_episode('p',e,True)
        self.assertTrue(self.state.progress('p','episode','11','1',1)['watched'])
        self.assertEqual(self.state.progress('p','episode','11','2',1),{})
        self.state.mark_episode('p',e,None)
        self.assertEqual(self.state.progress('p','episode','11','1',1),{})


class StorageTests(Fixture,unittest.TestCase):
    def vfs(self,deny=False,wrong=False):
        def file(path,mode='r'):
            if deny and mode=='w': raise PermissionError('denied')
            f=open(path,mode,encoding='utf-8')
            return types.SimpleNamespace(write=lambda text:bool(f.write(text)),
                read=lambda:'wrong' if wrong else f.read(),close=f.close)
        return types.SimpleNamespace(File=file,exists=os.path.isdir,translatePath=lambda path:path,
                                     delete=lambda path:os.unlink(path) if os.path.exists(path) else False)

    def test_recording_directory_roundtrip_cleanup_and_old_setting_preserved_on_denial(self):
        home=importlib.import_module('home_menu')
        self.assertTrue(home.probe_directory(str(self.folder),self.vfs()))
        self.assertFalse(home.probe_directory(str(self.folder),self.vfs(wrong=True)))
        self.assertFalse(home.probe_directory(str(self.folder),self.vfs(deny=True)))
        self.assertEqual(list(self.folder.glob('.xcmate-write-test-*')),[])
        self.options['recordings_folder']='previous'
        self.dialog.browseSingle=mock.Mock(return_value=str(self.folder))
        from capture_target import TargetFailure
        with mock.patch.dict(sys.modules,xbmcvfs=self.vfs(deny=True)),mock.patch('capture_ui.work',side_effect=lambda fn:fn()),mock.patch('capture_target.probe',side_effect=TargetFailure('TARGET_PERMISSION','WRITE',13)),mock.patch('capture_target.compatible_default',return_value=None):
            home.recording_folder()
        self.assertEqual(self.options['recordings_folder'],'previous')

    def test_recording_directory_setting_changes_only_after_successful_probe(self):
        home=importlib.import_module('home_menu')
        self.dialog.browseSingle=mock.Mock(return_value=str(self.folder))
        with mock.patch.dict(sys.modules,xbmcvfs=self.vfs()),mock.patch('capture_ui.work',side_effect=lambda fn:fn()): home.recording_folder()
        self.assertEqual(self.options['recordings_folder'],str(self.folder))
        self.assertEqual(list(self.folder.glob('.xcmate-write-test-*')),[])

    def test_engine_probe_without_binary_never_claims_recording_or_installs(self):
        probe=importlib.import_module('recording_probe')
        with mock.patch.object(probe.shutil,'which',return_value=None),mock.patch.object(probe.subprocess,'run') as run:
            text=probe.report()
        run.assert_not_called();self.assertIn('kein ausführbarer Kandidat',text)
        self.assertIn('nicht implementiert',text)

    def test_engine_version_probe_is_bounded_and_does_not_claim_test_recording(self):
        probe=importlib.import_module('recording_probe')
        with mock.patch.object(probe.shutil,'which',return_value='/available/ffmpeg'), \
             mock.patch.object(probe.subprocess,'run',return_value=types.SimpleNamespace(returncode=0)) as run:
            text=probe.report()
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0],['/available/ffmpeg','-version'])
        self.assertEqual(run.call_args.kwargs['timeout'],2)
        self.assertIn('Erst eine nachgewiesene kurze Testaufnahme',text)
