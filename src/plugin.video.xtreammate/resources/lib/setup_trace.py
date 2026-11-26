"""Fixed wizard phases, monotonic milliseconds and anonymous correlation only."""
import hashlib
import time

STAGES=frozenset(('WORK_TIMEOUT','SETUP_DISCOVER_DONE','GROUPS_RENDER_BEGIN','GROUPS_RENDER_END','GROUP_FOCUS','GROUP_TOGGLE','SETUP_SAVE_BEGIN','SETUP_SAVE_END','HANDOFF_TIMEOUT48','ENTRY48','QUEUED48','DISCOVER_BEGIN','DISCOVER_DONE','DISCOVER_FAILED','NATIVE_INIT_TIMEOUT48','SAVE_BEGIN','COPY_CATALOG','COPY_GUIDE','CONFIG_PUBLISH','VERIFY','SAVE_DONE','SAVE_FAILED','GUI_CLOSE_BEGIN','GUI_CLOSE_DONE','NATIVE_RELEASED','HOME_REQUESTED'))


def mark(stage,session='',**fields):
    if stage not in STAGES:return
    import xbmc
    code=hashlib.sha256(str(session).encode()).hexdigest()[:12] if session else 'NONE'
    safe=''
    if fields.get('kind') in ('live','vod','series'):safe+=' kind='+fields['kind']
    if type(fields.get('total')) is int:safe+=' total='+str(max(0,min(1000000,fields['total'])))
    try:xbmc.log('[XCMate][SETUP37] stage='+stage+' session='+code+' mono_ms='+str(int(time.monotonic()*1000))+safe,xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def failure(exc):
    """Log only fixed code locations and known callback names."""
    import os
    import xbmc

    modules = {"setup_navigation.py", "setup_wizard.py", "setup_window.py",
               "wizard_ui53.py", "wizard_ui54.py", "wizard_flow53.py"}
    locations = []
    frame = exc.__traceback__
    while frame:
        name = os.path.basename(frame.tb_frame.f_code.co_filename)
        if name in modules:
            locations.append(f"{name}:{frame.tb_lineno}")
        frame = frame.tb_next
    attribute = getattr(exc, "name", None)
    if attribute not in {"onInit", "onClick", "onAction", "getControl", "setFocusId",
                         "configure", "work", "stage", "draft", "render"}:
        attribute = "-"
    try:
        xbmc.log("[XCMate][SETUP37] stage=CALLBACK_FAILED type=" + type(exc).__name__
                 + " attribute=" + attribute + " location=" + ",".join(locations[-6:]),
                 xbmc.LOGINFO)
    except (AttributeError, RuntimeError):
        pass
