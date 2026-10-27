"""Observe every native setter; end-of-method snapshots miss transient frames."""
import importlib,time,unittest
from unittest import mock
import test_xcmate_kodi21_overlay as model


class MiniFlicker43(unittest.TestCase):
    def setUp(self):
        self.m=model.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.mini=self.o._mini;self.now=time.time()
        self.events=[dict(title='Programme '+str(i),start=self.now-10+i*100,stop=self.now+90+i*100,description='Detail') for i in range(16)]
        self.o._guide.get=lambda sid:dict(programme_events=list(self.events))
        self.o._highlight['channels']=0;self.o.visible_channels=self.o.channels
        self.calls=[]
        for control in (self.mini.heading,self.mini.hint,self.mini.list,*[c for row in self.mini.rows for c in row]):
            for method in ('setVisible','setText','setLabel','reset','addItems','selectItem'):
                if not hasattr(control,method):continue
                original=getattr(control,method)
                def observe(*a,_fn=original,_method=method,**kw):
                    result=_fn(*a,**kw);self.calls.append(_method)
                    self.assertLessEqual(sum(h.visible for h,_,_ in self.mini.rows),1,'transient multiple focus borders')
                    return result
                setattr(control,method,observe)

    def test_miniflicker01_show_never_exposes_all_highlights_even_between_setters(self):
        self.mini.render();self.mini.focus();self.mini.visible(True)
        self.assertEqual(sum(h.visible for h,_,_ in self.mini.rows),1)

    def test_miniflicker02_200_identical_worker_ticks_do_not_rebuild_or_repaint(self):
        self.mini.render();self.mini.focus();self.calls.clear()
        for _ in range(200):self.mini.render()
        self.assertEqual(self.calls,[])

    def test_miniflicker03_now_rollover_preserves_selected_identity(self):
        self.mini.render();self.mini.focus()
        for _ in range(3):self.mini.command('down')
        chosen=self.mini.events[self.mini.selected]['start'];self.calls.clear()
        with mock.patch('mini_epg.time.time',return_value=self.now+95):self.mini.render()
        self.assertEqual(self.mini.events[self.mini.selected]['start'],chosen)
        self.assertEqual(sum('●' in s.label for _,s,_ in self.mini.rows),1)

    def test_miniflicker04_sender_changes_during_refresh_keep_one_focus(self):
        self.mini.render();self.mini.focus()
        for n in range(30):
            self.o._highlight['channels']=n%len(self.o.channels)
            self.mini.render()
            self.assertLessEqual(sum(h.visible for h,_,_ in self.mini.rows),1)
        self.assertEqual(self.mini.sid,str(self.o.visible_channels[self.o._highlight['channels']].extra['stream_id']))

    def test_miniflicker05_twenty_open_close_cycles_clear_text_and_borders(self):
        for _ in range(20):
            self.mini.render();self.mini.focus();self.mini.visible(False)
            self.assertFalse(any(h.visible or s.visible or t.visible for h,s,t in self.mini.rows))
            self.assertTrue(all(not s.label and not t.text for _,s,t in self.mini.rows))

    def test_reverse_focus_order_hides_previous_before_showing_new(self):
        self.mini.focus()
        for _ in range(4):self.mini.command('down')
        for _ in range(4):self.mini.command('up')
        self.assertEqual(self.mini.selected,0)

    def test_same_length_title_or_description_change_does_not_reset_native_rows(self):
        self.mini.focus();self.calls.clear()
        self.events[0]=dict(self.events[0],title='Corrected title',description='New description')
        self.mini.render()
        self.assertNotIn('reset',self.calls);self.assertNotIn('addItems',self.calls)
        self.assertEqual(self.mini.rows[0][2].text,'Corrected title')

    def test_overlapping_provider_events_show_only_one_now_marker(self):
        self.events=[dict(title='Overlapping '+str(i),start=self.now-20+i,stop=self.now+100+i) for i in range(5)]
        self.mini.focus()
        self.assertEqual(sum('●' in s.label for _,s,_ in self.mini.rows),1)

    def test_focus_scrolls_to_last_event_and_back_retains_native_channel_focus(self):
        self.mini.focus()
        for _ in range(30):self.mini.command('down')
        self.assertEqual(self.mini.selected,15)
        self.assertIn('15',self.mini.rows[0][2].text)
        self.mini.command('back');self.assertIs(self.o.focus,self.o.control)
        self.assertFalse(any(h.visible for h,_,_ in self.mini.rows))

    def test_empty_and_historical_only_have_no_now_or_focus(self):
        self.events=[dict(title='Past',start=self.now-100,stop=self.now-5)]
        self.mini.focus()
        self.assertFalse(self.mini.focused);self.assertFalse(self.mini.events)
        self.assertFalse(any(h.visible or '●' in s.label for h,s,_ in self.mini.rows))
