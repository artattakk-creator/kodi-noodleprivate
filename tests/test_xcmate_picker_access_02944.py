"""Metadata has its own discoverable entry and never depends on a usable image."""
import importlib,sys,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON

class PickerAccess44(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.mod=importlib.import_module('media_picker43');self.parent=self.media_window();self.parent._details(self.parent.rows[0]);self.settle(self.parent)
    def picker(self,metadata=True):
        self.parent._picker_mode44=metadata;p=self.mod.ArtworkPicker('XCMateArtwork43.xml',str(ADDON),'Default','720p');p.configure(self.parent);self.addCleanup(p.close)
        self.jobs=[];p._submit=lambda fn,apply:self.jobs.append((fn,apply))
        with mock.patch.object(p,'_source'):p.show()
        return p
    def test_separate_metadata_menu_is_visible_and_request_is_owner_deferred(self):
        self.parent.native(1);control=self.parent.getControl(810);self.assertEqual(control.size(),7);self.assertIn('Metadaten',control.items[6].label)
        control.selectItem(6)
        with mock.patch.object(self.mod,'ArtworkPicker') as window:self.parent.onClick(810);window.assert_not_called()
        self.assertTrue(self.parent._picker_mode44);self.assertEqual(self.parent._picker_requested43,('p','vod',self.parent.selected['sid']))
    def test_metadata_preview_works_with_no_image_and_requires_separate_confirmation(self):
        p=self.picker();p._results([dict(name='Metadata',source='provider',url='',role='poster',attribution='Provider',metadata={'plot':'New plot'})]);p._preview()
        self.assertEqual(p.getFocusId(),507);self.assertFalse(p.getControl(300).visible);self.assertFalse(p.getControl(501).visible);self.assertFalse(self.jobs)
        self.dialog.multiselect=mock.Mock(return_value=[0]);self.dialog.yesno.return_value=False;p.onClick(507)
        fn,apply=self.jobs.pop();apply(fn());self.assertFalse(self.jobs);self.assertFalse(p.changed);self.assertFalse((self.folder/'media_choices43').exists())
    def test_tmdb_disabled_and_missing_token_are_distinct_before_keyboard_or_network(self):
        p=self.picker()
        for options,code in [({},'TMDB_DISABLED'),({'tmdb_research43':True},'TMDB_TOKEN_MISSING')]:
            self.options.clear();self.options.update(options);self.dialog.input.reset_mock();p._source('tmdb')
            self.assertIn(code,p.getControl(103).label);self.dialog.input.assert_not_called();self.assertFalse(self.jobs)
    def test_commons_and_local_images_explain_no_metadata_without_download_or_browse(self):
        p=self.picker();p._source('commons');self.assertIn('NO_METADATA',p.getControl(103).label);self.assertFalse(self.jobs)
        self.dialog.browseSingle=mock.Mock();p.onClick(404);self.dialog.browseSingle.assert_not_called()
    def test_metadata_candidate_without_poster_is_available_and_never_automatic_cover(self):
        source=importlib.import_module('media_sources43');self.options.update(tmdb_research43=True,tmdb_read_token43='private-read-token')
        with mock.patch.object(source,'get',return_value={'results':[{'id':9,'title':'Aladdin','release_date':'1992-11-25','overview':'Plot'}]}):rows=source.tmdb('Aladdin','vod')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['url'],'');self.assertEqual(rows[0]['metadata']['plot'],'Plot')
        fallback=importlib.import_module('media_metadata43');fallback._cache.clear();fallback._next=0;self.options['tmdb_fallback43']=True
        item=dict(kind='vod',name='Aladdin',year=1992,sid='1')
        with mock.patch.object(source,'tmdb',return_value=rows):self.assertEqual(fallback.fallback(item,'vod'),item)
    def test_source_failure_messages_are_distinct_and_never_expose_exception_text(self):
        status=importlib.import_module('picker_status44')
        messages={status.message(code,'tmdb') for code in ('TMDB_DISABLED','TMDB_TOKEN_MISSING','HTTP_AUTH','TIMEOUT','NO_RESULTS','SAVE_FAILED')}
        self.assertEqual(len(messages),6)
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):status.mark('ERROR','tmdb','https://private.invalid/SECRET')
        self.assertNotIn('SECRET',str(log.call_args_list));self.assertIn('OTHER',str(log.call_args_list))
    def test_episode_details_allow_series_art_and_restore_valid_episode_focus(self):
        w=self.media_window('series');w._details(w.rows[0]);self.settle(w);w.seasons=sorted({e['season'] for e in w.episodes});w.season=w.seasons[0];w.mode='episodes';w._show_episodes();w.setFocusId(330)
        self.assertTrue(w._detail_menu_show());self.assertEqual(w.getFocusId(),810);w._detail_menu_close();self.assertEqual(w.getFocusId(),330)
        self.mod.request(w,metadata=True);self.assertEqual(w._picker_requested43[1:],(w.kind,w.selected['sid']))
    def test_normal_grid_left_is_not_misreported_as_broken_detail_menu(self):
        w=self.parent;w.mode='grid'
        with mock.patch('detail_menu.mark') as mark:self.assertFalse(w._detail_menu_action(1));mark.assert_not_called()
