"""Bounded, pinned public transport and identity-safe optional research."""
import importlib,io,json,socket,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_media_choices_02943 import image


class Sources43(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.s=importlib.import_module('media_sources43');self.responses=[];self.requests=[]
        self.options.update(tmdb_research43=True,tmdb_read_token43='FIXTURE_ONLY_TOKEN')
        self.dns=mock.patch('download_redirect.addresses',return_value=['8.8.8.8']);self.dns.start();self.addCleanup(self.dns.stop)

    def response(self,data,status=200,mime='application/json',encoding='identity'):
        if isinstance(data,dict):data=json.dumps(data).encode()
        stream=io.BytesIO(data);value=types.SimpleNamespace(status=status,headers={'Content-Type':mime,'Content-Encoding':encoding},read=stream.read,close=mock.Mock())
        self.responses.append(value);return value

    def transport(self,url,ips,headers):
        self.requests.append((url,ips,dict(headers)));return self.responses.pop(0)

    def test_fixed_api_host_only_tls_and_no_userinfo_or_pipe_options(self):
        for url in ('http://api.themoviedb.org/3/search/movie','https://evil.example/3/search/movie','https://user:pass@api.themoviedb.org/3','https://api.themoviedb.org:444/3','https://api.themoviedb.org/3|extra'):
            with self.assertRaises(self.s.SourceError):self.s.get(url,api=True,transport=self.transport)
        self.assertFalse(self.requests)

    def test_checked_ip_is_passed_directly_to_transport_without_redirect_following(self):
        self.response({'results':[]})
        self.assertEqual(self.s.get(self.s.TMDB+'/search/movie',api=True,transport=self.transport),{'results':[]})
        self.assertEqual(self.requests[0][1],['8.8.8.8'])
        self.assertNotIn('Authorization',self.requests[0][2])

    def test_api_bearer_never_reused_for_images(self):
        self.response({});self.s.get(self.s.TMDB+'/movie/1',api=True,token='fixture',transport=self.transport)
        self.response(image(),mime='image/png');self.s.get('https://image.tmdb.org/t/p/w500/test.png',transport=self.transport)
        self.assertEqual(self.requests[0][2]['Authorization'],'Bearer fixture')
        self.assertNotIn('Authorization',self.requests[1][2])

    def test_redirect_and_http_classification_are_fixed_codes_not_sensitive_messages(self):
        for status,code in ((301,'REDIRECT_BLOCKED'),(401,'HTTP_AUTH'),(403,'HTTP_AUTH'),(404,'HTTP_NOT_FOUND'),(410,'HTTP_NOT_FOUND'),(429,'HTTP_RATE_LIMIT'),(503,'HTTP_SERVER')):
            response=self.response(b'private response',status=status)
            with self.assertRaises(self.s.SourceError) as caught:self.s.get(self.s.TMDB+'/movie/1',api=True,transport=self.transport)
            self.assertEqual(caught.exception.code,code);self.assertNotIn('private',str(caught.exception));response.close.assert_called_once()

    def test_mime_compression_and_byte_limits_do_not_decode_or_save_untrusted_input(self):
        for payload,mime,encoding in ((b'html','text/html','identity'),(b'bad','application/json','gzip'),(b'x'*(self.s.MAX_JSON+1),'application/json','identity')):
            self.response(payload,mime=mime,encoding=encoding)
            with self.assertRaises(self.s.SourceError):self.s.get(self.s.TMDB+'/movie/1',api=True,transport=self.transport)

    def test_cancellation_before_connection_or_during_read_never_returns_partial_data(self):
        with self.assertRaises(self.s.SourceError):self.s.get(self.s.TMDB+'/movie/1',api=True,cancel=lambda:True,transport=self.transport)
        self.assertFalse(self.requests)
        self.response({'x':'y'});calls=[]
        def cancel():calls.append(1);return len(calls)>1
        with self.assertRaises(self.s.SourceError):self.s.get(self.s.TMDB+'/movie/1',api=True,cancel=cancel,transport=self.transport)

    def test_dns_and_tls_failures_do_not_expose_url_or_query(self):
        with mock.patch('download_redirect.addresses',side_effect=socket.gaierror('private-host-query')):
            with self.assertRaises(self.s.SourceError) as caught:self.s.get(self.s.TMDB+'/movie/1',api=True,transport=self.transport)
        self.assertEqual(caught.exception.code,'DNS_ERROR');self.assertNotIn('private',str(caught.exception))

    def test_bad_token_cannot_leak_semaphore_slots_or_inject_http_headers(self):
        for _ in range(5):
            with self.assertRaises(self.s.SourceError):self.s.get(self.s.TMDB+'/movie/1',api=True,token='bad\r\nX: value',transport=self.transport)
        self.response({});self.s.get(self.s.TMDB+'/movie/1',api=True,transport=self.transport)

    def test_network_slots_bound_research_even_after_other_windows_are_closed(self):
        self.s._network_slots.acquire();self.s._network_slots.acquire()
        try:
            with self.assertRaises(self.s.SourceError) as caught:self.s.get(self.s.TMDB+'/movie/1',api=True,transport=self.transport)
            self.assertEqual(caught.exception.code,'RESEARCH_BUSY');self.assertFalse(self.requests)
        finally:self.s._network_slots.release();self.s._network_slots.release()

    def test_png_jpeg_require_full_decode_not_only_header_and_dimensions(self):
        self.assertEqual(self.s.validate_image(image()),(12,18))
        for value in (image()[:40],b'<html>',image()[:-15]):
            with self.assertRaises(self.s.SourceError):self.s.validate_image(value)

    def test_optional_missing_decoder_is_explicit_blocked_without_unvalidated_success(self):
        data=image()
        with mock.patch.dict('sys.modules',{'PIL':None}):
            with self.assertRaises(self.s.SourceError) as caught:self.s.validate_image(data)
        self.assertEqual(caught.exception.code,'IMAGE_DECODER_MISSING')

    def test_tmdb_disabled_or_missing_token_never_issues_a_request(self):
        with mock.patch.object(self.s,'get') as get:
            self.options['tmdb_research43']=False
            with self.assertRaises(self.s.SourceError):self.s.tmdb('Aladdin','vod')
            self.options['tmdb_research43']=True;self.options['tmdb_read_token43']=''
            with self.assertRaises(self.s.SourceError):self.s.tmdb('Aladdin','vod')
            get.assert_not_called()

    def test_tmdb_results_distinguish_same_title_year_and_actor_without_free_metadata(self):
        data={'results':[dict(id=1,title='Aladdin',release_date='1992-01-01',poster_path='/a.jpg',overview='One'),dict(id=2,title='Aladdin',release_date='2019-01-01',poster_path='/b.jpg',overview='Two')]}
        with mock.patch.object(self.s,'get',return_value=data):rows=self.s.tmdb('Aladdin','vod')
        self.assertEqual([r['year'] for r in rows],['1992','2019']);self.assertNotEqual(rows[0]['remote_id'],rows[1]['remote_id'])
        with mock.patch.object(self.s,'get',return_value={'results':[dict(id=4,name='Actor',profile_path='/a.jpg',overview='Not movie plot')]}):actors=self.s.tmdb('Actor','vod',person=True)
        self.assertEqual(actors[0]['role'],'replacement');self.assertEqual(actors[0]['metadata'],{})

    def test_tmdb_image_path_cannot_escape_fixed_cdn_or_carry_tokens(self):
        for value in ('//evil.example/a.jpg','/../a.jpg','/a.jpg?token=x','/a.svg','http://evil/a.jpg'):
            self.assertEqual(self.s._tmdb_image(value),'')

    def test_tmdb_metadata_does_not_change_work_identity_and_rejects_wrong_remote_id(self):
        candidate=dict(media_type='movie',remote_id=12)
        data=dict(id=13,overview='Wrong work')
        with mock.patch.object(self.s,'get',return_value=data):
            with self.assertRaises(self.s.SourceError):self.s.tmdb_details(candidate)
        data=dict(id=12,overview='Actual plot',release_date='1992-01-01',genres=[{'name':'Fantasy'}],runtime=90,credits={'cast':[{'name':'Actor'}]})
        with mock.patch.object(self.s,'get',return_value=data):fields=self.s.tmdb_details(candidate)
        self.assertEqual(fields['duration_secs'],5400);self.assertNotIn('sid',fields);self.assertNotIn('name',fields)

    def test_commons_only_known_licenses_and_cdn_images_no_metadata_or_html_scraping(self):
        good=dict(pageid=5,title='File:Actor.png',imageinfo=[dict(thumburl='https://upload.wikimedia.org/a.png',extmetadata={'LicenseShortName':{'value':'CC BY-SA 4.0'},'Artist':{'value':'<a>Author</a>'}})])
        bad=dict(pageid=6,title='File:Other.png',imageinfo=[dict(url='https://evil.example/a.png',extmetadata={'LicenseShortName':{'value':'Unknown'}})])
        with mock.patch.object(self.s,'get',return_value={'query':{'pages':{'5':good,'6':bad}}}) as get:
            result=self.s.commons('person name')
        self.assertEqual(len(result),1);self.assertEqual(result[0]['metadata'],{});self.assertIn('Author',result[0]['attribution']);self.assertIn('/wiki/File:',result[0]['attribution'])
        self.assertIn('commons.wikimedia.org/w/api.php',get.call_args.args[0])

    def test_automatic_fallback_requires_opt_in_exact_title_and_year_and_unique_work(self):
        module=importlib.import_module('media_metadata43');self.options['tmdb_fallback43']=True
        def candidate(remote,year):return dict(role='poster',media_type='movie',title='Aladdin',year=year,remote_id=remote,url='https://image.tmdb.org/t/p/w500/a.jpg',metadata={'plot':'Fallback'})
        row=dict(kind='vod',sid='1',name='Aladdin',year=1992)
        for values,works in (([candidate(1,'2019')],False),([candidate(1,'1992'),candidate(2,'1992')],False),([candidate(1,'1992')],True)):
            module._cache.clear();module._next=0
            with mock.patch.object(self.s,'tmdb',return_value=values):result=module.fallback(row,'vod')
            self.assertEqual('cover' in result,works);self.assertEqual(result['sid'],'1')
        module._cache.clear();module._next=0
        with mock.patch.object(self.s,'tmdb') as lookup:
            module.fallback(dict(row,year=''),'vod');module.fallback(dict(row,cover='https://images.example/valid.jpg'),'vod');lookup.assert_not_called()

    def test_rate_limit_has_global_backoff_without_retry_loop(self):
        module=importlib.import_module('media_metadata43');self.options['tmdb_fallback43']=True;module._cache.clear();module._next=0
        with mock.patch.object(self.s,'tmdb',side_effect=self.s.SourceError('HTTP_RATE_LIMIT')) as lookup:
            for n in range(20):module.fallback(dict(name='Title'+str(n),year=1992),'vod')
        self.assertEqual(lookup.call_count,1)
