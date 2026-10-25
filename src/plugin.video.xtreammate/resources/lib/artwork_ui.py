"""Explicit IR-friendly artwork management; worker progress, no automatic move."""
from concurrent.futures import ThreadPoolExecutor
import threading
import os
from localization import tr


def job(function):
    import xbmc,xbmcgui
    cancel=threading.Event();lock=threading.Lock();latest={}
    def progress(**value):
        with lock:latest.clear();latest.update(value)
    pool=ThreadPoolExecutor(max_workers=1);future=pool.submit(function,cancel.is_set,progress)
    dialog=xbmcgui.DialogProgress();dialog.create(tr(35200),tr(35220))
    try:
        while not future.done():
            with lock:value=dict(latest)
            total=value.get('files',0);done=value.get('done',0)
            percent=int(100*done/total) if total and value.get('stage') not in ('INVENTORY','VERIFYING') else 0
            stage=value.get('stage','WORKING')
            phase={'INVENTORY':35233,'COPYING':35234,'VERIFYING':35235,'CLEANUP':35236}.get(stage)
            text=(tr(phase) if phase else stage)+' · '+str(done)+' / '+str(total)+' · '+str(value.get('done_bytes',value.get('bytes',0)))+' Bytes'
            dialog.update(percent,text)
            if dialog.iscanceled() or getattr(xbmc.Monitor(),'abortRequested',lambda:False)():
                cancel.set();return None  # Worker retains original files/journal.
            xbmc.Monitor().waitForAbort(.1)
        return future.result()
    finally:dialog.close();pool.shutdown(wait=False,cancel_futures=True)


def _render(uri):
    import xbmcgui
    if not uri:return False
    class Probe(xbmcgui.WindowDialog):
        def __init__(self):
            super().__init__();self.addControls([xbmcgui.ControlImage(70,100,240,240,uri),xbmcgui.ControlLabel(70,350,1050,60,tr(35221))])
    window=Probe()
    try:
        window.show()
        return xbmcgui.Dialog().yesno(tr(35200),tr(35221),yeslabel=tr(35222),nolabel=tr(35223))
    finally:window.close()


def switch(mode,strategy='demand'):
    from artwork_gate import writer
    from artwork_config import choose,read
    with writer():
        current=read()
        if mode=='internal' and current.get('archive_mode',current['mode'])=='external':
            from artwork_vfs import StorageFailure
            raise StorageFailure('COPY_INCOMPLETE')
        return choose(mode,strategy=strategy)


def _pick():
    import xbmcgui
    from storage_sources import external_sources,kodi_sources
    dialog=xbmcgui.Dialog();kind=dialog.select(tr(35204),[tr(35224),tr(35225)])
    if kind not in (0,1):return None
    values=job(lambda cancel,progress:external_sources() if kind==0 else [row for row in kodi_sources() if row['path'].startswith('smb://')]) or []
    values.append(dict(label=tr(35226),path='/storage/' if kind==0 else 'smb://'))
    index=dialog.select(tr(35204),[v['label'] for v in values])
    if not 0<=index<len(values):return None
    return dialog.browseSingle(0,tr(35204),'files',defaultt=values[index]['path']) or None


