"""Single visible text layer, current/future selection before limits/publication."""
import importlib,sys,threading,time,types,unittest
from unittest import mock
import test_xcmate_kodi21_overlay as gui
from xcmate027_fixture import Fixture

class MiniVisual41(unittest.TestCase):
    def setUp(self):
        self.m=gui.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.mini=self.o._mini
    def test_one_text_layer_with_visible_focusable_native_navigation_at_720_and_1080(self):
        module=importlib.import_module('mini_epg');now=time.time()
        for width,height in ((1280,720),(1920,1080)):
            self.o._width=width;self.o._height=height;mini=module.MiniProgramme(self.o)
            self.o._guide.get=lambda sid:dict(now='',next='',programme_events=[dict(title='Native title must not duplicate',start=now-10,stop=now+100)])
            self.o._highlight['channels']=0;self.o.visible_channels=self.o.channels
            mini.render();mini.focus()
            self.assertTrue(mini.list.visible);self.assertTrue(mini.list.enabled);self.assertIs(self.o.focus,mini.list)
            self.assertEqual(mini.list.items,['']);self.assertEqual(mini.list.options['textColor'],'0x00000000')
            self.assertEqual(mini.rows[0][2].text,'Native title must not duplicate')
            self.assertIn('FF55DD99',mini.rows[0][1].label)
    def test_more_than_five_events_scroll_once_and_now_mark_does_not_follow_focus(self):
        now=time.time();self.o._guide.get=lambda sid:dict(now='',next='',programme_events=[dict(title='Long title '+str(i),start=now-1+i*100,stop=now+99+i*100) for i in range(12)])
        self.o._switch('channels');self.mini.focus()
        for _ in range(7):self.o.native(4)
        self.assertEqual(self.mini.selected,7);self.assertIn('7',self.mini.rows[2][2].text)
        self.assertTrue(self.mini.rows[2][0].visible)
        self.assertTrue(all(not c for c in self.mini.list.items));self.assertFalse(self.mini.rows[0][1].label.startswith('[COLOR'))
    def test_only_future_before_limit_and_no_fake_now_on_historical_only(self):
        module=importlib.import_module('mini_epg');now=time.time()
        past=[dict(title='Past '+str(i),start=now-1000-i,stop=now-100-i) for i in range(300)]
        future=[dict(title='Now',start=now-10,stop=now+10),dict(title='Next',start=now+10,stop=now+50)]
        rows,index=module.programme_rows(past+future,now)
        self.assertEqual([e['title'] for e in rows],['Now','Next']);self.assertEqual(index,0)
        self.assertEqual(module.programme_rows(past,now)[0],[])
    def test_twenty_open_close_and_long_non_latin_titles_leave_no_hidden_text(self):
        module=importlib.import_module('mini_epg')
        for title in ('A long title '*90,'長い番組のタイトル '*90,'عنوان برنامج طويل '*90):
            self.assertLessEqual(len(module.wrap_title(title,400).splitlines()),2)
        now=time.time();self.o._guide.get=lambda sid:dict(now='',next='',events=[dict(title='Now',start=now-1,stop=now+10)])
        for _ in range(20):
            self.o._switch('channels');self.o._switch('hidden')
            self.assertFalse(self.mini.list.visible)
            self.assertTrue(all(not stamp.label and not title.text for _,stamp,title in self.mini.rows))
    def test_native_action_92_preserves_back_contract_in_all_overlay_states(self):
        self.o._request_exit=mock.Mock()
        for mode,want in [('channels','hidden'),('groups','channels'),('info','hidden'),('extras','controls'),('controls','info')]:
            self.o._switch(mode);self.o.native(92);self.assertEqual(self.o.mode,want)
        self.o._switch('hidden');self.o.native(92);self.o._request_exit.assert_called_once()

class MiniSnapshot41(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.data=importlib.import_module('tv_data');self.store=importlib.import_module('guide_store')
    def test_sql_limit_after_time_selection_keeps_future_past_300_historical_slots(self):
        now=self.now;events=[dict(name='Past '+str(i),start_timestamp=now-20000+i*20,stop_timestamp=now-19980+i*20) for i in range(300)]
        events += [dict(name='Now',start_timestamp=now-10,stop_timestamp=now+100),dict(name='Next',start_timestamp=now+100,stop_timestamp=now+200)]
        self.store.import_cache('p',{'xml':events},revision='future')
        cache=importlib.import_module('guide_viewport').cache('p',[dict(sid='1',epg_channel_id='xml')],{},now,focus_sid='1')
        self.assertEqual([e['name'] for e in cache['xml']],['Now','Next'])
    def test_late_worker_for_old_sender_selection_cannot_publish(self):
        snap=self.data.GuideSnapshot(self.portal,self.client);channel=types.SimpleNamespace(tvg_id='xml',extra=dict(stream_id='1'))
        snap.request([channel]);entered=threading.Event();release=threading.Event();errors=[]
        def cache(*a,**kw):entered.set();release.wait(2);return {}
        def refresh():
            try:snap.refresh()
            except BaseException as e:errors.append(type(e).__name__)
        with mock.patch('guide_viewport.cache',side_effect=cache):
            worker=threading.Thread(target=refresh);worker.start();self.assertTrue(entered.wait(1))
            snap.request([types.SimpleNamespace(tvg_id='other',extra=dict(stream_id='2'))]);release.set();worker.join(2)
        self.assertFalse(errors);self.assertNotIn('1',snap._values);self.assertEqual(snap.generation,0)
