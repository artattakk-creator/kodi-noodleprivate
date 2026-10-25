"""Wizard action/owner handoff. No Home navigation while the wizard is closing."""
import json
import time
import uuid
import xbmc
import xbmcgui

KEY='XCMate.SetupTransition37'
ACTIVE='XCMate.SetupActive37'


def _home():return xbmcgui.Window(10000)


def active():
    try:return 0<=time.time()-float(_home().getProperty(ACTIVE))<7200
    except (ValueError,TypeError):return False


def _queue(stage,**fields):
    _home().setProperty(KEY,json.dumps(dict(stage=stage,at=time.time(),deadline=time.monotonic()+15,**fields)))


def maybe_fresh(router):
    from artwork_config import read,locked,_write
    value=read()
    if value.get('origin')!='FRESH' or value.get('wizard_attempted') or active():return
    with locked():
        value=read()
        if value.get('wizard_attempted'):return
        value['wizard_attempted']=True;_write(value)
    _queue('launch',url=router.url(action='setup_wizard'))


def run(router):
    from boot_diagnostics import finish_directory,mark
    from window_navigation import ownership
    if router._handle>=0:
        # Old directory bookmarks become an action on an established root.
        # Never instantiate a modal window under a still-changing directory.
        from main import Router
        router._params['action']='root';router._root()
        xbmc.executebuiltin('Container.Update('+router.url(action='root')+',replace)')
        _queue('launch',url=router.url(action='setup_wizard'));return
    finish_directory(router,cacheToDisc=False)
    with ownership() as acquired:
        if not acquired or active():return
        _home().setProperty(ACTIVE,str(time.time()))
        _home().clearProperty('XCMate.SetupClosedId37')
        try:
            from setup_wizard import setup
            portal=setup()
            # The owner pump has closed and returned. Service additionally
            # waits until Kodi reports that native window/dialog released.
            _queue('return',pid=str(portal['id']) if portal else '',closed=_home().getProperty('XCMate.SetupClosedId37'))
        except Exception:
            _queue('return',pid='',closed=_home().getProperty('XCMate.SetupClosedId37'))
            raise
        finally:_home().clearProperty(ACTIVE)


def poll():
    from window_lifecycle import state,lease
    raw=_home().getProperty(KEY)
    try:value=json.loads(raw) if raw and len(raw)<4096 else None
    except ValueError:return
    if not isinstance(value,dict) or value.get('stage') not in ('launch','return'):return
    if time.monotonic()>value.get('deadline',0):
        _home().clearProperty(KEY);return
    if active() or lease():return
    native=state()
    if native['modal'] or native['updating']:return
    try:closed=int(value.get('closed') or 0)
    except (ValueError,TypeError):closed=0
    if closed>=13000 and native['window']==closed:return
    if value['stage']=='launch':
        from urllib.parse import urlsplit,parse_qs
        current=urlsplit(xbmc.getInfoLabel('Container.FolderPath'))
        if current.netloc!='plugin.video.xtreammate' or parse_qs(current.query).get('action',['root'])[0]!='root':return
    if time.time()-value['at']<.2:return
    _home().clearProperty(KEY)  # Commit once before reentrant native dispatch.
    if value['stage']=='launch':xbmc.executebuiltin('RunPlugin('+value['url']+')')
    elif value.get('pid'):
        from urllib.parse import urlencode
        url='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='xcmate_home',pid=value['pid']))
        xbmc.executebuiltin('Container.Update('+url+',replace)')
    else:xbmc.executebuiltin('Container.Refresh')
