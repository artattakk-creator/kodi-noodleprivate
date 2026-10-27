"""Original bytes/cache-key paths and bounded selected-poster recovery."""
import hashlib,importlib,json,os,socket,sqlite3,ssl,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError,URLError
from xcmate027_fixture import Fixture,ADDON,ROOT
PNG=(ADDON/'resources/media/guide_focus_frame.png').read_bytes()


class GraphicsTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('art_errors','art_store','art_storage','artwork_db','branding'):sys.modules.pop(name,None)
        self.errors=importlib.import_module('art_errors');self.store=importlib.import_module('art_store');self.art=importlib.import_module('media_art');self.db=importlib.import_module('artwork_db')
        self.url='https://image.invalid/aladdin1992.png?token=PRIVATE';self.other='https://image.invalid/aladdin2019.png'
        self.item=dict(sid='1992',kind='vod',name='Aladdin',year='1992',cover=self.url)
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None;self.http.return_value=(PNG,{})

    def row(self,url=None):
        db=self.store.connect()
        try:return dict(db.execute('SELECT * FROM jobs WHERE ident=?',(self.store.key(url or self.url),)).fetchone())
        finally:db.close()

    def fail(self,error,now=100):
        self.store.enqueue([self.url]);self.http.side_effect=error;self.store.run_one(now)
        return self.row()

    def test_original_icon_has_new_immutable_cache_key_and_runtime_report_is_private(self):
        import xml.etree.ElementTree as ET
        branding=importlib.import_module('branding');expected='81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135'
        icon=Path(branding.icon());self.assertNotEqual(icon.name,'icon.png');self.assertEqual(icon.read_bytes(),(ADDON/'icon.png').read_bytes())
        self.assertEqual(hashlib.sha256(icon.read_bytes()).hexdigest(),expected)
        manifest=ET.parse(ADDON/'addon.xml').getroot();self.assertEqual(manifest.findtext("extension[@point='xbmc.addon.metadata']/assets/icon"),icon.name)
        status=branding.inspect();self.assertEqual(status['packaged'],'ORIGINAL');self.assertNotIn(str(self.folder),json.dumps(status))

    def test_home_start_uses_original_branding_and_offline_diagnostic_route(self):
        import home_menu
        with mock.patch.object(self.router,'_add_dir',create=True,wraps=self.router._add_dir) as add:
            home_menu.show(self.router,self.portal)
        self.assertTrue(any(Path(li.art.get('icon','')).name=='tv.png' for _,li,_ in self.added))
        self.router._params.update(action='branding_status');self.routes.dispatch(self.router)
        self.dialog.textviewer.assert_called_once();self.http.assert_not_called()

    def test_http_failures_are_distinct_and_permanent_statuses_exhaust_once(self):
        for number,code in [(401,'HTTP_AUTH'),(403,'HTTP_AUTH'),(404,'HTTP_NOT_FOUND'),(410,'HTTP_NOT_FOUND'),(429,'HTTP_RATE_LIMIT'),(500,'HTTP_SERVER'),(400,'HTTP_CLIENT')]:
            with self.subTest(number=number):self.assertEqual(self.errors.classify(HTTPError(self.url,number,'PRIVATE',{},None)),code)
        row=self.fail(HTTPError(self.url,404,'PRIVATE',{},None));self.assertEqual(row['status'],'HTTP_NOT_FOUND');self.assertEqual(row['attempts'],3)
        self.assertFalse(self.store.run_one(99999));self.http.assert_called_once()
        self.assertNotIn('PRIVATE',str(self.art.diagnose(self.item)))

    def test_dns_tls_timeout_and_connection_do_not_expose_exception_text(self):
        for error,code in [(URLError(socket.gaierror('PRIVATE')),'DNS_ERROR'),(URLError(ssl.SSLError('PRIVATE')),'TLS_ERROR'),(TimeoutError('PRIVATE'),'TIMEOUT'),(ConnectionError('PRIVATE'),'CONNECTION_ERROR')]:
            self.assertEqual(self.errors.classify(error),code)

    def test_rate_limit_respects_server_cooldown_even_for_manual_retry(self):
        row=self.fail(HTTPError(self.url,429,'PRIVATE',{'Retry-After':'900'},None))
        self.assertEqual((row['status'],row['next_at']),('HTTP_RATE_LIMIT',1000))
        self.assertEqual(self.store.retry_one(self.url,200),'WAIT');self.assertFalse(self.store.run_one(999))
        self.assertEqual(self.store.retry_one(self.url,1000),'PENDING')

    def test_transient_failure_retries_are_finite_and_inner_http_retries_disabled(self):
        self.store.enqueue([self.url]);self.http.side_effect=TimeoutError('PRIVATE')
        for t in (100,200,500):self.assertTrue(self.store.run_one(t))
        self.assertEqual(self.row()['attempts'],3);self.assertFalse(self.store.run_one(10000))
        self.assertEqual(self.http.call_count,3);self.assertEqual(self.http.call_args.kwargs['retry_limit'],0)

    def test_explicit_retry_only_selected_asset_and_rate_limited_across_reloads(self):
        self.store.enqueue([self.url,self.other]);db=self.store.connect()
        with db:db.execute("UPDATE jobs SET status='NETWORK_ERROR',attempts=3")
        db.close();before=self.row(self.other)
        self.assertEqual(self.store.retry_one(self.url,100),'PENDING');self.assertEqual(self.row()['attempts'],0)
        self.assertEqual(self.row(self.other),before)
        store=importlib.reload(self.store);self.assertEqual(store.retry_one(self.url,110),'WAIT')

    def test_ready_image_and_ready_status_are_never_reset_by_retry(self):
        path=self.art.fetch(self.url);before=Path(path).read_bytes();row=self.row()
        self.assertEqual(self.store.retry_one(self.url,100),'READY');self.assertEqual(self.row(),row);self.assertEqual(Path(path).read_bytes(),before)

    def test_same_record_alternative_is_selected_after_permanent_error_without_title_lookup(self):
        alternative='https://image.invalid/other-1992.png';item=dict(self.item,movie_image=alternative)
        self.fail(HTTPError(self.url,404,'PRIVATE',{},None))
        report=self.art.diagnose(item);self.assertEqual(self.art.sources(item)[0],alternative)
        self.assertNotEqual(self.art.sources(dict(self.item,sid='2019',cover=self.other))[0],alternative)
        self.assertNotIn('PRIVATE',str(report));self.assertEqual(self.art.poster_report(item)['source_field'],'movie_image')
        self.art.request.assert_called()

    def test_legacy_exhausted_network_failure_can_select_existing_alternative(self):
        self.store.enqueue([self.url]);db=self.store.connect()
        with db:db.execute("UPDATE jobs SET status='NETWORK_ERROR',attempts=3")
        db.close();item=dict(self.item,cover_big='https://image.invalid/aladdin-1992-alt.png')
        self.art.diagnose(item);self.assertEqual(self.art.sources(item)[0],item['cover_big'])

    def test_selected_report_is_readonly_and_never_contains_urls_or_ids(self):
        self.store.enqueue([self.url]);before=Path(self.db.path()).read_bytes()
        report=self.art.poster_report(self.item)
        self.assertEqual(report['source_field'],'cover');self.assertEqual(report['candidate_count'],1)
        for secret in ['PRIVATE','https://','1992']:self.assertNotIn(secret,json.dumps(report))
        self.assertEqual(Path(self.db.path()).read_bytes(),before)

    def test_detail_retry_runs_in_worker_and_keeps_manual_next_and_play_actions(self):
        window=self.media_window();window._details(window.rows[0]);self.settle(window)
        self.assertIn('poster_status',[action for label,action in window.actions]);self.assertIn('play',[action for label,action in window.actions])
        window._poster_status();self.dialog.select.return_value=1
        with mock.patch.object(self.art,'retry_poster',return_value='PENDING') as retry:
            self.assertFalse(retry.called);self.settle(window);retry.assert_called_once()

    def test_missing_provider_source_is_not_a_network_failure(self):
        item=dict(name='Aladdin',year=1992,sid='1');self.assertEqual(self.art.diagnose(item)['poster'],'NO_SOURCE')
        self.assertEqual(self.art.retry_poster(item),'NO_SOURCE');self.http.assert_not_called()
