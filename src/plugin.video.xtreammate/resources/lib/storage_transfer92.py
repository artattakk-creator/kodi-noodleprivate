"""Opt-in .92 migration gates; journal/hash/copy remain in artwork_migration."""
import hashlib
import os
import re
from pathlib import Path
from artwork_vfs import StorageFailure

def boot():
    # Kodi process, not Python interpreter/add-on restart. PID reuse protected.
    try:
        raw=Path('/proc/self/stat').read_text();start=raw[raw.rfind(')')+2:].split()[19]
    except (OSError,IndexError):raise StorageFailure('REBOOT_PROOF_UNAVAILABLE') from None
    return hashlib.sha256((str(os.getpid())+':'+start).encode()).hexdigest()

def require_reboot(source):
    proof=source.get('storage92') or {}
    rendered=proof.get('render_boot','')
    if not re.fullmatch('[a-f0-9]{64}',rendered) or rendered==boot():
        raise StorageFailure('REBOOT_READBACK_REQUIRED')

def prepare(target,confirmed=False):
    if confirmed is not True:raise StorageFailure('TARGET_PROBE_CONFIRMATION_REQUIRED')
    if '://' in target:
        # Existing NAS flow remains available, no invented free-space proof.
        raise StorageFailure('NAS_CAPACITY_NOT_VERIFIED_USE_ARTWORK_MANAGER')
    from artwork_migration import begin
    inventory=__import__('storage_inventory92').collect(budget=1)
    result=begin(target,shared=True,confirmed=True,strict87=True,reboot92=True)
    # Keep changing measurement timestamps OUT of source identity: repeated
    # preparation/resume must not create a new migration just for an audit.
    return dict(result,inventory_before=inventory)

def original_path(original,row):
    # Existing generic files are 64-hex .img; programme87 has exact owned names.
    ident=row['ident'];kind=row['kind']
    if kind=='programme87':
        from programme_storage87 import PATTERN
        if not PATTERN.fullmatch(ident):raise StorageFailure('SOURCE_CHANGED')
        name=ident
    else:
        if kind not in ('media','logos','posters89','programme89') or not re.fullmatch('[a-f0-9]{64}',ident):raise StorageFailure('SOURCE_CHANGED')
        name=ident+'.img'
    folder=Path(original.root)
    if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):raise StorageFailure('SOURCE_CHANGED')
    return str(folder.resolve()/name)
