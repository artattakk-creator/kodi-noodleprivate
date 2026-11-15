"""Reproduce frozen .94 review in its original index baseline, not .94 runtime."""
from contextlib import contextmanager
from pathlib import Path
import shutil,subprocess,tempfile,zipfile
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
@contextmanager
def baseline():
 import release_candidate94,package_xcmate71
 with tempfile.TemporaryDirectory() as folder:
  root=Path(folder);source=root/'src';source.mkdir()
  original=ROOT/'docs/XCMate/test-builds/02994'
  with zipfile.ZipFile(original/release_candidate94.NAME) as z:z.extractall(source)
  for name in release_candidate94.FROZEN:
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(subprocess.check_output(['git','show',release_candidate94.BASE+':'+name],cwd=ROOT))
  target=root/'docs/XCMate/test-builds/02994';target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(original,target)
  with mock.patch.object(release_candidate94,'ROOT',root),mock.patch.object(package_xcmate71,'ROOT',root):yield root
