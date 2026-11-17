"""Run unchanged historical package guards against immutable .96 source.

The user's retained artifact is checked first; a Git snapshot never substitutes
for corrupt local retained bytes. Child Python isolates historical imports from
current release modules. Only this helper's disposable clone is removed.
"""
import hashlib,os,subprocess,sys,tempfile
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
REFERENCE='bc06f521d23ee5c1e6c9aaca456c2b3cc062f3fc'
PACKAGE='docs/XCMate/test-builds/02996/plugin.video.xtreammate-0.1.29.96.zip'
DIGEST='64d08c78581d074a9c86fee26ba94011119c1ab0f297de6a0bc9afee13cf1ba9'
METHODS={'test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes','test_review_package_never_stages_or_authorizes_any_channel'}
_temp=None

def verify_retained96(package=None,sidecar=None):
    package=Path(package) if package is not None else ROOT/PACKAGE
    sidecar=Path(sidecar) if sidecar is not None else ROOT/(PACKAGE+'.sha256')
    if package.is_symlink() or hashlib.sha256(package.read_bytes()).hexdigest()!=DIGEST:raise ValueError('HISTORICAL96_PACKAGE')
    expected=subprocess.check_output(['git','show',REFERENCE+':'+PACKAGE+'.sha256'],cwd=ROOT)
    if sidecar.is_symlink() or sidecar.read_bytes()!=expected:raise ValueError('HISTORICAL96_SIDECAR')
    if sidecar.read_text().split()!=[DIGEST,Path(PACKAGE).name]:raise ValueError('HISTORICAL96_SIDECAR')

@lru_cache(maxsize=1)
def snapshot():
    global _temp
    _temp=tempfile.TemporaryDirectory(prefix='xcmate-historical96-')
    repo=Path(_temp.name)/'repo'
    subprocess.run(['git','clone','--shared','--quiet','--no-checkout',str(ROOT),str(repo)],check=True)
    subprocess.run(['git','checkout','--quiet','--detach',REFERENCE],cwd=repo,check=True)
    return repo

def check(method):
    if method not in METHODS:raise ValueError('HISTORICAL96_TEST_NOT_ALLOWED')
    verify_retained96();repo=snapshot()
    env=dict(os.environ,PYTHONPATH=str(repo/'tests')+os.pathsep+str(repo/'tools'),PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable,'-m','unittest','test_release_candidate96.Release96.'+method,'-v'],
        cwd=repo,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
