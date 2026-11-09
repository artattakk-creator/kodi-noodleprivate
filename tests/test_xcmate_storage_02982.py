"""Actual same-volume evidence, unknown/offline/capacity boundaries and probe."""
import importlib,json,os,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Storage82(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.s=importlib.import_module('art_storage82')
 def usage(self,free=2*1024**3,total=8*1024**3):return types.SimpleNamespace(free=free,total=total)
 def vfs(self,free=2*1024**3,total=8*1024**3):return types.SimpleNamespace(f_frsize=4096,f_bsize=4096,f_bavail=free//4096,f_blocks=total//4096)
 def test_same_real_volume_shutil_and_statvfs_agree_without_relocation(self):
  value=self.s.capacity(str(self.folder),self.usage(*[os.statvfs(self.folder).f_bavail*os.statvfs(self.folder).f_frsize,os.statvfs(self.folder).f_blocks*os.statvfs(self.folder).f_frsize]))
  self.assertEqual(value['capacity82'],'SAME_VOLUME_VERIFIED');self.assertEqual(value['statvfs_free82'],value['free'])
  self.assertNotIn(str(self.folder),json.dumps(value));self.assertEqual(len(value['volume82']),12)
 def test_emulated_alias_resolves_same_mount_and_never_uses_larger_other_volume(self):
  alias=self.folder/'alias';alias.symlink_to(self.folder,target_is_directory=True)
  with mock.patch('os.statvfs',return_value=self.vfs(free=64*1024**2)),mock.patch('shutil.disk_usage',return_value=self.usage()):
   value=self.s.capacity(str(alias))
  self.assertEqual(value['free'],64*1024**2);self.assertEqual(value['capacity82'],'CAPACITY_DISAGREEMENT')
 def test_full_target_and_exact_reserve_boundary_are_distinct(self):
  import art_storage
  reserve=1024**3;upcoming=4096;threshold=reserve+upcoming+art_storage.WRITE_HEADROOM
  for free,reason in [(1024,'BLOCKED_REAL_DISK'),(threshold-1,'RESERVE_BLOCKED'),(threshold,None)]:
   with mock.patch.object(art_storage,'capacity',return_value=dict(free=free,total=8*1024**3,reserve=reserve,budget=0,external=False,storage_availability='AVAILABLE')):
    if reason:
     with self.assertRaises(art_storage.ArtworkFailure) as caught:art_storage.check(upcoming)
     self.assertEqual(caught.exception.reason,reason)
    else:self.assertEqual(art_storage.check(upcoming)['free'],threshold)
 def test_unknown_or_offline_capacity_never_reports_a_safe_write(self):
  with mock.patch('os.statvfs',side_effect=OSError(19,'synthetic removed')):
   value=self.s.capacity(str(self.folder),self.usage())
  self.assertIsNone(value['free']);self.assertEqual(value['capacity82'],'STORAGE_OFFLINE')
 def test_explicit_bounded_probe_preserves_files_and_settings(self):
  root=self.folder/'programme_images46';root.mkdir();keep=root/'existing';keep.write_bytes(b'keep');before=dict(self.options)
  result=self.s.receipt(str(root),probe=True)
  self.assertEqual(result['write_probe82'],'VERIFIED_SAME_VOLUME');self.assertEqual(keep.read_bytes(),b'keep');self.assertEqual(list(root.iterdir()),[keep]);self.assertEqual(self.options,before)
 def test_probe_on_unknown_user_folder_is_refused_without_creating_files(self):
  result=self.s.receipt(str(self.folder/'unselected'),probe=True)
  self.assertEqual(result['write_probe82'],'OUTSIDE_OWN_CACHE');self.assertFalse((self.folder/'unselected').exists())
 def test_probe_never_bypasses_same_volume_disagreement_unknown_or_reserve(self):
  root=self.folder/'programme_images46';root.mkdir()
  for capacity,free,expected in [('CAPACITY_DISAGREEMENT',2*1024**3,'CAPACITY_DISAGREEMENT'),('CAPACITY_UNKNOWN',None,'CAPACITY_UNKNOWN'),('SAME_VOLUME_VERIFIED',32*1024**2+4095,'RESERVE_BLOCKED')]:
   with mock.patch('art_storage.capacity',return_value=dict(capacity82=capacity,free=free)),mock.patch('tempfile.mkstemp',side_effect=AssertionError('unadmitted probe write')):
    self.assertEqual(self.s.receipt(str(root),probe=True)['write_probe82'],expected)
  self.assertEqual(list(root.iterdir()),[])
