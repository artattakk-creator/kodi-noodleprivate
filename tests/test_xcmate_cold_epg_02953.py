"""Unmatched-channel XMLTV preview: bounded RAM, explicit Save, offline reload."""
import gzip,importlib,io,sys,types,unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock
import test_xcmate_epg_binding_02948 as old
from xcmate027_fixture import ADDON


class Cold53(unittest.TestCase):
    def setUp(self):
        self.m=old.Binding48(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.c=importlib.import_module('epg_candidate53');self.stream=importlib.import_module('stream_epg')
        import time
        fmt=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        self.xml=('<tv><channel id="new"><display-name>Comedy Central DE HD</display-name></channel><channel id="plus"><display-name>Comedy Central DE +1</display-name></channel><programme channel="new" start="'+fmt(self.m.now-60)+'" stop="'+fmt(self.m.now+600)+'"><title>Actual unmatched programme</title><desc>Actual feed description</desc></programme></tv>').encode()
        @contextmanager
        def stream(*a,**k):yield io.BytesIO(self.xml)
        p=mock.patch.object(self.stream,'source_stream',side_effect=stream);p.start();self.addCleanup(p.stop)
    def dialog(self):
        self.w=self.m.window();module=importlib.import_module('guide_mapping48')
        self.d=module.MappingWindow48('XCMateMapping48.xml',str(ADDON),'Default','720p');self.d.configure(self.w);self.d.onInit();self.addCleanup(self.d.close)
        self.d.source=dict(id=self.m.bid,name='Source B');self.d.candidate=dict(id='new',name='Comedy Central DE HD');self.d.rows=[self.d.candidate]
        p=mock.patch.object(self.d,'_submit',side_effect=lambda f,a:a(f()));p.start();self.addCleanup(p.stop)
        return self.d
    def snapshot(self):
        return {str(p):p.read_bytes() for p in self.m.folder.rglob('*') if p.is_file() and p.suffix not in ('.pyc',)}
    def test_cold_catalogue_search_names_and_ids_stays_in_ram(self):
        before=self.snapshot();cache=self.c.Candidates()
        rows=cache.channels(self.m.portal,self.m.bid,'Comedy',0,lambda:False)
        self.assertEqual([r['id'] for r in rows],['new','plus']);self.assertEqual(cache.channels(self.m.portal,self.m.bid,'plus',0,lambda:False)[0]['name'],'Comedy Central DE +1')
        self.assertEqual(self.snapshot(),before)
    def test_unmatched_id_updates_original_grid_with_open_panel_and_zero_file_writes(self):
        d=self.dialog();before=self.snapshot();d._preview()
        self.assertEqual(self.w.rows[0]['events'][0]['title'],'Actual unmatched programme')
        self.assertIn('Actual feed description',d.getControl(301).text);self.assertFalse(d._closed);self.assertTrue(d.getControl(900).visible)
        self.assertEqual(self.snapshot(),before);self.assertFalse(self.m.binding.named_channels('p',self.m.bid,'Comedy'))
    def test_cold_cancel_restores_original_grid_without_persistence(self):
        d=self.dialog();before=self.snapshot();original=list(self.w.rows);d._preview()
        with mock.patch.object(d,'show',side_effect=d.close):d.run()
        self.assertEqual(self.w.rows,original);self.assertEqual(self.snapshot(),before)
    def test_explicit_save_publishes_exact_source_and_survives_new_offline_reader(self):
        d=self.dialog();d._preview();d.onClick(405);self.assertTrue(d.saved)
        mappings=self.m.sources.configuration('p')['mappings'];self.assertEqual(mappings.sources48['1']['source'],self.m.bid)
        with mock.patch.object(self.stream,'source_stream',side_effect=AssertionError('offline')):
            result=self.m.local.now_next('p',[self.m.row()],mappings,self.m.now)['1']
            self.assertEqual(result['now'],'Actual unmatched programme');self.assertEqual(result['description'],'Actual feed description')
        self.assertEqual(self.m.sources.configuration('p')['mappings']['2'],'xml')
    def test_selected_source_collision_does_not_use_another_feed(self):
        self.c.publish(self.m.portal,self.m.bid,'new','Comedy',self.c.scan(self.m.portal,self.m.bid,'new'))
        from programme_index46 import window
        self.assertFalse(window('p','new',self.m.now-120,self.m.now+1200,source48=self.m.aid))
        self.assertTrue(window('p','new',self.m.now-120,self.m.now+1200,source48=self.m.bid))
    def test_failed_publication_never_writes_mapping(self):
        d=self.dialog();d._preview();before=Path(self.m.sources._file_path()).read_bytes()
        with mock.patch.object(self.c,'publish',side_effect=self.c.PreviewUnavailable('PREVIEW_WRITE_FAILED')):
            with self.assertRaises(self.c.PreviewUnavailable):d.onClick(405)
        self.assertFalse(d.saved);self.assertEqual(Path(self.m.sources._file_path()).read_bytes(),before)
    def test_cancelled_or_truncated_gzip_never_exposes_partial_result(self):
        before=self.snapshot()
        with self.assertRaises(InterruptedError):self.c.scan(self.m.portal,self.m.bid,'new',lambda:True)
        self.xml=gzip.compress(self.xml)[:-5]
        with self.assertRaises(EOFError):self.c.scan(self.m.portal,self.m.bid,'new')
        self.assertEqual(self.snapshot(),before)
    def test_explicit_preview_has_byte_and_event_caps_instead_of_unbounded_feed_memory(self):
        with self.assertRaises(self.c.PreviewUnavailable):self.c.Limited(io.BytesIO(b'abcd'),2,lambda:False).read(4)
        event=self.xml[self.xml.index(b'<programme'):self.xml.index(b'</programme>')+12]
        self.xml=b'<tv>'+event*513+b'</tv>'
        with self.assertRaises(self.c.PreviewUnavailable):self.c.scan(self.m.portal,self.m.bid,'new')
    def test_valid_gzip_uses_the_same_bounded_parser_and_zero_length_reads(self):
        self.xml=gzip.compress(self.xml)
        self.assertEqual(self.c.scan(self.m.portal,self.m.bid,'new')[0]['name'],'Actual unmatched programme')
        stream=io.BytesIO(b'ab');self.assertEqual(self.c.Limited(stream,2,lambda:False).read(0),b'');self.assertEqual(stream.tell(),0)
    def test_45_second_deadline_and_unsafe_xml_remain_fail_closed(self):
        from xmltv_stream import UnsafeXMLTV
        self.xml=b'<!DOCTYPE tv [<!ENTITY secret SYSTEM "file:///etc/passwd">]><tv/>'
        with self.assertRaises(UnsafeXMLTV):self.c.scan(self.m.portal,self.m.bid,'new')
        self.xml=b'<tv/>'
        with mock.patch('xmltv_stream.time.monotonic',side_effect=[0,46]):
            with self.assertRaises(TimeoutError):self.c.scan(self.m.portal,self.m.bid,'new')
