"""Real wizard scan/save retains source identity, XMLTV images and old data."""
import importlib
import json
from pathlib import Path
import sys
import time
import unittest
from unittest import mock
import test_xcmate_setup_0294 as old

class WizardEPG48(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.d=self.m.draft;now=self.m.now;stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        feed=self.m.folder/'feed48.xml';feed.write_text('<tv><channel id="xml"><display-name>Actual station</display-name></channel><programme channel="xml" start="'+stamp(now-60)+'" stop="'+stamp(now+3600)+'"><title>Actual programme</title><desc>Exact synopsis</desc><icon src="https://images.example.test/actual.png"/><credits><actor>Actual actor</actor><director>Actual director</director></credits></programme></tv>')
        self.d.epg_sources=[dict(id='feed48',name='Named source',uri=str(feed),local=True,enabled=True)]
        entries=self.d.adapter.entries
        def rows(kind,cid,cancel,allowed):
            for row in entries(kind,cid,cancel,allowed):
                if kind=='live':row=dict(row,epg_channel_id='xml')
                yield row
                if kind=='live':break
        self.d.adapter.entries=rows
        epg=sys.modules['epg'];epg._save_disk=lambda pid,data,notify=True:True;epg._mem_set=lambda *a:None
    def test_external_only_wizard_preserves_source_rank_images_cast_and_name_after_save(self):
        self.d.scan();self.assertEqual(self.d.report['epg'],1);portal=self.d.save()
        from programme_events46 import load
        from guide_publish44 import source_id
        event=load(portal,dict(sid='0',name='Station',epg_channel_id='xml'),now=self.m.now)
        self.assertEqual(event['title'],'Actual programme');self.assertEqual(event['xmltv_image'],'https://images.example.test/actual.png')
        self.assertEqual(event['cast'],['Actual actor']);self.assertEqual(event['director'],'Actual director')
        self.assertEqual(event['epg_source46'],source_id(self.d.epg_sources[0],1))
        from epg_binding48 import named_channels,save
        self.assertEqual(named_channels(portal['id'],event['epg_source46'])[0]['name'],'Actual station')
        self.assertTrue(save(portal,'0','xml',event['epg_source46']))
        self.assertEqual(self.m.portals.get_by_id('p'),self.m.portal)
    def test_failed_save_removes_only_unpublished_new_id_rich_facts(self):
        self.d.scan();verify=self.d._verify
        def fail(portal=None):
            if portal:raise self.m.draft_module_error()
            return verify()
        with mock.patch.object(self.d,'_verify',side_effect=fail):
            with self.assertRaises(ValueError):self.d.save()
        from programme_index46 import connect
        db=connect(False)
        try:self.assertEqual(db.execute('SELECT count(*) FROM facts WHERE pid=?',(self.d.pid,)).fetchone()[0],0)
        finally:db.close()
        self.assertEqual(self.m.portals.load_all(),[self.m.portal]);self.assertFalse(self.d.saved)
    def test_existing_unbacked_guide_blocks_save_without_mutating_its_bytes(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'old':[dict(channel='old',name='Protected',start_timestamp=self.m.now-60,stop_timestamp=self.m.now+900)]},trusted_feed=True)
        before=Path(guide.path()).read_bytes();self.d.scan()
        with self.assertRaisesRegex(ValueError,'EPG-BACKUP'):self.d.save()
        self.assertEqual(Path(guide.path()).read_bytes(),before);self.assertEqual(self.m.portals.load_all(),[self.m.portal])
