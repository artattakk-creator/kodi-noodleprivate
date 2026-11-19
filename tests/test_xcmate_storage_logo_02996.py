"""Real owned-file tests; Android/SMB device rendering remains NOT_TESTED."""
import importlib
import json
import os
import unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png

class StorageLogo96(Fixture, unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.row=dict(sid='1',name='Station',stream_icon='https://images.example.org/original.png')
  self.patch=mock.patch('utils.addon_data_dir',return_value=str(self.folder));self.patch.start();self.addCleanup(self.patch.stop)
 def logo(self):
  self.assertIsNotNone(importlib.util.find_spec('logo_overrides96'),'persistent station override module required')
  return importlib.import_module('logo_overrides96')
 def storage(self):
  self.assertIsNotNone(importlib.util.find_spec('storage_artwork96'),'one cache policy/dialog required')
  return importlib.import_module('storage_artwork96')
 def test_missing_cache_budget_starts_at_32_and_explicit_64_survives(self):
  module=importlib.import_module('programme_art46')
  self.options.pop('programme_art_budget46',None)
  self.assertEqual(module.limit(),32*1024**2)
  self.options['programme_art_budget46']='1';self.assertEqual(module.limit(),64*1024**2)
 def test_override_requires_confirmation_and_survives_provider_change_and_reload(self):
  module=self.logo();before=dict(self.row)
  with self.assertRaisesRegex(ValueError,'CONFIRMATION'):module.save(self.portal,self.row,png(),confirmed=False)
  self.assertFalse(module.root().exists())
  uri=module.save(self.portal,self.row,png(),confirmed=True)
  self.assertTrue(Path(uri).is_file());self.assertEqual(self.row,before)
  module=importlib.reload(module)
  changed=dict(self.row,stream_icon='https://images.example.org/refreshed.png')
  self.assertEqual(module.read(self.portal,[changed]),{'1':uri})
  self.assertEqual(importlib.import_module('logo_manifest86').read(self.portal,[changed],with_fallback=False),{'1':uri})
  self.assertEqual(module.read(dict(self.portal,id='other'),[changed]),{})
 def test_reset_only_selected_mapping_and_corrupt_file_fails_closed(self):
  module=self.logo();a=module.save(self.portal,self.row,png(),confirmed=True)
  other=dict(self.row,sid='2');module.save(self.portal,other,png(),confirmed=True)
  module.reset(self.portal,self.row,confirmed=True)
  self.assertEqual(module.read(self.portal,[self.row]),{})
  self.assertEqual(module.read(self.portal,[other]),{'2':a})
  Path(a).write_bytes(b'broken');self.assertEqual(module.read(self.portal,[other]),{})
 def test_path_and_image_guards_allow_only_explicit_smb_or_local_images(self):
  module=self.logo();local=self.folder/'chosen.png';local.write_bytes(png())
  class VFSFile:
   def __init__(self, uri):self.stream=open(uri,'rb')
   def readBytes(self, count):return self.stream.read(count)
   def close(self):self.stream.close()
  with mock.patch('xbmcvfs.File',VFSFile,create=True):
   self.assertEqual(module.selection(str(local)),png())
  for source in ('https://example.org/a.png','smb://host/share/../a.png','/tmp/a.svg','smb://host/share/a.png'):
   with self.assertRaises(ValueError):module.selection(source)
  bad=self.folder/'wrong.jpg';bad.write_text('not an image')
  with mock.patch('xbmcvfs.File',VFSFile,create=True),self.assertRaises((ValueError,OSError)):module.selection(str(bad))
 def test_disk_safety_floor_still_blocks_logo_write_without_mutating_mapping(self):
  module=self.logo()
  with mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=1024,total=4*1024**3)):
   with self.assertRaises(OSError):module.save(self.portal,self.row,png(),confirmed=True)
  self.assertEqual(module.read(self.portal,[self.row]),{})
 def test_truncated_png_decoder_error_is_safe_editor_validation_failure(self):
  module=self.logo()
  with self.assertRaises(Exception) as raised:module.validated(b'\x89PNG\r\n\x1a\n'+b'broken')
  self.assertIsInstance(raised.exception,ValueError)
  self.assertEqual(str(raised.exception),'LOGO_IMAGE_INVALID')
 def test_editor_preview_cancel_never_saves_override_or_provider_row(self):
  module=self.logo();editor=importlib.import_module('logo_editor96');before=dict(self.row)
  self.dialog.browseSingle=lambda *args,**kwargs:str(self.folder/'selected.png')
  choose=iter([1,0,3])
  run=lambda fn:fn(lambda:False,lambda **kw:None)
  with mock.patch('menu_icons45.select',side_effect=lambda *a,**kw:next(choose)),mock.patch('artwork_ui.job',side_effect=run),mock.patch.object(module,'selection',return_value=png()),mock.patch('decoded_assets88.put',return_value={'uri':'http://127.0.0.1/preview.png'}),mock.patch('artwork_ui._render',return_value=False):
   editor.edit(self.portal,self.row)
  self.assertEqual(self.row,before);self.assertFalse(module.root().exists())
 def test_every_artwork_storage_entry_routes_to_same_cache_dialog(self):
  with mock.patch('storage_artwork96.manage') as central:
   importlib.import_module('artwork_ui').manage()
  central.assert_called_once_with()
 def test_old_archive_cleanup_entry_uses_selective_temporary_preview(self):
  self.storage();choose=iter([14,-1])
  with mock.patch('menu_icons45.select',side_effect=lambda *a,**kw:next(choose)),mock.patch('storage_artwork96.cleanup_dialog',create=True) as cleanup:
   importlib.import_module('artwork_ui')._manage()
  cleanup.assert_called_once_with()
 def test_storage_status_menu_never_starts_forced_database_maintenance(self):
  choose=iter([1,-1]);run=lambda fn:fn(lambda:False,lambda **kw:None)
  with mock.patch('menu_icons45.select',side_effect=lambda *a,**kw:next(choose)),mock.patch('artwork_ui.job',side_effect=run),mock.patch('storage_ui92.show'),mock.patch('storage_maintenance92.run',return_value={}) as maintenance:
   importlib.import_module('storage_ui92').manage()
  maintenance.assert_not_called()
 def test_cache_budget_rejects_ram_only_kodi_setting_write(self):
  module=self.storage();guard=importlib.import_module('settings_guard96')
  Path(guard.path()).write_text('<settings><setting id="programme_art_budget46">0</setting></settings>')
  choose=iter([1,2,-1])
  run=lambda fn:fn(lambda:False,lambda **kw:None)
  with mock.patch('menu_icons45.select',side_effect=lambda *a,**kw:next(choose)),mock.patch('artwork_ui.job',side_effect=run):
   module.manage()
  self.assertIn('>0<',Path(guard.path()).read_text())
  self.dialog.ok.assert_called_once()
 def test_guide_channel_rows_resolve_confirmed_logo_before_provider(self):
  module=self.logo();uri=module.save(self.portal,self.row,png(),confirmed=True)
  from types import SimpleNamespace
  from xcmate027_fixture import Control
  import xml.etree.ElementTree as ET
  control=Control(ET.fromstring('<control type="list" id="210"/>'))
  parent=SimpleNamespace(portal=self.portal,getControl=lambda n:control,setFocusId=lambda n:None,
                         _load_events=lambda *a:None,mappings={})
  with mock.patch('media_art.request'),mock.patch('epg_views.prefetch_short_guides'):
   importlib.import_module('guide_window').GuideWindow._channels_ready(parent,([self.row],1))
  self.assertEqual(control.items[0].art['thumb'],uri)
 def test_large_guide_grid_refresh_uses_same_override_resolver(self):
  module=self.logo();uri=module.save(self.portal,self.row,png(),confirmed=True)
  from types import SimpleNamespace
  control=SimpleNamespace(setImage=mock.Mock())
  parent=SimpleNamespace(portal=self.portal,rows=[dict(channel=self.row,events=[])],_theme=None,getControl=lambda n:control)
  importlib.import_module('guide_grid_window').GuideGridWindow._refresh_logos(parent)
  control.setImage.assert_called_once_with(uri)
 def test_dynamic_write_uses_real_small_reserve_and_never_archive_fallback(self):
  module=self.storage();facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=100*1024**2,total=4*1024**3)
  with mock.patch('art_storage82.capacity',return_value=facts):
   receipt=module.check_dynamic(self.folder,1024)
   self.assertEqual(receipt['reserve'],32*1024**2)
  with mock.patch('art_storage82.capacity',return_value=dict(facts,free=1024)):
   with self.assertRaises(OSError):module.check_dynamic(self.folder,1024)
 def test_storage_report_measures_programme_temp_and_persistent_logo_volumes_separately(self):
  module=self.storage();seen=[]
  def capacity(folder, **kwargs):
   seen.append(str(folder));return dict(capacity82='SAME_VOLUME_VERIFIED',free=100*1024**2,total=4*1024**3)
  with mock.patch('art_storage82.capacity',side_effect=capacity):report=module.status()
  self.assertEqual({row['role'] for row in report.get('classes',[])},{'PROGRAMME_CACHE','TEMPORARY_CACHE','PERSISTENT_LOGOS'})
  self.assertGreaterEqual(len(set(seen)),3)
  self.assertTrue(all('path' not in row for row in report['classes']))
 def test_cleanup_preview_protects_pins_manual_databases_and_unknown_files(self):
  module=self.storage();cache=importlib.import_module('artwork_temp85').cache()
  cache.checked(create=True)
  body=png();digest=__import__('hashlib').sha256(body).hexdigest();file=cache.root/(digest+'.png');file.write_bytes(body)
  entries={digest:dict(file=file.name,size=len(body),at=1,until=1,pins={})}
  cache.atomic(cache.root/'index.json',json.dumps(dict(format=1,entries=entries)).encode())
  protect=[]
  for name in ('manual.png','guide.sqlite','guide.sqlite-wal','user-backup.json'):
   p=cache.root/name;p.write_bytes(b'KEEP');protect.append(p)
  plan=module.cleanup_preview();self.assertEqual(plan['files'],1);self.assertEqual(plan['bytes'],len(body));self.assertTrue(file.exists())
  with self.assertRaisesRegex(ValueError,'CONFIRMATION'):module.cleanup(plan,confirmed=False)
  result=module.cleanup(plan,confirmed=True);self.assertEqual(result['files'],1);self.assertFalse(file.exists())
  self.assertTrue(all(p.read_bytes()==b'KEEP' for p in protect))
 def test_cleanup_stale_preview_cannot_remove_newly_pinned_file(self):
  module=self.storage();cache=importlib.import_module('artwork_temp85').cache();cache.checked(create=True)
  digest='a'*64;file=cache.root/(digest+'.png');file.write_bytes(png());entry=dict(file=file.name,size=file.stat().st_size,until=1,pins={})
  cache.atomic(cache.root/'index.json',json.dumps(dict(format=1,entries={digest:entry})).encode());plan=module.cleanup_preview()
  entry['pins']={'manual':99999999999};cache.atomic(cache.root/'index.json',json.dumps(dict(format=1,entries={digest:entry})).encode())
  with self.assertRaisesRegex(OSError,'CHANGED'):module.cleanup(plan,confirmed=True)
  self.assertTrue(file.exists())
 def test_expired_manual_image_context_never_enters_selective_cleanup(self):
  module=self.storage();cache=importlib.import_module('artwork_temp85').cache();cache.checked(create=True)
  digest=__import__('hashlib').sha256(png()).hexdigest();file=cache.root/(digest+'.png');file.write_bytes(png())
  record=dict(file=file.name,size=file.stat().st_size,until=1,pins={},contexts={'confirmed':dict(manual85=True)})
  cache.atomic(cache.root/'index.json',json.dumps(dict(format=1,entries={digest:record})).encode())
  self.assertEqual(module.cleanup_preview()['files'],0);self.assertTrue(file.exists())
 def test_rolling_cache_never_expires_prior_confirmed_manual_context(self):
  cache=importlib.import_module('artwork_temp85').cache();cache.checked(create=True)
  digest=__import__('hashlib').sha256(png()).hexdigest();file=cache.root/(digest+'.png');file.write_bytes(png())
  record=dict(file=file.name,size=file.stat().st_size,until=1,pins={},contexts={'confirmed':dict(manual85=True)})
  cache.atomic(cache.root/'index.json',json.dumps(dict(format=1,entries={digest:record})).encode())
  from PIL import Image
  import io
  out=io.BytesIO();Image.new('RGB',(8,8),(1,2,3)).save(out,'PNG')
  cache.max_bytes=len(out.getvalue());cache.max_objects=1
  try:cache.put(out.getvalue())
  except OSError:self.fail('Confirmed manual bytes must not consume the rolling-cache budget')
  self.assertTrue(file.exists());self.assertIn(digest,cache.index())
 def test_logo_override_after_first_512_input_channels_is_not_omitted(self):
  module=self.logo();uri=module.save(self.portal,self.row,png(),confirmed=True)
  rows=[dict(self.row,sid='dummy-'+str(i)) for i in range(512)]+[self.row]
  self.assertEqual(module.read(self.portal,rows),{'1':uri})
