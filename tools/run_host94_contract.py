"""Run host tests with byte-verified historical inputs in a disposable clone.

PR #461 removed these ZIPs from main, not from immutable Git history. Tests
still exercise the exact historical bytes. Never restore them to the reviewed
checkout or a publication channel, and never fake a missing active package.
"""
import argparse,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE_BASE='85c9f1b9dc4aafea6eae6a055961ff159ad6e254'
ARCHIVE_COMMIT='b830fad1a19247cc08750970dc56edae0b8c2361'
DOCUMENT='docs/XCMate/ARCHIV_XCMATE_BINARIES_VOR_02990_2026-11-14_DE.md'


@lru_cache(maxsize=4)
def manifest(root):
    root=Path(root)
    raw=subprocess.check_output(['git','show',ARCHIVE_COMMIT+':'+DOCUMENT],cwd=root)
    if (root/DOCUMENT).read_bytes()!=raw:raise ValueError('ARCHIVE_DOCUMENT_CHANGED')
    rows={}
    for line in raw.decode().splitlines():
        match=re.match(r'\| \.\d+ \| \[`([^`]+)`\]\([^)]*\) \| (\d+) \| `([a-f0-9]{40})` \|$',line)
        if not match:continue
        name,size,sha=match.groups();path=Path(name)
        version=re.search(r'/plugin\.video\.xtreammate-0\.1\.29\.(\d+)\.zip(?:\.sha256)?$',name)
        if path.is_absolute() or '..' in path.parts or not version or int(version[1])>=90:raise ValueError('ARCHIVE_PATH_UNSAFE')
        if not name.startswith(('docs/XCMate/test-builds/','plugin.video.xtreammate/','online-test/')):raise ValueError('ARCHIVE_PATH_UNSAFE')
        if name in rows:raise ValueError('ARCHIVE_DUPLICATE')
        rows[name]=(int(size),sha)
    if len(rows)!=227:raise ValueError('ARCHIVE_FILE_SET_CHANGED')
    return rows


def read_archived(root,name):
    root=Path(root);entry=manifest(root).get(str(name))
    if entry is None:raise FileNotFoundError('NOT_AN_APPROVED_ARCHIVAL_INPUT')
    size,sha=entry
    object_id=subprocess.check_output(['git','rev-parse',ARCHIVE_BASE+':'+str(name)],cwd=root).decode().strip()
    if object_id!=sha:raise ValueError('ARCHIVE_HISTORY_MISMATCH')
    raw=subprocess.check_output(['git','cat-file','blob',sha],cwd=root)
    digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if len(raw)!=size or digest!=sha:raise ValueError('ARCHIVE_BLOB_CORRUPT')
    return raw


def materialize(root,shadow):
    root=Path(root).resolve();shadow=Path(shadow).resolve()
    if shadow==root or root in shadow.parents or shadow in root.parents:raise ValueError('ARCHIVE_MUST_USE_SEPARATE_CLONE')
    if not (shadow/'.git').is_dir():raise ValueError('ARCHIVE_CLONE_REQUIRED')
    rows=manifest(root);count=0
    for name in rows:
        target=shadow/name
        if any(p.is_symlink() for p in (target,*target.parents)):raise ValueError('ARCHIVE_SYMLINK')
        raw=read_archived(root,name)
        if target.exists():
            if target.read_bytes()!=raw:raise ValueError('ARCHIVE_MUST_NOT_OVERWRITE')
            continue
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);count+=1
    return count


def main(argv=None):
    command=list(sys.argv[1:] if argv is None else argv)
    if command[:1]==['--']:command=command[1:]
    if not command:raise SystemExit('Pass a host-test command after --')
    if subprocess.run(['git','diff','--quiet','HEAD','--','src/plugin.video.xtreammate','tests','tools'],cwd=ROOT).returncode:
        raise ValueError('HOST_TEST_REQUIRES_COMMITTED_SOURCE')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    with tempfile.TemporaryDirectory(prefix='xcmate94-host-',dir=os.environ.get('RUNNER_TEMP') or None) as temp:
        shadow=Path(temp)/'repo'
        subprocess.run(['git','clone','--shared','--quiet','--no-checkout',str(ROOT),str(shadow)],check=True)
        subprocess.run(['git','checkout','--quiet','--detach',head],cwd=shadow,check=True)
        count=materialize(ROOT,shadow)
        print('HOST94_ARCHIVAL_CONTEXT '+json.dumps(dict(source_commit=head,historical_files=count,archive_commit=ARCHIVE_COMMIT,source_modified=False,channels_published=False)),flush=True)
        env=dict(os.environ,XCMATE94_REVIEW_ROOT=str(ROOT),PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(shadow/'tests')+os.pathsep+str(shadow/'tools'))
        return subprocess.run(command,cwd=shadow,env=env).returncode

if __name__=='__main__':raise SystemExit(main())
