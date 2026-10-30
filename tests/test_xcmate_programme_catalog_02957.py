"""Real existing local SQLite catalogue and public Kodi library responses."""
import importlib,json,sys,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from xcmate027_fixture import Fixture

TITLE='Harry Potter und die Kammer des Schreckens'
URL='https://image.tmdb.org/t/p/w500/SYNTHETIC_CATALOG.jpg'


class Catalog57(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.catalog=importlib.import_module('programme_catalog57')
        self.event=dict(pid='p',title=TITLE,year=2002,genre='Spielfilm')

    def add_movie(self,pid='p',sid='hp',year=2002):
        self.index.import_group(pid,'vod','a',[dict(stream_id=sid,category_id='a',name=TITLE,year=year,stream_icon=URL)])

    def test_existing_same_portal_movie_image_needs_no_rpc_or_database_write(self):
        self.add_movie();from pathlib import Path
        filename=Path(self.index.path());before=filename.read_bytes()
        with mock.patch('socket.getaddrinfo',side_effect=AssertionError('catalog DNS')):
            value=self.catalog.xcmate(self.event)
        self.assertEqual(value['source'],'xcmate_catalog');self.assertEqual(value['url'],URL)
        self.assertEqual(filename.read_bytes(),before)

    def test_other_portals_disabled_groups_and_wrong_year_cannot_supply_art(self):
        self.add_movie(pid='foreign');self.assertIsNone(self.catalog.xcmate(self.event))
        self.add_movie(year=2003);self.assertIsNone(self.catalog.xcmate(self.event))
        self.add_movie();importlib.import_module('group_selection').save('p',[],kind='vod',known=['a','b'])
        self.assertIsNone(self.catalog.xcmate(self.event))

    def test_catalogue_duplicate_identities_do_not_guess_one_cover(self):
        self.index.import_group('p','vod','a',[dict(stream_id=str(i),category_id='a',name=TITLE,year=2002,stream_icon=URL) for i in range(2)])
        self.assertIsNone(self.catalog.xcmate(self.event))

    def test_existing_local_catalogue_has_priority_over_helper_and_personal_tmdb_api(self):
        self.add_movie();self.options.update(programme_catalog57=True,programme_helper57=True)
        event=importlib.import_module('programme_events46').describe(self.portal,dict(sid='1'),dict(title=TITLE,start=self.now-30,stop=self.now+600))
        event.update(year=2002,genre='Spielfilm')
        with mock.patch('programme_helper57.lookup',side_effect=AssertionError('helper before local')),mock.patch('programme_catalog57.kodi',side_effect=AssertionError('Kodi before local')):
            value=importlib.import_module('programme_urls55').resolve(event,allow_lookup=True,check=mock.Mock())
        self.assertEqual(value['source'],'xcmate_catalog')

    def test_kodi_library_movie_uses_only_supported_public_library_fields(self):
        def rpc(method,params,cancel=lambda:False):
            self.assertEqual(method,'VideoLibrary.GetMovies');self.assertEqual(params['filter']['value'],TITLE)
            return {'movies':[dict(movieid=42,title=TITLE,year=2002,art={'fanart':URL})],'limits':{'total':1}}
        self.assertEqual(self.catalog.kodi(self.event,rpc=rpc)['url'],URL)

    def test_episode_still_does_not_require_a_parent_series_fanart(self):
        event=dict(self.event,title='Test Series',year=2011,season=2,episode=3,subtitle='Test Episode')
        def rpc(method,params,cancel=lambda:False):
            if method=='VideoLibrary.GetTVShows':return dict(tvshows=[dict(tvshowid=42,title='Test Series',year=2011,art={})],limits={'total':1})
            self.assertEqual(params['tvshowid'],42);self.assertEqual(params['season'],2)
            return dict(episodes=[dict(title='Test Episode',showtitle='Test Series',season=2,episode=3,art={'thumb':URL})],limits={'total':1})
        result=self.catalog.kodi(event,rpc=rpc);self.assertEqual(result['image_scope57'],'episode');self.assertEqual(result['url'],URL)
