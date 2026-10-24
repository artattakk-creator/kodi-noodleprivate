"""Kodi 21 native window/dialog identity and privacy-safe lifecycle snapshots."""
import uuid
import xbmc,xbmcgui

OWNER_PROPERTY='XCMate.NativeOwner'
LEASE_PROPERTY='XCMate.NavigationLease'


def token(value):
    return value if isinstance(value,str) and len(value)==32 and all(c in '0123456789abcdef' for c in value) else ''


def state():
    def number(name):
        try:return int(getattr(xbmcgui,name)())
        except (AttributeError,RuntimeError,TypeError,ValueError):return None
    try:modal=bool(xbmc.getCondVisibility('System.HasActiveModalDialog'))
    except (AttributeError,RuntimeError):modal=True
    try:updating=bool(xbmc.getCondVisibility('Container.IsUpdating'))
    except (AttributeError,RuntimeError):updating=False
    return dict(window=number('getCurrentWindowId'),dialog=number('getCurrentWindowDialogId'),modal=modal,updating=updating)


def configure(view):
    view._native_owner=uuid.uuid4().hex;view._native_dialog_id=None
    setter=getattr(view,'setProperty',None)
    if setter:setter(OWNER_PROPERTY,view._native_owner)


def remember(view):
    if getattr(view,'_native_surface','window')!='dialog':return
    ident=state()['dialog']
    if ident is None or ident<13000:return
    try:
        if xbmcgui.Window(ident).getProperty(OWNER_PROPERTY)==view._native_owner:view._native_dialog_id=ident
    except (AttributeError,RuntimeError):pass


def capture(view):
    surface=getattr(view,'_native_surface','window')
    if surface=='dialog':
        remember(view);ident=getattr(view,'_native_dialog_id',None)
    else:ident=state()['window']
    return dict(window=ident,surface=surface,owner=token(getattr(view,'_native_owner','')))


def active(reference,snapshot=None):
    snapshot=state() if snapshot is None else snapshot
    if isinstance(reference,dict):
        ident=reference.get('window');surface=reference.get('surface','window')
        # An unidentified new dialog must never be treated as safely released.
        if surface=='dialog' and ident is None:return True
    else:ident=reference;surface='window'  # Existing in-memory legacy intents.
    return ident is not None and snapshot['dialog' if surface=='dialog' else 'window']==ident


def lease():
    try:return token(xbmcgui.Window(10000).getProperty(LEASE_PROPERTY))
    except (AttributeError,RuntimeError):return ''


def route_phase(router,phase,action):
    if phase not in ('ENTRY','RETURN'):return
    if action not in ('root','portal_home','xcmate_home','guide_grid','guide_browser','global_search','search_continue'):return
    try:
        snapshot=state()
        xbmc.log('[XCMate][ROUTE_STATE] phase={} action={} handle={} lease={} window={} dialog={} modal={} updating={} abort={}'.format(
            phase,action,'directory' if router._handle>=0 else 'action',lease(),snapshot['window'],snapshot['dialog'],
            int(snapshot['modal']),int(snapshot['updating']),int(getattr(xbmc.Monitor(),'abortRequested',lambda:False)())),xbmc.LOGINFO)
    except (AttributeError,RuntimeError,TypeError,ValueError):pass
