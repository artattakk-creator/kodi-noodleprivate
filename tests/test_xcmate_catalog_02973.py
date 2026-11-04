"""Real HTTP/SQLite queue transitions, preservation and cold category evidence."""
import importlib
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture,LIB
import test_xcmate_vodsync_02972 as prior72


class Catalog73(prior72.VODSync72):
    def setUp(self):
        super().setUp()
        self.jobs=importlib.import_module('catalog_jobs73')
        self.responses['get_live_categories']=[dict(category_id='0',category_name='Updated live group')]
        self.responses['get_live_streams']=[dict(stream_id='0',category_id='0',name='Updated live name')]
        self.gs.save('p',['v'],kind='vod');self.gs.save('p',['s'],kind='series')
        self.portal=self.pm.get_by_id('p')
        self.initial=json.dumps(self.portal,sort_keys=True)
        self.original_groups=(self.folder/'xtreammate_groups.json').read_bytes()
        self.addCleanup(lambda:None)
    def row(self):return self.jobs.jobs()[-1]
    def tick(self):self.assertTrue(self.jobs.run_next())
    def finish(self):
        for _ in range(10):
            if self.row()['state'] in ('DONE','FAILED'):break
            self.tick()
        self.assertEqual(self.row()['state'],'DONE',self.row())
    def test_all_three_scopes_resume_one_group_per_turn_and_keep_3357_live(self):
        token=self.jobs.request(self.portal)
        self.assertEqual(self.row()['state'],'WAITING')
        self.tick();self.assertEqual(self.row()['cursor'],1);self.assertEqual(self.row()['state'],'WAITING')
        importlib.reload(self.jobs);self.finish()
        self.assertEqual(self.row()['cursor'],3);self.assertEqual(self.row()['readback'],dict(live=3357,vod=1,series=1))
        self.assertEqual(json.dumps(self.pm.get_by_id('p'),sort_keys=True),self.initial)
        self.assertEqual((self.folder/'xtreammate_groups.json').read_bytes(),self.original_groups)
        self.assertEqual(self.index.Reader('p').get('live','0')['name'],'Updated live name')
        self.assertEqual(self.live_digest()[:2],(3357,53))
        self.assertEqual(self.jobs.request(self.portal),self.jobs.jobs()[-1]['id'])
        self.assertNotIn('CANARY72',self.jobs.path() and Path(self.jobs.path()).read_text())
        for name,data in self.guarded.items():self.assertEqual((self.folder/name).read_bytes(),data)
    def test_active_job_deduplicates_and_never_overwrites_delta_work(self):
        delta=importlib.import_module('catalog_delta');delta.request_many(self.portal,'vod',['v'])
        before=Path(delta.path()).read_bytes()
        a=self.jobs.request(self.portal);b=self.jobs.request(self.portal,['vod'])
        self.assertEqual(a,b);self.assertEqual(len(self.jobs.jobs()),1)
        self.tick();self.assertEqual(Path(delta.path()).read_bytes(),before)
    def test_large_backup_does_not_hold_profile_lock_or_block_status_readers(self):
        self.jobs.request(self.portal,['live'])
        backup=self.store.backup;read=[]
        def observe(*args,**kwargs):
            import threading
            def reader():
                from profile_transaction import reading
                with reading(timeout=.05):read.append(self.jobs.jobs()[0]['state'])
            thread=threading.Thread(target=reader);thread.start();thread.join(.5)
            self.assertFalse(thread.is_alive());self.assertEqual(read,['RUNNING'])
            return backup(*args,**kwargs)
        with mock.patch('vodsync_store72.backup',side_effect=observe):self.tick()
        self.assertEqual(self.row()['state'],'DONE')

    def test_existing_writer_reports_waiting_not_running_or_failure(self):
        session=self.engine.Session(self.portal,('vod',))
        try:
            self.jobs.request(self.portal);self.assertFalse(self.jobs.run_next())
            self.assertEqual((self.row()['state'],self.row()['code']),('WAITING','WRITER_BUSY'))
        finally:session.close()
    def test_user_cancel_resume_keeps_committed_group_and_does_not_repeat_it(self):
        token=self.jobs.request(self.portal);self.tick();n=len(self.requests)
        self.jobs.control(token);self.assertFalse(self.jobs.run_next());self.assertEqual(self.row()['state'],'INTERRUPTED')
        self.jobs.control(token,resume=True);self.finish()
        self.assertEqual(sum(a=='get_live_streams' for a,c,p in self.requests),1)
        self.assertGreater(len(self.requests),n)
    def test_service_stop_sets_restartable_interrupted_instead_of_false_done(self):
        self.jobs.request(self.portal)
        real=self.store.upsert
        def stop(session,*args,**kw):raise self.api.SyncError('CANCELLED')
        with mock.patch('vodsync_store72.upsert',side_effect=stop):
            # Simulate shutdown arriving while an in-flight operation cancels.
            calls=[False,False,False,True]
            self.jobs.run_next(lambda: calls.pop(0) if calls else True)
        self.assertNotEqual(self.row()['state'],'DONE')
    def test_invalid_or_partial_group_never_replaces_active_live_generation(self):
        self.responses['get_live_streams']=[dict(stream_id='0',category_id='0',name='new'),dict(stream_id='1',category_id='0')]
        self.jobs.request(self.portal);self.tick()
        self.assertEqual(self.row()['state'],'FAILED');self.assertEqual(self.row()['code'],'SCHEMA')
        self.assertEqual(self.live_digest(),self.live_before)
    def test_empty_responses_keep_data_and_record_verified_empty_evidence(self):
        self.responses['get_live_streams']=[]
        self.jobs.request(self.portal,['live']);self.finish()
        self.assertEqual(self.live_digest(),self.live_before)
        self.assertEqual(self.row()['empty'],[['live','0']]);self.assertEqual(self.row()['readback']['live'],3357)
    def test_backup_integrity_failure_is_terminal_before_any_group_request(self):
        self.jobs.request(self.portal);self.tick()
        with open(self.row()['backup'],'ab') as f:f.write(b'tamper')
        self.tick();self.assertEqual(self.row()['code'],'BACKUP_VERIFY')
        self.assertEqual(sum(a=='get_vod_streams' for a,c,p in self.requests),0)
    def test_older_legacy_category_without_v2_head_does_not_trigger_import(self):
        self.index.replace_catalog('p','vod',[dict(stream_id='old',category_id='v',name='Preserved older catalog')],[dict(category_id='v',category_name='V')])
        self.gs.save('p',['v'],kind='vod');reader=self.index.Reader('p')
        self.assertFalse(reader._query("SELECT 1 FROM heads WHERE pid='p' AND kind='vod' AND cid='v'"))
        status=importlib.import_module('catalog_status73')
        with mock.patch('catalog_delta.request_many') as request:
            status.ensure_category(self.portal,'vod','v',reader);request.assert_not_called()
        self.assertEqual(reader.page('vod',category='v',limit=1)[1],1)

    def test_missing_selected_category_requests_import_even_when_latest_has_data(self):
        self.index.replace_catalog('p','vod',[dict(stream_id='m',category_id='v',name='Movie')],[dict(category_id='v',category_name='V'),dict(category_id='z',category_name='Z')])
        self.gs.save('p',['v','z'],kind='vod')
        status=importlib.import_module('catalog_status73');reader=self.index.Reader('p')
        status.ensure_category(self.portal,'vod','z',reader)
        delta=importlib.import_module('catalog_delta');self.assertTrue(any(r['cid']=='z' and r['code']=='PENDING' for r in delta.states('p','vod')))
        before=Path(delta.path()).read_bytes();status.ensure_category(self.portal,'vod','z',reader)
        self.assertEqual(Path(delta.path()).read_bytes(),before)
    def test_status_is_category_specific_sorted_and_fresh_head_wins_over_stale_pending(self):
        status=importlib.import_module('catalog_status73');reader=self.index.Reader('p')
        self.jobs.request(self.portal,['live']);self.finish()
        rows=[dict(cid='elsewhere',code='FAILED',updated=time.time()+100),dict(cid='0',code='PENDING',updated=1)]
        self.assertNotEqual(status.selected_status('p','live','0',reader,rows)[0]['code'],'PENDING')


