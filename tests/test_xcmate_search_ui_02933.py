"""Typed rich search rows with local artwork and stable native IR focus."""
import base64,hashlib,importlib,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aKhkAAAAASUVORK5CYII=')


class SearchUI33(Fixture,unittest.TestCase):
    def query(self,kind='vod'):
        w=self.media_window();self.dialog.input.return_value='House';w._search();self.settle(w)
        w.onClick({'live':700,'vod':701,'series':702}[kind]);self.settle(w);return w

    def cache_image(self,url):
        art=importlib.import_module('media_art');root=Path(art.folder());root.mkdir(exist_ok=True)
        target=root/(hashlib.sha256(url.encode()).hexdigest()+'.img');target.write_bytes(PNG);return str(target)

    def test_live_name_hit_shows_local_now_title_without_claiming_programme_match(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml':[dict(channel='xml',name='Actual broadcast',start_timestamp=self.now-60,stop_timestamp=self.now+300)]})
        self.catalogs['get_live_streams'][0]['stream_icon']='https://image.invalid/logo'
        self.index.replace_catalog('p','live',self.catalogs['get_live_streams'],self.catalogs['get_live_categories'])
        path=self.cache_image('https://image.invalid/logo');w=self.query('live');item=w.getControl(710).getListItem(0)
        self.assertEqual(item.getProperty('XCMate.SearchKind'),'live');self.assertIn('Actual broadcast',item.getProperty('XCMate.SearchSecondary'))
        self.assertEqual(item.label,'House of Dragon TV');self.assertFalse(w._search_rows[0]['_now_match'])
        self.assertEqual(item.art['thumb'],path);sys.modules['utils'].http_get.assert_not_called()

    def test_movie_and_series_have_cached_poster_primary_title_and_type(self):
        for kind in ('vod','series'):
            with self.subTest(kind=kind):
                method='get_vod_streams' if kind=='vod' else 'get_series'
                rows=self.catalogs[method];rows[0].update(cover='https://image.invalid/'+kind,year='2024',genre='Drama')
                self.index.replace_catalog('p',kind,rows,self.catalogs['get_vod_categories' if kind=='vod' else 'get_series_categories'])
                path=self.cache_image('https://image.invalid/'+kind);w=self.query(kind)
                pos=next(i for i,r in enumerate(w._search_rows) if r['sid']=='1');item=w.getControl(710).getListItem(pos)
                self.assertEqual(item.getProperty('XCMate.SearchKind'),kind);self.assertEqual(item.art['poster'],path)
                self.assertIn('2024',item.getProperty('XCMate.SearchSecondary'));self.assertIn('Drama',item.getProperty('XCMate.SearchSecondary'))
                self.assertIn('House of Dragon',item.label);self.assertFalse(w._leaving)

    def test_missing_artwork_and_epg_use_safe_local_type_fallbacks(self):
        from search_results import item
        for kind,name in (('live','tv.png'),('vod','vod.png'),('series','series.png')):
            row=item(dict(kind=kind,name='Known title'))
            self.assertTrue(row.art['poster'].endswith(name));self.assertTrue(Path(row.art['poster']).is_file())
            self.assertTrue(row.getProperty('XCMate.SearchSecondary'));self.assertEqual(row.label,'Known title')
        sys.modules['utils'].http_get.assert_not_called()

    def test_rich_xml_has_two_noninteractive_artwork_shapes_and_two_text_lines(self):
        w=self.query();control=w.tree.find("./controls/control[@id='710']")
        for tag in ('itemlayout','focusedlayout'):
            layout=control.find(tag);self.assertEqual(layout.get('height'),'100')
            textures=[n.findtext('texture') for n in layout.findall("control[@type='image']")]
            self.assertIn('$INFO[ListItem.Art(thumb)]',textures);self.assertIn('$INFO[ListItem.Art(poster)]',textures)
            labels=[n.findtext('label') for n in layout.findall("control[@type='label']")]
            self.assertIn('$INFO[ListItem.Label]',labels);self.assertIn('$INFO[ListItem.Property(XCMate.SearchSecondary)]',labels)
            self.assertFalse(layout.findall("control[@type='button']"))

    def test_downloaded_poster_refreshes_existing_item_without_reset_or_focus_change(self):
        w=self.query();w.setFocusId(710);w.getControl(710).selectItem(2)
        row=w._search_rows[2];url=row['stream_icon'];li=w.getControl(710).getListItem(2)
        path=self.cache_image(url);w._search_art_poll=0;w._search_art_revision=None
        with mock.patch.object(w,'_fill',wraps=w._fill) as fill:w._search_tick()
        fill.assert_not_called();self.assertIs(w.getControl(710).getListItem(2),li)
        self.assertEqual(li.art['poster'],path);self.assertEqual(w.getFocusId(),710);self.assertEqual(w.getControl(710).getSelectedPosition(),2)

    def test_switch_tabs_and_select_movie_then_back_keeps_native_controls(self):
        w=self.query('live')
        for cid,kind in ((701,'vod'),(702,'series'),(700,'live'),(701,'vod')):
            w.onClick(cid);self.settle(w);self.assertEqual(w._search_kind,kind)
            self.assertEqual(w.getFocusId(),cid);self.assertTrue(all(item.getProperty('XCMate.SearchKind')==kind for item in w.getControl(710).items))
        w.native(4);w.native(7);self.settle(w);self.assertEqual(w.mode,'detail')
        w.native(92);self.settle(w);self.assertEqual(w.mode,'search');self.assertIn(w.getFocusId(),w._valid_focus());self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()
