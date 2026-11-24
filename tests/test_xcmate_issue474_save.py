"""Actual persisted mapping and dialog outcomes under Save failures."""
import importlib
import sqlite3
import unittest
from concurrent.futures import Future
from unittest import mock
import test_xcmate_epg_binding_02948 as old
import test_xcmate_mini_mapping_02996 as mini

class SaveIntegrity474(unittest.TestCase):
 def setUp(self):
  self.f=old.Binding48(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.context=importlib.import_module('mapping_context96')
 def test_cold_readback_io_failure_rolls_back_actual_mapping(self):
  before=self.f.sources._load_all();original=self.f.sources.configuration;failed=[]
  def read(pid):
   actual=self.f.sources._load_all().get('p',{}).get('source_mappings48',{}).get('1')
   if actual==dict(channel='xml',source=self.f.bid) and not failed:
    failed.append(True);raise OSError('SYNTHETIC_PRIVATE_PATH')
   return original(pid)
  with mock.patch.object(self.f.sources,'configuration',side_effect=read):
   with self.assertRaises((OSError,ValueError)):self.context.save_verified(self.f.portal,'1','xml',self.f.bid)
  self.assertTrue(failed);self.assertEqual(self.f.sources._load_all(),before)
 def test_readback_mismatch_rolls_back_instead_of_false_failure_with_changed_mapping(self):
  before=self.f.sources._load_all();original=self.f.sources.configuration;failed=[]
  def read(pid):
   value=original(pid)
   if '1' in value['mappings'] and not failed:
    failed.append(True);value['mappings'].sources48['1']=dict(channel='xml',source=self.f.aid)
   return value
  with mock.patch.object(self.f.sources,'configuration',side_effect=read):
   with self.assertRaises(ValueError):self.context.save_verified(self.f.portal,'1','xml',self.f.bid)
  self.assertEqual(self.f.sources._load_all(),before)
 def test_success_preserves_unknown_fields_and_other_portals(self):
  data=self.f.sources._load_all();data['p']['future_field']={'keep':'opaque'};data['other']={'sources':[],'mappings':{'1':'foreign'}};self.f.sources._write_all(data)
  self.assertTrue(self.context.save_verified(self.f.portal,'1','xml',self.f.bid))
  after=self.f.sources._load_all();self.assertEqual(after['p'].get('future_field'),{'keep':'opaque'});self.assertEqual(after['other'],data['other'])
 def test_rollback_restores_only_own_mapping_and_preserves_later_other_sender_change(self):
  binding=self.f.binding
  receipt=binding.commit_verified(self.f.portal,'1','xml',self.f.bid)
  binding.save(self.f.portal,'2','xml',self.f.aid)
  binding.rollback_verified(receipt)
  after=self.f.sources.configuration('p');self.assertNotIn('1',after['mappings']);self.assertEqual(binding.binding(after['mappings'],'2'),dict(channel='xml',source=self.f.aid))
 def test_rollback_never_overwrites_conflicting_new_choice(self):
  receipt=self.f.binding.commit_verified(self.f.portal,'1','xml',self.f.bid)
  self.f.binding.save(self.f.portal,'1','xml',self.f.aid)
  with self.assertRaisesRegex(ValueError,'MAPPING_CONFLICT'):self.f.binding.rollback_verified(receipt)
  after=self.f.sources.configuration('p');self.assertEqual(self.f.binding.binding(after['mappings'],'1'),dict(channel='xml',source=self.f.aid))
 def test_unexpected_preparation_exception_still_rolls_back(self):
  before=self.f.sources._load_all()
  def fail():raise KeyError('SYNTHETIC_SECRET')
  with self.assertRaises(ValueError):self.f.binding.commit_verified(self.f.portal,'1','xml',self.f.bid,prepare=fail)
  self.assertEqual(self.f.sources._load_all(),before)

class MiniSaveUI474(unittest.TestCase):
 def setUp(self):
  self.owner=mini.MiniMapping96(methodName='runTest');self.owner.setUp();self.addCleanup(self.owner.doCleanups)
  self.d=self.owner.dialog;self.f=self.owner.fixture
  self.d._preview()
 def test_save_ack_follows_actual_snapshot_apply_and_precedes_close(self):
  observed=[]
  def notify(*a,**kw):
   saved=self.f.sources.configuration('p')['source_mappings48']['1']
   observed.append((saved,self.owner.snapshot.get('1',self.f.now)['now'],self.d._closed))
  with mock.patch.object(self.f.dialog,'notification',side_effect=notify):self.d.onClick(405)
  self.assertTrue(self.d.saved);self.assertTrue(self.d._closed)
  self.assertEqual(observed,[(dict(channel='xml',source=self.f.bid),'Source 2',False)])
 def test_parent_render_failure_keeps_verified_binding_and_dialog(self):
  with mock.patch.object(self.owner.parent,'_render',side_effect=RuntimeError('SYNTHETIC_SECRET_MUST_NOT_LEAK')):self.d.onClick(405)
  self.assertTrue(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources.configuration('p')['source_mappings48']['1'],dict(channel='xml',source=self.f.bid))
  self.assertIn('MAPPING_UI_REFRESH_FAILED',self.d.getControl(103).text)
  self.assertNotIn('SYNTHETIC_SECRET',self.d.getControl(103).text)
 def test_parent_exit_keeps_completed_worker_binding_without_gui_ack(self):
  receipt=self.f.binding.commit_verified(self.f.portal,'1','xml',self.f.bid)
  future=Future();future.set_running_or_notify_cancel();self.d.future=future;self.d._saving53=True
  self.owner.parent._closed=True
  with mock.patch.object(self.d,'show'):self.d.run()
  future.set_result(receipt)
  self.assertTrue(self.d._closed);self.assertFalse(self.d.saved)
  self.assertEqual(self.f.sources.configuration('p')['source_mappings48']['1'],dict(channel='xml',source=self.f.bid))
 def test_write_failure_reports_fixed_error_and_preserves_open_dialog(self):
  before=self.f.sources._load_all()
  with mock.patch.object(self.f.sources,'_write_all',side_effect=OSError('SYNTHETIC_PRIVATE_PATH')):self.d.onClick(405)
  self.assertFalse(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources._load_all(),before)
  self.assertIn('MAPPING_WRITE_FAILED',self.d.getControl(103).text)
  self.assertNotIn('SYNTHETIC_PRIVATE',self.d.getControl(103).text)
 def test_unexpected_gui_type_error_keeps_verified_binding(self):
  with mock.patch.object(self.owner.parent,'_render',side_effect=TypeError('SYNTHETIC_SECRET')):self.d.onClick(405)
  self.assertTrue(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources.configuration('p')['source_mappings48']['1'],dict(channel='xml',source=self.f.bid))
 def receipt(self):
  return self.f.binding.commit_verified(self.f.portal,'1','xml',self.f.bid,prepare=lambda:self.d.adapter96.prepare_saved(self.d.candidate,self.f.bid))
 def test_unrelated_save_does_not_invalidate_exact_tuple_ack(self):
  receipt=self.receipt();self.f.binding.save(self.f.portal,'2','xml',self.f.aid)
  self.d._committed474(receipt)
  self.assertTrue(self.d.saved)
  self.assertEqual(self.f.binding.binding(self.f.sources.configuration('p')['mappings'],'1'),dict(channel='xml',source=self.f.bid))
  self.assertNotIn('MAPPING_CONFLICT',self.d.getControl(103).text)
 def test_newer_mapping_cannot_be_acknowledged_as_old_worker_result(self):
  receipt=self.receipt();self.f.binding.save(self.f.portal,'1','xml',self.f.aid)
  self.d._committed474(receipt)
  self.assertFalse(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.binding.binding(self.f.sources.configuration('p')['mappings'],'1'),dict(channel='xml',source=self.f.aid))
  self.assertIn('MAPPING_CONFLICT',self.d.getControl(103).text)
 def test_profile_changed_receipt_never_updates_ui_or_another_profile(self):
  receipt=self.receipt();before=self.f.sources._load_all()
  with mock.patch('epg_handoff63.profile_scope',return_value='different-profile'):self.d._committed474(receipt)
  self.assertFalse(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources._load_all(),before)
  self.assertIn('MAPPING_PROFILE_CHANGED',self.d.getControl(103).text)
 def test_failed_mini_apply_can_preview_another_source_and_retry(self):
  with mock.patch.object(self.owner.parent,'_render',side_effect=RuntimeError('SYNTHETIC')):self.d.onClick(405)
  self.d.source=dict(id=self.f.aid,name='First XMLTV');self.d.previewed=False
  self.d._preview()
  self.assertTrue(self.d.previewed)
  self.assertEqual(self.owner.snapshot.get('1',self.f.now)['now'],'Source 1')
  self.d.onClick(405);self.assertTrue(self.d.saved)
 def test_sqlite_selected_source_failure_keeps_verified_binding(self):
  original=sqlite3.connect;failed=[]
  class Connection:
   def __init__(self,inner):object.__setattr__(self,'inner',inner)
   def __getattr__(self,name):return getattr(self.inner,name)
   def __setattr__(self,name,value):setattr(self.inner,name,value)
   def __enter__(self):self.inner.__enter__();return self
   def __exit__(self,*args):return self.inner.__exit__(*args)
   def execute(self,sql,*args,**kw):
    if 'FROM guide44_inputs' in sql and 'SELECT title' in sql:
     failed.append(True);raise sqlite3.OperationalError('interrupted')
    return self.inner.execute(sql,*args,**kw)
  with mock.patch('sqlite3.connect',side_effect=lambda *a,**k:Connection(original(*a,**k))):self.d.onClick(405)
  self.assertTrue(failed);self.assertTrue(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources.configuration('p')['source_mappings48']['1'],dict(channel='xml',source=self.f.bid))
  self.assertIn('MAPPING_RELOAD_FAILED',self.d.getControl(103).text)

class GridSaveUI474(unittest.TestCase):
 def setUp(self):
  self.f=old.Binding48(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
  from xcmate027_fixture import ADDON
  self.parent=self.f.window()
  self.d=importlib.import_module('guide_mapping48').MappingWindow48('XCMateMapping48.xml',str(ADDON),'Default','720p')
  self.d.configure(self.parent);self.d.onInit();self.addCleanup(self.d.close)
  self.d.source=dict(id=self.f.bid,name='Second XMLTV');self.d.candidate=dict(id='xml',name='Disney Channel')
  p=mock.patch.object(self.d,'_submit',side_effect=lambda load,ready:ready(load()));p.start();self.addCleanup(p.stop)
  self.d._preview()
 def test_save_publishes_verified_grid_and_visible_manual_marker(self):
  self.d.onClick(405)
  self.assertTrue(self.d.saved);self.assertTrue(self.d._closed)
  row=self.parent.rows[self.parent.row]
  self.assertEqual((row['mapping'],row['epg_id'],row['events'][0]['title']),('MANUAL','xml','Source 2'))
  self.assertIn('manuell',self.parent.getControl(102).label.lower())
 def test_grid_apply_failure_keeps_verified_binding_and_restores_parent_rows(self):
  original=self.d.adapter96.original['rows']
  with mock.patch.object(self.parent,'_render',side_effect=RuntimeError('SYNTHETIC')):self.d.onClick(405)
  self.assertTrue(self.d.saved);self.assertFalse(self.d._closed)
  self.assertEqual(self.f.sources.configuration('p')['source_mappings48']['1'],dict(channel='xml',source=self.f.bid))
  self.assertEqual(self.parent.rows,original)
