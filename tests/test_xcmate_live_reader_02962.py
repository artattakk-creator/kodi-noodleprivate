"""803 groups, concurrent WAL generations and independent station delivery."""
import importlib,json,sqlite3,sys,threading,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Live62(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.home=importlib.import_module('widget_home50');self.reader=importlib.import_module('live_home62')
  self.portal.update(start_group_id='a',start_stream_id='foreign')
  self.stations=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i)) for i in range(88)]
  self.index.import_group('p','live','a',self.stations)
 def render(self):
  self.router._directory_done=False;self.router._params.update(action='widget_live_start_group');self.added.clear();self.ends.clear();self.home.render(self.router,self.portal)
 def test_803_groups_and_88_stations_need_no_empty_sid_lookup_or_group_scan(self):
  db=self.index.connect(write=True)
  with db:db.executemany('INSERT OR IGNORE INTO groups VALUES(?,?,?,?,?)',[('p','live','g'+str(i),'Unused '+str(i),i+1) for i in range(802)])
  db.close();queries=[];original=sqlite3.connect
  class Observed(sqlite3.Connection):
   def execute(self,sql,args=()):queries.append((sql,args));return super().execute(sql,args)
  with mock.patch('live_home62.sqlite3.connect',side_effect=lambda *a,**k:original(*a,**dict(k,factory=Observed))):rows,code=self.home.rows(self.portal)
  self.assertEqual(code,'READY');self.assertEqual([r['sid'] for r in rows],[str(i) for i in range(88)])
  self.assertFalse(any('selected_categories' in sql or 'JOIN' in sql or 'sid=?' in sql for sql,args in queries))
  self.assertTrue(all('cid=?' in sql for sql,args in queries if 'FROM groups' in sql));self.assertLessEqual(len(queries),6)
 def test_same_budget_fault_on_redundant_empty_lookup_reproduces_old_zero_but_new_reader_delivers_88(self):
  import types
  root=Path(__file__).resolve().parents[1];hooks=json.loads((root/'tests/fixtures/xcmate_02962_reviewed_hooks.json').read_text())['modules']
  old=types.ModuleType('old_home61');exec(hooks['src/plugin.video.xtreammate/resources/lib/widget_home50.py']['old'],old.__dict__)
  original=sqlite3.connect
  class Budget(sqlite3.Connection):
   def execute(self,sql,args=()):
    if 'direct44' in sql and 'i.sid=?' in sql and '' in args:
     exc=sqlite3.OperationalError('synthetic exhausted ARM SQL budget');exc.sqlite_errorname='SQLITE_INTERRUPT';raise exc
    return super().execute(sql,args)
  with mock.patch('sqlite3.connect',side_effect=lambda *a,**k:original(*a,**dict(k,factory=Budget))):
   old.render(self.router,self.portal);self.assertEqual(len(self.added),0)
   self.render();self.assertEqual(len(self.added),88);self.assertTrue(self.ends[0][1]['succeeded'])
 def test_concurrent_wal_writer_publishes_new_generation_while_reader_keeps_one_consistent_group(self):
  original=sqlite3.connect;selected=threading.Event();done=threading.Event();errors=[]
  class Pinned(sqlite3.Connection):
   def execute(self,sql,args=()):
    result=super().execute(sql,args)
    if sql.startswith('SELECT generation'):
     selected.set();assert done.wait(5)
    return result
  def writer():
   try:
    self.assertTrue(selected.wait(5));db=original(self.index.path(),timeout=2)
    with db:
     db.execute("UPDATE items_v2 SET generation='next',payload=replace(payload,'Station ','New ') WHERE pid='p' AND kind='live' AND cid='a'")
     db.execute("UPDATE heads SET generation='next' WHERE pid='p' AND kind='live' AND cid='a'")
    db.close()
   except Exception as exc:errors.append(type(exc).__name__)
   finally:done.set()
  thread=threading.Thread(target=writer);thread.start()
  with mock.patch('live_home62.sqlite3.connect',side_effect=lambda *a,**k:original(*a,**dict(k,factory=Pinned))):rows,code=self.home.rows(self.portal)
  thread.join(5);self.assertFalse(thread.is_alive());self.assertFalse(errors);self.assertEqual(code,'READY');self.assertEqual(len(rows),88)
  self.assertTrue(all(r['name'].startswith('Station ') for r in rows))
 def test_epg_assets_and_decorator_failures_never_remove_sender_identities_or_click_targets(self):
  for error in (sqlite3.OperationalError('PRIVATE'),ValueError('PRIVATE'),OSError('PRIVATE'),TypeError('PRIVATE')):
   with mock.patch('widget_render47.values',side_effect=error):self.render()
   self.assertEqual(len(self.added),88)
   self.assertTrue(all(not folder and 'action=play_live' in url and item.props['XCMate.ProgrammeChannel46'] for url,item,folder in self.added))
   self.assertFalse(self.builtins)
  sys.modules['utils'].http_get.assert_not_called()
 def test_invalid_payload_keeps_database_identity_without_foreign_group_metadata(self):
  db=self.index.connect(write=True)
  with db:db.execute("UPDATE items_v2 SET payload='not-json' WHERE sid='0'")
  db.close();rows,code=self.home.rows(self.portal);self.assertEqual(len(rows),88);self.assertEqual(rows[0]['name'],'Station 0');self.assertEqual(rows[0]['category_id'],'a')
 def test_last_good_is_allowed_only_for_current_enabled_group_and_matching_policy(self):
  from widget_data41 import store,files,policy
  rows,_=self.home.rows(self.portal);name=files('p','live')[0];store(name,policy(self.portal,'live'),rows)
  with mock.patch.object(self.reader,'read',side_effect=self.reader.Failure('SQLITE_BUSY','HEAD')):
   values,code=self.home.rows(self.portal);self.assertEqual(code,'LAST_GOOD');self.assertEqual(len(values),88)
   self.portal['start_group_id']='other';self.assertFalse(self.home.rows(self.portal)[0])
  self.portal['start_group_id']='a';__import__('group_selection').save('p',[],kind='live',known=['a'])
  self.assertEqual(self.home.rows(self.portal),([],'GROUP_DISABLED'))
 def test_foreign_snapshot_and_payload_failures_cannot_publish_empty_success(self):
  from widget_data41 import store,files,policy
  store(files('p','live')[0],policy(self.portal,'live'),[dict(sid='bad',name='Foreign',category_id='b')])
  with mock.patch.object(self.reader,'read',side_effect=self.reader.Failure('BUDGET','PAGE')):self.render()
  self.assertFalse(self.added);self.assertFalse(self.ends[0][1]['succeeded'])