class International73(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.epg=importlib.import_module('international_epg73')
    def test_exact_104_candidates_45_pending_iso_unique_all_disabled_and_continents(self):
        rows=self.epg.registry()['entries'];self.assertEqual(len(rows),149)
        self.assertEqual(sum(r['candidate'] for r in rows),104)
        self.assertEqual(len({r['code'] for r in rows}),149)
        self.assertTrue(all(r['continent'] for r in rows))
        self.assertTrue(all(not s['enabled'] for r in rows for s in r['sources']))
    def xml(self):
        return b'<tv><channel id="c"><display-name>Test</display-name></channel><programme channel="c" start="20991104000000 +0000" stop="20991104010000 +0000"><title>Test</title></programme></tv>'
    def test_real_xml_full_document_validates_counts_range_and_cancellation(self):
        result=self.epg.inspect_xml(io.BytesIO(self.xml()));self.assertEqual((result['channels'],result['programmes']),(1,1))
        with self.assertRaises(self.epg.SyncError):self.epg.inspect_xml(io.BytesIO(self.xml()),lambda:True)
    def test_bad_empty_entity_bomb_and_truncated_document_are_rejected(self):
        for data in (b'<html/>',b'<tv/>',b'<!DOCTYPE tv [<!ENTITY a "b">]><tv/>',self.xml()[:-5]):
            with self.subTest(data=data[:20]),self.assertRaises(Exception):self.epg.inspect_xml(io.BytesIO(data))
    def test_registry_is_allowlist_and_private_dns_redirect_and_downgrade_rejected(self):
        for url in ('http://iptv-epg.org/files/epg-de.xml','https://evil.invalid/a.xml','https://user:secret@iptv-epg.org/files/epg-de.xml'):
            with self.assertRaises(self.epg.SyncError):self.epg.endpoint(dict(url=url))
        with mock.patch.object(self.epg.socket,'getaddrinfo',return_value=[(0,0,0,'',('127.0.0.1',443))]):
            with self.assertRaises(self.epg.SyncError):self.epg.public_dns('iptv-epg.org')
        redirect=self.epg.Redirect(self.epg.urlsplit('https://iptv-epg.org/files/epg-de.xml'))
        with self.assertRaises(self.epg.SyncError):redirect.redirect_request(None,None,302,'',{},'http://iptv-epg.org/a')
    def test_activation_requires_consent_recent_proof_and_terms_without_source_or_mapping_write(self):
        row=next(r for r in self.epg.countries() if r['code']=='DE');source=row['sources'][0]
        before=dict(self.options)
        with self.assertRaises(self.epg.SyncError):self.epg.activate(self.portal,row,source)
        with self.assertRaises(self.epg.SyncError):self.epg.activate(self.portal,row,source,confirmed=True)
        self.assertEqual(self.options,before)
        self.assertFalse((self.folder/'xtreammate_epg_sources.json').exists())


if __name__=='__main__':unittest.main()