def _manage():
    import xbmcgui
    from artwork_config import read
    from artwork_vfs import StorageFailure
    import artwork_migration as migration
    dialog=xbmcgui.Dialog()
    while True:
        value=read()
        labels=[tr(i) for i in (35201,35202,35203,35204,35205,35206,35207,35208,35209,35210,35211,35212,35213,35232)]
        choice=dialog.select(tr(35200)+' · '+value['mode'],labels)
        if choice<0:return
        try:
            if choice==0:
                from art_store import status
                data=job(lambda cancel,progress:dict(artwork=status(cancel),migration=migration.status()))
                if data is not None:
                    # Only counts/codes, never actual SMB path, provider URL or credentials.
                    import json
                    dialog.textviewer(tr(35200),tr(35230)+'\n'+value['mode']+' · '+(value.get('target','') if value['mode']=='external' else 'INTERNAL/KODI_TEXTURES')+'\n'+json.dumps(data,ensure_ascii=False,indent=2))
            elif choice in (1,2):
                mode='dynamic' if choice==1 else 'internal'
                if not dialog.yesno(tr(35200),tr(35214 if mode=='dynamic' else 35215)):continue
                if mode=='internal' and value.get('archive_mode',value['mode'])=='external':
                    job(lambda cancel,progress:migration.begin('INTERNAL'));dialog.ok(tr(35200),tr(35216))
                else:job(lambda cancel,progress:switch(mode))
            elif choice==3:
                target=_pick()
                if target:job(lambda cancel,progress:migration.begin(target));dialog.ok(tr(35200),tr(35216))
            elif choice==4:
                probe=job(lambda cancel,progress:migration.probe_image())
                if probe:
                    approved=_render(probe['uri'])
                    job(lambda cancel,progress:migration.remove_probe(probe))
                    if not approved:dialog.ok(tr(35200),tr(35223))
            elif choice==5:job(migration.inventory)
            elif choice==6:job(migration.copy)
            elif choice==7:
                def check(cancel,progress):return migration.verify(cancel,progress)
                if job(check):
                    uri=job(lambda cancel,progress:migration.display_candidate())
                    probe=None
                    if not uri:
                        probe=job(lambda cancel,progress:migration.probe_image());uri=probe['uri'] if probe else ''
                    approved=_render(uri)
                    if probe:job(lambda cancel,progress:migration.remove_probe(probe))
                    if approved:job(lambda cancel,progress:migration.approve_render(True))
            elif choice==8:
                if dialog.yesno(tr(35200),tr(35217)):job(migration.activate)
            elif choice==9:
                state=job(lambda cancel,progress:migration.status())
                if state and state['stage'] in ('ACTIVE','CLEANUP_PAUSED') and dialog.yesno(tr(35200),tr(35218,state['files'],state['bytes'])):
                    if dialog.yesno(tr(35200),tr(35219)):
                        result=job(lambda cancel,progress:migration.cleanup_report(state['transfer'],cancel,progress))
                        if result:
                            import json
                            dialog.textviewer(tr(35210),json.dumps(result,ensure_ascii=False,indent=2))
            elif choice==10:
                if value['mode']=='dynamic':dialog.ok(tr(35200),tr(35214));continue
                if dialog.yesno(tr(35200),tr(35227)):
                    def preload(cancel,progress):
                        from artwork_config import choose,locked,_write
                        from artwork_gate import writer
                        import uuid
                        with writer():
                            with locked():
                                config=read()
                                if config['mode']=='dynamic':return False
                                config['strategy']='all';config['origin']='USER';config['preload_generation']=uuid.uuid4().hex;_write(config)
                        return True
                    job(preload)
            elif choice==11:
                if dialog.yesno(tr(35200),tr(35237 if value.get('reserve_policy')=='adaptive' else 35228)):
                    def adaptive(cancel,progress):
                        from artwork_config import locked,_write
                        with locked():
                            config=read();config['reserve_policy']='fixed' if value.get('reserve_policy')=='adaptive' else 'adaptive';_write(config)
                    job(adaptive)
            elif choice==12:
                if dialog.yesno(tr(35200),tr(35229)):
                    from metadata_export import export
                    result=job(export)
                    if result:
                        import json
                        dialog.textviewer(tr(35213),json.dumps(result,ensure_ascii=False,indent=2))
            elif choice==13:
                import xbmcaddon
                from utils import setting_bool
                old=setting_bool('media_art_paused',False)
                if dialog.yesno(tr(35200),tr(35232)):
                    xbmcaddon.Addon().setSetting('media_art_paused','false' if old else 'true')
        except Exception as error:
            code=getattr(error,'code','ARTWORK_WRITER_BUSY' if isinstance(error,BlockingIOError) else type(error).__name__)
            # Fixed code only; no exception strings or private target paths.
            allowed={'StorageFailure','OSError','OperationalError','PermissionError','WriterBusy','BlockingIOError',
                     'INVALID_TARGET','TARGET_CREDENTIALS_NOT_ALLOWED','UNSUPPORTED_TARGET','STORAGE_OFFLINE','TARGET_WRITE_FAILED',
                     'TARGET_COLLISION','IMAGE_VERIFY_FAILED','INVALID_PROFILE_NAMESPACE','TARGET_SYMLINK','NO_TRANSFER','COPY_INCOMPLETE',
                     'SOURCE_IMAGE_INVALID','SOURCE_CHANGED','RENDER_NOT_VERIFIED','CLEANUP_NOT_AUTHORIZED','ARTWORK_WRITER_BUSY','METADATA_TARGET_REQUIRED'}
            dialog.ok(tr(35200),code if code in allowed else 'ARTWORK_OPERATION_FAILED')


def manage():
    from window_navigation import ownership
    with ownership() as acquired:
        if acquired:_manage()
