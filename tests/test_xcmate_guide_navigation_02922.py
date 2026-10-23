"""Group-scoped SQLite, actual native-focus fixture, XML layering and IR routes."""
import importlib
import json
import sys
import time
import types
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET
from PIL import Image
from xcmate027_fixture import Fixture,ADDON,QueuedPool


class GuideNavigationTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('guide_grid_window','guide_grid_data'):
            sys.modules.pop(name,None)
        self.grid=importlib.import_module('guide_grid_window');self.data=importlib.import_module('guide_grid_data')
        patch=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);patch.start();self.addCleanup(patch.stop)
        self.origin=int(time.time())//1800*1800
        self.store=importlib.import_module('guide_store')
        self.store.import_cache('p',{'xml':[dict(channel='xml',name='Current readable title',start_timestamp=self.origin-60,stop_timestamp=self.origin+1800),dict(channel='xml',name='Following readable title',start_timestamp=self.origin+1800,stop_timestamp=self.origin+3600)]},now=self.origin-1000)

    def window(self):
        w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.doModal();self.settle(w);return w

    def key(self,w,k):w.native(k);self.settle(w)

    def large(self,size=2501,start=1979):
        self.index.import_group('p','live','a',[dict(stream_id=str(i),category_id='a',name='Channel '+str(i),epg_channel_id='xml') for i in range(size)])
        self.index.import_group('p','live','b',[dict(stream_id='b'+str(i),category_id='b',name='Group B '+str(i),epg_channel_id='xml') for i in range(13)])
        self.portal.update(start_group_id='a',start_stream_id=str(start))

    def test_start_group_only_and_start_sender_visible_at_original_ordinal_over_2400(self):
        self.large();snapshot=json.dumps(self.portal,sort_keys=True);w=self.window()
        self.assertEqual((w.category,w.total,w.offset,w.row),('a',2501,1976,3))
        self.assertEqual(w.rows[w.row]['channel']['sid'],'1979');self.assertEqual(w.rows[0]['channel']['sid'],'1976')
        self.assertEqual(w.getFocusId(),1000+w.row*24);self.assertEqual(json.dumps(self.portal,sort_keys=True),snapshot)
        self.assertEqual(len(w.rows),8);self.assertTrue(all(row['channel']['category_id']=='a' for row in w.rows))

    def test_readonly_position_keeps_catalog_bytes_and_order(self):
        self.large();before=Path(self.index.path()).read_bytes();reader=self.index.Reader('p')
        self.assertEqual(reader.position('live','1979','a'),1979);self.assertIsNone(reader.position('live','1979','b'))
        self.assertEqual(Path(self.index.path()).read_bytes(),before)
        rows,total=reader.page('live',category='a',limit=2);self.assertEqual([r['sid'] for r in rows],['0','1'])

    def test_invalid_or_disabled_saved_group_falls_back_without_settings_write(self):
        self.portal['start_group_id']='removed';before=dict(self.portal);w=self.window()
        self.assertEqual(w.category,'a');self.assertEqual(w.rows[w.row]['channel']['sid'],'1');self.assertEqual(self.portal,before);self.assertFalse(self.options)

    def test_saved_group_mismatch_falls_back_to_allowed_group_of_start_sender(self):
        self.portal.update(start_group_id='b',start_stream_id='1');w=self.window()
        self.assertEqual(w.category,'a');self.assertEqual(w.row,0);self.assertEqual(self.portal['start_group_id'],'b')

    def test_missing_start_sender_uses_saved_group_and_does_not_show_other_channels(self):
        self.large(start=99999);self.portal['start_group_id']='b';w=self.window()
        self.assertEqual(w.category,'b');self.assertEqual(w.total,13);self.assertEqual(w.offset,0)
        self.assertTrue(all(r['channel']['sid'].startswith('b') for r in w.rows))

    def test_no_groups_opens_named_empty_group_screen_with_home_control(self):
        self.index.replace_catalog('p','live',[],[],[],{},'empty')
        w=self.window();self.assertEqual(w.mode,'groups');self.assertFalse(w.rows);self.assertEqual(w.getFocusId(),202)
        self.assertTrue(w.getControl(201).visible);self.assertIn('Keine',w.getControl(201).label)
        self.key(w,7);self.assertTrue(w._closed);self.assertTrue(w._return_home)

    def test_first_programme_left_enters_sender_column_then_groups_without_time_shift(self):
        self.portal.update(start_group_id='a',start_stream_id='1');w=self.window();cursor=w.cursor
        self.key(w,1);self.assertEqual(w.getFocusId(),730);self.assertEqual(w.cursor,cursor)
        self.key(w,1);self.assertEqual(w.mode,'groups');self.assertEqual(w.getFocusId(),200);self.assertEqual(w.cursor,cursor)
        self.assertFalse(w.getControl(310).visible);self.assertFalse(w.getControl(700).visible)
        self.assertEqual([i.label for i in w.getControl(200).items],['A','B']);self.assertNotIn('Alle',[i.label for i in w.getControl(200).items])

    def test_left_inside_schedule_moves_to_previous_programme_before_sender_boundary(self):
        self.portal.update(start_group_id='a',start_stream_id='1');w=self.window()
        self.key(w,2);self.assertEqual(w._selected()['title'],'Following readable title');cursor=w.cursor
        self.key(w,1);self.assertLess(w.cursor,cursor);self.assertGreaterEqual(w.getFocusId(),1000)
        self.key(w,1);self.assertEqual(w.getFocusId(),730)

    def test_group_select_contains_only_selected_group_and_back_restores_group_focus(self):
        self.large(start=0);w=self.window();self.key(w,92);self.key(w,4)
        w.native(7)
        self.assertEqual(w.rows,[]);self.assertEqual(w._cells,{})
        self.assertTrue(all(w.getControl(700+r).text=='' for r in range(8)))
        self.settle(w)
        self.assertEqual(w.category,'b');self.assertEqual(w.total,13);self.assertEqual(w.mode,'grid')
        self.assertTrue(all(r['channel']['sid'].startswith('b') for r in w.rows));self.assertFalse(w.getControl(200).visible)
        self.key(w,92);self.assertEqual(w.getControl(200).getSelectedPosition(),1)

    def test_back_is_grid_groups_home_and_double_back_is_absorbed(self):
        w=self.window();w._running=True
        self.key(w,92);self.assertEqual(w.mode,'groups');self.key(w,92);self.assertFalse(w._leaving)
        w._group_back_after=0;self.key(w,92);self.assertTrue(w._leaving);self.assertFalse(w._closed)
        self.key(w,92);self.assertFalse(w._closed);w._leave_after=0;w._owner_tick();self.assertTrue(w._closed)
        self.assertTrue(w._return_home);self.assertFalse(self.builtins)

    def test_group_view_restore_exact_channel_cursor_and_timeline_after_twenty_cycles(self):
        self.large(start=1979);w=self.window();self.key(w,2)
        snapshot=(w.category,w.offset,w.row,w.cursor,w.origin)
        for _ in range(20):
            self.key(w,92);self.assertEqual(w.mode,'groups');self.key(w,4);self.key(w,7)
            self.assertEqual(w.category,'b');self.key(w,92);self.key(w,3);self.key(w,7)
            self.assertEqual((w.category,w.offset,w.row,w.cursor,w.origin),snapshot)
        self.assertFalse(w._closed);self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()

    def test_up_from_first_visible_row_reaches_all_six_native_headers_and_down_restores_cell(self):
        self.large(start=1976);w=self.window();cell=w.getFocusId()
        self.key(w,3);self.assertEqual(w.getFocusId(),312)
        visited={w.getFocusId()}
        for _ in range(6):self.key(w,2);visited.add(w.getFocusId())
        self.assertEqual(visited,set(range(310,316)))
        self.key(w,4);self.assertEqual(w.getFocusId(),cell);self.assertEqual(w.offset,1976)

    def test_header_up_can_page_to_previous_channels_and_sender_column_can_scroll_up(self):
        self.large(start=8);w=self.window();self.key(w,3);self.assertEqual(w.getFocusId(),312)
        self.key(w,3);self.assertEqual((w.offset,w.row),(0,7));self.assertGreaterEqual(w.getFocusId(),1000)
        w.offset=8;w.row=0;w._load();self.settle(w);self.key(w,1);self.key(w,3)
        self.assertEqual((w.offset,w.row,w.getFocusId()),(0,7,737))

    def test_blue_local_shortcut_and_header_background_refresh_do_not_steal_focus(self):
        w=self.window();self.key(w,218);self.assertEqual(w.getFocusId(),312)
        self.key(w,2);self.assertEqual(w.getFocusId(),313)
        w._load(background=True);self.settle(w);self.assertEqual(w.getFocusId(),313)
        self.assertEqual(w._focus_zone,'header');self.assertFalse(self.builtins)

    def test_sender_focus_survives_background_refresh_and_right_returns_to_programme(self):
        self.portal.update(start_group_id='a',start_stream_id='1');w=self.window();self.key(w,1)
        self.assertEqual(w.getFocusId(),730);w._load(background=True);self.settle(w);self.assertEqual(w.getFocusId(),730)
        self.key(w,2);self.assertGreaterEqual(w.getFocusId(),1000)

    def test_header_now_prime_time_day_and_groups_work_via_native_ok(self):
        import datetime
        w=self.window();self.key(w,218)
        self.key(w,7);self.assertLess(abs(w.cursor-time.time()),3);self.assertEqual(w.getFocusId(),312)
        for _ in range(3):self.key(w,2)
        self.assertEqual(w.getFocusId(),315);self.key(w,7)
        local=datetime.datetime.fromtimestamp(w.cursor);self.assertEqual((local.hour,local.minute),(20,15));self.assertEqual(w.getFocusId(),315)
        self.key(w,2);self.assertEqual(w.getFocusId(),310);self.key(w,2);self.assertEqual(w.getFocusId(),311)
        day=local.date();self.key(w,7);self.assertEqual(datetime.datetime.fromtimestamp(w.cursor).date(),day+datetime.timedelta(days=1))
        self.key(w,1);self.key(w,7);self.assertEqual(datetime.datetime.fromtimestamp(w.cursor).date(),day)
        self.key(w,2);self.key(w,2);self.key(w,2);self.assertEqual(w.getFocusId(),313);self.key(w,7);self.assertEqual(w.mode,'groups')

    def test_selected_sender_and_full_event_title_are_in_footer_even_for_tiny_cells(self):
        w=self.window();self.assertIn(w.rows[w.row]['channel']['name'],w.getControl(103).label)
        self.assertIn(w._selected()['title'],w.getControl(103).label)
        for r in range(8):self.assertEqual(w.getControl(750+r).visible,r==w.row and r<len(w.rows))

    def test_native_labels_have_explicit_normal_and_focus_contrast_and_transparent_frame(self):
        root=ET.parse(ADDON/'resources/skins/Default/720p/XCMateGuideGrid.xml').getroot()
        for e in root.findall('.//control[@type="button"]'):
            self.assertEqual(e.findtext('textcolor'),'FFF4F7F9');self.assertEqual(e.findtext('focusedcolor'),'FFFFFFFF')
            self.assertTrue(e.findtext('texturefocus').endswith('guide_focus_frame.png'))
        with Image.open(ADDON/'resources/media/guide_focus_frame.png') as frame:
            self.assertEqual(frame.getpixel((64,27))[3],0);self.assertEqual(frame.getpixel((64,3))[3],255)

    def test_sender_frame_is_behind_logo_and_name_without_overlap_into_programmes(self):
        controls=ET.parse(ADDON/'resources/skins/Default/720p/XCMateGuideGrid.xml').getroot().find('controls')
        indices={int(e.get('id')):i for i,e in enumerate(controls) if e.get('id')}
        for r in range(8):
            self.assertLess(indices[730+r],indices[720+r]);self.assertLess(indices[750+r],indices[700+r])
            button=next(e for e in controls if e.get('id')==str(730+r))
            self.assertLessEqual(int(button.findtext('left'))+int(button.findtext('width')),340)

    def test_appearance_keeps_guide_contrast_with_user_dark_text_preference(self):
        appearance=importlib.import_module('appearance');appearance.save(dict(appearance.DEFAULT,text='000000',focus='FFFFFF',icon_opacity=25))
        target=Path(appearance.window_source('XCMateGuideGrid.xml'))/'resources/skins/Default/720p/XCMateGuideGrid.xml'
        root=ET.parse(target).getroot()
        self.assertTrue(all(e.text!='FF000000' for e in root.findall('.//textcolor')))
        self.assertTrue(all('colordiffuse' not in e.attrib for e in root.findall('.//texturefocus')))

    def test_group_refresh_failure_preserves_focusable_group_screen(self):
        w=self.window();w._show_groups()
        with mock.patch.object(self.index.Reader,'groups',side_effect=OSError('PRIVATE')):self.settle(w)
        self.assertEqual(w.mode,'groups');self.assertEqual(w.getFocusId(),200);self.assertFalse(w._closed)
        self.assertNotIn('PRIVATE',w.getControl(102).label)

    def test_open_groups_cancels_stale_grid_completion_without_reopening_grid(self):
        w=self.window();w._load(background=True);future=w._pending_future;w._show_groups();self.settle(w)
        self.assertTrue(future.cancelled());self.assertEqual(w.mode,'groups');self.assertEqual(w.getFocusId(),200)

    def test_logos_and_provider_mapping_unchanged_and_no_gui_io_on_directions(self):
        w=self.window();before=Path(self.store.path()).read_bytes();portal=dict(self.portal)
        with mock.patch.object(self.data,'page',side_effect=AssertionError('GUI SQL')):
            self.key(w,4);self.key(w,3);self.key(w,2);self.key(w,1)
        art=importlib.import_module('media_art')
        with mock.patch.object(art,'local_art',return_value={'thumb':'/local/persistent.img'}):w._refresh_logos()
        self.assertEqual(w.getControl(720).image,'/local/persistent.img');self.assertEqual(Path(self.store.path()).read_bytes(),before);self.assertEqual(self.portal,portal)
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()
