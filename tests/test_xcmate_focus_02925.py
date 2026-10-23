"""Delayed native visibility, semantic actions and Premium render ordering."""
import importlib
from pathlib import Path
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from xcmate027_fixture import Fixture, ADDON


class FocusTests(Fixture, unittest.TestCase):
    def test_delayed_detail_visibility_never_commits_search_and_recovers_on_owner(self):
        w=self.media_window();control=w.getControl(300)
        with mock.patch.object(control,'isVisible',return_value=False):
            w._details(w.rows[0]);w._pool.drain()
            with mock.patch.object(w,'_search') as search:
                w.onClick(400)
            search.assert_not_called()
            self.assertNotEqual(w._mode_focus.get('detail'),400)
        w._owner_tick()
        self.assertEqual(w.getFocusId(),300)
        self.assertIsNone(w._focus_pending)

    def test_metadata_refresh_keeps_explicit_search_and_down_returns_to_actions(self):
        w=self.media_window();w._details(w.rows[0]);w._pool.drain()
        w.setFocusId(400);w._detail_ready((w.selected,{}))
        self.assertEqual(w.getFocusId(),400)
        with mock.patch.object(w,'_search') as search:w.onClick(400)
        search.assert_called_once()
        w.native(4)
        self.assertEqual(w.getFocusId(),300)

    def test_new_detail_does_not_inherit_search_or_old_action_index(self):
        w=self.media_window();w._details(w.rows[0]);w._pool.drain()
        w.getControl(300).selectItem(len(w.actions)-1);w.setFocusId(400)
        w._details(w.rows[1]);w._pool.drain()
        self.assertEqual(w.getFocusId(),300)
        self.assertEqual(w.getControl(300).getSelectedPosition(),0)
        with mock.patch.object(w,'_play') as play, mock.patch.object(w,'_search') as search:
            w.native(7)
        play.assert_called_once();search.assert_not_called()

    def test_refresh_preserves_selected_action_identity(self):
        w=self.media_window();w._details(w.rows[0]);w._pool.drain()
        pos=next(i for i,a in enumerate(w.actions) if a[1]=='favourite')
        w.getControl(300).selectItem(pos);w._detail_ready((w.selected,{}))
        self.assertEqual(w.actions[w.getControl(300).getSelectedPosition()][1],'favourite')
        self.assertEqual(w.getFocusId(),300)

    def test_stale_search_callback_is_ignored_when_actions_have_focus(self):
        w=self.media_window();w._details(w.rows[0]);w._pool.drain()
        with mock.patch.object(w,'_search') as search:w.onClick(400)
        search.assert_not_called()

    def test_late_detail_focus_is_cancelled_by_back_without_reopening(self):
        w=self.media_window()
        with mock.patch.object(w.getControl(300),'isVisible',return_value=False):
            w._details(w.rows[0]);w.native(92);self.settle(w)
        w._owner_tick()
        self.assertEqual(w.mode,'landing');self.assertIsNone(getattr(w,'_focus_pending',None))
        self.assertIn(w.getFocusId(),w._valid_focus())

    def test_series_and_fullscreen_return_keep_action_focus(self):
        w=self.media_window('series')
        with mock.patch.object(w.getControl(300),'isVisible',return_value=False):
            w._details(w.rows[0]);w._pool.drain()
        w._owner_tick();self.assertEqual(w.getFocusId(),300)
        w.onInit();self.assertEqual(w.getFocusId(),300)
        self.assertTrue(w.actions)


class RenderTests(Fixture, unittest.TestCase):
    def test_premium_keeps_core_focus_and_shade_below_focus_and_text(self):
        import sys
        # Run renderer against a deterministic asset resolver; real-package
        # install, IDs and image hashes remain covered by the .24 port tests.
        renderer=importlib.import_module('theme_render')
        fake=type('Assets',(),{'asset':staticmethod(lambda key,fallback='',snapshot=None:'/premium/'+key+'.png')})
        tree=ET.parse(ADDON/'resources/skins/Default/720p/XCMateMedia.xml')
        before=sum(1 for n in tree.iter() if (n.text or '').endswith('xcmate_focus_neon.png'))
        with mock.patch.dict(sys.modules,{'theme_store':fake}):
            renderer.apply_xml(tree,{},'XCMateMedia.xml')
        self.assertGreater(before,0)
        self.assertEqual(sum(1 for n in tree.iter() if (n.text or '').endswith('xcmate_focus_neon.png')),before)
        for layout in tree.iter('focusedlayout'):
            children=list(layout)
            shade=[n for n in children if 'poster.shade' in n.findtext('texture','')]
            self.assertEqual(shade,[])
        for layout in tree.iter('itemlayout'):
            children=list(layout)
            for index,node in enumerate(children):
                if 'poster.shade' in node.findtext('texture',''):
                    self.assertEqual(children[index-1].findtext('texture'),'$INFO[ListItem.Art(poster)]')

    def test_generated_premium_focus_is_opaque_and_cache_path_changes(self):
        import sys,hashlib
        renderer=importlib.import_module('theme_render');appearance=importlib.import_module('appearance')
        # No install needed to verify renderer cache namespace/alpha contract.
        theme=dict(revision='previous-revision',spec=dict(palette={}))
        values=dict(appearance.DEFAULT,icon_opacity=25,panel_opacity=25,text='000000')
        fake=type('Assets',(),{'asset':staticmethod(lambda key,fallback='',snapshot=None:'/premium/'+key+'.png')})
        with mock.patch.dict(sys.modules,{'theme_store':fake}),mock.patch.object(renderer,'snapshot',return_value=theme),mock.patch.object(appearance,'read',return_value=values):
            directory=appearance.window_source('XCMateMedia.xml')
        old=hashlib.sha256(theme['revision'].encode()).hexdigest()[:16]
        self.assertNotIn('ui_'+old+'_',directory)
        tree=ET.parse(Path(directory)/'resources/skins/Default/720p/XCMateMedia.xml')
        for node in tree.iter():
            if (node.text or '').endswith('xcmate_focus_neon.png'):
                self.assertIn(node.get('colordiffuse'),(None,'FF000000'))
        for layout in tree.iter('focusedlayout'):
            for text in layout.iter('textcolor'):self.assertEqual(text.text,'FFF0F2F5')


if __name__=='__main__':unittest.main()
