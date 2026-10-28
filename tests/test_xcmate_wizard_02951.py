"""Synthetic settings, large native lists and real cancellable-worker lifetimes."""
import importlib
import json
import os
import subprocess
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,ADDON,Control,WindowXML


class Settings51(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('setup_wizard','wizard_settings51'):sys.modules.pop(name,None)
        self.wizard=importlib.import_module('setup_wizard')
        self.settings=importlib.import_module('wizard_settings51')
        self.gui=sys.modules['xbmcgui'];self.gui.DLG_YESNO_NO_BTN=10;self.gui.ALPHANUM_HIDE_INPUT=2
        original=sys.modules['xbmcaddon'].Addon
        def addon(*args):
            obj=original(*args);obj.getSetting=lambda key:self.options.get(key,'');return obj
        patch=mock.patch.object(sys.modules['xbmcaddon'],'Addon',side_effect=addon);patch.start();self.addCleanup(patch.stop)
        self.options.update(new_portal_type='2',new_portal_name='Synthetic setup',
            new_portal_xc_host='https://synthetic.invalid:8443/',
            new_portal_xc_user='synthetic-user',new_portal_xc_pass='synthetic-password')

    def test_exact_current_settings_ids_and_no_active_account_borrowing(self):
        before=dict(self.options);choice,data=self.settings.proposal()
        self.assertEqual(choice,3)
        self.assertEqual(data['xc_user'],'synthetic-user');self.assertNotIn('id',data)
        self.assertEqual(self.options,before)
        self.options.clear();self.assertIsNone(self.settings.proposal())
        self.assertEqual(self.portals,[self.portal])

    def test_complete_settings_are_used_without_asking_credentials_again(self):
        choice,data=self.settings.proposal()
        result=self.wizard.input_data(self.dialog,choice,data)
        self.dialog.input.assert_not_called()
        self.assertEqual(result['xc_host'],'https://synthetic.invalid:8443')
        self.assertEqual(result['xc_pass'],data['xc_pass'])

    def test_partial_settings_only_ask_the_missing_field_hidden(self):
        self.options.pop('new_portal_xc_pass')
        choice,data=self.settings.proposal();self.dialog.input.return_value='synthetic-completion'
        result=self.wizard.input_data(self.dialog,choice,data)
        self.assertEqual(self.dialog.input.call_count,1)
        # .53: only the missing NEW password is visible by default; saved values never open.
        self.assertEqual(self.dialog.input.call_args.kwargs,{'option':0})
        self.assertEqual(result['xc_user'],'synthetic-user')

    def test_confirmation_contains_no_values_and_default_is_no(self):
        self.dialog.yesno.return_value=True;self.dialog.input.return_value='Synthetic setup'
        with mock.patch('setup_window.open_setup',return_value={'id':'new'}) as opened:
            self.assertEqual(self.wizard.setup(),{'id':'new'})
        self.dialog.select.assert_not_called();self.assertEqual(self.dialog.input.call_count,1)
        args,kwargs=self.dialog.yesno.call_args
        self.assertEqual(kwargs['defaultbutton'],10)
        self.assertNotIn('synthetic-password',str(args));self.assertNotIn('synthetic-user',str(args))
        self.assertEqual(opened.call_args.args[0]['type'],'xtream')

    def test_declining_settings_allows_clean_manual_input_without_write(self):
        before=dict(self.options);self.dialog.yesno.return_value=False;self.dialog.select.return_value=3
        self.dialog.input.side_effect=['https://manual.invalid','manual-user','manual-password','Manual']
        with mock.patch('setup_window.open_setup') as opened:self.wizard.setup()
        self.assertEqual(opened.call_args.args[0]['xc_user'],'manual-user')
        self.assertEqual(self.options,before)

    def test_manual_cancel_starts_no_worker_and_preserves_portals(self):
        self.dialog.select.return_value=-1
        with mock.patch('setup_window.open_setup') as opened:self.assertIsNone(self.wizard.setup())
        opened.assert_not_called();self.assertEqual(self.portals,[self.portal])

    def test_cancel_missing_required_field_does_not_start_discovery(self):
        self.options.pop('new_portal_xc_pass');self.dialog.yesno.return_value=True
        with mock.patch('setup_window.open_setup') as opened:self.assertIsNone(self.wizard.setup())
        opened.assert_not_called()

    def test_settings_type_isolated_from_other_credentials(self):
        self.options['new_portal_type']='3';self.options['new_portal_stb_url']='https://stb.invalid'
        self.options['new_portal_stb_mac']='00:11:22:33:44:55'
        choice,data=self.settings.proposal();self.assertEqual(choice,0)
        self.assertFalse(any(k.startswith('xc_') for k in data))
        self.dialog.input.return_value=''
        self.assertEqual(self.wizard.input_data(self.dialog,choice,data)['stb_mac'],'00:11:22:33:44:55')

    def test_default_stalker_mac_is_not_a_configured_account(self):
        self.options.update(new_portal_type='3',new_portal_stb_mac='00:1A:79:00:00:00')
        self.assertIsNone(self.settings.proposal())

    def test_m3u_url_file_and_epg_settings_roundtrip_without_xtream_fields(self):
        for setting,choice in [('0',2),('1',1)]:
            self.options.update(new_portal_type=setting,new_portal_m3u_url='https://playlist.invalid/list.m3u',new_portal_epg_url='https://epg.invalid/guide.xml')
            actual,data=self.settings.proposal();self.assertEqual(actual,choice)
            result=self.wizard.input_data(self.dialog,actual,data)
            self.assertEqual(result['epg_url'],'https://epg.invalid/guide.xml')
            self.assertNotIn('xc_pass',result)
        self.dialog.input.assert_not_called()

    def test_invalid_settings_type_never_guesses_other_portal(self):
        for value in ('4','-1','broken'):
            self.options['new_portal_type']=value;self.assertIsNone(self.settings.proposal())

    def test_invalid_prefilled_origin_can_be_corrected_locally(self):
        self.options['new_portal_xc_host']='ftp://synthetic.invalid'
        self.dialog.input.return_value='https://corrected.invalid'
        choice,data=self.settings.proposal();result=self.wizard.input_data(self.dialog,choice,data)
        self.assertEqual(result['xc_host'],'https://corrected.invalid')
        self.assertEqual(self.dialog.input.call_count,1)


class GroupUI51(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('setup_window','wizard_groups51'):sys.modules.pop(name,None)
        self.ui=importlib.import_module('setup_window')
        p=mock.patch.object(Control,'setPercent',lambda c,v:setattr(c,'percent',v),create=True);p.start();self.addCleanup(p.stop)
        self.draft=types.SimpleNamespace(pid='synthetic-session',data={'type':'xtream','name':'Synthetic'},
            categories={k:[{'category_id':str(n),'category_name':k+' group '+str(n)} for n in range(1201)] for k in ('live','vod','series')},
            selected={k:set() for k in ('live','vod','series')},scanned=False,dispose=mock.Mock(),report=dict(live=1,vod=1,series=1,epg=0,sources=[],warnings=[]))
        self.window=self.ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');self.window.configure(self.draft)
        self.window._initialized=True;self.window.discovered(self.draft.categories)
        self.addCleanup(self.window._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(self.window.close)

    def drain(self):
        for _ in range(200):
            self.window.pump()
            if self.window._rendered[self.window.kind]==len(self.window._entries) and self.window.kind not in self.window._bulk:return
        self.fail('render not bounded')

    def test_first_render_is_bounded_and_other_tabs_stay_lazy(self):
        w=self.window
        self.assertGreater(len(w.getControl(100).items),0);self.assertLessEqual(len(w.getControl(100).items),32)
        self.assertEqual(w.getControl(101).items,[]);self.assertEqual(w.getControl(102).items,[])
        self.assertEqual(w.getFocusId(),100);self.assertIn('1201',w.getControl(3).text)

    def test_each_pump_adds_at_most_32_rows_and_all_1201_are_reachable(self):
        w=self.window;counts=[];before=len(w.getControl(100).items)
        for _ in range(40):
            w.pump();after=len(w.getControl(100).items);counts.append(after-before);before=after
        self.assertEqual(before,1201);self.assertLessEqual(max(counts),32)
        w.getControl(100).selectItem(1200);w.onClick(100)
        self.assertEqual(self.draft.selected['live'],{'1200'})

    def test_slow_item_creation_respects_time_slice(self):
        w=self.window;clock=[0]
        def make(label):
            from xcmate027_fixture import ListItem
            clock[0]+=.005;return ListItem(label)
        before=len(w.getControl(100).items)
        with mock.patch('wizard_groups51.time.monotonic',side_effect=lambda:clock[0]),mock.patch('wizard_groups51.xbmcgui.ListItem',side_effect=make):w.pump()
        self.assertLessEqual(len(w.getControl(100).items)-before,2)

    def test_toggle_has_no_addon_query_reset_or_selection_movement(self):
        w=self.window;self.drain();control=w.getControl(100);control.selectItem(987)
        with mock.patch.object(sys.modules['xbmcaddon'],'Addon',side_effect=AssertionError('per-row metadata')),mock.patch.object(control,'reset',side_effect=AssertionError('reset')),mock.patch.object(control,'selectItem',side_effect=AssertionError('cursor')):
            w.onClick(100);self.assertEqual(self.draft.selected['live'],{'987'})
            w.onClick(100);self.assertEqual(self.draft.selected['live'],set())
        self.assertEqual(control.getSelectedPosition(),987)

    def test_bulk_is_bounded_and_cursors_survive_all_none(self):
        w=self.window;self.drain();control=w.getControl(100);control.selectItem(999)
        with mock.patch.object(w,'_item_state',wraps=w._item_state) as state:
            w.onClick(13);self.assertEqual(state.call_count,0);self.assertEqual(len(self.draft.selected['live']),1201)
            w.pump();self.assertLessEqual(state.call_count,32)
        self.drain();self.assertTrue(all(i.getProperty('setup_selected')=='true' for i in control.items))
        w.onClick(14);self.drain();self.assertTrue(all(i.getProperty('setup_selected')=='false' for i in control.items))
        self.assertEqual(control.getSelectedPosition(),999)

    def test_bulk_tab_switch_does_not_leave_stale_marks_or_change_other_selections(self):
        w=self.window;self.drain();w.onClick(13);w.pump();w.onClick(11);w.onClick(13)
        self.drain();w.onClick(10);self.drain()
        self.assertTrue(all(i.getProperty('setup_selected')=='true' for i in w.getControl(100).items))
        self.assertEqual(len(self.draft.selected['vod']),1201)

    def test_fast_tab_roundtrip_keeps_cursors_and_rejects_late_hidden_click(self):
        w=self.window;self.drain();w.getControl(100).selectItem(888);w.onClick(100)
        w.onClick(11);self.drain();w.getControl(101).selectItem(777);w.onClick(101)
        w.onClick(100);self.assertEqual(self.draft.selected['vod'],{'777'})
        w.onClick(12);self.drain();w.onClick(10)
        self.assertEqual(w.getControl(100).getSelectedPosition(),888);self.assertEqual(self.draft.selected['live'],{'888'})

    def test_cancel_mid_render_never_appends_late_rows(self):
        w=self.window;before=len(w.getControl(100).items);w.onAction(types.SimpleNamespace(getId=lambda:92))
        for _ in range(10):w.pump()
        self.assertEqual(len(w.getControl(100).items),before);self.assertTrue(w.cancel.is_set())
        self.draft.dispose.assert_called_once()

    def test_native_reinit_does_not_restart_discovery_or_reset_lists(self):
        w=self.window;before=list(w.getControl(100).items)
        with mock.patch.object(w,'_start_discovery',side_effect=AssertionError('duplicate discovery')):w.onInit()
        self.assertEqual(w.getControl(100).items,before)

    def test_only_owner_can_render_and_worker_results_never_access_controls(self):
        error=[]
        def wrong_thread():
            try:self.window._groups()
            except RuntimeError as exc:error.append(str(exc))
        t=threading.Thread(target=wrong_thread);t.start();t.join(1)
        self.assertEqual(error,['XM-SETUP-GUI-THREAD'])

    def test_zero_and_one_group_tabs_have_safe_focus_and_navigation(self):
        w=self.window;self.draft.categories['series']=[];self.draft.categories['vod']=self.draft.categories['vod'][:1]
        w.onClick(12);self.assertEqual(w.getFocusId(),17);self.assertTrue(w.getControl(6).visible)
        w.onClick(11);self.assertEqual(w.getFocusId(),101);w.onClick(101)
        self.assertEqual(self.draft.selected['vod'],{'0'})

    def test_m3u_reclassification_of_last_group_moves_focus_off_empty_list(self):
        w=self.window;self.draft.data['type']='m3u';self.draft.playlist='synthetic-staging.sqlite'
        self.draft.categories['live']=self.draft.categories['live'][:1];w._groups_loaded=False;w.render();w.setFocusId(100)
        self.draft.selected['live']={'0'};self.dialog.select.return_value=1
        with mock.patch('m3u_store.group') as move:w.onAction(types.SimpleNamespace(getId=lambda:117))
        move.assert_called_once();self.assertEqual(w.getFocusId(),17)
        self.assertFalse(w.getControl(100).visible);self.assertEqual(self.draft.selected['live'],set())

    def test_neutral_buttons_rows_and_progress_have_no_provider_artwork(self):
        tree=ET.parse(ADDON/'resources/skins/Default/720p/XCMateSetup.xml')
        for node in tree.findall(".//control[@type='button']"):
            self.assertTrue(node.findtext('texturefocus').endswith('wizard_plain51.png'))
            self.assertTrue(node.findtext('texturenofocus').endswith('wizard_plain51.png'))
            self.assertNotEqual(node.find('texturefocus').get('colordiffuse'),node.find('texturenofocus').get('colordiffuse'))
        for ident in ('100','101','102'):
            row=tree.find(".//control[@id='"+ident+"']")
            self.assertNotIn('lightweight_splash',ET.tostring(row).decode())
            self.assertIn('ListItem.Label',ET.tostring(row).decode())
        for field in ('texturebg','midtexture'):
            self.assertTrue(tree.findtext(".//control[@id='4']/"+field).endswith('wizard_plain51.png'))

    def test_markers_are_allowlisted_and_never_include_private_fields(self):
        trace=importlib.import_module('setup_trace');logs=[];xbmc=sys.modules['xbmc']
        with mock.patch.object(xbmc,'log',side_effect=lambda line,*a:logs.append(line),create=True),mock.patch.object(xbmc,'LOGINFO',1,create=True):
            trace.mark('GROUP_TOGGLE','synthetic-session',kind='live',total=4,password='synthetic-password',url='https://synthetic.invalid')
            trace.mark('untrusted synthetic-password')
        self.assertEqual(len(logs),1);self.assertIn('total=4',logs[0])
        for token in ('synthetic-session','synthetic-password','synthetic.invalid'):self.assertNotIn(token,logs[0])


class WorkerLifetime51(Fixture,unittest.TestCase):
    def test_lock_io_failure_is_not_reported_as_an_existing_worker(self):
        module=importlib.import_module('wizard_session51')
        with mock.patch.object(module.fcntl,'flock',side_effect=OSError('synthetic filesystem failure')):
            with self.assertRaises(OSError) as caught:module.acquire()
        self.assertNotIsInstance(caught.exception,module.Busy)
        release=module.acquire();release()

    def test_open_setup_retains_real_lease_after_back_until_delayed_discovery_finishes(self):
        ui=importlib.import_module('setup_window');session=importlib.import_module('wizard_session51')
        import setup_draft
        end=threading.Event();entered=threading.Event();windows=[]
        draft=types.SimpleNamespace(dispose=mock.Mock(),data={'type':'xtream'},categories={k:[] for k in ('live','vod','series')})
        def run(window):
            windows.append(window)
            def job():entered.set();end.wait(2)
            window.work(job,lambda value:self.fail('late apply'))
            self.assertTrue(entered.wait(1));window.close()
        with mock.patch.object(setup_draft,'Draft',return_value=draft),mock.patch.object(ui.SetupWindow,'run',run):
            try:
                self.assertIsNone(ui.open_setup({'type':'xtream'}))
                with self.assertRaises(session.Busy):session.acquire()
                draft.dispose.assert_not_called()
            finally:end.set();windows[0]._pool.shutdown(wait=True)
        draft.dispose.assert_called_once();release=session.acquire();release()

    def test_window_construction_failure_disposes_draft_and_releases_lease(self):
        ui=importlib.import_module('setup_window');session=importlib.import_module('wizard_session51')
        import setup_draft
        draft=types.SimpleNamespace(dispose=mock.Mock())
        with mock.patch.object(setup_draft,'Draft',return_value=draft),mock.patch.object(ui,'SetupWindow',side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):ui.open_setup({})
        draft.dispose.assert_called_once();release=session.acquire();release()

    def test_busy_reopening_never_constructs_another_draft(self):
        ui=importlib.import_module('setup_window');session=importlib.import_module('wizard_session51')
        import setup_draft
        release=session.acquire();self.addCleanup(release)
        with mock.patch.object(setup_draft,'Draft') as draft:
            with self.assertRaises(session.Busy):ui.open_setup({})
        draft.assert_not_called()

    def test_real_staged_save_reports_progress_and_keeps_existing_portal(self):
        import test_xcmate_setup_0294 as model
        fixture=model.StorageTests(methodName='runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
        fixture.draft.scan();updates=[]
        portal=fixture.draft.save(status=lambda *row:updates.append(row))
        self.assertTrue(fixture.draft.verification['portal']);self.assertTrue(any(row[0] is None for row in updates))
        self.assertEqual(fixture.portals.get_by_id('p'),fixture.portal)
        self.assertEqual(fixture.index.Reader(portal['id']).page('live',limit=1)[1],2400)

    def test_session_lease_blocks_reopening_until_cancelled_worker_cleanup(self):
        module=importlib.import_module('wizard_session51');release=module.acquire()
        self.addCleanup(release)
        with self.assertRaises(module.Busy):module.acquire()
        release();again=module.acquire();again()

    def test_session_lease_is_cross_process_and_never_removes_lock_inode(self):
        module=importlib.import_module('wizard_session51');release=module.acquire();self.addCleanup(release)
        filename=self.folder/'.wizard-worker51.lock';inode=filename.stat().st_ino
        code='import fcntl,sys; f=open(sys.argv[1]);\ntry: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\nexcept BlockingIOError: sys.exit(23)'
        result=subprocess.run([sys.executable,'-c',code,str(filename)],capture_output=True)
        self.assertEqual(result.returncode,23);release();self.assertEqual(filename.stat().st_ino,inode)

    def test_watchdog_releases_gui_and_late_job_cannot_apply_or_spawn_duplicate(self):
        ui=importlib.import_module('setup_window');session=importlib.import_module('wizard_session51')
        p=mock.patch.object(Control,'setPercent',lambda *a:None,create=True);p.start();self.addCleanup(p.stop)
        window=ui.WorkWindow('XCMateSetup.xml',str(ADDON),'Default','720p');window.configure_work()
        self.addCleanup(window._pool.shutdown,wait=True,cancel_futures=True)
        window._initialized=True;window.stage='discover';release=session.acquire()
        entered=threading.Event();end=threading.Event();applied=mock.Mock();cleaned=mock.Mock()
        def cleanup():cleaned();release()
        window._data_state.cleanup=cleanup
        def job():entered.set();end.wait(2);return 'late'
        window.work(job,applied);self.assertTrue(entered.wait(1))
        try:
            window._job_started-=36;window.pump();self.assertTrue(window._closed)
            self.dialog.ok.assert_called_once();cleaned.assert_not_called()
            with self.assertRaises(session.Busy):session.acquire()
        finally:end.set();window._pool.shutdown(wait=True)
        applied.assert_not_called();cleaned.assert_called_once();again=session.acquire();again()

    def test_watchdog_idle_budget_renews_on_real_worker_progress(self):
        ui=importlib.import_module('setup_window')
        p=mock.patch.object(Control,'setPercent',lambda *a:None,create=True);p.start();self.addCleanup(p.stop)
        w=ui.WorkWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure_work();self.addCleanup(w.close)
        w._initialized=True;w.stage='summary';end=threading.Event()
        w.work(lambda:end.wait(2),lambda value:None)
        try:
            w._data_state.progress_at-=179;w.status(None,'Synthetic progress');w.pump();self.assertFalse(w._closed)
        finally:end.set();w.close();w._pool.shutdown(wait=True)

    def test_auth_network_and_timeout_failures_are_distinct_and_redacted(self):
        ui=importlib.import_module('setup_window')
        cases=[(ValueError('authentication failed'),'XM-SETUP-AUTH'),(OSError('synthetic-password'),'XM-SETUP-NET'),(TimeoutError('synthetic-password'),'XM-SETUP-TIMEOUT')]
        for exc,expected in cases:
            code,message=ui._failure_details(exc);self.assertEqual(code,expected)
            self.assertNotIn('synthetic-password',message)
