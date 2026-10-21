"""Native 720p layout contracts and IR order; Android readability NOT_RUN."""
import ast
import importlib
import unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB


class MediaRails299(Fixture,unittest.TestCase):
    def test_header_and_vertical_viewport_have_real_poster_ratio_and_title_area(self):
        w=self.media_window();root=w.tree
        scroll=root.find(".//control[@id='600']")
        self.assertEqual(scroll.get('type'),'grouplist')
        self.assertEqual([int(n.find('control[@type="list"]').get('id')) for n in scroll.findall('control')],[112,111,110])
        self.assertLess(int(w.getControl(120).node.findtext('top')),int(scroll.findtext('top')))
        for cid in (110,111,112):
            layout=w.getControl(cid).node.find('itemlayout')
            poster=layout.find('control[@type="image"]');title=layout.find('control[@type="textbox"]')
            width=int(poster.findtext('width'));height=int(poster.findtext('height'))
            self.assertGreaterEqual(width,150);self.assertLessEqual(width,190)
            self.assertEqual(width*3,height*2)
            self.assertGreaterEqual(int(title.findtext('height')),56)
        self.assertGreater(sum(int(g.findtext('height')) for g in scroll.findall('control')),int(scroll.findtext('height')))

    def test_continue_then_favourites_then_new_and_top_categories_search(self):
        self.state.toggle('p','vod','2')
        self.state.save_progress(dict(pid='p',kind='vod',sid='3'),600,2700)
        w=self.media_window();self.assertEqual(w.getFocusId(),112)
        w.native(4);self.assertEqual(w.getFocusId(),111)
        w.native(4);self.assertEqual(w.getFocusId(),110)
        w.native(3);w.native(3);w.native(3);self.assertEqual(w.getFocusId(),120)
        w.native(2);self.assertEqual(w.getFocusId(),400)
        w.native(4);self.assertEqual(w.getFocusId(),112)
        self.assertFalse(self.builtins)

    def test_empty_rows_shrink_skip_focus_and_do_not_hide_large_new_titles(self):
        w=self.media_window()
        self.assertEqual(w.getControl(610).height,48);self.assertEqual(w.getControl(611).height,48)
        self.assertEqual(w.getControl(612).height,368)
        self.assertNotIn(111,w._valid_focus());self.assertNotIn(112,w._valid_focus())
        w.native(3);self.assertEqual(w.getFocusId(),120)
        w.native(4);self.assertEqual(w.getFocusId(),110)

    def test_favourite_horizontal_position_and_identity_survive_detail_back(self):
        for sid in ('1','2','3'):self.state.toggle('p','vod',sid)
        w=self.media_window();w.setFocusId(111);w.native(2)
        pos=w.getControl(111).getSelectedPosition();sid=w.rails[111][pos]['sid']
        w.native(7);self.settle(w);w.native(92);self.settle(w)
        self.assertEqual(w.getFocusId(),111)
        self.assertEqual(w.rails[111][w.getControl(111).getSelectedPosition()]['sid'],sid)
        importlib.import_module('utils').http_get.assert_not_called()

    def test_kodi_python_never_requests_unwrappable_grouplist(self):
        w=self.media_window()
        with self.assertRaises(AssertionError):w.getControl(600)
        self.assertEqual(w.getControl(620).kind,'group')
        self.assertNotIn('getControl(600)',(LIB/'media_window.py').read_text())

    def test_playback_close_search_and_owner_are_unchanged_from_hotfix(self):
        import json
        frozen=json.loads((Path(__file__).parent/'fixtures/xcmate_0298_ui_freeze.json').read_text())
        import hashlib
        for name,sha in frozen['modules'].items():self.assertEqual(hashlib.sha256((LIB/name).read_bytes()).hexdigest(),sha,name)
        tree=ast.parse((LIB/'media_window.py').read_text())
        for name,signature in frozen['methods'].items():
            fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(fn,include_attributes=False),signature,name)


if __name__=='__main__':unittest.main()
