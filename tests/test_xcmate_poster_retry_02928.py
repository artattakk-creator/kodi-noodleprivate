"""One selected poster: real queue/cache, same-record alternatives, finite retry."""
import importlib,json,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON

PNG=(ADDON/'resources/media/guide_focus_frame.png').read_bytes()


class PosterRetry28Tests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('art_errors','art_store','art_storage','artwork_db'):
            sys.modules.pop(name,None)
        self.art=importlib.import_module('media_art');self.store=importlib.import_module('art_store')
        self.url='https://image.invalid/primary.png?token=SECRET'
        self.alt='https://image.invalid/same-record.png';self.foreign='https://image.invalid/foreign.png'
        self.item=dict(sid='one',name='Same title',year='1992',cover=self.url,movie_image=self.alt,fanart='https://image.invalid/background.png')
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None;self.http.return_value=(PNG,{})

    def row(self,url):
        db=self.store.connect()
        try:
            row=db.execute('SELECT * FROM jobs WHERE ident=?',(self.store.key(url),)).fetchone()
            return dict(row) if row else None
        finally:db.close()

    def status(self,url,status,attempts=1,next_at=0):
        self.store.enqueue([url]);db=self.store.connect()
        with db:db.execute('UPDATE jobs SET status=?,attempts=?,next_at=? WHERE ident=?',(status,attempts,next_at,self.store.key(url)))
        db.close()

    def test_failed_primary_retries_only_same_record_alternative_and_persists_across_reload(self):
        self.status(self.url,'TIMEOUT',1,9999999999)
        foreign_path=self.art.fetch(self.foreign);foreign_row=self.row(self.foreign)
        self.http.reset_mock();self.art.request.reset_mock()
        self.assertEqual(self.art.retry_poster(self.item),'PENDING')
        self.assertEqual(self.art.sources(self.item)[0],self.alt)
        self.art.request.assert_called_once_with([dict(cover=self.alt)],priority=-20)
        self.assertEqual(self.row(self.url)['status'],'TIMEOUT')
        self.assertTrue(self.store.run_one());self.http.assert_called_once()
        self.assertEqual(self.http.call_args.args[0],self.alt)
        self.assertEqual(self.row(self.foreign),foreign_row);self.assertEqual(Path(foreign_path).read_bytes(),PNG)
        self.assertEqual(self.art.poster_report(self.item)['source_field'],'movie_image')
        self.art=importlib.reload(self.art)
        self.assertEqual(self.art.sources(self.item)[0],self.alt)
        self.assertEqual(Path(self.art.cached(self.alt)).read_bytes(),PNG)

    def test_working_cached_image_protected_without_http_or_queue_mutation(self):
        path=self.art.fetch(self.url);before=self.row(self.url);self.http.reset_mock();self.art.request.reset_mock()
        self.assertEqual(self.art.retry_poster(self.item),'READY')
        self.assertEqual(self.row(self.url),before);self.assertEqual(Path(path).read_bytes(),PNG)
        self.http.assert_not_called();self.art.request.assert_not_called()

    def test_stale_ready_row_without_file_is_actually_redownloaded(self):
        path=self.art.fetch(self.url);Path(path).unlink();self.http.reset_mock()
        self.assertEqual(self.store.retry_one(self.url),'PENDING')
        self.assertTrue(self.store.run_one());self.http.assert_called_once()
        self.assertEqual(Path(self.art.cached(self.url)).read_bytes(),PNG)

    def test_existing_worker_lease_and_server_cooldown_preserved(self):
        self.status(self.url,'RUNNING',1,9999999999)
        self.assertEqual(self.art.retry_poster(self.item),'RUNNING')
        self.assertIsNone(self.row(self.alt));self.http.assert_not_called()
        self.status(self.url,'HTTP_RATE_LIMIT',1,9999999999)
        self.assertEqual(self.art.retry_poster(dict(cover=self.url)),'WAIT')
        self.assertEqual(self.row(self.url)['next_at'],9999999999)
        self.art.request.assert_not_called()

    def test_no_source_and_ambiguous_title_never_find_an_unrelated_image(self):
        self.status(self.url,'HTTP_NOT_FOUND',3)
        self.status(self.foreign,'PENDING');before=self.row(self.foreign)
        item=dict(sid='two',name='Same title',year='1992',cover=self.url)
        self.assertEqual(self.art.retry_poster(item),'PENDING')
        self.art.request.assert_called_once_with([dict(cover=self.url)],priority=-20)
        self.assertEqual(self.art.sources(item)[0],self.url)
        self.assertEqual(self.art.retry_poster(dict(name='Same title')),'NO_SOURCE')
        self.http.assert_not_called();self.assertEqual(self.row(self.foreign),before)

    def test_busy_snapshot_does_not_mutate_queue_and_report_is_private(self):
        self.status(self.url,'TIMEOUT');before=self.row(self.url)
        with mock.patch.object(self.art,'_image_snapshot',return_value=({},'DB_BUSY')):
            self.assertEqual(self.art.retry_poster(self.item),'DB_BUSY')
        self.assertEqual(self.row(self.url),before);self.assertIsNone(self.row(self.alt))
        self.http.assert_not_called();self.art.request.assert_not_called()
        report=json.dumps(self.art.poster_report(self.item))
        for private in ('SECRET','https://','Same title'):self.assertNotIn(private,report)


if __name__=='__main__':unittest.main()
