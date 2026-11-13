"""Reproduce frozen .92 review in its original index baseline, not .93 runtime."""
from contextlib import contextmanager
from pathlib import Path
import shutil,subprocess,tempfile,zipfile
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
@contextmanager
def baseline():
 import release_candidate92,package_xcmate71
 with tempfile.TemporaryDirectory() as folder:
  root=Path(folder);source=root/'src';source.mkdir()
  original=ROOT/'docs/XCMate/test-builds/02992'
  with zipfile.ZipFile(original/release_candidate92.NAME) as z:z.extractall(source)
  for name in release_candidate92.FROZEN:
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(subprocess.check_output(['git','show',release_candidate92.BASE+':'+name],cwd=ROOT))
  target=root/'docs/XCMate/test-builds/02992';target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(original,target)
  with mock.patch.object(release_candidate92,'ROOT',root),mock.patch.object(package_xcmate71,'ROOT',root):yield root
