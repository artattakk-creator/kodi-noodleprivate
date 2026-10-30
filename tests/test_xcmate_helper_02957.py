"""Public Helper contract with synthetic metadata; no Android/image PASS."""
import copy,importlib,json,sys,threading,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from urllib.parse import parse_qs,urlsplit
from xcmate027_fixture import Fixture,ADDON

TITLE='Harry Potter und die Kammer des Schreckens'
URL='https://image.tmdb.org/t/p/w500/SYNTHETIC_ONLY.jpg'


def movie(title=TITLE,year=2002,remote=672):
    return dict(type='movie',title=title,year=year,uniqueid={'tmdb':str(remote)},
        file='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=movie&tmdb_id='+str(remote),
        art={'fanart':'image://'+URL.replace(':','%3a').replace('/','%2f')+'/'})


class Helper57(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.options.update(programme_helper57=True,programme_catalog57=False)
        self.helper=importlib.import_module('programme_helper57');self.rpc=importlib.import_module('helper_rpc57')
        self.urls=importlib.import_module('programme_urls55');self.sources=importlib.import_module('programme_sources57');self.sources._backoff.clear()
        self.row=dict(sid='1',name='Test station',kind='live',category_id='a',epg_channel_id='xml')
        self.event=importlib.import_module('programme_events46').describe(self.portal,self.row,dict(title=TITLE,year=2002,genre='Spielfilm',start=self.now-30,stop=self.now+600),canonical='xml')
        self.event.update(year=2002,genre='Spielfilm');self.calls=[];self.items=[movie()];self.detail=movie()
        self.addon=dict(addonid=self.helper.ADDON,enabled=True,installed=True,version='6.19.4')

    def reply(self,method,params,cancel=lambda:False):
        self.calls.append((method,copy.deepcopy(params)))
        if method=='Addons.GetAddonDetails':return {'addon':self.addon}
        query=parse_qs(urlsplit(params['directory']).query)
        rows=self.items if query['info']==['search'] else [self.detail]
        return dict(files=rows,limits=dict(total=len(rows),start=0,end=len(rows)))

    def native(self,request):
        request=json.loads(request)
        return json.dumps(dict(jsonrpc='2.0',id=57,result=self.reply(request['method'],request['params'])))

    def resolve(self,**kwargs):
        with mock.patch.object(sys.modules['xbmc'],'executeJSONRPC',side_effect=self.native,create=True),mock.patch('media_sources43.get',side_effect=AssertionError('No personal TMDb API')):
            with ThreadPoolExecutor(1) as pool:return pool.submit(self.urls.resolve,self.event,allow_lookup=True,check=mock.Mock(),**kwargs).result(5)

    def test_helper_finds_exact_2002_movie_without_any_xcmate_api_token(self):
        value=self.resolve();self.assertEqual(value['code'],'READY');self.assertEqual(value['source'],'tmdb_helper')
        self.assertEqual(value['provider_id'],672);self.assertEqual(value['matched_year56'],2002)
        self.assertEqual(value['image'],URL+self.urls.OPTIONS);self.assertEqual(value['helper_version57'],'6.19.4')
        self.assertFalse(self.options.get('tmdb_read_token43'));self.assertFalse(self.options.get('programme_tmdb46'))
        self.assertFalse(self.builtins)

    def test_exact_full_sequel_title_is_not_replaced_by_the_first_harry_potter(self):
        self.items=[movie('Harry Potter und der Stein der Weisen',2001,671)]
        value=self.resolve();self.assertEqual(value['code'],'NO_UNIQUE_MATCH');self.assertEqual(value['source'],'placeholder')
        self.assertFalse(any('tmdb_id' in parse_qs(urlsplit(p.get('directory','')).query) for m,p in self.calls if m=='Files.GetDirectory'))

    def test_two_same_title_remakes_without_year_are_ambiguous(self):
        self.event.pop('year');self.items=[movie(),movie(year=2020,remote=999)]
        self.assertEqual(self.resolve()['code'],'NO_UNIQUE_MATCH')

    def test_missing_genre_and_year_can_only_pass_full_cross_type_uniqueness_and_details(self):
        self.event.pop('year');self.event.pop('genre');value=self.resolve()
        self.assertEqual(value['code'],'READY')
        query=parse_qs(urlsplit(next(p['directory'] for m,p in self.calls if m=='Files.GetDirectory')).query)
        self.assertEqual(query['tmdb_type'],['both']);self.assertEqual(query['query'],[TITLE])

    def test_same_title_movie_and_tv_show_are_not_guessed(self):
        self.event.pop('genre');tv=dict(movie(remote=888),type='tvshow',file='plugin://plugin.video.themoviedb.helper/?tmdb_type=tv&tmdb_id=888')
        self.items=[movie(),tv];self.assertEqual(self.resolve()['code'],'NO_UNIQUE_MATCH')

    def test_independent_details_must_confirm_the_same_year_title_and_id(self):
        for detail in (movie(year=2003),movie(remote=671),movie(title='Another film')):
            self.calls.clear();self.detail=detail
            with self.assertRaises(self.rpc.Error):self.helper.lookup(self.event,rpc=self.reply)

    def test_next_page_marker_refuses_to_claim_a_complete_unique_match(self):
        self.items.append(dict(file='plugin://plugin.video.themoviedb.helper/?info=search&page=2',title='Next page'))
        self.assertEqual(self.resolve()['code'],'NO_UNIQUE_MATCH')

    def test_missing_or_conflicting_tmdb_identity_is_not_a_picture_success(self):
        for row in (dict(movie(),file='',uniqueid={}),dict(movie(),uniqueid={'tmdb':'671'})):
            self.items=[row]
            with self.assertRaises(self.rpc.Error) as error:self.helper.lookup(self.event,rpc=self.reply)
            self.assertEqual(error.exception.code,'HELPER_NO_ID')

    def test_disabled_or_missing_helper_never_invokes_its_plugin_directory(self):
        self.addon['enabled']=False;value=self.resolve()
        self.assertEqual(value['code'],'HELPER_NOT_AVAILABLE');self.assertFalse(any(m=='Files.GetDirectory' for m,p in self.calls))

    def test_unknown_helper_major_is_explicitly_unsupported_without_plugin_calls(self):
        self.addon['version']='7.0.0';self.assertEqual(self.resolve()['code'],'HELPER_VERSION_UNSUPPORTED')
        self.assertFalse(any(m=='Files.GetDirectory' for m,p in self.calls))

    def test_missing_art_and_unsafe_image_wrappers_are_not_verified_images(self):
        for art in ({},{'fanart':'image://smb%3a%2f%2fprivate%2fcover.jpg/'},{'fanart':URL+'?token=PRIVATE'},
                    {'fanart':'https://127.0.0.1/private.png'},{'fanart':'image://https%253a%252f%252fimage.tmdb.org%252fposter.jpg/'}):
            self.detail=dict(movie(),art=art)
            with self.assertRaises(self.rpc.Error) as error:self.helper.lookup(self.event,rpc=self.reply)
            self.assertEqual(error.exception.code,'HELPER_ART_MISSING')

    def test_movie_prefers_fanart_then_poster_and_never_fetches_during_matching(self):
        self.detail=dict(movie(),art={'poster':URL})
        value=self.helper.lookup(self.event,rpc=self.reply);self.assertEqual(value['url'],URL)
        self.assertEqual(value['image_scope57'],'movie')

    def test_broken_helper_backdrop_uses_validated_poster_without_another_metadata_lookup(self):
        poster='https://image.tmdb.org/t/p/w500/SYNTHETIC_POSTER.jpg';self.detail['art']['poster']=poster
        from media_sources43 import SourceError
        check=mock.Mock(side_effect=[SourceError('HTTP_NOT_FOUND'),None])
        with mock.patch.object(sys.modules['xbmc'],'executeJSONRPC',side_effect=self.native,create=True),ThreadPoolExecutor(1) as pool:
            value=pool.submit(self.urls.resolve,self.event,allow_lookup=True,check=check).result(5)
        self.assertEqual(value['source_url'],poster);self.assertEqual(check.call_count,2)
        self.assertEqual(sum(method=='Files.GetDirectory' for method,params in self.calls),2)

    def test_provider_event_image_has_priority_and_starts_no_helper_or_catalogue(self):
        self.event['xmltv_image']=URL
        with mock.patch.object(self.sources,'attempts',side_effect=AssertionError('Unnecessary external lookup')):
            value=self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())
        self.assertEqual(value['source'],'xmltv_event')

    def test_failed_provider_preflight_continues_to_helper_with_same_shared_validator(self):
        self.event['xmltv_image']='https://image.tmdb.org/t/p/w500/FAILED_PROVIDER.jpg'
        from media_sources43 import SourceError
        check=mock.Mock(side_effect=[SourceError('HTTP_NOT_FOUND'),None])
        with mock.patch.object(sys.modules['xbmc'],'executeJSONRPC',side_effect=self.native,create=True),ThreadPoolExecutor(1) as pool:
            value=pool.submit(self.urls.resolve,self.event,allow_lookup=True,check=check).result(5)
        self.assertEqual(value['source'],'tmdb_helper');self.assertEqual(check.call_count,2)

    def test_missing_helper_backoff_does_not_block_distinct_valid_provider_images(self):
        self.addon['enabled']=False;self.resolve();self.calls.clear()
        self.event=dict(self.event,key='another-event');self.resolve();self.assertEqual(self.calls,[])
        self.event['xmltv_image']=URL
        self.assertEqual(self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())['source'],'xmltv_event')

    def test_existing_valid_positive_56_url_is_preserved_without_global_relookup(self):
        self.event['xmltv_image']=URL;value=self.urls.resolve(self.event,allow_lookup=False,check=mock.Mock())
        with mock.patch.object(self.sources,'attempts',side_effect=AssertionError('global retry')):
            again=self.urls.resolve(self.event,allow_lookup=True,check=mock.Mock())
        self.assertEqual(value['image'],again['image'])

    def test_helper_movie_url_is_shared_by_real_guide_detail_and_current_widget_readers(self):
        guide=importlib.import_module('guide_store');events=importlib.import_module('programme_events46')
        guide.import_cache('p',{'xml':[dict(channel='xml',name=TITLE,descr='LOCAL EPG TEXT',category='Spielfilm',date='2002',start_timestamp=self.now-30,stop_timestamp=self.now+600)]},'r57',now=self.now,trusted_feed=True)
        selected=dict(start=self.now-30,stop=self.now+600);self.event=events.load(self.portal,self.row,selected,now=self.now)
        value=self.resolve();self.assertEqual(value['code'],'READY');importlib.import_module('programme_art46')._memory.clear()
        with mock.patch.object(self.rpc,'call',side_effect=AssertionError('GUI lookup')),mock.patch('media_sources43.get',side_effect=AssertionError('GUI metadata')):
            info=importlib.import_module('local_epg').now_next('p',[self.row],{},self.now)['1']
            widget=importlib.import_module('widget_items45').describe(self.portal,'live',self.row,{},info)
            dialog=importlib.import_module('programme_window46').ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
            dialog.configure(self.portal,self.row,selected);dialog._ready=True;dialog.event=events.load(self.portal,self.row,selected,now=self.now);dialog.pump()
        self.assertEqual(widget['props']['XCMate.ProgrammeKey46'],dialog.event['key'])
        self.assertEqual(widget['props']['XCMate.ProgrammeImage46'],dialog.getControl(110).image)
        self.assertEqual(dialog.getControl(110).image,value['image']);self.assertEqual(dialog.event['description'],'LOCAL EPG TEXT')

    def test_disabling_helper_hides_its_url_without_deleting_persisted_record(self):
        value=self.resolve();index=importlib.import_module('programme_index46');before=index.art(self.event)
        self.options['programme_helper57']=False;self.assertIsNone(self.urls.display(self.event,before))
        self.assertEqual(index.art(self.event)['source_url'],before['source_url'])

    def test_xmltv_news_stays_local_and_is_never_guessed_as_a_movie(self):
        self.event['genre']='Nachrichten';self.assertEqual(self.resolve()['code'],'NO_UNIQUE_MATCH')
        self.assertEqual(self.calls,[])

    def test_prepared_helper_url_cannot_cross_source_mapping_sender_or_time_identity(self):
        value=self.resolve()
        for change in ({'canonical':'other-epg'},{'source_key46':'foreign-source'},{'sid':'other-sender'},
                       {'start':self.event['start']+1},{'title':'Harry Potter und der Stein der Weisen'}):
            self.assertIsNone(self.urls.display(dict(self.event,**change),value))

    def test_cancelled_helper_reply_never_publishes_a_late_event_image(self):
        cancel=threading.Event();original=self.reply
        def reply(method,params,**kw):
            value=original(method,params,**kw)
            if method=='Files.GetDirectory':cancel.set()
            return value
        with mock.patch.object(self,'reply',side_effect=reply),mock.patch.object(sys.modules['xbmc'],'executeJSONRPC',side_effect=self.native,create=True),ThreadPoolExecutor(1) as pool:
            result=pool.submit(self.urls.resolve,self.event,allow_lookup=True,check=mock.Mock(),cancel=cancel.is_set).result(5)
        self.assertIsNone(result);self.assertIsNone(importlib.import_module('programme_index46').art(self.event))

    def test_future_classified_movie_is_prioritized_within_existing_bounded_page(self):
        pre=importlib.import_module('programme_prefetch48');pre._next.clear();pre._positions.clear();pre._future56.clear();seen=[]
        rows=[dict(title='Short '+str(i),start=self.now+i*600,stop=self.now+(i+1)*600) for i in range(1,20)]
        rows[12].update(title=TITLE,genre='Spielfilm')
        info=dict(now='',start=0,stop=0,canonical46='xml',snapshot_revision='same',events=rows)
        with mock.patch('local_epg.now_next',return_value={'1':info}),mock.patch.object(self.urls,'enqueue',side_effect=lambda event,**kw:seen.append(event)):
            pre.prepare(self.portal,[self.row])
        self.assertEqual(len(seen),2);self.assertEqual(seen[0]['title'],'Short 1');self.assertEqual(seen[1]['title'],TITLE)


