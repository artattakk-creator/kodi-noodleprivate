"""Fresh-installer storage handoff. Existing setup/portal state is never reset."""
import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path
NAME='setup_storage92.json'

def read(profile):
    path=Path(profile)/NAME
    if not path.exists():return None
    if path.is_symlink() or path.stat().st_size>4096:raise OSError('STORAGE_SETUP_JOURNAL_INVALID')
    data=json.loads(path.read_bytes())
    if data.get('v')!=1 or data.get('state') not in ('WAITING','REQUESTED','PREPARED','DEFERRED'):raise OSError('STORAGE_SETUP_JOURNAL_INVALID')
    return data

def write(profile,data):
    folder=Path(profile);folder.mkdir(parents=True,exist_ok=True)
    if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):raise OSError('STORAGE_SETUP_PATH_UNSAFE')
    raw=json.dumps(data,sort_keys=True).encode()
    if len(raw)>4096:raise OSError('STORAGE_SETUP_JOURNAL_LIMIT')
    facts=os.statvfs(folder)
    if facts.f_bavail*(facts.f_frsize or facts.f_bsize)<4*1024**2+2*len(raw):raise OSError('STORAGE_SETUP_RESERVE_BLOCKED')
    fd,tmp=tempfile.mkstemp(prefix='.storage92-',dir=folder)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,folder/NAME)
        directory=os.open(folder,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
        if read(profile)!=data:raise OSError('STORAGE_SETUP_READBACK')
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def initialize(profile,fresh):
    if not fresh or read(profile) is not None:return
    write(profile,dict(v=1,state='WAITING'))

def run(profile):
    import xbmc,xbmcaddon,xbmcgui
    state=read(profile)
    if state is None or state['state'] in ('PREPARED','DEFERRED'):return 'PRESERVED'
    dialog=xbmcgui.Dialog()
    try:version=tuple(int(n) for n in xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('version').split('.'))
    except (RuntimeError,ValueError):version=()
    if version<(0,1,29,92):
        # No import of another add-on's utils; no writes under the wrong ID.
        dialog.ok('XCMate – Speicher','Die Speicherwahl benötigt XCMate 0.1.29.92. Bestehende Einstellungen bleiben erhalten. Später unter Einstellungen → Speicher öffnen.')
        write(profile,dict(v=1,state='DEFERRED'));return 'DEFERRED_VERSION'
    if state['state']=='REQUESTED' and not dialog.yesno('XCMate – Speicher','Unterbrochene Speicherwahl erneut öffnen?'):
        write(profile,dict(v=1,state='DEFERRED'));return 'DEFERRED'
    nonce=uuid.uuid4().hex;window=xbmcgui.Window(10000)
    write(profile,dict(v=1,state='REQUESTED',nonce=nonce))
    window.clearProperty('XCMate.Storage92.SetupAck')
    xbmc.executebuiltin('RunPlugin(plugin://plugin.video.xtreammate/?action=storage_setup92&setupnonce92='+nonce+')')
    monitor=xbmc.Monitor();deadline=time.monotonic()+180
    while time.monotonic()<deadline and not monitor.abortRequested():
        try:answer=json.loads(window.getProperty('XCMate.Storage92.SetupAck') or '{}')
        except ValueError:answer={}
        if answer.get('nonce')==nonce and answer.get('state') in ('PREPARED','DEFERRED'):
            write(profile,dict(v=1,state=answer['state']));return answer['state']
        monitor.waitForAbort(.1)
    # Timeout is not a successful storage migration, nor permission to reset it.
    dialog.ok('XCMate – Speicherwahl offen','Die Auswahl ist noch nicht bestätigt. Keine Speicherumstellung als erfolgreich gewertet. Fortsetzen unter XCMate → Einstellungen → Speicher.')
    return 'REQUEST_PENDING'
