"""Image policy/error regressions, real SQLite/bytes and live status consumer."""
import importlib
import io
import json
from pathlib import Path
import unittest
from unittest import mock

from PIL import Image
import test_xcmate_epg_02952 as epg
import test_xcmate_epg_handoff_02963 as handoff


class Artwork482(unittest.TestCase):
    def setUp(self):
        self.f=epg.EPG52(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.put('a',[self.f.event(title='Synthetic Artwork482',extra='<category>Spielfilm</category><date>2024</date>')])
        self.event=importlib.import_module('programme_events46').load(self.f.portal,self.f.channel)
        self.requests=importlib.import_module('programme_requests68')
        self.policy=importlib.import_module('storage_policy92')
        self.f.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True)

    def test_legacy_global_choices_do_not_veto_enabled_sources(self):
        self.f.options.update(programme_xmltv96=True, programme_tmdb46=False,
                              programme_tvmaze67=False)
        for raw in ('{"version":1,"image_epg":"no"}',
                    '{"version":1,"image_epg":"later"}',
                    '{broken'):
            with self.subTest(raw=raw):
                self.policy.path().write_text(raw)
                self.assertTrue(self.policy.images_enabled())
                self.assertTrue(self.requests.request(self.event, priority=True))
                self.assertEqual(self.policy.path().read_text(), raw)

    def test_existing_intent_gets_policy_reason_when_all_sources_are_off(self):
        self.assertTrue(self.requests.request(self.event,priority=True))
        self.f.options.update(programme_xmltv96=False,programme_tmdb46=False,programme_tvmaze67=False)
        with mock.patch('series_requests85.drain'),mock.patch('programme_urls55.enqueue',side_effect=AssertionError('NO_LOOKUP')):
            self.assertEqual(self.requests.drain(),0)
        self.assertEqual(self.requests.result(self.event).get('code'),'IMAGE_EPG_DISABLED')

    def test_tvmaze_reactivation_works_with_legacy_deferred_value(self):
        self.policy.path().write_text('{"version":1,"image_epg":"later"}')
        self.f.options.update(programme_xmltv96=False,programme_tmdb46=False,programme_tvmaze67=False)
        self.policy.images_enabled();self.assertFalse(self.requests.request(self.event))
        self.f.options['programme_tvmaze67']=True
        self.policy.images_enabled();self.assertTrue(self.requests.request(self.event))
        self.assertEqual(self.requests.result(self.event).get('code'),'REQUESTED')

    def test_invalid_settings_actual_worker_preserves_reason_and_private_bytes(self):
        settings=self.f.folder/'settings.xml';settings.write_bytes(b'<settings>')
        token=self.f.folder/'tmdb_read_access_token.txt';token.write_bytes(b'SYNTHETIC_PRIVATE_BYTES_ONLY')
        q=importlib.import_module('programme_urls55');q._queue.clear();q._pending.clear();q._stop.clear()
        q._queue['synthetic482']=(self.event,True,False,importlib.import_module('epg_handoff63').profile_scope(),False)
        q._pending.add('synthetic482');seen=[];complete=self.requests.completed
        def done(event,value):
            seen.append(value);complete(event,value);q._stop.set()
        with mock.patch('programme_requests68.completed',side_effect=done),mock.patch('home_schedule75.applicable',return_value=False),mock.patch('media_sources43.get',side_effect=AssertionError('NO_NETWORK')):
            q._run()
        self.assertEqual(seen[-1]['code'],'SETTINGS_XML_INVALID')
        art=self.requests.result(self.event)
        self.assertEqual(art['code'],'SETTINGS_XML_INVALID')
        self.assertIn('einstellungen',importlib.import_module('programme_diagnostics59').message(self.event,art).casefold())
        self.assertEqual(settings.read_bytes(),b'<settings>');self.assertEqual(token.read_bytes(),b'SYNTHETIC_PRIVATE_BYTES_ONLY')

    def test_detail_has_unbacked_logo_and_hides_absent_metadata_and_artwork(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON

        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.f.portal, self.f.channel)
        self.addCleanup(window.close)
        with mock.patch.object(window, '_start_read85'):
            window.onInit()
        self.assertNotIn(113, window.controls)
        self.assertFalse(window.getControl(114).visible)
        self.assertFalse(window.getControl(110).visible)
        self.assertFalse(window.getControl(103).visible)
        self.assertFalse(window.getControl(104).visible)
        window._paint_facts(dict(channel='Welt HD', title='Report',
                                 subtitle='Belegte Folge', description='Belegter Text',
                                 genre='Doku', cast=['Belegter Name']))
        self.assertEqual(window.getControl(101).label, 'Report')
        self.assertEqual(window.getControl(102).label, 'Belegte Folge')
        self.assertIn('Belegter Name', window.getControl(103).text)
        self.assertFalse(window.getControl(109).visible)

    def test_detail_renders_each_verified_image_in_its_own_role(self):
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON
        from agent_programme100 import fits, view

        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.f.portal, self.f.channel)
        self.addCleanup(window.close)
        window.event = dict(self.event, _detail93=True)
        backdrop = dict(source='agent_tmdb', role81='backdrop', image='/verified/backdrop.png')
        poster = dict(source='agent_tmdb', role81='poster', image='/verified/poster.png')
        with mock.patch('programme_image69.eligible', side_effect=lambda value,event: fits(value,view(event))):
            window._paint_art({},backdrop,poster)
        self.assertEqual(window.getControl(110).image,backdrop['image'])
        self.assertEqual(window.getControl(114).image,poster['image'])

    def test_healthy_explicit_lookup_decodes_correct_bytes_and_reaches_detail_consumer(self):
        self.f.folder.joinpath('settings.xml').write_text('<settings><setting id="programme_tmdb46">true</setting><setting id="tmdb_research43">true</setting></settings>')
        png=io.BytesIO();Image.new('RGB',(1280,720),(27,89,139)).save(png,'PNG');body=png.getvalue()
        class Response(io.BytesIO):status=200;headers={'Content-Type':'image/png'}
        def api(url,**kwargs):
            row=dict(id=6801,title='Synthetic Artwork482',name='Synthetic Artwork482',release_date='2024-01-01',first_air_date='2024-01-01',backdrop_path='/artwork482.png')
            return dict(total_pages=1,total_results=1,results=[row]) if '/search/' in url else row
        def check(url,cancel=lambda:False):
            from programme_transport77 import verified
            return verified(url,cancel,connect=lambda *args:Response(body),resolver=lambda *args:['93.184.216.34'],keep_data81=True)
        with mock.patch('media_sources43.get',side_effect=api),mock.patch('tmdb_token61.effective_tmdb_read_token',return_value='SYNTHETIC_NOT_REAL'),mock.patch('home_schedule75.applicable',return_value=False),mock.patch('artwork_display84.observe',return_value=False):
            value=importlib.import_module('programme_urls55').resolve(self.event,allow_lookup=True,url_mode69=True,check=check)
            self.requests.completed(self.event,value);art=self.requests.result(self.event)
        self.assertEqual(art['source'],'tmdb_movie');self.assertEqual(art['status68'],'LOCAL_IMAGE_READY')
        with Image.open(art['image']) as decoded:self.assertEqual(decoded.getpixel((20,20)),(27,89,139))
        from programme_window46 import ProgrammeWindow46
        from xcmate027_fixture import ADDON
        window=ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
        window.configure(self.f.portal,self.f.channel);window._ready=True;window.event=self.event;self.addCleanup(window.close)
        window.pump()
        self.assertTrue(window.getControl(110).visible);self.assertEqual(window.getControl(110).image,art['image'])


