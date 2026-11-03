"""Explicit start-group choice and verified pre-publication configuration backup."""
import errno
import hashlib
import os
import sqlite3
import stat
import tempfile


def failure(exc):
    code=getattr(exc,'code',None)
    messages={
        'XM-SETUP-CHECKPOINT':'Der Einrichtungsstand konnte lokal nicht sicher gespeichert werden. Zugang und Auswahl bleiben im Arbeitsspeicher; Speicherdiagnose prüfen. Kein bestätigter Netzwerkfehler.',
        'XM-SETUP-STORAGE':'Der lokale Speicher bietet keinen bestätigten sicheren Dateizugriff. Vorhandene Daten bleiben erhalten.',
        'XM-SETUP-DISCOVERY-BUSY':'Eine Anbieterprüfung läuft noch. Abwarten oder abbrechen; es wird kein zweiter Auftrag gestartet.',
        'XM-SETUP-BACKUP':'Die Sicherung konnte nicht vollständig verifiziert werden. Es wurden keine Portal-Einstellungen veröffentlicht.',
        'XM-SETUP-START':'Die Startgruppe muss zu den ausgewählten Sendergruppen gehören.'}
    from wizard_fault54 import describe
    seen=set();cause=exc
    for _ in range(4):
        if cause is None or id(cause) in seen:break
        seen.add(id(cause))
        code=getattr(cause,'code',None)
        if code in messages:return code,messages[code]
        network=describe(cause)
        if network:return network
        number=getattr(cause,'errno',None)
        storage={errno.ENOSPC,errno.EDQUOT,errno.EROFS,errno.EACCES,errno.EPERM,errno.ENOSYS,errno.ENOTSUP,errno.EIO,errno.ENOENT,errno.ENOTDIR,errno.EMFILE,errno.ENFILE,errno.EFBIG}
        if isinstance(cause,OSError) and number in storage:
            return 'XM-SETUP-STORAGE','Lokaler Datei-/Speicherzugriff fehlgeschlagen. Freien Speicher und Berechtigungen am Kodi-Datenpfad prüfen; keine Daten löschen.'
        if isinstance(cause,sqlite3.Error):
            return 'XM-SETUP-DB','Lokale Datenbank konnte nicht geprüft oder geschrieben werden. Auswahl bleibt erhalten; später erneut speichern.'
        cause=cause.__cause__
    return None



def choose_start(window):
    draft=window.draft
    if not draft.selected['live']:
        draft.data['start_group_id']='*';return True
    # Only the explicit Startgruppe button opens this dialog.
    ids=['*']+[str(g['category_id']) for g in draft.categories['live'] if str(g['category_id']) in draft.selected['live']]
    import xbmcgui
    labels=['Alle ausgewählten Sendergruppen']+[str(g['category_name']) for g in draft.categories['live'] if str(g['category_id']) in draft.selected['live']]
    current=draft.data.get('start_group_id','*')
    from menu_icons45 import select
    choice=select(xbmcgui.Dialog(),'Startgruppe für Live-TV',labels,preselect=ids.index(current) if current in ids else 0,default='list')
    if type(choice) is not int or not 0<=choice<len(ids):return False
    draft.data['start_group_id']=ids[choice]
    from setup_diagnostics71 import emit
    emit('SELECTED',draft.pid,**{k:len(v) for k,v in draft.selected.items()})
    return True


def backup(session):
    """Only bounded configuration files. Never copy/delete databases or addons.

    Must be called under the existing profile writer lock. A fresh backup is
    retained for manual recovery; automatic rollback still targets only the
    newly allocated portal ID.
    """
    from utils import addon_data_dir
    from wizard_resume53 import private_folder,write_file
    from wizard_storage71 import protect
    import xbmcvfs
    root=addon_data_dir();folder=os.path.join(root,'setup_backup71')
    private_folder(folder)
    target=tempfile.mkdtemp(prefix='before-',dir=folder);private_folder(target)
    names=('portals.json','xtreammate_groups.json','xtreammate_epg_sources.json','settings.xml','tmdb_read_access_token.txt')
    files=[(name,os.path.join(root,name)) for name in names]
    files.append(('guisettings.xml',xbmcvfs.translatePath('special://masterprofile/guisettings.xml')))
    manifest=dict(version=1,files={})
    try:
        for label,path in files:
            if os.path.islink(path):raise OSError('BACKUP_SYMLINK')
            if not os.path.exists(path):manifest['files'][label]=dict(existed=False);continue
            source_fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
            with os.fdopen(source_fd,'rb') as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):raise OSError('BACKUP_NOT_REGULAR')
                raw=stream.read(8*1024*1024+1)
            if len(raw)>8*1024*1024:raise ValueError('BACKUP_BUDGET')
            destination=os.path.join(target,label)
            fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            try:
                protect(destination,fd=fd)
                with os.fdopen(fd,'wb') as out:fd=None;out.write(raw);out.flush();os.fsync(out.fileno())
            finally:
                if fd is not None:os.close(fd)
            with open(destination,'rb') as check:
                if check.read()!=raw:raise OSError('BACKUP_READBACK')
            manifest['files'][label]=dict(existed=True,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        write_file(os.path.join(target,'manifest.json'),manifest)
        with open(os.path.join(target,'manifest.json'),encoding='utf-8') as check:
            if __import__('json').load(check)!=manifest:raise OSError('BACKUP_MANIFEST')
        return target
    except (OSError,ValueError,TypeError) as exc:
        from setup_draft import SaveError
        from setup_diagnostics71 import emit
        emit('FAILED',session,error=exc,path='ADDON_DATA')
        raise SaveError('XM-SETUP-BACKUP') from exc
