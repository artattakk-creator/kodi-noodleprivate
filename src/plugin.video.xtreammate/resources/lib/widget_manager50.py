"""Three direct choices -> verified native Home profile save, always opt-in."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from localization import tr
KINDS=((32401,'live'),(32403,'vod'),(32404,'series'))
ERRORS={'PROFILE_BUDGET','INVALID_SOURCE','SINGLE_WIDGET_HOME','UNVERIFIED_SKIN_VERSION','UNVERIFIED_SHORTCUTS_VERSION','UNSUPPORTED_SKIN','PLAYER_ACTIVE','NATIVE_EDITOR_BUSY','NO_SAVED_BINGIE_PROFILE','UNVERIFIED_MENU_SHARING','HOME_ID_UNVERIFIED','INVALID_PROPERTIES','DUPLICATE_PROPERTIES','OCCUPIED_SLOT','UNSAFE_BACKUP_FOLDER','UNSAFE_TARGET','UNSAFE_PLAN','BACKUP_VERIFY_FAILED','TARGET_CHANGED_NO_OVERWRITE','TARGET_VERIFY_FAILED','CANDIDATE_VERIFY_FAILED','PROFILE_CHANGED','SKIN_CHANGED','UNVERIFIED_SKIN_FILE','UNVERIFIED_TEMPLATE','UNVERIFIED_OVERRIDES','UNVERIFIED_HERO_REGION','UNVERIFIED_FONTS','PLAN_BUSY'}


def runtime():
    import xbmc,xbmcaddon,xbmcgui,xbmcvfs
    if xbmc.getSkinDir()!='skin.titan.bingie.mod':raise ValueError('UNSUPPORTED_SKIN')
    skin=xbmcaddon.Addon('skin.titan.bingie.mod');shortcuts=xbmcaddon.Addon('script.skinshortcuts')
    if skin.getAddonInfo('version')!='2.2.3':raise ValueError('UNVERIFIED_SKIN_VERSION')
    if shortcuts.getAddonInfo('version')!='2.1.0':raise ValueError('UNVERIFIED_SHORTCUTS_VERSION')
    if xbmc.getCondVisibility('Player.HasMedia'):raise ValueError('PLAYER_ACTIVE')
    if xbmc.getCondVisibility('Window.IsVisible(script-skinshortcuts.xml)') or xbmcgui.Window(10000).getProperty('skinshortcuts-isrunning')=='True':raise ValueError('NATIVE_EDITOR_BUSY')
    return Path(xbmcvfs.translatePath('special://profile/')).resolve(),Path(skin.getAddonInfo('path')).resolve()


def rebuild():
    import xbmc,xbmcgui
    xbmcgui.Window(10000).setProperty('skinshortcuts-reloadmainmenu','True')
    # Same entry point as BINGIE 2.2.3 Home.xml. Native builder reloads only
    # after a successful build; never reset its hashes, settings or cache.
    xbmc.executebuiltin('RunScript(script.skinshortcuts,type=buildxml&mainmenuID=900&group=mainmenu|powermenu)')


def trace(event,kind='',slot=0):
    if event not in ('BINDING_SAVED','SKIN_PATCH_VERIFIED','RESTORED'):return
    import xbmc
    try:xbmc.log('[XCMate][WIDGET50] event='+event+' kind='+(kind if kind in ('live','vod','series') else 'skin')+' slot='+str(int(slot)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def error(exc):
    import xbmc,xbmcgui
    code=str(exc) if str(exc) in ERRORS else 'LOCAL_UNAVAILABLE'
    xbmcgui.Dialog().ok('XCMate',tr(36410,code))
    if code in ('NO_SAVED_BINGIE_PROFILE','HOME_ID_UNVERIFIED','SINGLE_WIDGET_HOME'):
        if xbmcgui.Dialog().yesno('XCMate',tr(36428),nolabel=tr(36426),yeslabel=tr(36429),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
            runtime()
            xbmc.executebuiltin('RunScript(script.skinshortcuts,type=manage&group=mainmenu)')


def show(router,portal):
    if router._handle<0:
        import xbmc
        xbmc.executebuiltin('ActivateWindow(Videos,'+router.url(action='widget_setup',pid=portal['id'])+',return)');return
    import xbmcgui,xbmcplugin
    from menu_icons45 import icon
    from boot_diagnostics import finish_directory
    xbmcplugin.setContent(router._handle,'files');xbmcplugin.setPluginCategory(router._handle,tr(32443))
    for label,kind in KINDS:
        item=xbmcgui.ListItem(tr(label));item.setProperty('IsPlayable','false')
        item.setInfo('video',dict(title=tr(label),plot=tr(36400)))
        image=icon({'live':'home_live','vod':'movies_home','series':'series_home'}[kind]);item.setArt(dict(icon=image,thumb=image))
        menus=[(tr(36401),'RunPlugin('+router.url(action='widget_skin50',pid=portal['id'])+')'),
               (tr(36402),'RunPlugin('+router.url(action='widget_restore50',pid=portal['id'])+')'),
               (tr(36303),'RunPlugin('+router.url(action='widget_manage49',pid=portal['id'])+')'),
               (tr(36403),'ActivateWindow(Videos,'+router.url(action='widget_sources49',pid=portal['id'])+',return)')]
        item.addContextMenuItems(menus)
        xbmcplugin.addDirectoryItem(router._handle,router.url(action='widget_link50',pid=portal['id'],kind=kind),item,isFolder=False)
    finish_directory(router,succeeded=True,cacheToDisc=False)


def link(router,portal):
    import xbmcgui
    from menu_icons45 import select
    from widget_binding50 import context,options,prepare,apply
    from widget_skin50 import applied
    try:
        profile,skin=runtime();kind=router._params.get('kind','')
        if kind not in ('live','vod','series'):raise ValueError('INVALID_SOURCE')
        if kind=='live' and not applied(skin):
            if xbmcgui.Dialog().yesno('XCMate',tr(36404),nolabel=tr(36426),yeslabel=tr(36401),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):skin_setup()
            return
        ctx=context(profile,skin);choices=options(ctx,kind,portal['id'])
        already=[v for v in choices if v['state']=='ALREADY_LINKED']
        if already:xbmcgui.Dialog().ok('XCMate',tr(36406,already[0]['slot']+1));return
        choices=[v for v in choices if v['state']!='ALREADY_LINKED']
        if not choices:xbmcgui.Dialog().ok('XCMate',tr(36407));return
        labels=[tr(36408,v['slot']+1)+(' · '+tr(36409) if v['state']=='UPGRADE_OWN_LIVE' else '') for v in choices]
        choice=select(xbmcgui.Dialog(),tr(36411),labels,default='grid')
        if not isinstance(choice,int) or not 0<=choice<len(choices):return
        label=tr(dict((kind,label) for label,kind in KINDS)[kind]);plan=prepare(ctx,kind,portal['id'],choices[choice]['slot'],label)
        if plan.get('code')=='ALREADY_LINKED':return
        entries=plan['entries'];message=tr(36412,label,choices[choice]['slot']+1,entries[0]['before'],entries[0]['after'])
        xbmcgui.Dialog().textviewer(tr(36411),message)
        if not xbmcgui.Dialog().yesno(tr(36413),tr(36427,label,choices[choice]['slot']+1),nolabel=tr(36426),yeslabel=tr(36414),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):return
        current_profile,current_skin=runtime()
        apply(plan['id'],current_profile,current_skin,confirmed=True)
        trace('BINDING_SAVED',kind,choices[choice]['slot']+1)
        rebuild();xbmcgui.Dialog().notification('XCMate',tr(36415))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ET.ParseError) as exc:error(exc)


def skin_setup():
    import xbmcgui
    from widget_skin50 import prepare,apply,applied,FILES
    try:
        profile,skin=runtime()
        if applied(skin):xbmcgui.Dialog().ok('XCMate',tr(36416));return
        plan=prepare(skin)
        hashes='\n'.join(name+'\n'+e['before']+' → '+e['after'] for name,e in zip(FILES,plan['entries']))
        xbmcgui.Dialog().textviewer(tr(36401),tr(36417)+'\n\n'+hashes)
        if not xbmcgui.Dialog().yesno(tr(36413),tr(36418),nolabel=tr(36426),yeslabel=tr(36419),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):return
        current_profile,current_skin=runtime()
        if current_profile!=profile or current_skin!=skin:raise ValueError('PROFILE_CHANGED')
        apply(plan['id'],skin,confirmed=True);trace('SKIN_PATCH_VERIFIED');rebuild();xbmcgui.Dialog().notification('XCMate',tr(36415))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ET.ParseError) as exc:error(exc)


def restore():
    import xbmcgui
    from menu_icons45 import select
    from widget_transaction50 import folder,load
    try:
        profile,skin=runtime();plans=[]
        for p in folder().iterdir():
            if not p.is_dir() or len(p.name)!=32:continue
            try:
                for kind in ('binding','skin'):
                    try:plan=load(p.name,kind)
                    except (OSError,ValueError,KeyError):continue
                    status=json.loads((p/'state.json').read_text()).get('state')
                    if status in ('APPLIED','APPLYING','INTERRUPTED','RESTORING'):plans.append(plan)
                    break
            except (OSError,ValueError,KeyError):pass
        plans.sort(key=lambda p:p.get('at',0),reverse=True)
        labels=[tr(36421 if p['kind']=='skin' else 36420)+' · '+p['id'][:8] for p in plans]
        if not labels:xbmcgui.Dialog().ok('XCMate',tr(36422));return
        choice=select(xbmcgui.Dialog(),tr(36402),labels,default='shield')
        if not isinstance(choice,int) or not 0<=choice<len(plans):return
        plan=plans[choice]
        if not xbmcgui.Dialog().yesno(tr(36402),tr(36423),nolabel=tr(36426),yeslabel=tr(36424),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):return
        current_profile,current_skin=runtime()
        if current_profile!=profile or current_skin!=skin:raise ValueError('PROFILE_CHANGED')
        if plan['kind']=='binding':
            from widget_binding50 import apply
            apply(plan['id'],profile,skin,confirmed=True,restore=True)
        else:
            from widget_skin50 import apply
            apply(plan['id'],skin,confirmed=True,restore=True)
        trace('RESTORED');rebuild();xbmcgui.Dialog().notification('XCMate',tr(36425))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ET.ParseError) as exc:error(exc)
