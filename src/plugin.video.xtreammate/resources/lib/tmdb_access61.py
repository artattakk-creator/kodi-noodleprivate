"""Explicit local token UI; never prints file contents or error text."""
import hashlib
from localization import tr

def show():
    import xbmcaddon,xbmcgui
    from menu_icons45 import select
    import tmdb_token61 as tokens
    dialog=xbmcgui.Dialog();addon=xbmcaddon.Addon()
    while True:
        state=tokens.status()
        labels=[tr(36621),tr({'FILE_VALID':36622,'FILE_MISSING':36623}.get(state,36624)),tr(36600),tr(36625),tr(36640),tr(36626)]
        choice=select(dialog,tr(36620),labels,actions=['settings','information','settings','check','back','check'])
        if not isinstance(choice,int) or not 0<=choice<len(labels) or choice==4:return
        if choice==0:
            source=dialog.browseSingle(1,tr(36621),'files','.txt',False,False)
            if not source:continue
            try:
                source=tokens.import_source_path(source)
                tokens.validate(tokens.read(source))
                old=tokens.read(tokens.location(),missing=True)
                expected=hashlib.sha256(old).hexdigest() if old is not None else None
                if old is not None and not dialog.yesno(tr(36620),tr(36627),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
                tokens.import_file(source,expected)
                dialog.ok(tr(36620),tr(36628))
            except (tokens.TokenError,OSError) as exc:
                code=exc.code if isinstance(exc,tokens.TokenError) else 'TOKEN_UNREADABLE'
                dialog.ok(tr(36620),tr(36629,code))
        elif choice==1:
            dialog.ok(tr(36620),labels[1]+'\n'+tr(36630))
        elif choice==2:
            from tmdb_connection60 import launch
            launch()
        else:
            enabled=choice==3
            if not dialog.yesno(tr(36620),tr(36631 if enabled else 36632),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
            addon.setSetting('programme_tmdb46','true' if enabled else 'false')
            addon.setSetting('tmdb_research43','true' if enabled else 'false')
