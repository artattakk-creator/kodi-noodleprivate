"""Authorized live list changes with strict native Omega lifecycle callbacks."""
import sys
import time
import types
import unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as omega


class ContinuousTests(unittest.TestCase):
    def setUp(self): omega.OverlayLifecycleTests.setUp(self)

    def large(self,count=1001):
        o=self.overlay
        o.channels=[types.SimpleNamespace(name='Sender '+str(i),tvg_id='',extra={'stream_id':str(i),'category_id':str(i%10)}) for i in range(1,count+1)]
        o.groups=[dict(category_id=str(i),category_name='Gruppe '+str(i)) for i in range(10)]
        o.index=sys.modules['tv_data'].CatalogIndex(o.channels)
        o.enabled=None;o.category_id='*';o._scroll_to_current=False;o._highlight['channels']=0;o._render()
        return o

    def test_active_group_labels_have_no_toggle_status_or_disabled_rows(self):
        o=self.overlay;o.enabled={'a'};o._switch('groups')
        self.assertEqual([row[0] for row in o.rows],['*','a'])
        self.assertFalse(any(s.startswith(('AN ','AUS ')) for s in o.control.items))
        o._toggle=mock.Mock();o.native(7);o._toggle.assert_not_called()
        self.assertEqual(o.mode,'channels')

    def test_zero_active_groups_keep_management_access_and_do_not_reactivate(self):
        o=self.overlay;o.enabled=set();o._switch('groups')
        self.assertEqual(len(o.rows),1);self.assertFalse(o.rows[0][2])
        o.native(7);self.assertEqual(o.mode,'groups')
        with mock.patch.object(o,'_toggle') as manage:
            o.native(117);manage.assert_called_once()
        sys.modules['group_selection'].save.assert_not_called()

    def test_management_uses_cached_categories_and_rebuilds_without_tuning(self):
        o=self.overlay;o.enabled={'a'};o._switch('groups');o.category_id='a'
        groups=sys.modules['group_selection'];groups.choose_groups=mock.Mock(return_value=True)
        groups.enabled_ids=lambda *a:{'b'}
        o._tune=mock.Mock();o.native(117)
        groups.choose_groups.assert_called_once_with(o.portal,'live',categories=o.groups,allow_refresh=False)
        self.assertEqual([row[0] for row in o.rows],['*','b'])
        self.assertEqual(o.category_id,'');o._tune.assert_not_called()  # .35: empty group data never implies All.
        self.client._get_json.assert_not_called()

    def test_cancelled_management_preserves_selection_focus_and_video(self):
        o=self.overlay;o.enabled={'a'};o._switch('groups');o.control.selectItem(1)
        groups=sys.modules['group_selection'];groups.choose_groups=mock.Mock(return_value=False)
        before=(o.category_id,o.control.selected,list(o.control.items))
        o.native(117)
        self.assertEqual((o.category_id,o.control.selected,list(o.control.items)),before)
        self.assertEqual(o.enabled,{'a'})

    def test_thousand_channels_scroll_both_ways_without_page_rows_or_wrong_ok(self):
        o=self.large();control_count=len(o.controls);o._tune=mock.Mock()
        start=time.monotonic()
        for pos in range(1,1001):
            o.native(4)
            self.assertEqual(o._highlight['channels'],pos)
            self.assertEqual(o.control.items[o.control.selected],'Sender '+str(pos+1))
            self.assertLessEqual(o.control.size(),100)
        o.native(4);self.assertEqual(o._highlight['channels'],1000)
        o.native(7);self.assertEqual(o._tune.call_args.args[0].extra['stream_id'],'1001')
        for pos in range(999,-1,-1):
            o.native(3);self.assertEqual(o._highlight['channels'],pos)
        o.native(3);self.assertEqual(o._highlight['channels'],0)
        self.assertEqual(len(o.controls),control_count)
        self.assertTrue(all('Senderseite' not in s for s in o.control.items))
        self.assertNotIn('Seite',o.sub.label)
        self.assertLess(time.monotonic()-start,5)  # Cloud model only.
        self.client._get_json.assert_not_called();self.client.get_short_epg.assert_not_called()

    def test_bridge_and_native_boundary_movement_each_apply_exactly_once(self):
        o=self.large();o._highlight['channels']=99;o._render()
        o.native(4);self.assertEqual(o._highlight['channels'],100)
        o.handle_command('up');self.assertEqual(o._highlight['channels'],99)
        o.native(6);self.assertEqual(o._highlight['channels'],199)
        o.native(5);self.assertEqual(o._highlight['channels'],99)


from xcmate027_fixture import Fixture
import importlib


class ManagementTests(Fixture,unittest.TestCase):
    def test_cached_checkbox_management_commits_inactive_group_without_http(self):
        groups=importlib.import_module('group_selection')
        cats=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
        groups.save('p',['a'],known=['a','b'],auto_new=False)
        self.dialog.select.return_value=0
        self.dialog.multiselect=mock.Mock(return_value=[1])
        with mock.patch.object(groups,'_categories',side_effect=AssertionError('HTTP during navigation')):
            self.assertTrue(groups.choose_groups(self.portal,'live',categories=cats,allow_refresh=False))
        self.assertEqual(groups.load('p'),{'b'})
        self.assertEqual(self.dialog.multiselect.call_args.kwargs['preselect'],[0])
        sys.modules['utils'].http_get.assert_not_called()

    def test_back_discards_checkbox_changes_and_preserves_auto_new(self):
        groups=importlib.import_module('group_selection')
        cats=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
        groups.save('p',['a'],known=['a'],auto_new=True)
        before=Path(groups._path()).read_bytes()
        self.dialog.select.side_effect=[0,-1]
        self.dialog.multiselect=mock.Mock(return_value=None)
        self.assertFalse(groups.choose_groups(self.portal,'live',categories=cats,allow_refresh=False))
        self.assertEqual(Path(groups._path()).read_bytes(),before)
        self.assertEqual(self.dialog.multiselect.call_args.kwargs['preselect'],[0,1])
