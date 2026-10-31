"""Explicit private token actions. Never display paths, contents or raw errors."""
import hashlib
from localization import tr

def activate(addon):
    addon.setSetting('programme_tmdb46','true')
    addon.setSetting('tmdb_research43','true')
    from programme_refresh63 import request
    request()

def imported(choice,dialog,addon,gui,tokens):
    if choice==7:
        raw=dialog.input(tr(36661),type=getattr(gui,'INPUT_ALPHANUM',0),option=getattr(gui,'ALPHANUM_HIDE_INPUT',1))
        if not raw:return
        raw=raw.encode('utf-8');value=tokens.validate(raw)
        if tokens.read(tokens.location(),missing=True) is None:
            addon.setSetting('tmdb_read_token43',value)
            tokens.effective_tmdb_read_token(force=True)
            dialog.ok(tr(36620),tr(36628));return
        dialog.ok(tr(36620),tr(36662))
    else:
        source=dialog.browseSingle(1,tr(36621),'files','.txt',False,False)
        if not source:return
        from tmdb_import63 import selected
        progress=None
        try:
            factory=getattr(gui,'DialogProgress',None)
            if factory is not None:
                progress=factory();progress.create(tr(36620),tr(36663))
            raw=selected(source,cancel=(lambda:progress.iscanceled()) if progress else lambda:False)
        finally:
            if progress:progress.close()
        tokens.validate(raw)
    target=tokens.location()
    try:old=tokens.read(target,missing=True)
    except tokens.TokenError:raise tokens.TokenError('TOKEN_WRITE') from None
    expected=hashlib.sha256(old).hexdigest() if old is not None else None
    if old is not None and not dialog.yesno(tr(36620),tr(36627),defaultbutton=getattr(gui,'DLG_YESNO_NO_BTN',10)):return
    if choice==6 and not dialog.yesno(tr(36620),tr(36664),defaultbutton=getattr(gui,'DLG_YESNO_NO_BTN',10)):return
    tokens.import_bytes(raw,expected,target=target)
    if choice==6:activate(addon)
    dialog.ok(tr(36620),tr(36628)+'\n'+tr(36665 if choice==6 else 36666))

def show():
    import xbmcaddon,xbmcgui
    from menu_icons45 import select
    import tmdb_token61 as tokens
    dialog=xbmcgui.Dialog();addon=xbmcaddon.Addon()
    while True:
        state=tokens.status()
        labels=[tr(36621),tr({'FILE_VALID':36622,'FILE_MISSING':36623}.get(state,36624)),tr(36600),tr(36625),tr(36640),tr(36626),tr(36660),tr(36661)]
        choice=select(dialog,tr(36620),labels,actions=['settings','information','settings','check','back','check','settings','settings'])
        if not isinstance(choice,int) or not 0<=choice<len(labels) or choice==4:return
        if choice in (0,6,7):
            try:imported(choice,dialog,addon,xbmcgui,tokens)
            except (tokens.TokenError,OSError,UnicodeError) as exc:
                code=exc.code if isinstance(exc,tokens.TokenError) else 'TOKEN_UNREADABLE'
                dialog.ok(tr(36620),tr(36629,code)+'\n'+tr(36667))
        elif choice==1:dialog.ok(tr(36620),labels[1]+'\n'+tr(36630))
        elif choice==2:
            from tmdb_connection60 import launch
            launch()
        elif choice==3:
            if dialog.yesno(tr(36620),tr(36631),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):activate(addon)
        elif choice==5:
            if not dialog.yesno(tr(36620),tr(36632),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
            addon.setSetting('programme_tmdb46','false');addon.setSetting('tmdb_research43','false')
