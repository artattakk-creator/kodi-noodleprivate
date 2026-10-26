"""Optional adapter is inert until enabled; focused EPG is RAM/time-derived."""
import importlib,importlib.util,json,sys,time,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
ROOT=Path(__file__).resolve().parents[1]

class WidgetAdapter41(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.focus=importlib.import_module('widget_focus41');self.focus._next=0;self.focus._last=None
    def bank(self):
        now=time.time();row=dict(sid='1')
        self.focus.publish(self.portal,[row],{'1':dict(events=[dict(title='Now',start=now-10,stop=now+10),dict(title='Next',start=now+10,stop=now+40)])})
        return self.focus.token(self.portal,row),time.time()
    def enable(self,token):
        sys.modules['xbmc'].getCondVisibility=lambda c:c in ('Skin.HasSetting(xcmate41.adapter.enabled)','Control.HasFocus(90241)')
        sys.modules['xbmc'].getInfoLabel=lambda label:token
    def test_disabled_adapter_never_reads_focus_or_changes_home_configuration(self):
        self.bank()
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=AssertionError('disabled focus')):self.focus.poll()
        self.assertNotIn('XCMate.Widget41.Now',self.properties);self.assertFalse(self.builtins)
    def test_focus_and_natural_rollover_use_same_real_events_without_sql_network_or_tune(self):
        token,now=self.bank();self.enable(token)
        with mock.patch.object(self.focus.time,'time',return_value=now):self.focus.poll()
        self.assertEqual(self.properties['XCMate.Widget41.Now'],'Now');self.assertEqual(self.properties['XCMate.Widget41.Next'],'Next')
        self.assertEqual(self.properties['XCMate.Widget41.Progress'],'50')
        self.focus._next=0
        with mock.patch.object(self.focus.time,'time',return_value=now+11):self.focus.poll()
        self.assertEqual(self.properties['XCMate.Widget41.Now'],'Next');self.assertFalse(self.builtins)
        sys.modules['utils'].http_get.assert_not_called()
    def test_different_focus_or_expired_bank_clears_previous_channel_information(self):
        token,now=self.bank();self.enable(token);self.focus.poll()
        self.focus._next=0;self.enable('f'*32);self.focus.poll()
        self.assertEqual(self.properties['XCMate.Widget41.Next'],'');self.assertEqual(self.properties['XCMate.Widget41.Progress'],'0')
    def test_versioned_skin_xml_has_half_tile_logos_real_focus_fields_and_no_auto_install(self):
        folder=ROOT/'integrations/titan-bingie-mod/0.1.29.41';manifest=json.loads((folder/'manifest.json').read_text())
        self.assertFalse(manifest['auto_install']);self.assertEqual(manifest['target_version'],'2.2.3')
        tree=ET.parse(folder/'Includes_XCMate41.xml');live=tree.find(".//control[@id='90241']")
        for layout in ('itemlayout','focusedlayout'):
            image=next(c for c in live.find(layout).findall('control') if c.findtext('texture')=='$INFO[ListItem.Art(icon)]')
            self.assertEqual((int(image.findtext('width')),int(image.findtext('height'))),(80,45))
        text=(folder/'Includes_XCMate41.xml').read_text();self.assertIn('XCMate.Widget41.Progress',text)
        self.assertNotIn('Watched',text);self.assertNotIn('PlayMedia',text)
    def test_preflight_reports_invalid_xml_and_id_collision_without_writes(self):
        spec=importlib.util.spec_from_file_location('adapter_check41',ROOT/'tools/check_bingie_adapter_02941.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        skin=self.folder/'skin';skin.mkdir();(skin/'addon.xml').write_text('<addon id="skin.titan.bingie.mod" version="2.2.3"/>')
        (skin/'broken.xml').write_text('<a><b></a>');(skin/'home.xml').write_text('<window><controls><control id="90241"/></controls></window>')
        before={p.name:p.read_bytes() for p in skin.iterdir()};report=module.check(skin)
        self.assertFalse(report['installation_performed']);self.assertFalse(report['skin_changed']);self.assertIn('CONTROL_ID_COLLISION',report['errors'])
        self.assertTrue(any(isinstance(v,dict) and v['code']=='SKIN_XML_INVALID' for v in report['errors']))
        self.assertEqual({p.name:p.read_bytes() for p in skin.iterdir()},before)
