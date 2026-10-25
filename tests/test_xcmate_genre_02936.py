"""Genre aliases, additive/resumable migration, active revisions and unchanged UI."""
import importlib
import json
import sqlite3
import sys
import time
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class Genre36(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.genre=importlib.import_module('genre_search')
        self.genre._retry.clear();self.genre._offset=0
        self.entries=[dict(stream_id='1',series_id='1',category_id='a',name='Distant Worlds',genre='Science Fiction / Drama'),
                      dict(stream_id='2',series_id='2',category_id='a',name='Sci-Fi',genre='Sci-Fi'),
                      dict(stream_id='3',series_id='3',category_id='a',name='Western Journey',genre='Adventure'),
                      dict(stream_id='4',series_id='4',category_id='a',name='Blue Horizon',genre=['Western','Thriller']),
                      dict(stream_id='5',series_id='5',category_id='b',name='Blue 2024',genre='Sci Fi'),
                      dict(stream_id='6',series_id='6',category_id='a',name='Missing metadata',category_name='Western',year=2024),
                      dict(stream_id='7',series_id='7',category_id='a',name='No invented genre',genre='Fictional Westernized')]
        for kind in ('vod','series'):self.index.replace_catalog('p',kind,self.entries,self.catalogs['get_vod_categories'])

    def ready(self,pid='p',kind='vod'):
        for _ in range(1000):
            if not self.genre.advance(pid,kind):return
        self.fail('genre indexing did not converge')

    def page(self,query,kind='vod',**kw):return self.index.Reader('p').page(kind,query,**kw)

    def test_genre_only_metadata_matches_and_exact_title_precedes_genre(self):
        self.ready();rows,total=self.page('Sci-Fi')
        self.assertEqual([r['sid'] for r in rows],['2','1','5']);self.assertEqual(total,3)
        self.assertEqual(rows[1]['genre'],'Science Fiction / Drama')

    def test_hyphen_space_science_fiction_aliases_and_series_share_semantics(self):
        self.ready();self.ready(kind='series')
        for query in ('Sci-Fi','sci fi','Science Fiction','Science-Fiction','SCI FI'):
            for kind in ('vod','series'):
                rows,_=self.page(query,kind)
                self.assertEqual({r['sid'] for r in rows},{'1','2','5'})

    def test_western_title_first_no_duplicate_and_no_category_or_substring_invention(self):
        self.ready();rows,total=self.page('Western')
        self.assertEqual([r['sid'] for r in rows],['3','4']);self.assertEqual(total,2)
        self.assertNotIn('6',{r['sid'] for r in rows});self.assertNotIn('7',{r['sid'] for r in rows})

    def test_mixed_genre_and_title_uses_and_without_promoting_metadata_year(self):
        self.ready();rows,_=self.page('Sci-Fi 2024');self.assertEqual([r['sid'] for r in rows],['5'])
        self.assertEqual(self.page('Western Blue')[0][0]['sid'],'4')
        self.assertEqual(self.page('Western Thriller')[0][0]['sid'],'4')
        self.assertEqual(self.page('Sci-Fi 1999')[0],[])

    def test_conservative_accent_aliases_and_whole_token_matching(self):
        self.assertEqual(self.genre.terms('Komödie, Krimi / Action'),['action','comedy','crime'])
        self.assertEqual(self.genre.terms('Science Fictional / Westernized'),[])
        self.assertEqual(self.genre.terms(None),[])
        self.assertEqual(self.genre.terms({'genre':'Western'}),[])

    def test_active_groups_portal_and_kind_are_enforced(self):
        self.ready();self.ready(kind='series')
        self.index.replace_catalog('other','vod',[dict(stream_id='9',category_id='a',name='Other',genre='Sci-Fi')],self.catalogs['get_vod_categories'])
        self.ready(pid='other');importlib.import_module('group_selection').save('p',{'a'},kind='vod')
        rows,_=self.page('Sci-Fi');self.assertEqual({r['sid'] for r in rows},{'1','2'})
        self.assertEqual({r['sid'] for r in self.page('Sci-Fi','series')[0]},{'1','2','5'})

    def test_reader_never_creates_tables_or_backfills_on_query(self):
        db=self.index.connect();before=list(db.execute("SELECT name,sql FROM sqlite_master ORDER BY name"));db.close()
        with mock.patch.object(self.genre,'advance',side_effect=AssertionError('writer on query')):
            rows,total=self.page('Sci-Fi')
        self.assertEqual([r['sid'] for r in rows],['2'])
        db=self.index.connect();self.assertEqual(before,list(db.execute("SELECT name,sql FROM sqlite_master ORDER BY name")));db.close()

    def test_migration_only_adds_derived_tables_and_preserves_all_source_records(self):
        db=self.index.connect();tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        def snapshot(db):return {name:[tuple(r) for r in db.execute('SELECT * FROM '+name)] for name in tables}
        before=snapshot(db);schema=[tuple(r) for r in db.execute("SELECT name,sql FROM sqlite_master")];db.close()
        self.ready();self.ready(kind='series')
        db=self.index.connect();self.assertEqual(before,snapshot(db))
        after={r[0]:r[1] for r in db.execute("SELECT name,sql FROM sqlite_master")}
        for name,sql in schema:self.assertEqual(after[name],sql)
        db.close()

    def test_cancel_rolls_back_tables_terms_and_checkpoint(self):
        calls=[0]
        def cancelled():calls[0]+=1;return calls[0]>=3
        self.assertFalse(self.genre.advance('p','vod',cancel=cancelled))
        self.assertEqual(self.genre.status(self.index.Reader('p'),'vod','Western'),'PENDING')
        self.ready();self.assertEqual(self.page('Western')[1],2)

    def test_partial_batch_is_not_published_and_checkpoint_resumes(self):
        entries=[dict(stream_id=str(i),category_id='a',name='Item '+str(i),genre='Western') for i in range(300)]
        self.index.replace_catalog('p','vod',entries,self.catalogs['get_vod_categories'])
        self.assertTrue(self.genre.advance('p','vod'))
        db=self.index.connect();state=dict(db.execute('SELECT * FROM xcmate_genre_state WHERE kind="vod"').fetchone());db.close()
        self.assertEqual(state['offset'],128);self.assertEqual(state['ready'],0)
        self.assertEqual(self.page('Western')[0],[])
        self.ready();self.assertEqual(self.page('Western')[1],300)

    def test_new_catalogue_revision_hides_old_genre_until_complete_rebuild(self):
        self.ready();self.assertEqual(self.page('Western')[1],2)
        self.index.replace_catalog('p','vod',[dict(stream_id='4',category_id='a',name='Blue',genre='Horror')],self.catalogs['get_vod_categories'],revision_id='next')
        self.assertEqual(self.page('Western')[0],[])
        self.ready();self.assertEqual(self.page('Horror')[0][0]['sid'],'4')
        self.assertEqual(self.page('Western')[0],[])

    def test_current_generation_and_duplicate_group_sid_are_safe(self):
        for cid in ('a','b'):
            self.index.import_group('p','vod',cid,iter([dict(stream_id='50',category_id=cid,name='Shared',genre='Western')]))
        self.ready();rows,_=self.page('Western');self.assertEqual(sum(r['sid']=='50' for r in rows),1)
        # New active generation must never inherit the old Western token.
        self.index.import_group('p','vod','a',iter([dict(stream_id='50',category_id='a',name='Shared',genre='Horror')]))
        self.ready();rows,_=self.page('Horror');self.assertEqual(sum(r['sid']=='50' for r in rows),1)

    def test_live_search_is_never_treated_as_genre_or_required_to_open_genre_tables(self):
        self.ready();reader=self.index.Reader('p')
        self.assertEqual(self.genre.status(reader,'live','Western'),'UNUSED')
        self.assertEqual(self.genre.clause(reader,'live','Western'),None)
        self.assertEqual(reader.page('live','Western')[0],[])

    def test_missing_or_corrupt_database_is_not_replaced(self):
        filename=str(self.folder/'missing.sqlite')
        self.assertFalse(self.genre.advance('p','vod',filename));self.assertFalse((self.folder/'missing.sqlite').exists())
        path=self.folder/'broken.sqlite';path.write_bytes(b'broken')
        with self.assertRaises(sqlite3.DatabaseError):self.genre.advance('p','vod',str(path))
        self.assertEqual(path.read_bytes(),b'broken')

    def test_ready_background_check_does_not_acquire_writer_lock(self):
        self.ready();db=sqlite3.connect(self.index.path());db.execute('BEGIN IMMEDIATE')
        try:self.assertFalse(self.genre.advance('p','vod'))
        finally:db.rollback();db.close()

    def test_sql_search_does_not_extract_every_payload_json(self):
        self.ready();original=self.index.json.loads;calls=[]
        def loads(value):calls.append(value);return original(value)
        with mock.patch.object(self.index.json,'loads',side_effect=loads):
            rows,total=self.page('Western',limit=1)
        self.assertEqual(total,2);self.assertEqual(len(rows),1)
        self.assertLessEqual(len(calls),3)  # page + existing group selection file, never all titles

    def test_title_ranking_pagination_and_pin_bind_parameters_correctly(self):
        self.ready();self.assertEqual(self.page('Sci-Fi',offset=1,limit=1)[0][0]['sid'],'1')
        self.assertEqual(self.page('Sci-Fi',pin='5')[0][0]['sid'],'5')
        self.assertEqual(self.page('Sci-Fi',category='a')[1],2)

    def test_pending_search_uses_existing_native_status_and_refreshes_without_new_live_scan(self):
        w=self.media_window();self.dialog.input.return_value='Western';w._search();self.settle(w)
        self.assertTrue(w._search_genre_pending);self.assertEqual(w._search_data['vod']['code'],'GENRE_PENDING')
        cursor=w._search_cursor;self.ready();self.ready(kind='series')
        w._search_genre_poll=0;w._search_tick();self.settle(w)
        self.assertFalse(w._search_genre_pending);self.assertIs(w._search_cursor,cursor)
        self.assertEqual(w._search_data['vod']['total'],2)

    def test_pending_refresh_is_bounded_and_close_cancels_it(self):
        w=self.media_window();self.dialog.input.return_value='Western';w._search();self.settle(w)
        w._search_genre_until=0;w._search_genre_poll=0;w._search_tick()
        self.assertFalse(w._search_genre_pending);self.assertFalse(w._pool.jobs)
        w.close();w._search_tick();self.assertFalse(w._pool.jobs)

    def test_background_worker_integration_does_not_run_in_gui_poll(self):
        import ast
        source=ast.parse((__import__('xcmate027_fixture').LIB/'app_services.py').read_text())
        worker=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='_run')
        poll=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='poll')
        self.assertIn('index_genres(cancelled)',ast.unparse(worker))
        self.assertNotIn('index_genres',ast.unparse(poll))

    def test_fifty_thousand_rows_migrate_in_bounded_batches_and_query_with_sql_deadline(self):
        entries=[dict(stream_id=str(i),category_id='a',name='Item '+str(i),genre='Science Fiction' if i%10==0 else 'Drama') for i in range(50000)]
        self.index.replace_catalog('p','vod',entries,self.catalogs['get_vod_categories'])
        self.ready()
        reader=self.index.Reader('p',timeout=.15,query_seconds=1)
        rows,total=reader.page('vod','Sci-Fi',limit=48)
        self.assertEqual(total,5000);self.assertEqual(len(rows),48)
        db=self.index.connect();self.assertEqual(db.execute('SELECT offset FROM xcmate_genre_state WHERE kind="vod"').fetchone()[0],50000);db.close()

    def test_ready_transition_during_page_does_not_cache_incomplete_genre_result(self):
        search=importlib.import_module('search_data')
        with mock.patch.object(self.genre,'status',side_effect=lambda reader,kind,query:'PENDING' if not hasattr(self,'_genre_raced') else 'READY'):
            original=self.index.Reader.page
            def page(reader,*a,**kw):
                result=original(reader,*a,**kw);self._genre_raced=True;return result
            with mock.patch.object(self.index.Reader,'page',page):
                result=search.search(self.portal,'Western',kind='vod',incremental=True)
        self.assertEqual(result['vod']['code'],'GENRE_PENDING')
        self.assertNotIn(('vod',0),result['_cursor'].media_cache)

    def test_busy_worker_defers_retry_and_cancel_never_reads_portals(self):
        with mock.patch.object(self.genre,'advance',side_effect=sqlite3.OperationalError('PRIVATE BUSY')) as advance:
            for _ in range(4):self.genre.run_next()
        self.assertEqual(advance.call_count,2)  # one per kind, then deferred
        with mock.patch.object(sys.modules['portals'],'get_active',side_effect=AssertionError('after shutdown')):
            self.assertFalse(self.genre.run_next(lambda:True))