class Episode57(Helper57):
    # Keep only episode-specific methods in this subclass's executed suite.
    def setUp(self):
        super().setUp();self.event.update(title='Test Series',season=2,episode=3,subtitle='Test Episode');self.event.pop('year',None)
        self.event['key']=importlib.import_module('programme_events46').key('p','1',self.event)
        self.series=dict(type='tvshow',title='Test Series',year=2011,uniqueid={'tmdb':'1399'},
            file='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=1399',art={'fanart':'https://image.tmdb.org/t/p/w500/SYNTHETIC_SERIES.jpg'})
        self.episode=dict(type='episode',title='Test Episode',showtitle='Test Series',season=2,episode=3,
            uniqueid={'tmdb':'999001'},file='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=1399&season=2&episode=3',art={'thumb':URL})

    def reply(self,method,params,cancel=lambda:False):
        if method=='Addons.GetAddonDetails':return {'addon':self.addon}
        self.calls.append((method,params));query=parse_qs(urlsplit(params['directory']).query)
        rows=[self.episode if query.get('episode') else self.series]
        return dict(files=rows,limits=dict(total=1))

    def test_episode_identity_uses_parent_series_id_plus_season_episode_not_episode_tmdb_id(self):
        value=self.resolve();self.assertEqual(value['code'],'READY');self.assertEqual(value['provider_id'],1399)
        self.assertEqual(value['image_scope57'],'episode');self.assertEqual(value['match'],'EXACT_HELPER_EPISODE57')

    def test_wrong_episode_or_wrong_subtitle_is_refused(self):
        for patch in (dict(episode=4),dict(season=1),dict(title='Other Episode'),dict(showtitle='Other Series')):
            original=self.episode;self.episode=dict(original,**patch)
            with self.assertRaises(self.rpc.Error):self.helper.lookup(self.event,rpc=self.reply)
            self.episode=original

    def test_missing_episode_still_is_explicit_series_fallback(self):
        self.episode['art']={};value=self.resolve()
        self.assertEqual(value['image_scope57'],'series_fallback');self.assertIn('kein Episodenbild',value['attribution'])

    def test_parent_poster_in_episode_thumb_is_never_claimed_as_a_real_episode_still(self):
        self.episode['art']['thumb']='https://image.tmdb.org/t/p/original/SYNTHETIC_SERIES.jpg'
        self.assertEqual(self.resolve()['image_scope57'],'series_fallback')

    def test_existing_generic_series_art_does_not_mask_a_helper_exact_episode_still(self):
        self.options['programme_catalog57']=True
        generic=dict(url='https://image.tmdb.org/t/p/w500/GENERIC_SERIES.jpg',source='xcmate_catalog',match='EXACT_CATALOG_SERIES57',image_scope57='series_fallback')
        with mock.patch('programme_catalog57.xcmate',return_value=generic),mock.patch('programme_catalog57.kodi',return_value=None):
            value=self.resolve()
        self.assertEqual(value['source'],'tmdb_helper');self.assertEqual(value['image_scope57'],'episode')

    def test_failed_episode_still_preflight_can_use_explicitly_labelled_series_image(self):
        from media_sources43 import SourceError
        check=mock.Mock(side_effect=[SourceError('HTTP_NOT_FOUND'),None])
        with mock.patch.object(sys.modules['xbmc'],'executeJSONRPC',side_effect=self.native,create=True),ThreadPoolExecutor(1) as pool:
            value=pool.submit(self.urls.resolve,self.event,allow_lookup=True,check=check).result(5)
        self.assertEqual(value['image_scope57'],'series_fallback');self.assertIn('kein Episodenbild',value['attribution'])

    def test_series_fallback_is_labelled_in_existing_hero_description_without_changing_epg_text(self):
        self.event['description']='LOCAL SERIES DESCRIPTION';self.episode['art']={};self.resolve()
        info=dict(now='Test Series',start=self.event['start'],stop=self.event['stop'],events=[self.event],canonical46='xml',next='',progress=.5)
        value=dict(art={'thumb':''},props={},info={'plot':''})
        importlib.import_module('programme_widgets46').decorate(value,self.portal,self.row,info)
        self.assertEqual(value['props']['XCMate.ProgrammeImageScope57'],'series_fallback')
        self.assertTrue(value['props']['XCMate.ProgrammeDescription46'].startswith('Serienbild (kein Episodenbild)'))
        self.assertEqual(self.event['description'],'LOCAL SERIES DESCRIPTION')


def load_tests(loader,tests,pattern):
    # The episode fixture shares utilities, not its movie scenario assertions.
    suite=unittest.TestSuite(loader.loadTestsFromTestCase(Helper57))
    for name in Episode57.__dict__:
        if name.startswith('test_'):suite.addTest(Episode57(name))
    return suite
