"""Issue #38: real entry/router/profile/SQLite paths; Kodi calls alone modeled.

No main/portals/utils/DB facades: regressions must fail on the released 0.1.28.
These tests do not claim to reproduce the unidentified Android OS hang.
"""
import ast
import builtins
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

ADDON=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate'
LIB=ADDON/'resources/lib'


class BootTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.folder=Path(temp.name);self.profile=self.folder/'profile';self.profile.mkdir()
        self.options={};self.allow_legacy=False;self.logs=[];self.items=[];self.ends=[];self.calls=[]
        self.portal=dict(id='p',name='Saved account',type='xtream',enabled=True,
            xc_host='https://SECRET.invalid',xc_user='SECRET_USER',xc_pass='SECRET_PASS',
            start_stream_id='1',start_group_id='a',autoplay_start=False)
        self.portal_file=self.profile/'portals.json';self.portal_file.write_text(json.dumps([self.portal]))
        class ListItem:
            def addContextMenuItems(self,items,replaceItems=False):self.context=list(items)
            def __init__(inner,label='',path=''): inner.label=label;inner.props={}
            def setArt(inner,art): pass
            def setInfo(inner,kind,values): pass
            def setProperty(inner,k,v): inner.props[k]=v
        self.dialog=types.SimpleNamespace(notification=mock.Mock(),ok=mock.Mock(),yesno=mock.Mock(return_value=False))
        def setting(k):
            if k.startswith('playlist') and not self.allow_legacy:
                raise AssertionError('legacy settings on startup')
            return self.options.get(k,'')
        addon=types.SimpleNamespace(getAddonInfo=lambda k:dict(id='plugin.video.xtreammate',version='0.1.28.1',path=str(ADDON)).get(k,''),
            getSetting=setting,getLocalizedString=lambda ident:'',openSettings=mock.Mock())
        xbmc=types.ModuleType('xbmc');xbmc.LOGDEBUG=0;xbmc.LOGINFO=1;xbmc.LOGWARNING=2;xbmc.LOGERROR=3
        xbmc.log=lambda msg,*a,**kw:self.logs.append(msg);xbmc.executebuiltin=self.calls.append
        xbmc.Monitor=lambda:types.SimpleNamespace(abortRequested=lambda:False)
        xbmc.Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:False)
        gui=types.ModuleType('xbmcgui');gui.ListItem=ListItem;gui.Dialog=lambda:self.dialog;gui.NOTIFICATION_INFO='info'
        gui.Window=lambda *a:types.SimpleNamespace(setProperty=lambda *a:None,getProperty=lambda *a:'')
        plugin=types.ModuleType('xbmcplugin')
        plugin.setContent=lambda *a:None;plugin.setPluginCategory=lambda *a:None
        plugin.addDirectoryItem=lambda h,url,li,isFolder=True:self.items.append((h,url,li))
        plugin.endOfDirectory=lambda *a,**kw:self.ends.append((a,kw))
        vfs=types.ModuleType('xbmcvfs')
        vfs.translatePath=lambda p:p.replace('special://userdata/addon_data/plugin.video.xtreammate/',str(self.profile)+'/')
        # Local profile reads must not call Kodi VFS (e.g. disconnected cache).
        vfs.exists=mock.Mock(side_effect=AssertionError('VFS startup probe'))
        vfs.mkdirs=mock.Mock(side_effect=AssertionError('VFS startup write'))
        self.patch=mock.patch.dict(sys.modules);self.patch.start();self.addCleanup(self.patch.stop)
        for name,module in list(sys.modules.items()):
            file=getattr(module,'__file__',None)
            if file and str(LIB) in str(file): sys.modules.pop(name,None)
        sys.modules.update(xbmc=xbmc,xbmcgui=gui,xbmcplugin=plugin,xbmcvfs=vfs,
            xbmcaddon=types.SimpleNamespace(Addon=lambda *a:addon))
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        self.argv=mock.patch.object(sys,'argv',['plugin://plugin.video.xtreammate/','7','']);self.argv.start();self.addCleanup(self.argv.stop)
        spec=importlib.util.spec_from_file_location('boot_actual_default',ADDON/'default.py')
        self.entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.entry)

    def run_entry(self,action='root',handle=7):
        sys.argv=['plugin://plugin.video.xtreammate/',str(handle),'?action='+action]
        start=time.monotonic();self.entry.run()
        self.assertLess(time.monotonic()-start,2,'local start exceeded 2 seconds')

    def test_actual_entry_imports_no_http_epg_or_catalogue_and_reads_existing_profile_once(self):
        original=builtins.__import__;seen=[]
        def guarded(name,*a,**kw):
            if name.split('.')[0] in ('httpx','urllib.request','epg','xtream','library_index'):
                raise AssertionError('expensive import on startup: '+name)
            seen.append(name);return original(name,*a,**kw)
        before=self.portal_file.read_bytes()
        with mock.patch('builtins.__import__',side_effect=guarded): self.run_entry()
        self.assertEqual(len(self.items),6);self.assertEqual(len(self.ends),1)
        self.assertEqual(self.portal_file.read_bytes(),before)
        for phase in ('ARTWORK_PROFILE','HOME_FAST','HOME_PORTALS','PORTALS_LOAD','ROOT_MENU','HOME_MENU'):
            self.assertTrue(any(phase+'_BEGIN' in s for s in self.logs),phase)
            self.assertTrue(any(phase+'_DONE duration_ms=' in s for s in self.logs),phase)
        self.assertEqual(sum('PORTALS_LOAD_BEGIN' in s for s in self.logs),1)
        self.assertNotIn('SECRET','\n'.join(self.logs))

    def test_empty_profile_is_read_only_and_assistant_is_available_without_modal(self):
        self.portal_file.unlink();self.run_entry()
        self.assertTrue(any('setup_wizard' in u for _,u,_ in self.items))
        self.assertTrue(any('import_legacy_settings' in u for _,u,_ in self.items))
        self.assertFalse(self.portal_file.exists());self.assertEqual(len(self.ends),1)
        self.dialog.ok.assert_not_called()

    def test_corrupt_or_invalid_portals_fail_closed_without_migration_or_overwrite(self):
        for raw in (b'broken',b'{}',b'[null]',b'[{"id":"p"}]',b'x'*(4*1024*1024+1)):
            with self.subTest(raw_length=len(raw)):
                self.portal_file.write_bytes(raw);self.items.clear();self.ends.clear();self.logs.clear();self.run_entry()
                self.assertTrue(any('PORTALS_LOAD_FAILED' in s for s in self.logs))
                self.assertEqual(self.portal_file.read_bytes(),raw);self.assertFalse(self.items)
                self.assertEqual(self.ends,[((7,),dict(succeeded=False,cacheToDisc=False))])
        self.assertTrue(any('START_FAILED' in s for s in self.logs))

    def test_unreadable_portals_never_become_new_profile(self):
        portals=importlib.import_module('portals');before=self.portal_file.read_bytes()
        with mock.patch.object(portals.os,'open',side_effect=PermissionError('SECRET')): self.run_entry()
        self.assertFalse(self.items);self.assertEqual(len(self.ends),1)
        self.assertEqual(self.portal_file.read_bytes(),before);self.assertNotIn('SECRET','\n'.join(self.logs))

    @unittest.skipUnless(hasattr(os,'mkfifo'),'FIFO requires POSIX')
    def test_fifo_portal_file_is_rejected_without_blocking_open(self):
        self.portal_file.unlink();os.mkfifo(self.portal_file)
        # A subprocess timeout makes this regression fail instead of hanging
        # the test runner if blocking open() is accidentally restored.
        script="""import sys,types,importlib.util
sys.path.insert(0,sys.argv[1])
sys.modules['utils']=types.SimpleNamespace(addon_data_dir=lambda:sys.argv[2],error=lambda *a:None,info=lambda *a:None,debug=lambda *a:None)
sys.modules['xbmcvfs']=types.SimpleNamespace(exists=lambda p:True)
import portals
try: portals.load_all()
except RuntimeError: pass
else: raise AssertionError('FIFO accepted')
"""
        subprocess.run([sys.executable,'-B','-c',script,str(LIB),str(self.profile)],check=True,timeout=2,capture_output=True)
        self.assertTrue(self.portal_file.exists())

    def test_repeated_entry_and_restart_preserve_all_profile_files(self):
        for name in ('xtreammate_groups.json','favourites.json','epg_sources.json','resume.json','appearance.json','settings.xml'):
            (self.profile/name).write_bytes(('original-'+name).encode())
        before={p.name:p.read_bytes() for p in self.profile.iterdir()}
        for _ in range(6): self.run_entry()
        sys.modules.pop('main',None);sys.modules.pop('portals',None);self.run_entry()
        self.assertEqual(len(self.ends),7)
        self.assertEqual({p.name:p.read_bytes() for p in self.profile.iterdir() if p.name not in ('.artwork-config.lock','artwork_config_v1.json')},before)
        self.assertEqual(json.loads((self.profile/'artwork_config_v1.json').read_text())['mode'],'internal')

    def test_init_error_and_post_completion_error_finish_exactly_once(self):
        main=importlib.import_module('main');home=importlib.import_module('home_menu')
        with mock.patch.object(main.Router,'__init__',side_effect=RuntimeError('SECRET')): self.run_entry(action='settings')
        self.assertEqual(len(self.ends),1);self.ends.clear()
        real=home.show
        def fail_after(*args): real(*args);raise RuntimeError('SECRET')
        with mock.patch.object(home,'show',side_effect=fail_after): self.run_entry()
        self.assertEqual(len(self.ends),1);self.assertFalse(self.ends[0][1].get('succeeded') is False)
        self.assertNotIn('SECRET','\n'.join(self.logs));self.dialog.ok.assert_not_called()

    def test_main_import_failure_and_script_handle_close_safely(self):
        original=builtins.__import__
        def broken(name,*a,**kw):
            if name=='main': raise ImportError('SECRET')
            return original(name,*a,**kw)
        with mock.patch('builtins.__import__',side_effect=broken): self.run_entry(action='settings')
        self.assertEqual(len(self.ends),1);self.ends.clear()
        with mock.patch('builtins.__import__',side_effect=broken): self.run_entry(handle=-1)
        self.assertFalse(self.ends);self.assertNotIn('SECRET','\n'.join(self.logs))

    def test_root_does_not_touch_locked_epg_or_library_database_or_slow_provider(self):
        # Real SQLite exclusive locks stand in for ongoing imports in legacy
        # rollback-journal mode. Main menu needs neither database nor provider.
        locks=[]
        for name in ('guide_v1.sqlite','library_v1.sqlite'):
            db=sqlite3.connect(self.profile/name);db.execute('CREATE TABLE locked(x)');db.commit();db.execute('BEGIN EXCLUSIVE');locks.append(db)
        try:
            utils=importlib.import_module('utils')
            with mock.patch.object(utils,'http_get',side_effect=AssertionError('provider on root')):
                self.run_entry()
            self.assertEqual(len(self.items),6);self.assertEqual(len(self.ends),1)
        finally:
            for db in locks: db.close()

    def test_widget_lock_has_bounded_wait_and_root_still_opens(self):
        index=importlib.import_module('library_index');db=index.connect(write=True)
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.execute('PRAGMA journal_mode=DELETE');db.execute('BEGIN EXCLUSIVE')
        try:
            for action in ('widget_live_start_group','widget_recent_vod','widget_recent_series'):
                self.ends.clear();self.run_entry(action);self.assertEqual(len(self.ends),1)
                # .41: explicit temporarily-unavailable row, valid directory.
                self.assertTrue(self.ends[0][0][1])
            self.items.clear();self.ends.clear();self.run_entry();self.assertEqual(len(self.items),6)
        finally: db.close()

    def test_widget_expensive_query_is_interrupted_and_leaves_database_intact(self):
        index=importlib.import_module('library_index');db=index.connect(write=True)
        with db: db.executemany('INSERT INTO catalog VALUES(?,?,?,?)',[(str(i),'live','r',0) for i in range(50)])
        db.close();reader=index.Reader('p',timeout=.05,query_seconds=.02)
        start=time.monotonic()
        with self.assertRaises(index.IndexReadError):
            reader._query('SELECT SUM(a.updated+b.updated+c.updated+d.updated) FROM catalog a,catalog b,catalog c,catalog d')
        self.assertLess(time.monotonic()-start,.5)
        self.assertIsNone(reader.state('vod'))
        db=sqlite3.connect(index.path());self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok');db.close()

    def test_diagnostic_fields_reject_url_action_and_exception_text(self):
        boot=importlib.import_module('boot_diagnostics')
        boot.mark('ROUTE',action='https://SECRET.invalid')
        boot.mark('START_FAILED',error='SECRET')
        boot.mark('SECRET')
        self.assertNotIn('SECRET','\n'.join(self.logs));self.assertIn('action=OTHER',self.logs[0])


    def test_parallel_widgets_and_root_read_committed_data_during_real_wal_import(self):
        from concurrent.futures import ThreadPoolExecutor
        index=importlib.import_module('library_index');main=importlib.import_module('main')
        groups=[dict(category_id='a',category_name='Saved')]
        for kind,key in (('live','stream_id'),('vod','stream_id'),('series','series_id')):
            index.replace_catalog('p',kind,[{key:'1','name':'Stored '+kind,'category_id':'a'}],groups)
        vfs=sys.modules['xbmcvfs'];vfs.exists=os.path.exists
        def mkdirs(path): os.makedirs(path,exist_ok=True);return True
        vfs.mkdirs=mkdirs;vfs.delete=os.unlink;vfs.File=lambda p,mode='r':open(p,mode,encoding='utf-8')
        utils=importlib.import_module('utils')
        # A committed programme avoids short-EPG work and demonstrates real
        # local EPG data can coexist with an in-progress catalogue writer.
        epg=importlib.import_module('epg')
        epg._mem_set('p',{'1':[dict(name='Stored guide',start_timestamp=time.time()-60,stop_timestamp=time.time()+3600)]})
        db=index.connect(write=True);db.execute('BEGIN IMMEDIATE')
        db.execute("UPDATE titles SET title='Uncommitted' WHERE kind='vod'")
        try:
            actions=('root','widget_live_start_group','widget_recent_vod','widget_recent_series')*3
            with mock.patch.object(utils,'http_get',side_effect=AssertionError('widget network')), \
                 mock.patch.object(utils,'http_stream',side_effect=AssertionError('widget network')):
                def invoke(pair):
                    handle,action=pair
                    main.Router(['plugin://plugin.video.xtreammate/',str(handle),'?action='+action]).dispatch()
                started=time.monotonic()
                with ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(invoke,enumerate(actions,10)))
            self.assertLess(time.monotonic()-started,2)
            self.assertEqual(len(self.ends),12);self.assertEqual(len({a[0] for a,_ in self.ends}),12)
            for handle,action in enumerate(actions,10):
                rows=[li for h,_,li in self.items if h==handle]
                self.assertEqual(len(rows),6 if action=='root' else 1)
                self.assertTrue(all('Uncommitted' not in li.label for li in rows))
        finally: db.rollback();db.close()

    def test_duplicate_epg_worker_returns_instead_of_waiting_for_refresh_lock(self):
        epg=importlib.import_module('epg')
        epg._REFRESH_LOCK.acquire()
        try:
            started=time.monotonic()
            self.assertIsNone(epg._refresh_portal_epg('p',self.portal))
            self.assertLess(time.monotonic()-started,.5)
            self.items.clear();self.run_entry();self.assertEqual(len(self.items),6)
        finally: epg._REFRESH_LOCK.release()

    def test_active_epg_worker_receives_abort_and_root_is_independent(self):
        epg=importlib.import_module('epg');stream=importlib.import_module('stream_epg')
        entered=threading.Event();abort=threading.Event();finished=threading.Event();errors=[]
        sys.modules['xbmc'].Monitor=lambda:types.SimpleNamespace(abortRequested=abort.is_set)
        def slow_provider(portal,force=False,cancel=lambda:False):
            entered.set()
            while not cancel():
                if abort.wait(.01): break
            finished.set();return {}
        def work():
            try: epg._refresh_portal_epg('p',self.portal)
            except BaseException as exc: errors.append(exc)
        with mock.patch.object(stream,'refresh',side_effect=slow_provider):
            worker=threading.Thread(target=work);worker.start()
            try:
                self.assertTrue(entered.wait(1));self.run_entry();self.assertEqual(len(self.items),6)
            finally: abort.set();worker.join(1)
        self.assertFalse(worker.is_alive());self.assertTrue(finished.is_set());self.assertFalse(errors)

    def test_epg_transport_receives_cancellation_callback(self):
        from contextlib import contextmanager
        stream=importlib.import_module('stream_epg');utils=importlib.import_module('utils');seen=[]
        cancel=lambda:True
        @contextmanager
        def transport(uri,**kw): seen.append(kw);yield object()
        with mock.patch.object(utils,'http_stream',side_effect=transport):
            with stream.source_stream({'uri':'https://SECRET.invalid'},cancel=cancel): pass
        self.assertIs(seen[0]['cancel'],cancel)

    def test_explicit_legacy_import_finishes_directory_before_migration(self):
        main=importlib.import_module('main');portals=importlib.import_module('portals')
        self.portal_file.unlink()
        # Ordinary startup neither reads legacy settings nor writes portals.
        self.run_entry();self.ends.clear()
        def migrate(): self.assertEqual(len(self.ends),1)
        with mock.patch.object(portals,'import_from_settings',side_effect=migrate) as migration:
            self.run_entry('import_legacy_settings');migration.assert_called_once()
        self.assertEqual(len(self.ends),1)


    def test_explicit_legacy_migration_is_idempotent_for_all_portal_types(self):
        self.portal_file.unlink();self.allow_legacy=True
        self.options.update(playlist1_enabled='true',playlist1_type='0',playlist1_url='https://SECRET.invalid/list',
            playlist2_enabled='true',playlist2_type='2',playlist2_xc_host='https://SECRET.invalid',playlist2_xc_user='SECRET_USER',playlist2_xc_pass='SECRET_PASS',
            playlist3_enabled='true',playlist3_type='3',playlist3_stb_url='https://SECRET.invalid/c',playlist3_stb_mac='00:11:22:33:44:55')
        portals=importlib.import_module('portals');portals.import_from_settings()
        first=self.portal_file.read_bytes();portals.import_from_settings()
        self.assertEqual(self.portal_file.read_bytes(),first)
        self.assertEqual([p['type'] for p in portals.load_all()],['m3u','xtream','stb'])
        self.allow_legacy=False;self.run_entry();self.assertEqual(len(self.items),6)


if __name__=='__main__': unittest.main()
