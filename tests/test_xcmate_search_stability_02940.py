"""Confirmed search pages survive pending/enrichment/out-of-order tab replies."""
import importlib,sys,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class SearchPages40(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.pages=importlib.import_module('search_snapshot')
    def view(self):
        w=self.media_window();w._open_search('House');self.settle(w);return w
    def pending(self,w,kind,code='INDEX_PENDING'):
        w._search_ready({kind:dict(rows=[],total=None,code=code),'_view':(kind,w._search_offset)})

    def test_twenty_tab_cycles_keep_confirmed_results_when_replies_are_pending(self):
        w=self.view();expected={k:list(v['rows']) for k,v in w._search_data.items()}
        # Disable requests to replay deterministic delayed partial worker replies.
        with mock.patch.object(w,'_search_load'):
            for _ in range(20):
                for cid,kind in ((700,'live'),(701,'vod'),(702,'series')):
                    w._search_click(cid);self.pending(w,kind)
                    self.assertEqual([r['sid'] for r in w._search_rows],[r['sid'] for r in expected[kind]])
                    self.assertFalse(w._search_loading)

    def test_final_confirmed_zero_replaces_old_rows_but_pending_error_does_not(self):
        w=self.view();before=list(w._search_rows)
        for code in ('INDEX_PENDING','INDEX_ERROR','GENRE_PENDING'):
            self.pending(w,w._search_kind,code);self.assertEqual(w._search_rows,before)
        w._search_ready({w._search_kind:dict(rows=[],total=0,code='READY'),'_view':(w._search_kind,0)})
        self.assertEqual(w._search_rows,[]);self.assertEqual(w.getControl(710).size(),0)

    def test_no_list_reset_or_cover_replacement_for_identical_or_pending_rows(self):
        w=self.view();control=w.getControl(710);items=list(control.items);control.selectItem(7);w.setFocusId(710)
        with mock.patch.object(control,'reset',side_effect=AssertionError('unnecessary ListItem rebuild')):
            for _ in range(20):self.pending(w,w._search_kind);w._search_ready(w._search_data)
        self.assertEqual(control.items,items);self.assertEqual(control.getSelectedPosition(),7)
        self.assertEqual(w.getFocusId(),710)

    def test_epg_metadata_changes_update_existing_items_without_resetting_names(self):
        w=self.view();w._search_click(700);self.settle(w);items=list(w.getControl(710).items)
        rows=[dict(r,_now_title='Updated programme') for r in w._search_rows]
        with mock.patch.object(w.getControl(710),'reset',side_effect=AssertionError('EPG rebuild')):
            w._search_ready(dict(live=dict(rows=rows,total=len(rows),code='READY'),_view=('live',0)))
        self.assertEqual(w.getControl(710).items,items)
        self.assertIn('Updated programme',items[0].props['XCMate.SearchSecondary'])

    def test_each_kind_has_independent_second_page_and_position(self):
        w=self.view();w.onClick(721);self.settle(w);second=[r['sid'] for r in w._search_rows];w.getControl(710).selectItem(4)
        w._search_click(702);self.settle(w);w._search_click(701);self.settle(w)
        self.assertEqual(w._search_offset,48);self.assertEqual([r['sid'] for r in w._search_rows],second)
        self.assertEqual(w.getControl(710).getSelectedPosition(),4)
        # Late page zero reply cannot replace visible page 48.
        w._search_ready(dict(vod=dict(rows=[dict(sid='other',name='page zero')],total=100,code='READY'),_view=('vod',0)))
        self.assertEqual([r['sid'] for r in w._search_rows],second)

    def test_new_query_cancels_old_callback_and_does_not_inherit_confirmed_rows(self):
        w=self.view();w._open_search('House');old_apply=w._pending_apply;old_cancel=w._search_cancel
        w._open_search('No matching titles');old_apply(dict(vod=dict(rows=[dict(sid='stale',name='House')],total=1,code='READY')))
        self.assertTrue(old_cancel.is_set());self.settle(w)
        self.assertEqual(w._search_rows,[]);self.assertEqual(w._search_query,'No matching titles')

    def test_portal_switch_rejects_old_worker_callback_even_with_same_query(self):
        w=self.view();w._search_load();apply=w._pending_apply;before=w._search_data
        w.portal=dict(w.portal,id='different');apply(dict(vod=dict(rows=[dict(sid='stale')],total=1,code='READY')))
        self.assertIs(w._search_data,before)

    def test_page_cache_is_bounded_and_final_disabled_is_authoritative(self):
        pages=self.pages.Pages(('p','Rock','session','category'))
        for offset in range(0,48*40,48):pages.publish(dict(vod=dict(rows=[dict(sid=str(offset))],total=2000,code='READY')),('vod',offset))
        self.assertEqual(len(pages.pages),24)
        pages.publish(dict(vod=dict(rows=[],total=0,code='DISABLED')),('vod',48*39))
        self.assertEqual(pages.section('vod',48*39)['rows'],[])

    def test_film_and_series_pages_publish_before_expensive_epg_prepare(self):
        data=importlib.import_module('search_data')
        first=data.search(self.portal,'House',kind='vod',incremental=True)
        self.assertEqual(first['vod']['code'],'INDEX_PENDING')
        with mock.patch.object(data.LiveSearch,'_prepare',side_effect=AssertionError('EPG before media publication')):
            second=data.search(self.portal,'House',kind='vod',incremental=True,continuation=first['_cursor'])
        self.assertEqual(second['vod']['total'],100);self.assertEqual(len(second['vod']['rows']),48)
        self.assertEqual(second['series']['total'],3);self.assertIs(second['_cursor'],first['_cursor'])
