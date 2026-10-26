"""Actual native controls with modeled Kodi owner/IR and local guide data."""
import importlib,json,time,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as model

class Navigation38(unittest.TestCase):
    def setUp(self):
        self.m=model.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.o._switch('hidden');self.sid=self.o.sid

    def test_five_left_levels_twenty_cycles_never_stop_or_retune(self):
        for _ in range(20):
            for wanted in ('channels','groups','nav_expanded','hidden'):
                self.o.handle_command('left');self.assertEqual(self.o.mode,wanted)
            self.assertEqual(self.o.sid,self.sid)
        self.m.player.stop.assert_not_called()

    def test_reverse_rail_levels_restore_groups_then_same_mini_focus(self):
        for _ in range(3):self.o.handle_command('left')
        self.o.handle_command('back');self.assertEqual(self.o.mode,'groups')
        self.o.handle_command('right');self.assertEqual(self.o.mode,'channels');self.assertEqual(self.o.sid,self.sid)

    def test_compact_expanded_full_height_buttons_and_local_icons(self):
        for _ in range(2):self.o.handle_command('left')
        rail=self.o._nav_rail;self.assertEqual(rail.panel.options['height'],self.o._height-48)
        before=rail.panel.options['height'];self.o.handle_command('left');self.assertEqual(rail.panel.options['height'],before)
        actions=[e[3] for e in rail.items]
        self.assertTrue({'global_search','favourites','home_live','movies_home','series_home','guide_grid','settings_home','xcmate_home','startup_current'}<=set(actions))
        for _ in range(len(rail.items)*2):self.o.handle_command('down');self.assertIs(self.o.focus,rail.buttons[rail.position])
        for image in rail.icons:self.assertIn('/navigation/',image.image)

    def test_mini_highlight_changes_programmes_without_tune(self):
        self.o.handle_command('left');self.o._guide.get=mock.Mock(side_effect=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[dict(title='Station '+sid,start=time.time()-60,stop=time.time()+300,description='Actual local programme')]))
        self.o._render();before=self.o._mini.sid
        with mock.patch.object(self.o,'_tune') as tune:
            self.o.handle_command('down');self.assertNotEqual(self.o._mini.sid,before)
            self.o.handle_command('right');self.assertEqual(self.o.mode,'channels');self.assertTrue(self.o._mini.focused)
            self.o.handle_command('back');self.assertFalse(self.o._mini.focused);self.assertEqual(self.o.mode,'channels')
            tune.assert_not_called()
        self.assertEqual(self.o.sid,self.sid)

    def test_programme_focus_does_not_skip_groups_on_left(self):
        self.o.handle_command('left');self.o._guide.get=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[dict(title='Now',start=time.time()-1,stop=time.time()+60)])
        self.o.handle_command('right');self.assertTrue(self.o._mini.focused)
        self.o.handle_command('left');self.assertEqual(self.o.mode,'channels');self.assertFalse(self.o._mini.focused)
        self.o.handle_command('left');self.assertEqual(self.o.mode,'groups')

    def test_empty_epg_has_no_fictitious_programme_or_tune(self):
        self.o.handle_command('left');self.o._guide.get=lambda sid:dict(now='',next='',now_time='',now_end_time='',events=[])
        self.o._render();self.o.handle_command('right');self.assertFalse(self.o._mini.focused);self.assertFalse(self.o._mini.events)

    def test_real_previous_now_next_order_and_no_invalid_times(self):
        module=importlib.import_module('mini_epg')
        events=[dict(title='After',start=110,stop=130),dict(title='Before',start=70,stop=90),dict(title='Now',start=90,stop=110),dict(title='Invalid',start=110,stop=100)]
        rows,pos=module.programme_rows(events,100);self.assertEqual([e['title'] for e in rows],['Before','Now','After']);self.assertEqual(pos,1)

    def test_worker_reads_previous_current_next_from_real_guide_sqlite(self):
        import sqlite3,tempfile,sys,types
        from pathlib import Path
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);path=Path(temp.name)/'guide.sqlite'
        now=int(time.time());pid=self.o.portal['id'];channel=self.o.index.by_sid[self.sid]
        db=sqlite3.connect(path)
        db.executescript('CREATE TABLE guide_meta(pid TEXT);CREATE TABLE guide_alias(pid TEXT,alias TEXT,cid TEXT);CREATE TABLE programmes(pid TEXT,cid TEXT,title TEXT,description TEXT,start INTEGER,stop INTEGER,source INTEGER);')
        db.execute('INSERT INTO guide_meta VALUES(?)',(pid,));db.execute('INSERT INTO guide_alias VALUES(?,?,?)',(pid,self.sid,'xml'))
        for title,start,stop in [('Previous',now-600,now-30),('Current',now-30,now+300),('Next',now+300,now+900)]:db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',(pid,'xml',title,'Local description',start,stop,0))
        db.commit();db.close()
        store=importlib.import_module('guide_store');self.o._guide.request([channel]);self.o._guide.request_programme(self.sid)
        helpers=dict(epg=types.SimpleNamespace(load_cache=lambda pid:{},_mem_clear=lambda pid:None),epg_sources=types.SimpleNamespace(configuration=lambda pid:{'mappings':{}}),epg_status=types.SimpleNamespace(revision=lambda pid:'local-fixture'),logo_cache=types.SimpleNamespace(request=lambda channels:None))
        with mock.patch.dict(sys.modules,helpers),mock.patch.object(store,'path',return_value=str(path)),mock.patch.object(sys.modules['utils'],'addon_data_dir',return_value=temp.name):self.o._guide.refresh()
        result=self.o._guide.get(self.sid)
        self.assertEqual([e['title'] for e in result['programme_events']],['Previous','Current','Next'])
        self.assertEqual(result['now'],'Current');self.assertEqual(self.o.sid,self.sid)

    def test_midnight_rows_show_real_date_without_changing_chronological_order(self):
        import datetime
        module=importlib.import_module('mini_epg');now=datetime.datetime(2026,10,26,12).timestamp()
        event=dict(start=datetime.datetime(2026,10,27,23,30).timestamp(),stop=datetime.datetime(2026,10,28,0,30).timestamp())
        label=module.time_label(event,now);self.assertIn('27.10.',label);self.assertIn('28.10.',label)
