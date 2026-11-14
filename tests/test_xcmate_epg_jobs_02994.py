import gzip,importlib,json,os,sqlite3,stat,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from xcmate027_fixture import Fixture
import test_xcmate_epg_resume_02954 as resume54


class Jobs94(Fixture,unittest.TestCase):
 def jobs(self):return importlib.import_module('epg_jobs94')
 def test_request_survives_new_reader_and_requires_actual_ack(self):
  m=self.jobs();j=m.request('p');self.assertEqual(j['state'],'QUEUED');self.assertNotIn('ack',m.read('p'))
  self.assertEqual(m.snapshot('p',now=j['requested']+16)['state'],'SERVICE_NOT_CONFIRMED')
  self.assertEqual(m.request('p')['id'],j['id']);self.assertTrue(m.acknowledge('p',j['id']))
  self.assertEqual(m.read('p')['state'],'RUNNING');self.assertFalse(m.acknowledge('p',j['id']))
 def test_expired_request_cannot_execute_late(self):
  m=self.jobs();j=m.request('p')
  with mock.patch.object(m.time,'time',return_value=j['requested']+16):self.assertFalse(m.acknowledge('p',j['id']))
  self.assertEqual(m.read('p')['state'],'SERVICE_NOT_CONFIRMED')
 def test_single_flight_and_cross_thread_updates_are_atomic(self):
  m=self.jobs()
  with ThreadPoolExecutor(max_workers=6) as pool:values=list(pool.map(lambda _:m.request('p'),range(12)))
  self.assertEqual(len({v['id'] for v in values}),1);j=values[0];m.acknowledge('p',j['id'])
  with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(lambda i:m.observe('p',j['id'],format(i,'024x'),'PARSE',programmes=i),range(12)))
  self.assertEqual(len(m.read('p')['sources']),12)
 def test_no_heartbeat_or_artificial_progress_and_compression_counts_wire_bytes(self):
  m=self.jobs();j=m.request('p');m.acknowledge('p',j['id']);m.observe('p',j['id'],'provider','PARSE',programmes=4)
  before=m.read('p')['progress']
  with mock.patch.object(m.time,'time',return_value=before+200):m.observe('p',j['id'],'provider','PARSE',programmes=4)
  self.assertEqual(m.read('p')['progress'],before);self.assertTrue(m.snapshot('p',now=before+200)['stalled'])
  n=importlib.import_module('network_io');raw=b'<tv>'+b'x'*10000+b'</tv>';compressed=gzip.compress(raw)
  reader=n.wire_reader94(iter([compressed]),{'Content-Encoding':'gzip','Content-Length':str(len(compressed))},None,lambda:False)
  self.assertEqual(reader.read(20000),raw);self.assertEqual(reader.wire94,dict(bytes=len(compressed),total=len(compressed)))
 def test_unknown_total_never_invents_percentage(self):
  m=importlib.import_module('network_io');r=m.wire_reader94(iter([b'x']),{'Content-Length':'100','Transfer-Encoding':'chunked'},None,lambda:False)
  r.read(10);self.assertEqual(r.wire94['total'],0)
 def test_cancel_and_late_callbacks_cannot_overwrite_new_job(self):
  m=self.jobs();j=m.request('p');self.assertTrue(m.cancel('p',j['id']));self.assertFalse(m.acknowledge('p',j['id']))
  newer=m.request('p');m.acknowledge('p',newer['id']);self.assertFalse(m.finish('p',j['id'],'DONE'))
  self.assertFalse(m.observe('p',j['id'],'provider','DONE',committed=99));self.assertEqual(m.read('p')['state'],'RUNNING')
 def test_telemetry_is_private_allowlisted_and_bounded(self):
  m=self.jobs();j=m.request('p');m.acknowledge('p',j['id']);m.observe('p',j['id'],'provider','DOWNLOAD',bytes=3,uri='https://secret.invalid',token='SECRET',programmes=-4)
  with open(m.path('p')) as stream:raw=stream.read()
  self.assertNotIn('SECRET',raw);self.assertNotIn('https:',raw);self.assertNotIn('token',raw)
  self.assertEqual(stat.S_IMODE(os.stat(m.path('p')).st_mode),0o600)
  with self.assertRaises(ValueError):m.observe('p',j['id'],'http://private','DOWNLOAD')
 def test_ui_status_keeps_waiting_distinct_from_running_and_no_synthetic_percent(self):
  m=self.jobs();j=m.request('p');p=importlib.import_module('epg_progress94')
  self.assertFalse(p.row(j,'provider')['busy']);m.acknowledge('p',j['id']);m.observe('p',j['id'],'provider','DOWNLOAD',bytes=10)
  value=p.row(m.snapshot('p'),'provider');self.assertTrue(value['busy']);self.assertIsNone(value['percent'])
  m.observe('p',j['id'],'provider','DONE',committed=5,verified=5);self.assertFalse(p.row(m.snapshot('p'),'provider')['busy'])


