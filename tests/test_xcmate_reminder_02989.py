"""P0-H: real JSON/SQLite, crash recovery, exact owner choices and no auto-tune."""
import importlib,json,sys,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,ADDON
class ReminderH89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.actions=__import__('programme_actions88');self.timers=__import__('guide_timers');self.runtime=__import__('reminder_runtime89');self.runtime._next=0
  self.event=dict(pid='p',sid='1',title='Future programme',start=self.now+600,stop=self.now+1800)
 def due(self,event=None):
  event=event or self.event;self.actions.toggle(event);self.runtime.worker(now=event['start']-299);return self.runtime.read('Ready')
 def choice(self,ready,value):
  self.runtime.put('Choice',dict(nonce=ready['nonce'],choice=value));self.runtime.worker(now=self.event['start']-298);return self.runtime.read('Ack')
 def test_future_bookmark_and_one_timer_default_five_minutes_and_rearm_idempotence(self):
  self.assertTrue(self.actions.toggle(self.event));rows=self.timers.list_timers('p');self.assertEqual(len(rows),1);self.assertEqual(rows[0]['notify_at'],self.event['start']-300)
  self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1);self.assertFalse(self.actions.toggle(self.event));self.assertEqual(self.timers.list_timers('p')[0]['state'],'cancelled')
  self.assertTrue(self.actions.toggle(self.event));self.assertEqual(len(self.timers.list_timers('p')),1);self.assertEqual(self.timers.list_timers('p')[0]['state'],'pending')
 def test_started_programme_remains_only_bookmark_without_late_timer(self):
  self.assertTrue(self.actions.toggle(dict(self.event,start=self.now-1)));self.assertFalse((self.folder/'guide_timers_v1.sqlite').exists());self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1)
 def test_dismiss_is_durable_keeps_watchlist_and_never_fires_again_after_restart(self):
  ready=self.due();self.assertTrue(ready['nonce']);self.assertEqual(self.choice(ready,'dismiss')['code'],'DISMISSED');self.assertEqual(self.timers.list_timers('p')[0]['state'],'dismissed')
  self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1);self.properties.clear();importlib.reload(self.runtime);self.runtime.worker(now=self.event['start']-290);self.assertFalse(self.runtime.read('Ready'))
 def test_two_due_alarms_are_sequential_and_unmark_cancels_active_alarm(self):
  self.actions.toggle(self.event);other=dict(self.event,sid='2');self.actions.toggle(other);self.runtime.worker(now=self.event['start']-299);first=self.runtime.read('Ready')
  self.runtime.worker(now=self.event['start']-298);self.assertEqual(self.runtime.read('Ready')['nonce'],first['nonce'])
  self.runtime.put('Choice',dict(nonce=first['nonce'],choice='dismiss'));self.runtime.worker(now=self.event['start']-298);self.runtime.worker(now=self.event['start']-297);second=self.runtime.read('Ready');self.assertNotEqual(first['id'],second['id'])
  event=other if second['sid']=='2' else self.event;self.assertFalse(self.actions.toggle(event));self.runtime.worker(now=self.event['start']-296);self.assertFalse(self.runtime.read('Ready'));self.assertEqual(self.runtime.read('Ack')['code'],'CANCELLED')
 def test_failed_bookmark_file_write_retains_recoverable_intent_then_replays_exact_state(self):
  bridge=__import__('reminder_bridge89')
  with mock.patch('logo_store89.atomic',side_effect=OSError('write failed')):
   with self.assertRaises(OSError):self.actions.toggle(self.event)
  db=self.timers.db()
  try:self.assertEqual(db.execute('SELECT count(*) FROM bookmark_intents89').fetchone()[0],1);bridge.recover(db);self.assertEqual(db.execute('SELECT count(*) FROM bookmark_intents89').fetchone()[0],0)
  finally:db.close()
  self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1);self.assertEqual(len(self.timers.list_timers('p')),1)
 def test_switch_is_persisted_before_closing_dialog_and_exact_resolver_called_once(self):
  ready=self.due();ui=__import__('reminder_ui89');ui._verify=None;ui._tune=None;closed=[]
  fake=SimpleNamespace(row=ready,pump89=lambda:self.runtime.put('Choice',dict(nonce=ready['nonce'],choice='switch')),close=lambda:closed.append(True));ui._dialog=fake
  with mock.patch('xbmc.executebuiltin') as play:
   ui.poll();self.assertEqual(closed,[]);play.assert_not_called()
   with mock.patch.object(self.runtime,'validate_event',return_value=True):self.runtime.worker(now=self.event['start']-298)
   self.assertEqual(self.timers.list_timers('p')[0]['state'],'selected');ui.poll();self.assertEqual(closed,[True]);play.assert_not_called()
   ui._tune['after']=0
   with mock.patch('exit_jobs.blocked',return_value=False),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmc.getCondVisibility',return_value=False):ui.poll()
   self.assertEqual(play.call_count,1);url=play.call_args.args[0];self.assertIn('action=play_live',url);self.assertIn('pid=p',url);self.assertIn('sid=1',url);self.assertNotIn('SECRET',url)
  ui._verify=None;ui._dialog=None;ui._tune=None
 def test_missing_sender_or_changed_programme_has_clear_error_without_tune(self):
  ready=self.due()
  with mock.patch.object(self.runtime,'channel',return_value=(None,None)):ack=self.choice(ready,'switch')
  self.assertEqual(ack['code'],'CHANNEL_UNAVAILABLE');self.assertEqual(ack['choice'],'dismiss');self.assertNotIn('url',ack);self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1)
 def test_canonical_programme_revalidation_rejects_changed_time_or_title(self):
  actual=dict(self.event,code='LOCAL_EVENT')
  with mock.patch('programme_events46.load',return_value=actual):self.assertTrue(self.runtime.validate_event(self.portal,dict(sid='1'),self.event))
  for row in (dict(actual,title='Wrong programme'),dict(actual,start=self.event['start']+60)):
   with mock.patch('programme_events46.load',return_value=row):self.assertFalse(self.runtime.validate_event(self.portal,dict(sid='1'),self.event))
 def test_old_timer_is_backed_up_without_deleting_original_and_callback_still_deduplicates(self):
  self.timers.add('p','2','Other',self.event);before=self.timers.list_timers('p');self.actions.toggle(self.event);self.assertTrue((self.folder/'guide_timers_v1.sqlite.before89.bak').is_file());self.assertEqual(len(self.timers.list_timers('p')),2)
  self.assertEqual(next(r for r in self.timers.list_timers('p') if r['sid']=='2'),before[0])
 def test_exactly_two_remote_buttons_and_default_dismiss_no_snooze_or_auto_tune(self):
  import xml.etree.ElementTree as E
  root=E.parse(ADDON/'resources/skins/Default/720p/XCMateReminder89.xml').getroot();self.assertEqual([c.get('id') for c in root.findall(".//control[@type='button']")],['610','611']);self.assertEqual(root.findtext('defaultcontrol'),'611')
  self.assertNotIn('Snooze',(ADDON/'resources/skins/Default/720p/XCMateReminder89.xml').read_text())
 def test_existing_guide_timer_and_detail_button_deduplicate_same_canonical_event(self):
  self.timers.add('p','1','Channel',self.event,minutes=3);self.actions.toggle(self.event)
  self.assertEqual(len(self.timers.list_timers('p')),1);self.assertEqual(self.timers.list_timers('p')[0]['notify_at'],self.event['start']-180)
 def test_legacy_exact_identity_import_preserves_file_and_deduplicates_new_bookmark(self):
  old=dict(self.event,channel=self.index.Reader('p').get('live','1')['name'],notify_at=self.event['start']-300,notified=False)
  path=self.folder/'reminders.json';raw=json.dumps([old]).encode();path.write_bytes(raw);self.actions.toggle(self.event)
  self.runtime._legacy_stamp=None;self.runtime.worker(now=self.event['start']-299)
  self.assertEqual(len(self.timers.list_timers('p')),1);self.assertTrue(self.runtime.read('Ready'));self.assertEqual(path.read_bytes(),raw)
  self.assertTrue(self.runtime.legacy_identity(dict(stream_url='https://provider.invalid/live/user/private/1.ts'),dict(self.portal,xc_host='https://provider.invalid',xc_user='user',xc_pass='private'),dict(sid='1')))
  self.assertFalse(self.runtime.legacy_identity(dict(stream_url='https://other.invalid/live/user/private/1.ts'),dict(self.portal,xc_host='https://provider.invalid',xc_user='user',xc_pass='private'),dict(sid='1')))
 def test_ambiguous_name_only_legacy_is_preserved_and_never_auto_tuned(self):
  old=dict(self.event,channel=self.index.Reader('p').get('live','1')['name']);old.pop('pid');old.pop('sid')
  path=self.folder/'reminders.json';raw=json.dumps([old]).encode();path.write_bytes(raw);self.runtime._legacy_stamp=None
  self.runtime.worker(now=self.event['start']-299);self.assertFalse(self.runtime.read('Ready'));self.assertFalse(self.timers.list_timers('p'));self.assertEqual(path.read_bytes(),raw)
 def test_crash_after_claim_never_replays_popup_and_keeps_watchlist(self):
  self.due();self.properties.clear();importlib.reload(self.runtime);self.runtime.worker(now=self.event['start']-290)
  self.assertFalse(self.runtime.read('Ready'));self.assertEqual(self.timers.list_timers('p')[0]['state'],'dismissed');self.assertEqual(len(__import__('guide_bookmarks').entries('p')),1)
 def test_back_timeout_and_skin_change_only_request_dismiss(self):
  ui=__import__('reminder_ui89')
  for kind in ('back','timeout','skin'):
   dialog=object.__new__(ui.ReminderDialog89);dialog.configure(dict(self.event,nonce=kind));dialog.native89=13001
   if kind=='back':dialog.onAction(SimpleNamespace(getId=lambda:92))
   if kind=='timeout':dialog.opened-=121
   with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=13002 if kind=='skin' else 13001),mock.patch('xbmc.executebuiltin') as play:
    dialog.pump89();self.assertEqual(self.runtime.read('Choice')['choice'],'dismiss');play.assert_not_called()
 def test_owned_nonmodal_live_navigator_allows_alarm_but_foreign_modals_do_not(self):
  ui=__import__('reminder_ui89');self.properties['XtreamMate.NavigatorIdentity']='a'*32
  with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=13001),mock.patch('xbmc.getCondVisibility',return_value=False),mock.patch.dict(sys.modules,{'live_overlay':SimpleNamespace(session_from_property=lambda _:dict(pid='p',sid='1'))}):
   self.assertTrue(ui.surface_ready89())
   self.properties['XtreamMate.NavigatorIdentity']='';self.assertFalse(ui.surface_ready89())
   self.properties['XtreamMate.NavigatorIdentity']='a'*32
   with mock.patch('xbmc.getCondVisibility',return_value=True):self.assertFalse(ui.surface_ready89())
 def test_claim_published_while_waiting_for_profile_lock_is_not_treated_as_orphan(self):
  ready=self.due();original=self.runtime.read;reads=[]
  def stale(name):
   reads.append(name)
   return {} if name=='Ready' and reads.count('Ready')==1 else original(name)
  with mock.patch.object(self.runtime,'read',side_effect=stale):self.runtime.worker(now=self.event['start']-298)
  self.assertEqual(self.runtime.read('Ready')['nonce'],ready['nonce']);self.assertEqual(self.timers.list_timers('p')[0]['state'],'notified')
 def test_already_notified_legacy_receipt_suppresses_pending_duplicate_until_explicit_rearm(self):
  self.actions.toggle(self.event)
  old=dict(self.event,channel=self.index.Reader('p').get('live','1')['name'],notified=True)
  path=self.folder/'reminders.json';raw=json.dumps([old]).encode();path.write_bytes(raw);self.runtime._legacy_stamp=None
  self.runtime.worker(now=self.event['start']-299)
  self.assertFalse(self.runtime.read('Ready'));self.assertEqual(self.timers.list_timers('p')[0]['state'],'notified');self.assertEqual(path.read_bytes(),raw)
  self.assertFalse(self.actions.toggle(self.event));self.assertTrue(self.actions.toggle(self.event));self.runtime.worker(now=self.event['start']-298)
  self.assertTrue(self.runtime.read('Ready'));self.assertEqual(len(self.timers.list_timers('p')),1)
