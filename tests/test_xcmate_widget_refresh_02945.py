"""Existing native Home rows, exact clicks and worker/GUI ownership boundaries."""
import importlib,json,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class ListControl:
    def __init__(self,items):self.items=items;self.position=0;self.resets=0
    def size(self):return len(self.items)
    def getListItem(self,i):return self.items[i]
    def getSelectedPosition(self):return self.position
    def selectItem(self,i):self.position=i
    def reset(self):self.items=[];self.position=0;self.resets+=1
    def addItems(self,items):self.items.extend(items)

class WidgetRefresh45(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.w=importlib.import_module('widget_refresh45');self.i=importlib.import_module('widget_items45')
        self.w._next=0;self.w._scan_at=0;self.w._ids=[];self.w._seen={};self.w._last_code={};self.w._cursor=0
    def row(self,sid='1',kind='vod',name='Film'):return dict(sid=sid,kind=kind,name=name,added_at=self.now,cover='')
    def frame(self,rows,kind='vod'):
        self.assertTrue(self.w.publish(self.portal,kind,rows));return self.w.read('p',kind)
    def control(self,rows,kind='vod'):
        return ListControl([self.i.item(self.i.describe(self.portal,kind,r,{})) for r in rows])
    def home(self,control):
        window=types.SimpleNamespace(getFocusId=lambda:510,getControl=lambda cid:control)
        stack=[]
        for target,attrs in [(sys.modules['xbmc'],dict(getSkinDir=lambda:'skin.titan.bingie.mod',getCondVisibility=lambda _:False)),(sys.modules['xbmcgui'],dict(getCurrentWindowId=lambda:10000,getCurrentWindowDialogId=lambda:0,Window=lambda _:window))]:
            for k,v in attrs.items():p=mock.patch.object(target,k,v,create=True);p.start();self.addCleanup(p.stop)
        p=mock.patch.object(self.w,'container_ids',return_value=[510]);p.start();self.addCleanup(p.stop)
    def test_existing_home_binding_updates_new_title_without_new_shortcut_or_root(self):
        old=[self.row('1'),self.row('2')];control=self.control(old);control.position=1;self.home(control)
        self.frame([self.row('3'),*old]);self.w.poll()
        self.assertEqual([x.getProperty('XCMate.MediaId') for x in control.items],['3','1','2']);self.assertEqual(control.position,2)
        self.assertTrue(all('action=media_detail' in x.getProperty('XCMate.ClickTarget44') for x in control.items));self.assertFalse(self.builtins)
    def test_identical_frame_never_resets_or_reassigns_items_or_focus(self):
        rows=[self.row()];control=self.control(rows);self.home(control);self.frame(rows);self.w.poll();before=list(control.items)
        with mock.patch.object(control,'reset',side_effect=AssertionError('unchanged reset')):
            for _ in range(20):self.w._next=0;self.w.poll()
        self.assertEqual(control.items,before);self.assertEqual(control.resets,0)
    def test_epg_and_art_delta_update_in_place_without_list_reset(self):
        control=self.control([self.row()]);frame=self.frame([self.row(name='Corrected')]);self.w.apply(control,frame,['1'])
        self.assertEqual(control.items[0].label,'Corrected');self.assertEqual(control.resets,0)
    def test_foreign_item_portal_or_url_prevents_entire_container_write(self):
        for change in [('XCMate.WidgetKind41','other'),('XCMate.ClickTarget44','plugin://foreign/?action=media_detail'),('XCMate.PortalId','other')]:
            control=self.control([self.row()]);control.items[0].setProperty(*change);self.assertIsNone(self.w.binding(control));self.assertEqual(control.resets,0)
    def test_only_verified_legacy_all_titles_footer_is_removed(self):
        control=self.control([self.row()]);footer=sys.modules['xbmcgui'].ListItem('All movies');footer.getPath=lambda:'plugin://plugin.video.xtreammate/?action=movies_home&pid=p';control.items.append(footer)
        own=self.w.binding(control);self.assertEqual(own[2],['1','__legacy_directory45']);self.w.apply(control,self.frame([self.row()]),own[2]);self.assertEqual(control.size(),1)
    def test_wrong_footer_is_not_mistaken_for_own_widget(self):
        control=self.control([self.row()]);footer=sys.modules['xbmcgui'].ListItem('Other');footer.getPath=lambda:'plugin://plugin.video.xtreammate/?action=movies_home&pid=foreign';control.items.append(footer);self.assertIsNone(self.w.binding(control))
    def test_failed_or_zero_worker_result_keeps_last_good_publication(self):
        frame=self.frame([self.row()]);before=Path(self.w.path('p','vod')).read_bytes()
        self.assertFalse(self.w.publish(self.portal,'vod',[]));self.assertFalse(self.w.publish(self.portal,'vod',[self.row('2')],'BUDGET'));self.assertEqual(Path(self.w.path('p','vod')).read_bytes(),before)
    def test_new_interpreter_reads_atomic_published_frame(self):
        first=self.frame([self.row()]);spec=importlib.util.spec_from_file_location('separate_widget45',Path(self.w.__file__));other=importlib.util.module_from_spec(spec);spec.loader.exec_module(other)
        self.assertEqual(other.read('p','vod'),first);self.assertIsNone(other.read('other','vod'))
    def test_cancelled_foreign_modal_or_active_player_defers_gui_publication(self):
        control=self.control([self.row()]);self.home(control);self.frame([self.row('2')])
        with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=10138):self.w.poll()
        self.w._next=0
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):self.w.poll()
        self.assertEqual(control.items[0].getProperty('XCMate.MediaId'),'1');self.assertEqual(control.resets,0)
    def test_three_existing_source_urls_have_only_real_title_tiles_and_exact_clicks(self):
        for action,kind in [('widget_live_start_group','live'),('widget_recent_vod','vod'),('widget_recent_series','series')]:
            self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
            self.assertTrue(self.added);self.assertTrue(all(li.props.get('XCMate.WidgetKind41')==kind for _,li,_ in self.added))
            for url,li,folder in self.added:self.assertEqual(url,li.props['XCMate.ClickTarget44']);self.assertIn('sid='+li.props['XCMate.MediaId'],url);self.assertFalse(folder)
    def test_live_publication_uses_actual_local_epg_and_guide_progress(self):
        guide=importlib.import_module('guide_store');guide.import_cache('p',{'xml':[dict(name='Actual news',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        frame=self.frame([dict(self.row(kind='live'),epg_channel_id='xml')],kind='live');value=frame['items'][0]
        self.assertEqual(value['props']['XtreamMate.Now'],'Actual news');self.assertTrue(value['props']['XCMate.EpgPercent41']);self.assertIn('action=play_live',value['url'])
    def test_corrupt_oversized_or_expired_frame_is_not_published_to_home(self):
        path=Path(self.w.path('p','vod'))
        for data in ['{', 'x'*(self.w.MAX_BYTES+1),json.dumps(dict(pid='p',kind='vod',at=time.time()-601,items=[{}]))]:path.write_text(data);self.assertIsNone(self.w.read('p','vod'))
