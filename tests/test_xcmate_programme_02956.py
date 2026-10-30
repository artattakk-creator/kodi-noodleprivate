"""One real local EPG/art index, synthetic metadata API, no Android claim."""
import importlib,sys,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON


class Programme56(Fixture,unittest.TestCase):
    TITLE='Harry Potter und die Kammer des Schreckens'
    def setUp(self):
        super().setUp()
        self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC_TEST_TOKEN')
        self.urls=importlib.import_module('programme_urls55');self.match=importlib.import_module('programme_match46')
        self.events=importlib.import_module('programme_events46');self.art=importlib.import_module('programme_art46')
        self.row=dict(sid='1',kind='live',category_id='a',name='Test station',epg_channel_id='xml')
        self.event=self.events.describe(self.portal,self.row,dict(title=self.TITLE,start=self.now-60,stop=self.now+600),canonical='xml')
        self.event['genre']='Spielfilm'
        self.search=dict(total_pages=1,total_results=1,results=[dict(id=9123456,title=self.TITLE,release_date='2002-11-14',adult=False)])
        self.details=dict(id=9123456,title=self.TITLE,release_date='2002-11-14',adult=False,backdrop_path='/synthetic_HP_event.jpg')

    def resolve(self,search=None,details=None):
        import io
        from PIL import Image
        from pathlib import Path
        data=io.BytesIO();Image.new('RGB',(160,90),(20,80,130)).save(data,'PNG')
        Path(self.art.root()).mkdir(exist_ok=True)
        with mock.patch.object(self.art,'space'),mock.patch('media_sources43.get',side_effect=[search or self.search,details or self.details,data.getvalue()]):
            return self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())

    def test_yearless_explicit_movie_requires_complete_unique_search_and_independent_details(self):
        value=self.resolve();self.assertEqual(value['code'],'READY')
        self.assertEqual(value['match'],'EXACT_UNIQUE_FILM_TITLE');self.assertEqual(value['matched_year56'],2002)
        self.assertNotIn('year',self.event)
        self.assertNotIn('SYNTHETIC_TEST_TOKEN',value['image']);self.assertIn('/synthetic_HP_event.jpg',value['source_url']);self.assertTrue(__import__('os').path.isfile(value['image']))

    def test_remakes_with_same_title_do_not_get_a_guessed_year(self):
        search=dict(self.search,total_results=2,results=self.search['results']+[dict(id=77,title=self.TITLE,release_date='2020-01-01')])
        value=self.resolve(search=search);self.assertEqual(value['source'],'placeholder');self.assertEqual(value['code'],'NO_YEAR')

    def test_partial_search_page_cannot_prove_unique_movie(self):
        value=self.resolve(search=dict(self.search,total_pages=2,total_results=21))
        self.assertEqual(value['code'],'NO_YEAR');self.assertEqual(value['source'],'placeholder')

    def test_wrong_sequel_or_changed_details_year_is_not_the_exact_event(self):
        for details in (dict(self.details,title='Harry Potter und der Stein der Weisen'),dict(self.details,release_date='2003-01-01'),dict(self.details,id=77)):
            with mock.patch('media_sources43.get',side_effect=[self.search,details]):
                self.assertIsNone(self.match.candidate(self.event))

    def test_explicit_wrong_year_cannot_enter_the_yearless_recovery_path(self):
        event=dict(self.event,year=2003)
        row=dict(remote_id=9123456,title=self.TITLE,year='2002',url='https://image.tmdb.org/t/p/w500/synthetic_HP_event.jpg',role='fanart')
        with mock.patch('programme_match46.unique_movie56',side_effect=AssertionError('yearless fallback')),mock.patch('media_sources43.get',return_value=self.search):
            self.assertIsNone(self.match.candidate(event))

    def test_disabled_optional_provider_is_diagnosed_without_api_request(self):
        self.options['programme_tmdb46']=False
        with mock.patch('media_sources43.get',side_effect=AssertionError('disabled API')):
            value=self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())
        self.assertEqual(value['code'],'TMDB_DISABLED')

    def test_unclassified_event_does_not_become_a_movie_by_title_guess(self):
        self.event.pop('genre')
        with mock.patch('media_sources43.get',side_effect=AssertionError('unclassified API')):
            value=self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())
        self.assertEqual(value['code'],'NOT_CLASSIFIED_MOVIE')

    def test_missing_backdrop_is_no_valid_url_not_image_success(self):
        value=self.resolve(details=dict(self.details,backdrop_path=''))
        self.assertEqual(value['code'],'NO_VALID_URL');self.assertEqual(value['source'],'placeholder')

    def test_existing_revision_gets_periodic_background_preparation_after_quiet_startup(self):
        self.urls._revisions.clear()
        with mock.patch.object(self.urls.time,'monotonic',return_value=10):
            self.assertFalse(self.urls.refreshed('p','unchanged'));self.assertFalse(self.urls.refreshed('p','unchanged'))
        with mock.patch.object(self.urls.time,'monotonic',return_value=71):
            self.assertTrue(self.urls.refreshed('p','unchanged'))

    def test_prepared_url_survives_restart_and_readers_start_no_metadata_search(self):
        self.resolve();self.art._memory.clear()
        with mock.patch('media_sources43.get',side_effect=AssertionError('reader API')),mock.patch.object(self.urls,'enqueue',side_effect=AssertionError('reader enqueue')):
            first=self.art.cached(self.event);again=self.art.cached(dict(self.event))
        self.assertEqual(first['image'],again['image']);self.assertEqual(first['source'],'tmdb_movie')

    def import_future(self):
        guide=importlib.import_module('guide_store');raw=[]
        for i in range(7):
            start=self.now-60+i*600
            raw.append(dict(channel='xml',name=self.TITLE if i==5 else 'Test programme '+str(i),descr='Stored local description',category='Spielfilm',start_timestamp=start,stop_timestamp=start+600))
        guide.import_cache('p',{'xml':raw},'unchanged-epg-revision',now=self.now,trusted_feed=True)
        return raw

    def test_background_rotates_announced_films_beyond_next_without_new_revision(self):
        raw=self.import_future();pre=importlib.import_module('programme_prefetch48');pre._next.clear();pre._positions.clear();pre._future56.clear();seen=[]
        with mock.patch('programme_urls55.enqueue',side_effect=lambda event,**kw:seen.append(dict(event))):
            for _ in range(6):pre._next.clear();pre.prepare(self.portal,[self.row])
        future=next(v for v in seen if v['title']==self.TITLE)
        detail=self.events.load(self.portal,self.row,dict(start=raw[5]['start_timestamp'],stop=raw[5]['stop_timestamp']),now=self.now)
        self.assertEqual(future['key'],detail['key']);self.assertEqual(future['canonical'],detail['canonical'])

    def test_future_detail_and_hero_use_one_url_only_when_that_event_is_actually_now(self):
        raw=self.import_future();selected=dict(start=raw[5]['start_timestamp'],stop=raw[5]['stop_timestamp'])
        self.event=self.events.load(self.portal,self.row,selected,now=self.now)
        value=self.resolve();self.assertEqual(value['code'],'READY')
        self.art._memory.clear();items=importlib.import_module('widget_items45');local=importlib.import_module('local_epg')
        present=items.describe(self.portal,'live',self.row,{},local.now_next('p',[self.row],{},self.now)['1'])
        self.assertNotEqual(present['props']['XCMate.ProgrammeKey46'],self.event['key'])
        self.assertNotEqual(present['props']['XCMate.ProgrammeImage46'],value['image'])
        with mock.patch('media_sources43.get',side_effect=AssertionError('GUI API')):
            widget=items.describe(self.portal,'live',self.row,{},local.now_next('p',[self.row],{},selected['start']+60)['1'])
            window=importlib.import_module('programme_window46').ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
            window.configure(self.portal,self.row,selected);window._ready=True;window.event=self.events.load(self.portal,self.row,selected,now=self.now);window.pump()
        self.assertEqual(widget['props']['XCMate.ProgrammeKey46'],self.event['key'])
        self.assertEqual(widget['props']['XCMate.ProgrammeImage46'],value['image'])
        self.assertEqual(window.getControl(110).image,value['image'])

    def test_future_preparation_survives_a_gap_with_no_current_programme(self):
        raw=self.import_future();pre=importlib.import_module('programme_prefetch48');pre._next.clear();seen=[]
        info=dict(now='',start=0,stop=0,canonical46='xml',snapshot_revision='unchanged',events=[dict(title=self.TITLE,start=raw[5]['start_timestamp'],stop=raw[5]['stop_timestamp'],genre='Spielfilm')])
        with mock.patch('local_epg.now_next',return_value={'1':info}),mock.patch('programme_urls55.enqueue',side_effect=lambda event,**kw:seen.append(event)):
            self.assertTrue(pre.prepare(self.portal,[self.row]))
        self.assertEqual(len(seen),1);self.assertEqual(seen[0]['title'],self.TITLE)
        self.assertEqual(seen[0]['start'],raw[5]['start_timestamp'])