class HeroStatus482(unittest.TestCase):
    def setUp(self):
        self.f=handoff.Handoff63(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.read();self.hero=importlib.import_module('hero_epg63')
        self.hero._next=0;self.hero._last=None;self.hero._focus=None;self.hero._art=None
        from localization import tr
        self.labels={'XCMate.NoEpg63':tr(36102),'XCMate.RemainingFormat63':tr(36668,'{0}'),
                     'XCMate.Home50':'true','XCMate.PortalId':'p','XCMate.MediaId':'1','XCMate.WidgetToken41':'1'*32}

    def poll(self,code):
        label=lambda expr:self.labels.get(expr.removeprefix('ListItem.Property(').removesuffix(')'), '')
        with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmc.getInfoLabel',side_effect=label),mock.patch('programme_requests68.request',return_value=True),mock.patch('programme_requests68.result',return_value=dict(code=code,source='placeholder')):
            self.hero._next=0;self.hero.poll()
        prefix='XCMate.Hero63.'+self.f.properties.get('XCMate.Hero63.Active','')+'.'
        return {key[len(prefix):]:value for key,value in self.f.properties.items() if key.startswith(prefix)}

    def test_live_bank_carries_loading_and_specific_failure_into_existing_description_binding(self):
        for code,word in (('RUNNING','Bildsuche'),('SETTINGS_XML_INVALID','Einstellungen'),('IMAGE_EPG_DISABLED','deaktiviert')):
            with self.subTest(code=code):
                bank=self.poll(code)
                self.assertEqual(bank.get('ArtStatus'),code)
                self.assertIn(word.casefold(),bank.get('Description','').casefold())
                self.assertIn('Local description',bank['Description'])

    def test_terminal_results_have_visible_sanitized_reason_in_existing_hero_binding(self):
        for code,word in (('RESERVE_BLOCKED','Reserve'),('NO_IMAGE','kein'),('NO_MATCH','kein'),
                          ('HTTP_AUTH','Zugriff'),('HTTP_RATE_LIMIT','Anfragen'),('TIMEOUT','Zeitbudget'),
                          ('BLOCKED_IMAGE_HOST_OR_URL','Sicherheit')):
            with self.subTest(code=code):
                bank=self.poll(code)
                self.assertEqual(bank['ArtStatus'],code)
                self.assertIn(word.casefold(),bank['ArtStatusText'].casefold())
                self.assertIn(bank['ArtStatusText'],bank['Description'])
        state=importlib.import_module('programme_state482')
        self.assertNotIn('SYNTHETIC_PRIVATE_URL',state.text({'code':'SYNTHETIC_PRIVATE_URL'}))

    def test_native_status_fixture_uses_verified_revision_and_publishes_without_database_writes(self):
        from tools.kodi_home88_host.status_fixture482 import build
        bridge=self.f.bridge;original=bridge.get('p','1')
        self.assertIsNotNone(original)
        info=build('p',self.f.row,importlib.import_module('time').time(),original)
        self.assertEqual(info['snapshot_revision'],original['snapshot_revision'])
        with mock.patch('sqlite3.connect',side_effect=AssertionError('RAM_FIXTURE_SQL')):
            bridge.remember('p',self.f.row,dict(info,snapshot_revision=('native-status482',1)),{})
            self.assertIsNone(bridge.get('p','1',mappings={}))
            bridge.remember('p',self.f.row,info,{})
            published=bridge.get('p','1',mappings={})
        self.assertIsNotNone(published)
        self.assertEqual(published['now'],'Native status482')
        self.assertTrue(published['programme_key47'])

    def test_channel_without_event_never_inherits_previous_event_status(self):
        self.poll('RUNNING');self.labels['XCMate.MediaId']='2';self.labels['XCMate.WidgetToken41']='2'*32
        bank=self.poll('RUNNING')
        self.assertEqual(bank.get('ArtStatus'),'')
        self.assertNotIn('Bildsuche',bank.get('Description',''))


if __name__=='__main__':unittest.main()
