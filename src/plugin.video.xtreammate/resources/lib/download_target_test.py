"""Explicit tiny target transfer: no provider, no media job, own nonce files only."""
import hashlib,os,uuid

PAYLOAD=b'XCMate selected target test\n'*64


def run(root=None):
    import download_targets as targets
    import media_files as files
    from storage_diagnostics import mark,kind
    root=targets.normalize(root or targets.configured());targets.check_identity(root)
    caps=targets.probe(root);token=uuid.uuid4().hex
    target=files.join(root,'.xcmate-target-test-'+token+'.probe')
    digest=hashlib.sha256(PAYLOAD).hexdigest();owned=None;created=False;stage=None;stage_identity=None
    mark('DOWNLOAD','TARGET_TEST_BEGIN',kind(root),'SMB2' if root.startswith('smb://') else 'USB_STAGE' if caps['staging'] else 'NATIVE')
    try:
        files.capacity(root,len(PAYLOAD))
        if root.startswith('smb://'):
            import download_smb as smb
            stage=files.join(targets.stage_root(),'.xcmate-test-'+token+'.probe')
            fd=os.open(stage,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);stage_identity=os.fstat(fd)
            with os.fdopen(fd,'wb') as stream:stream.write(PAYLOAD);stream.flush();os.fsync(stream.fileno())
            smb.upload_exclusive(stage,target);created=True
            correct=files.size(target)==len(PAYLOAD) and smb.digest(target,len(PAYLOAD))==digest
        else:
            fd=os.open(files.native(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);owned=os.fstat(fd);created=True
            with os.fdopen(fd,'wb') as stream:stream.write(PAYLOAD);stream.flush();os.fsync(stream.fileno())
            fd=os.open(files.native(target),os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as stream:correct=stream.read(len(PAYLOAD)+1)==PAYLOAD
        if not correct:raise targets.Failure('TARGET_VERIFY_FAILED','TEST_READBACK')
        # Remove only our acknowledged creation after content verification.
        if owned is not None:
            current=os.stat(files.native(target),follow_symlinks=False)
            if (current.st_dev,current.st_ino)!=(owned.st_dev,owned.st_ino):raise targets.Failure('TARGET_CHANGED','TEST_CLEANUP')
        files.remove(target);created=False
        mark('DOWNLOAD','TARGET_TEST_DONE',kind(root),count=len(PAYLOAD))
        return dict(bytes=len(PAYLOAD),sha256=digest,backend=caps['backend'],removed=True)
    except Exception as exc:
        mark('DOWNLOAD','FAILED',kind(root),error=exc)
        # On uncertain/corrupted/replaced output never remove by name alone.
        # The new nonce probe may remain; no existing file is overwritten/deleted.
        raise
    finally:
        if stage_identity is not None:
            try:
                current=os.stat(stage,follow_symlinks=False)
                if (current.st_dev,current.st_ino)==(stage_identity.st_dev,stage_identity.st_ino):os.unlink(stage)
            except FileNotFoundError:pass


def show():
    import xbmcgui
    from capture_ui import work
    from localization import tr
    if not xbmcgui.Dialog().yesno('XCMate',tr(35008)):return
    try:
        result=work(run)
        if result:xbmcgui.Dialog().ok('XCMate',tr(35009)+'\n'+str(result['bytes'])+' bytes\nSHA256 '+result['sha256'])
    except Exception as exc:
        from transfer_diagnostics import describe
        xbmcgui.Dialog().ok('XCMate',describe(exc,'download'))