class Pipeline94(unittest.TestCase):
 setUp=resume54.EPG54.setUp
 def test_cold_readback_contains_every_source_row_and_digest(self):
  self.assertEqual(self.mod.run(self.portal)['phase'],'READY')
  r=importlib.import_module('epg_readback94');from guide_store import path
  db=sqlite3.connect(path());sid=next(iter(self.mod.read(self.portal)['sources']));expected=r.digest(db,self.portal['id'],sid)
  revision=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(self.portal['id'],)).fetchone()[0];db.close()
  self.assertEqual(r.verify(path(),self.portal['id'],sid,expected,revision),expected)
  with sqlite3.connect(path()) as db:db.execute('UPDATE guide44_inputs SET title=? WHERE source_id=?',('Changed after commit',sid))
  with self.assertRaisesRegex(OSError,'READBACK_MISMATCH'):r.verify(path(),self.portal['id'],sid,expected,revision)
 def test_publication_is_not_reported_ready_when_cold_readback_fails(self):
  with mock.patch('epg_readback94.verify',side_effect=OSError('EPG_READBACK_MISMATCH')):state=self.mod.run(self.portal)
  self.assertNotEqual(state['phase'],'READY');self.assertTrue(all(s['code']!='READY' for s in state['sources'].values()))
  self.assertIsNotNone(self.m.portals.get_by_id(self.portal['id']))
 def test_readback_cancel_and_changed_revision_are_separate_failures(self):
  self.mod.run(self.portal);r=importlib.import_module('epg_readback94');from guide_store import path
  sid=next(iter(self.mod.read(self.portal)['sources']));db=sqlite3.connect(path());expected=r.digest(db,self.portal['id'],sid);revision=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(self.portal['id'],)).fetchone()[0];db.close()
  with self.assertRaisesRegex(OSError,'REVISION_CHANGED'):r.verify(path(),self.portal['id'],sid,expected,'wrong')
  with self.assertRaises(InterruptedError):r.verify(path(),self.portal['id'],sid,expected,revision,cancel=lambda:True)
 def test_streamed_xmltv_gzip_and_duplicate_counts_match_actual_persisted_rows(self):
  raw=self.files[0].read_text();event=raw[raw.index('<programme'):raw.index('</programme>')+12]
  self.files[0].write_bytes(gzip.compress(raw.replace('</tv>',event+'</tv>').encode()))
  progress=[];source=self.d.epg_sources[0];streams=list(self.stream.active_streams(self.portal))
  counts=self.stream.import_source(self.portal['id'],source,1,streams,{},progress=progress.append)
  self.assertEqual(counts['programmes'],2);self.assertEqual(counts['stored'],1);self.assertEqual(counts['stored_unique66'],1)
  self.assertIn('MATCHING',[r['phase'] for r in progress])
 def test_import_never_deletes_user_selected_xmltv_and_has_no_persistent_raw_copy(self):
  before=[f.read_bytes() for f in self.files];self.mod.run(self.portal)
  self.assertEqual([f.read_bytes() for f in self.files],before)
  from guide_store import path
  with sqlite3.connect(path()) as db:self.assertEqual(db.execute('SELECT count(*) FROM xml_stage').fetchone()[0],0)
