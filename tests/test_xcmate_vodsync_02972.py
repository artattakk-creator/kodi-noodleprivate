"""Issue #355: real Xtream HTTP, existing SQLite catalog, faults and cold reads."""
from contextlib import contextmanager
import errno
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import types
import unittest
from unittest import mock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from xcmate027_fixture import Fixture, LIB, ADDON, Control


def load_real(name):
    spec = importlib.util.spec_from_file_location(name, LIB / (name + '.py'))
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    return module


class VODSync72(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        xbmc = sys.modules['xbmc']
        for name in ('LOGDEBUG', 'LOGINFO', 'LOGWARNING', 'LOGERROR'): setattr(xbmc, name, 0)
        sys.modules['xbmcgui'].NOTIFICATION_INFO = 'info'
        self.logs = []; xbmc.log = lambda text, *args, **kw: self.logs.append(text)
        # Execute the actual urllib transport/encoding and stream decoder.
        spec = importlib.util.spec_from_file_location('transport72', LIB / 'utils.py')
        transport = importlib.util.module_from_spec(spec); spec.loader.exec_module(transport)
        transport.HAVE_HTTPX = False
        transport._default_headers = lambda: {}
        transport.setting_bool = lambda key, default=False: default
        sys.modules['utils'].http_get = transport.http_get
        sys.modules['utils'].http_stream = transport.http_stream
        for name, value in (('service_cancelled', lambda: False), ('service_timeout', lambda n: n)):
            p = mock.patch('network_io.' + name, value); p.start(); self.addCleanup(p.stop)
        load_real('xtream')
        self.pm = load_real('portals')
        self.api = importlib.import_module('vodsync_api72')
        self.engine = importlib.import_module('vodsync72')
        self.store = importlib.import_module('vodsync_store72')
        self.gs = importlib.import_module('group_selection')
        self.filename = self.index.path()
        db = self.index.connect(write=True)
        with db:
            for table in ('catalog', 'titles', 'groups', 'heads', 'items_v2'):
                db.execute("DELETE FROM " + table + " WHERE kind IN ('vod','series')")
        db.close()
        self.index.replace_catalog('p', 'live', [dict(stream_id=str(i), category_id=str(i % 53), name='Synthetic live ' + str(i)) for i in range(3357)],
                                   [dict(category_id=str(i), category_name='Synthetic group ' + str(i)) for i in range(53)])
        self.gs.save('p', [str(i) for i in range(53)], kind='live')
        self.gs.save('p', [], kind='vod'); self.gs.save('p', [], kind='series')
        self.requests = []; self.responses = {}
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self):
                q = parse_qs(urlsplit(self.path).query); action = q.get('action', ['AUTH'])[0]
                owner.requests.append((action, q.get('category_id', [''])[0], q.get('page', ['1'])[0]))
                if q.get('username') != [owner.portal['xc_user']] or q.get('password') != [owner.portal['xc_pass']]:
                    self.send_error(401); return
                value = owner.responses.get(action, [])
                if callable(value): value = value(q)
                code, data = value if isinstance(value, tuple) else (200, value)
                raw = data if isinstance(data, bytes) else json.dumps(data).encode()
                self.send_response(code); self.send_header('Content-Length', str(len(raw))); self.end_headers()
                try: self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        self.portal.update(xc_host='http://127.0.0.1:' + str(server.server_port), xc_user='synthetic &+ü', xc_pass='CANARY72 /+&=ü', include_vod=False, include_series=False)
        self.pm.save_all([self.portal])
        self.responses.update(AUTH={'user_info': {'auth': 1, 'status': 'Active'}},
            get_vod_categories=[dict(category_id='v', category_name='Synthetic movies')],
            get_series_categories=[dict(category_id='s', category_name='Synthetic series')],
            get_vod_streams=[dict(stream_id='m1', category_id='v', name='Synthetic movie', cover='https://images.example.test/poster.jpg')],
            get_series=[dict(series_id='s1', category_id='s', name='Synthetic series', cover='https://images.example.test/series.jpg')])
        self.publisher = mock.Mock(return_value=True)
        p = mock.patch.dict(sys.modules, widget_refresh45=types.SimpleNamespace(publish=self.publisher)); p.start(); self.addCleanup(p.stop)
        self.live_before = self.live_digest()
        self.guarded = {}
        for name in ('guide_v1.sqlite', 'xtreammate_epg_sources.json', 'tmdb_read_access_token.txt', 'favourites.json', 'guisettings.xml', 'keyboard.xml'):
            path = self.folder / name; path.write_bytes(b'SYNTHETIC_PRESERVE_' + name.encode()); self.guarded[name] = path.read_bytes()

    def live_digest(self):
        db = self.index.connect()
        try:
            values = [tuple(row) for row in db.execute("SELECT * FROM readable_titles WHERE pid='p' AND kind='live' ORDER BY sid")]
            groups = [tuple(row) for row in db.execute("SELECT * FROM groups WHERE pid='p' AND kind='live' ORDER BY cid")]
            return len(values), len(groups), hashlib.sha256(json.dumps([values, groups]).encode()).hexdigest()
        finally: db.close()

    def session(self, kinds=('vod', 'series')):
        s = self.engine.Session(self.pm.get_by_id('p'), kinds)
        self.addCleanup(s.close); s.discover()
        return s

    def run_scan(self, kinds=('vod', 'series')):
        s = self.session(kinds)
        return s, s.run({k: [g['category_id'] for g in s.groups[k]] for k in kinds})

    def assert_guarded(self):
        self.assertEqual(self.live_digest(), self.live_before)
        self.assertEqual(self.live_before[:2], (3357, 53))
        p = self.pm.get_by_id('p')
        for key, value in self.portal.items():
            if key not in ('include_vod', 'include_series'): self.assertEqual(p[key], value, key)
        self.assertEqual(len(self.pm.load_all()), 1)
        self.assertEqual(self.gs.load('p', 'live'), {str(i) for i in range(53)})
        for name, data in self.guarded.items(): self.assertEqual((self.folder / name).read_bytes(), data)
        self.assertFalse(any('live' in action or 'epg' in action for action, _, _ in self.requests))

    def test_vod02_real_http_existing_id_both_kinds_and_cold_subprocess(self):
        s, report = self.run_scan()
        self.assertEqual(report['state'], 'DONE', report)
        self.assertEqual(report['readback'], {'vod': 1, 'series': 1})
        script = """import json,sqlite3,sys
db=sqlite3.connect(sys.argv[1]); rows=db.execute("SELECT kind,count(*) FROM readable_titles WHERE pid='p' GROUP BY kind").fetchall()
assert dict(rows)=={'live':3357,'vod':1,'series':1};print('COLD_OK')
"""
        child = subprocess.run([sys.executable, '-c', script, self.filename], capture_output=True, text=True, check=True)
        self.assertEqual(child.stdout.strip(), 'COLD_OK'); self.assertEqual(child.stderr, '')
        self.assertEqual(self.index.Reader('p').page('vod', limit=1)[0][0]['sid'], 'm1')
        self.assert_guarded()

    def test_vod03_film_only_then_series_only_zero_live_epg_requests(self):
        a, r = self.run_scan(('vod',)); a.close()
        self.assertEqual(r['readback'], {'vod': 1}); self.assertNotIn('get_series_categories', [a for a, _, _ in self.requests])
        b, r = self.run_scan(('series',)); b.close()
        self.assertEqual(r['readback'], {'series': 1}); self.assert_guarded()

    def test_vod01_empty_categories_not_inferred_provider_absence_or_success(self):
        self.responses.update(get_vod_categories=[], get_series_categories=[])
        s = self.session(); self.assertEqual(s.errors, {'vod': 'SOURCE_EMPTY', 'series': 'SOURCE_EMPTY'})
        with self.assertRaisesRegex(self.api.SyncError, 'NO_SELECTION'): s.run({})
        self.assert_guarded()

    def test_vod01_explicit_remote_adapter_bypasses_stale_empty_cache(self):
        adapter = importlib.import_module('source_adapters').for_portal(self.portal)
        with mock.patch.object(sys.modules['utils'], 'cache_get', return_value=[]):
            self.assertEqual(adapter.categories('vod', remote=True)[0]['category_id'], 'v')
        self.assertIn(('get_vod_categories', '', '1'), self.requests)

    def test_vod04_known_wrapper_and_two_pages(self):
        self.responses['get_vod_categories'] = {'data': {'items': self.responses['get_vod_categories']}}
        def pages(q):
            n = int(q.get('page', ['1'])[0])
            return dict(data=[dict(stream_id='m'+str(n), category_id='v', name='Movie '+str(n))], pagination=dict(page=n, total_pages=2, total=2))
        self.responses['get_vod_streams'] = pages
        s, report = self.run_scan(('vod',))
        self.assertEqual(report['readback']['vod'], 2, report)
        self.assertEqual([page for a, _, page in self.requests if a == 'get_vod_streams'], ['1', '2']); self.assert_guarded()

    def test_vod04_category_fault_matrix_never_becomes_empty_success(self):
        variants = [(b'<html>failed</html>', 'SCHEMA'), ({'unknown': []}, 'SCHEMA'), ({'error': 'private server error'}, 'API_ERROR'),
                    ((401, b'denied'), 'AUTH'), ((403, b'denied'), 'FORBIDDEN'), ((429, b'retry'), 'RATE_LIMIT'),
                    ((404, b'missing'), 'ENDPOINT_MISSING'), ((500, b'failed'), 'HTTP'),
                    ([dict(category_name='Missing identity')], 'IDENTITY'),
                    ([dict(category_id='v', category_name='One'), dict(category_id='v', category_name='Two')], 'DUPLICATE_ID')]
        for value, code in variants:
            with self.subTest(code=code):
                self.responses['get_vod_categories'] = value
                s = self.session(('vod',)); self.assertEqual(s.errors['vod'], code); s.close()
                self.assertEqual(self.index.Reader('p').page('vod')[1], 0); self.assert_guarded()

    def test_vod04_user_specific_disabled_has_separate_code(self):
        self.responses['AUTH'] = {'user_info': dict(auth=1, status='Active', vod_enabled=0, series_enabled=False)}
        s = self.session()
        self.assertEqual(s.errors, dict(vod='VOD_DISABLED', series='SERIES_DISABLED'))
        self.assertEqual(self.requests, [('AUTH', '', '1')]); self.assert_guarded()

    def test_vod04_invalid_titles_after_256_rows_keep_entire_old_group(self):
        bad = [dict(stream_id=str(i), category_id='v', name='New '+str(i)) for i in range(270)]
        for ending, code in (({}, 'IDENTITY'), (dict(stream_id='0', category_id='v', name='Duplicate'), 'DUPLICATE_ID')):
            self.responses['get_vod_streams'] = bad + [ending]
            s, r = self.run_scan(('vod',)); self.assertEqual(r['state'], 'FAILED', r)
            self.assertEqual(r['errors'][0]['code'], code); self.assertEqual(r['readback']['vod'], 0); s.close(); self.assert_guarded()

    def test_vod04_truncated_body_after_full_batch_never_publishes(self):
        raw = json.dumps([dict(stream_id=str(i), category_id='v', name='Movie '+str(i)) for i in range(270)]).encode()[:-3]
        self.responses['get_vod_streams'] = raw
        s, r = self.run_scan(('vod',)); self.assertEqual(r['state'], 'FAILED', r)
        self.assertEqual(r['readback']['vod'], 0); self.assert_guarded()

    def test_vod04_total_mismatch_and_repeat_page_never_commit(self):
        for value, code in ((dict(data=self.responses['get_vod_streams'], total=7), 'PARTIAL_RESPONSE'),
                            (dict(data=self.responses['get_vod_streams'], page=1, total_pages=2), 'DUPLICATE_ID')):
            self.responses['get_vod_streams'] = value
            s, r = self.run_scan(('vod',)); self.assertEqual(r['state'], 'FAILED', r)
            self.assertIn(r['errors'][0]['code'], (code, 'PAGINATION')); s.close()
            self.assertEqual(self.index.Reader('p').page('vod')[1], 0); self.assert_guarded()

    def test_vod05_repeat_incremental_changes_and_missing_titles_retained(self):
        s, r = self.run_scan(('vod',)); self.assertEqual(r['new'], 1, r)
        r = s.run({'vod': ['v']}); self.assertEqual((r['new'], r['changed'], r['unchanged']), (0, 0, 1), r)
        self.responses['get_vod_streams'][0]['name'] = 'Updated title'
        self.responses['get_vod_streams'].append(dict(stream_id='m2', category_id='v', name='Second'))
        r = s.run({'vod': ['v']}); self.assertEqual((r['new'], r['changed']), (1, 1), r)
        self.responses['get_vod_streams'] = [dict(stream_id='m2', category_id='v', name='Second')]
        r = s.run({'vod': ['v']}); self.assertEqual(r['readback']['vod'], 2)
        self.assertEqual(self.index.Reader('p').get('vod', 'm1')['name'], 'Updated title'); self.assert_guarded()

    def test_vod05_empty_response_preserves_existing_published_group(self):
        s, r = self.run_scan(('vod',)); self.responses['get_vod_streams'] = []
        r = s.run({'vod': ['v']}); self.assertEqual(r['state'], 'FAILED', r)
        self.assertEqual(r['errors'][0]['code'], 'SOURCE_EMPTY'); self.assertEqual(r['readback']['vod'], 1); self.assert_guarded()

    def test_vod05_missing_provider_artwork_retains_persistent_reference(self):
        s, _ = self.run_scan(('vod',)); self.responses['get_vod_streams'][0]['cover'] = ''
        r = s.run({'vod': ['v']}); self.assertEqual(r['unchanged'], 1, r)
        self.assertEqual(self.index.Reader('p').get('vod', 'm1')['cover'], 'https://images.example.test/poster.jpg'); self.assert_guarded()

    def test_vod06_cancel_in_staging_retains_old_heads_and_selection(self):
        s = self.session(('vod',)); stopped = threading.Event()
        self.responses['get_vod_streams'] = [dict(stream_id=str(i), category_id='v', name='New') for i in range(600)]
        old = (self.folder / 'xtreammate_groups.json').read_bytes()
        def status(percent, value):
            if value.get('read', 0) >= 256: stopped.set()
        r = s.run({'vod': ['v']}, stopped.is_set, status)
        self.assertEqual(r['state'], 'CANCELLED', r); self.assertEqual(r['readback']['vod'], 0)
        self.assertEqual((self.folder / 'xtreammate_groups.json').read_bytes(), old); self.assert_guarded()

    def test_vod06_backup_failure_blocks_any_import_or_activation(self):
        s = self.session(('vod',)); old = (self.folder / 'xtreammate_groups.json').read_bytes()
        with mock.patch.object(self.store, 'backup', side_effect=OSError(errno.ENOSPC, 'CANARY72 private.invalid')):
            with self.assertRaises(OSError): s.run({'vod': ['v']})
        self.assertFalse(any(a == 'get_vod_streams' for a, _, _ in self.requests))
        self.assertEqual(self.index.Reader('p').page('vod')[1], 0); self.assertEqual((self.folder / 'xtreammate_groups.json').read_bytes(), old); self.assert_guarded()

    def test_vod06_reserve_and_readonly_during_stage_do_not_publish(self):
        for number in (errno.ENOSPC, errno.EROFS):
            s = self.session(('vod',))
            original = importlib.import_module('import_budget').check_space
            def fail(path, upcoming=0):
                if str(path) == self.filename and upcoming: raise OSError(number, 'CANARY72')
                return original(path, upcoming)
            with mock.patch('import_budget.check_space', side_effect=fail): r = s.run({'vod': ['v']})
            self.assertEqual(r['state'], 'FAILED', r); self.assertEqual(r['readback']['vod'], 0); s.close(); self.assert_guarded()

    def test_vod06_no_concurrent_scan_or_service_writer(self):
        s = self.session()
        with self.assertRaisesRegex(self.api.SyncError, 'BUSY'): self.engine.Session(self.portal)
        worker = importlib.import_module('catalog_delta52').serial_worker(lambda: 'SHOULD_NOT_RUN')
        self.assertFalse(worker()); self.assert_guarded()

    def test_vod06_sqlite_lock_has_no_visible_partial_group_and_can_retry(self):
        s = self.session(('vod',)); blocker = sqlite3.connect(self.filename)
        blocker.execute('BEGIN IMMEDIATE')
        try:
            r = s.run({'vod': ['v']})
            self.assertEqual(r['state'], 'FAILED', r); self.assertEqual(r['errors'][0]['code'], 'SQLITE')
            self.assertEqual(r['readback']['vod'], 0)
        finally: blocker.rollback(); blocker.close()
        r = s.run({'vod': ['v']}); self.assertEqual(r['readback']['vod'], 1, r); self.assert_guarded()

    def test_vod06_real_process_hard_kill_after_staging_batch_then_resume(self):
        s = self.session(('vod',))
        script = r'''import os,sys,types
sys.path.insert(0,sys.argv[1]); folder=sys.argv[2]
sys.modules['utils']=types.SimpleNamespace(addon_data_dir=lambda:folder)
import vodsync_api72 as api
api.iterate=lambda *a,**k:iter([dict(stream_id='crash'+str(i),category_id='v',name='Synthetic') for i in range(600)])
from vodsync_store72 import upsert
session=types.SimpleNamespace(pid='p',filename=folder+'/library_v1.sqlite',account=sys.argv[3],client=None,heartbeat=lambda db:None)
def stop(n,value):
 if value.get('read',0)>=256:os._exit(77)
upsert(session,'vod',dict(category_id='v',category_name='Synthetic'),lambda:False,stop)
'''
        child = subprocess.run([sys.executable, '-c', script, str(LIB), str(self.folder), s.account], capture_output=True)
        self.assertEqual(child.returncode, 77, child.stderr.decode()); self.assertEqual(child.stdout, b'')
        self.assertEqual(self.index.Reader('p').page('vod')[1], 0)
        r = s.run({'vod': ['v']}); self.assertEqual(r['state'], 'DONE', r)
        self.assertEqual(r['readback']['vod'], 1); self.assertIsNone(self.index.Reader('p').get('vod', 'crash1')); self.assert_guarded()

    def test_vod06_committed_receipt_recovers_activation_without_redownload(self):
        s = self.session(('vod',)); activate = s.activate
        with mock.patch.object(s, 'activate', side_effect=OSError(errno.EROFS, 'CANARY72')):
            r = s.run({'vod': ['v']})
        self.assertEqual(r['state'], 'FAILED', r); self.assertFalse(self.pm.get_by_id('p')['include_vod'])
        before = self.requests.count(('get_vod_streams', 'v', '1'))
        r = s.run({'vod': ['v']}); self.assertEqual(r['state'], 'DONE', r)
        self.assertEqual(r['readback']['vod'], 1); self.assertEqual(self.requests.count(('get_vod_streams', 'v', '1')), before); self.assert_guarded()

    def test_vod07_zero_to_nonzero_selection_and_unselected_groups_preserved(self):
        self.responses['get_vod_categories'].append(dict(category_id='v2', category_name='Not chosen'))
        s = self.session(('vod',)); r = s.run({'vod': ['v']})
        self.assertEqual(r['groups_found']['vod'], 2); self.assertEqual(r['groups_selected']['vod'], 1)
        self.assertEqual(self.gs.load('p', 'vod'), {'v'})
        self.assertFalse(any(cid == 'v2' for a, cid, _ in self.requests)); self.assert_guarded()

    def test_vod07_no_selection_or_cancel_never_changes_existing_profile(self):
        before = {p.name: p.read_bytes() for p in self.folder.glob('*.json')}
        s = self.session()
        with self.assertRaisesRegex(self.api.SyncError, 'NO_SELECTION'): s.run({})
        for name, raw in before.items(): self.assertEqual((self.folder / name).read_bytes(), raw)
        self.assert_guarded()

    def test_vod07_first_discovery_preselects_all_but_explicit_none_stays_none(self):
        from vodsync_ui72 import preselected
        rows = [dict(category_id='v', category_name='Synthetic')]
        self.assertEqual(preselected('p', 'vod', rows), [0])
        self.gs.save('p', [], kind='vod', known=['v'])
        self.assertEqual(preselected('p', 'vod', rows), [])

    def test_vod07_provider_ignores_category_does_not_modify_other_group(self):
        self.responses['get_vod_streams'].append(dict(stream_id='foreign', category_id='unselected', name='Other'))
        s, r = self.run_scan(('vod',)); self.assertEqual(r['skipped'], 1, r)
        self.assertEqual(r['readback']['vod'], 1); self.assertIsNone(self.index.Reader('p').get('vod', 'foreign')); self.assert_guarded()

    def test_vod08_backup_scoped_verified_private_and_restore_on_isolated_copy(self):
        s, r = self.run_scan(('vod',))
        self.responses['get_vod_streams'].append(dict(stream_id='m2', category_id='v', name='Second'))
        s.run({'vod': ['v']}); meta = self.store.verify_backup(s.backup)
        self.assertFalse(meta['credentials']); self.assertEqual(meta['kinds'], ['vod'])
        raw = Path(s.backup + '.json').read_bytes(); self.assertNotIn(b'CANARY72', raw); self.assertNotIn(self.portal['xc_host'].encode(), raw)
        db = sqlite3.connect(s.backup)
        try:
            restored = self.folder / 'isolated-restored.sqlite'
            copy = sqlite3.connect(restored); db.backup(copy)
            self.assertEqual(copy.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(copy.execute('SELECT count(*) FROM titles').fetchone()[0], 1)
            self.assertEqual(copy.execute("SELECT count(*) FROM titles WHERE kind='live'").fetchone()[0], 0); copy.close()
        finally: db.close()
        self.assertEqual(self.index.Reader('p').page('vod')[1], 2); self.assert_guarded()

    def test_vod08_safe_diagnostics_never_echo_credentials_or_exception_urls(self):
        s = self.session(('vod',)); self.engine.emit(s, 'FAILED', 'vod', error=OSError(errno.EACCES, 'CANARY72 https://private.invalid/token'))
        from vodsync_ui72 import describe
        text = describe(self.api.failure(OSError(errno.EACCES, 'CANARY72 private.invalid')).code)
        joined = '\n'.join(self.logs) + text
        for secret in ('CANARY72', 'private.invalid', '127.0.0.1', self.portal['xc_user'], self.portal['xc_pass']): self.assertNotIn(secret, joined)

    def test_vod08_corrupt_backup_blocks_retry_before_new_provider_request(self):
        s, r = self.run_scan(('vod',)); count = len(self.requests)
        with open(s.backup, 'ab') as stream: stream.write(b'corrupt')
        with self.assertRaisesRegex(self.api.SyncError, 'BACKUP_VERIFY'): s.run({'vod': ['v']})
        self.assertEqual(len(self.requests), count); self.assertEqual(self.index.Reader('p').page('vod')[1], 1); self.assert_guarded()

    def test_vod09_only_media_widgets_are_refreshed(self):
        s, r = self.run_scan()
        self.assertEqual({call.args[1] for call in self.publisher.call_args_list}, {'vod', 'series'})
        self.assert_guarded()

    def test_vod09_media_owner_reads_new_titles_without_skin_dependency(self):
        s, r = self.run_scan(('vod',))
        self.portal.update(self.pm.get_by_id('p'))
        w = self.media_window('vod')
        self.assertTrue(any('Synthetic movie' in item.label for item in w.getControl(110).items))
        self.assert_guarded()

    def test_vod04_timeout_tls_and_transport_errors_are_safe_and_distinct(self):
        for error, code in ((TimeoutError('CANARY72 URL'), 'TIMEOUT'), (ConnectionResetError('CANARY72 URL'), 'NETWORK')):
            s = self.session(('vod',))
            with mock.patch.object(sys.modules['utils'], 'http_stream', side_effect=error): r = s.run({'vod': ['v']})
            self.assertEqual(r['errors'][0]['code'], code); self.assertNotIn('CANARY72', json.dumps(r)); s.close(); self.assert_guarded()

    def test_vod05_own_obsolete_generations_do_not_accumulate(self):
        s, r = self.run_scan(('vod',))
        for _ in range(4): s.run({'vod': ['v']})
        db = self.index.connect()
        try: self.assertEqual(db.execute("SELECT count(*) FROM items_v2 WHERE pid='p' AND kind='vod'").fetchone()[0], 1)
        finally: db.close()
        self.assert_guarded()

    def test_vod09_actual_window_owner_completion_result_and_back(self):
        from concurrent.futures import wait
        from setup_window import WorkWindow
        import vodsync_ui72
        owner = threading.get_ident(); calls = []
        original = Control.setText
        def guard(control, text):
            self.assertEqual(threading.get_ident(), owner); calls.append(text); return original(control, text)
        self.dialog.yesno.return_value = True
        def drive(window):
            window.show(); self.assertTrue(wait([window._future], timeout=5).done); window.pump()
            self.assertEqual(window.stage, 'ready'); self.assertEqual(window.getFocusId(), 16)
            window.onClick(16); self.assertTrue(wait([window._future], timeout=5).done); window.pump()
            self.assertEqual(window.report['state'], 'DONE', window.report); self.assertEqual(window.getFocusId(), 17)
            window.onClick(17); window.native(92); window._pool.shutdown(wait=True)
            self.assertTrue(window._data_state.disposed)
        with mock.patch.object(WorkWindow, 'run', drive), mock.patch.object(Control, 'setText', guard), mock.patch.object(Control, 'setPercent', lambda c, p: None, create=True), mock.patch('menu_icons45.multiselect', side_effect=[[0, 1], [0], [0]]):
            vodsync_ui72.show(self.pm.get_by_id('p'))
        self.assertTrue(any('DB-Readback' in text for text in calls)); self.assert_guarded()

    def test_vod09_close_during_discovery_retains_lock_until_worker_stops(self):
        from setup_window import WorkWindow
        import vodsync_ui72
        started = threading.Event(); release = threading.Event()
        def delayed(q):
            started.set(); release.wait(3)
            return [dict(category_id='v', category_name='Synthetic')]
        self.responses['get_vod_categories'] = delayed
        def drive(window):
            window.show(); self.assertTrue(started.wait(3))
            window.native(92); self.assertTrue(window._closed)
            with self.assertRaisesRegex(self.api.SyncError, 'BUSY'): self.engine.Session(self.pm.get_by_id('p'))
            release.set(); window._pool.shutdown(wait=True)
            self.assertTrue(window._data_state.disposed)
            retry = self.engine.Session(self.pm.get_by_id('p')); retry.close()
        with mock.patch.object(WorkWindow, 'run', drive), mock.patch.object(Control, 'setPercent', lambda c, p: None, create=True), mock.patch('menu_icons45.multiselect', return_value=[0]):
            vodsync_ui72.show(self.pm.get_by_id('p'))
        self.assertEqual(self.index.Reader('p').page('vod')[1], 0); self.assert_guarded()


class WizardWarning72(unittest.TestCase):
    def test_53_0_0_requires_explicit_live_only_confirmation(self):
        from test_xcmate_setup_02971 import Setup71
        m = Setup71('runTest'); m.setUp(); self.addCleanup(m.doCleanups)
        m.d.adapter.categories = lambda kind, remote: [dict(category_id=str(i), category_name='Synthetic') for i in range(53)] if kind == 'live' else []
        m.m.dialog.yesno.return_value = False
        w = m.window(); m.finish(w); m.finish(w)
        self.assertTrue(w._closed); self.assertIsNone(w.result)
        self.assertEqual(m.m.portals.load_all(), [m.m.portal])
        m.m.dialog.yesno.assert_called_once()
        self.assertIn('SOURCE_EMPTY', m.m.dialog.yesno.call_args.args[1])

    def test_vod_api_fault_is_diagnosed_before_explicit_live_only_choice(self):
        from test_xcmate_setup_02971 import Setup71
        m = Setup71('runTest'); m.setUp(); self.addCleanup(m.doCleanups)
        from vodsync_api72 import SyncError
        def categories(kind, remote):
            if kind == 'vod': raise SyncError('API_ERROR')
            return [dict(category_id='1', category_name='Synthetic')] if kind == 'live' else []
        m.d.adapter.categories = categories; m.m.dialog.yesno.return_value = True
        w = m.window(); m.finish(w); m.finish(w)
        self.assertEqual(w.stage, 'groups'); self.assertIn('API_ERROR', m.m.dialog.yesno.call_args.args[1])
        self.assertIsNone(w.result)


if __name__ == '__main__': unittest.main(verbosity=2)
