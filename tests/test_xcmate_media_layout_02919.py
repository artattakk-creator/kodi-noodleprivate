"""Geometry/layering contracts, not a claim of real Kodi/TV rendering."""
import unittest
from xcmate027_fixture import Fixture


class CompactPosterTests(Fixture,unittest.TestCase):
    def test_movies_and_series_keep_title_font_size_independent_of_smaller_poster(self):
        for kind in ('vod','series'):
            w=self.media_window(kind)
            for cid in (110,111,112,210):
                for tag in ('itemlayout','focusedlayout'):
                    layout=w.getControl(cid).node.find(tag)
                    poster=next(c for c in layout.findall('control') if 'ListItem.Art(poster)' in c.findtext('texture',''))
                    self.assertEqual((poster.findtext('width'),poster.findtext('height')),('108','162'))
                    title=layout.find('control[@type="textbox"]')
                    self.assertEqual(title.findtext('font'),'font13')
                    self.assertGreaterEqual(int(title.findtext('width')),164)
                    self.assertGreaterEqual(int(title.findtext('height')),56)
                    self.assertGreater(int(title.findtext('top')),int(poster.findtext('top'))+162)
                    self.assertLessEqual(int(title.findtext('top'))+int(title.findtext('height')),int(layout.get('height')))

    def test_dual_contrast_native_focus_frame_surrounds_poster_and_does_not_cover_it(self):
        w=self.media_window()
        for cid in (110,111,112,210):
            layout=w.getControl(cid).node.find('focusedlayout');images=layout.findall('control[@type="image"]')
            self.assertEqual(len(images),3)
            black,neon,poster=images
            self.assertEqual(black.find('texture').get('colordiffuse'),'FF000000')
            self.assertIsNone(neon.find('texture').get('colordiffuse'))
            for frame in (black,neon):
                self.assertTrue(frame.findtext('texture').endswith('xcmate_focus_neon.png'))
                self.assertEqual(frame.findtext('visible'),'Control.HasFocus(%s)'%cid)
                self.assertLess(int(frame.findtext('left')),int(poster.findtext('left')))
                self.assertLess(int(frame.findtext('top')),int(poster.findtext('top')))
                self.assertGreater(int(frame.findtext('width')),108)
                self.assertGreater(int(frame.findtext('height')),162)
            self.assertLessEqual(int(black.findtext('left'))+int(black.findtext('width')),int(layout.get('width')))

    def test_horizontal_ir_and_back_keep_selected_cover_in_every_rail_and_media_kind(self):
        for kind in ('vod','series'):
            for sid in ('1','2','3'):self.state.toggle('p',kind,sid)
            if kind=='vod':
                for sid in ('1','2','3'):self.state.save_progress(dict(pid='p',kind=kind,sid=sid),300,1200)
            else:
                for sid in ('1','2','3'):self.state.save_progress(dict(pid='p',kind='episode',sid=sid+'1',series_id=sid,season=1,episode=1),300,1200)
            w=self.media_window(kind)
            for cid in (112,111,110):
                w.setFocusId(cid);w.native(2);pos=w.getControl(cid).getSelectedPosition()
                rows=w.rows if cid==110 else w.rails[cid];sid=rows[pos]['sid']
                w.native(7);self.settle(w);w.native(92);self.settle(w)
                self.assertEqual(w.getFocusId(),cid)
                rows=w.rows if cid==110 else w.rails[cid]
                self.assertEqual(rows[w.getControl(cid).getSelectedPosition()]['sid'],sid)
            self.assertFalse(self.builtins)

    def test_compact_rows_fit_scroll_viewport_and_keep_category_column_contract(self):
        w=self.media_window()
        self.assertEqual(w.getControl(612).height,288)
        self.assertEqual(w.getControl(110).node.find('itemlayout').get('width'),'180')
        self.assertEqual(w.getControl(210).node.find('itemlayout').get('width'),'190')
        w.native(3);self.assertEqual(w.getFocusId(),120)
        w.native(2);self.assertEqual(w.getFocusId(),400)
        w.setFocusId(120);w.native(7);self.settle(w)
        self.assertEqual((w._cols,w.getControl(210).width),(4,916))
        w.setFocusId(200);w.native(2)
        self.assertEqual((w._cols,w.getControl(210).width),(4,916));self.assertEqual(w.getControl(210).selected,0)
        w.native(2)
        self.assertEqual((w._cols,w.getControl(210).width),(6,1192));self.assertEqual(w.getControl(210).selected,1)


if __name__=='__main__':unittest.main()
