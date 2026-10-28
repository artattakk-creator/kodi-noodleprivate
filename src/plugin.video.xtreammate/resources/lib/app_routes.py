"""New routes only. Legacy provider/player entry points remain compatible."""
from localization import tr

ACTIONS=('live_hero48','programme_details46','widget_adapter46','widget_adapter45','native_options45','downloads_manage45','guide_backup44','update_notice','navigation_rail','artwork_manage','device_info', 'live_guide','search_continue','download_target_test','stability_test','download_folder','download_capabilities','theme_manager','branding_status','xcmate_licenses','guide_grid','playlist_editor','source_live','source_play','source_start','art_status','art_retry','art_db_health','ui_language','appearance_settings','xcmate_home','settings_home','settings_section','account_select','home_start','home_live',
         'movies_home','series_home','media_detail','media_favourites','global_search','search_section',
         'widget_live_start_group','widget_recent_vod','widget_recent_series','widget_setup','widget_manage49','widget_help49',
         'record_now','recordings_manage','recording_folder','recording_capabilities','about_xcmate','guide_browser','media_play','guide_timers','guide_status')
LABELS={'live':32460,'vod':32461,'series':32462}


def portal_for(router):
    from portals import get_active
    from home_menu import active_portal
    requested=router._params.get('pid','')
    if requested:
        from media_portal44 import selected
        return selected(router)
    return active_portal(get_active())


def _end(router,ok=True):
    from boot_diagnostics import finish_directory
    finish_directory(router,ok,cacheToDisc=False)


def dispatch(router):
    from experimental45 import protected,active,route
    if protected(router._params) and not active():return route(router,lambda:dispatch(router))
    import xbmc,xbmcgui,xbmcaddon
    from home_menu import settings,show,recording_folder
    action=router._params.get('action','xcmate_home')
    if action=='update_notice':
        from update_notice41 import show as show_notice
        show_notice();return
    if action=='live_guide':
        _end(router)
        if router._handle<0:
            from live_guide_navigation import run
            run(router._params.get('token',''))
        return
    if action=='search_continue':
        _end(router)
        from search_handoff import run
        run(router._params.get('token',''));return
    from portal_snapshot import PortalReadError
    try:portal=portal_for(router)
    except PortalReadError:
        if action!='media_play':raise
        from media_intent import failed
        failed(str(router._params.get('intent') or ''),str(router._params.get('pid') or ''))
        import xbmcplugin
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem())
        xbmcgui.Dialog().notification('XCMate',tr(35968));return
    if action=='media_play' and not portal:
        from media_intent import failed
        failed(str(router._params.get('intent') or ''),str(router._params.get('pid') or ''))
        import xbmcplugin
        xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
    if action in ('guide_timers','guide_status','widget_setup','widget_manage49') and not portal:
        _end(router,False)
        xbmcgui.Dialog().notification('XCMate',tr(32466));return
    if action=='live_hero48':
        _end(router)
        from live_hero48 import launch
        launch(router,portal);return
    if action=='programme_details46':
        from programme_window46 import route as programme_route
        programme_route(router,portal);return
    if action=='widget_adapter46':
        _end(router)
        from widget_adapter46 import show
        show();return
    if action=='widget_adapter45':
        _end(router)
        from widget_adapter45 import show
        show();return
    if action=='widget_setup':
        from widget_sources49 import show as widget_sources
        widget_sources(router,portal);return
    if action=='widget_help49':
        _end(router)
        from widget_sources49 import help as widget_help
        widget_help();return
    if action=='widget_manage49':
        _end(router)
        from widget_ui45 import manage
        manage(router,portal);return
    if action=='native_options45':
        _end(router)
        from settings_options45 import show
        show(router,router._params.get('group','system'));return
    if action=='downloads_manage45':
        _end(router)
        from downloads_ui import manage
        manage();return
    if action=='navigation_rail':
        _end(router)
        if portal:
            from nav_rail import standalone
            standalone(router,portal)
        return
    if action=='artwork_manage':
        _end(router)
        from artwork_ui import manage
        manage();return
    if action=='guide_backup44':
        _end(router)
        from guide_backup44 import show
        show();return
    if action=='device_info':
        _end(router)
        from device_info import show
        show();return
    if action=='download_target_test':
        _end(router);from download_target_test import show as target_test
        target_test();return
    if action=='stability_test':
        _end(router)
        from stability_monitor import show as show_stability
        show_stability();return
    if action=='branding_status':
        _end(router)
        from branding import show_status
        show_status();return
    if action=='xcmate_licenses':
        _end(router)
        from pathlib import Path
        root=Path(xbmcaddon.Addon().getAddonInfo('path'))
        text='XCMate · GS Media\nhttps://github.com/artattakk-creator/kodi-noodleprivate\n\n'
        for name in ('ORIGIN_AND_CHANGES.txt','LICENSE','THIRD_PARTY_SMB.txt','THIRD_PARTY_TABLER.txt','THIRD_PARTY_METADATA_43.txt'):
            text+=name+'\n'+(root/name).read_text(encoding='utf-8')+'\n\n'
        xbmcgui.Dialog().textviewer(tr(33406),text);return
    if action=='art_db_health':
        _end(router)
        from artwork_health_ui import manage
        manage();return
    if action in ('art_status','art_retry'):
        _end(router)
        from art_store import status,retry
        if action=='art_retry':
            from experimental45 import confirm
            if not confirm():return
            retry()
        from artwork_health_ui import show_status
        show_status();return
    if action=='ui_language':
        _end(router)
        from localization import choose_language
        if choose_language(): xbmc.executebuiltin('Container.Refresh')
        return
    if action=='theme_manager':
        _end(router)
        from theme_ui import manage
        manage();return
    if action=='appearance_settings':
        _end(router)
        from appearance import configure
        configure()
        return
    if action in ('settings_home','settings_section'):
        settings(router,portal,router._params.get('section','') if action=='settings_section' else '')
        return
    if action=='account_select':
        from portals import get_active
        rows=get_active()
        selected=router._params.get('selected','')
        _end(router)
        if not selected:
            i=__import__('menu_icons45').select(xbmcgui.Dialog(),tr(32463),[p.get('name',tr(32417)) for p in rows],default='user')
            if i<0 or i>=len(rows): return
            selected=str(rows[i]['id'])
        if selected not in {str(p['id']) for p in rows}: return
        xbmcaddon.Addon().setSetting('active_portal_id',selected)
        xbmc.executebuiltin('Container.Update('+router.url(action='xcmate_home',pid=selected)+')')
        return
    if action in ('download_folder','download_capabilities'):
        _end(router)
        from download_target_ui import choose
        choose(action=='download_capabilities');return
    if action=='recording_folder':
        _end(router); recording_folder(router._params.get('check')=='1'); return
    if action in ('record_now','recordings_manage'):
        _end(router)
        from capture_ui import start,manage
        if action=='recordings_manage':manage()
        elif portal:start(portal)
        else:xbmcgui.Dialog().ok('XCMate',tr(32466))
        return
    if action=='guide_timers':
        _end(router)
        if portal:
            from guide_timers import manage
            manage(portal['id'])
        return
    if action=='guide_status':
        _end(router)
        if portal:
            from guide_store import status_lines
            xbmcgui.Dialog().textviewer(tr(32464),'\n'.join(status_lines(portal)))
        return
    if action in ('about_xcmate','recording_capabilities','widget_setup'):
        _end(router)
        if action=='about_xcmate':
            text='XCMate '+xbmcaddon.Addon().getAddonInfo('version')+tr(32465)
        elif action=='recording_capabilities':
            from capture_ui import report
            text=report()
        else:
            text=widget_instructions(router,portal)
        xbmcgui.Dialog().textviewer('XCMate',text)
        return
    if not portal:
        _end(router,False)
        xbmcgui.Dialog().ok('XCMate',tr(32466))
        return
    router._params['pid']=portal['id']
    if action=='playlist_editor':
        _end(router,portal.get('type')=='m3u')
        if portal.get('type')=='m3u':
            from playlist_editor import open_editor
            open_editor(portal)
    elif action in ('source_live','source_play','source_start'):
        from source_live import browse,play
        browse(router,portal) if action=='source_live' else play(router,portal,direct=action=='source_start')
    elif action=='xcmate_home': show(router,portal)
    elif action=='home_start':
        from live_timing import begin
        begin(router,menu=True)
        if portal.get('type') in ('m3u','stb'):
            if router._handle>=0:
                from window_navigation import _anchor_home
                import uuid
                if not _anchor_home(router,portal,uuid.uuid4().hex):return
            from source_live import play
            play(router,portal,direct=True);return
        sid=str(portal.get('start_stream_id') or '')
        xc=router._xc(portal) if portal.get('type')=='xtream' else None
        from live_start import channel
        from live_timing import emit
        emit(router._live_timing,'PORTAL_REQUEST_BEGIN',network=0)
        router._start_channel=channel(portal,xc) if xc else None
        emit(router._live_timing,'PORTAL_REQUEST_END',network=0)
        if not sid or router._start_channel is None:
            _end(router,False)
            if xbmcgui.Dialog().yesno('XCMate',tr(32467)):
                xbmc.executebuiltin('Container.Update('+router.url(action='startup_settings',pid=portal['id'])+')')
            return
        # Legacy folder URLs must complete with Home before direct playback.
        # New Home entries run as actions (handle -1), retaining that directory.
        if router._handle>=0:
            from window_navigation import _anchor_home
            import uuid
            if not _anchor_home(router,portal,uuid.uuid4().hex):return
        router._play_start_direct()
    elif action=='home_live':
        if portal.get('type') in ('m3u','stb'):
            from source_live import browse
            browse(router,portal)
        else: router._live_groups()
    elif action=='global_search':
        from search_handoff import handoff
        from window_navigation import open_route
        from search_navigation import anchor,open_root
        open_route(router,portal,lambda:open_root(router,portal),after_close=handoff,anchor=anchor)
    elif action=='search_section': search(router,portal)
    elif action.startswith('widget_'): widget(router,portal,action)
    elif action in ('movies_home','series_home','media_detail','media_favourites'):
        kind=router._params.get('kind','series' if action=='series_home' else 'vod')
        if kind not in ('vod','series'):
            _end(router,False);return
        if not portal.get('include_vod' if kind=='vod' else 'include_series',True):
            _end(router,False)
            xbmcgui.Dialog().ok('XCMate',tr(32468))
            return
        from window_navigation import open_route
        from media_window import open_media
        from media_search import handoff
        open_route(router,portal,lambda:open_media(router,portal,kind,router._params.get('sid',''),favourites=action=='media_favourites'),after_close=handoff)
    elif action=='guide_grid':
        from window_navigation import open_route
        from guide_grid_window import open_grid
        from search_handoff import handoff
        open_route(router,portal,lambda:open_grid(router,portal),after_close=handoff)
    elif action=='guide_browser':
        from window_navigation import open_route
        from guide_window import open_guide
        from search_handoff import handoff
        open_route(router,portal,lambda:open_guide(router,portal),after_close=handoff)
    elif action=='media_play':
        from media_progress import play
        try:
            from exit_jobs import blocked
            if blocked():
                import xbmcplugin,xbmcgui
                xbmcplugin.setResolvedUrl(router._handle,False,xbmcgui.ListItem());return
            play(router,portal)
        finally:
            from media_intent import failed
            failed(str(router._params.get('intent') or ''),portal['id'])


def search(router,portal):
    import xbmc,xbmcgui,xbmcplugin
    from library_index import Reader
    query=router._params.get('q')
    if query is None:
        _end(router)
        query=xbmcgui.Dialog().input(tr(32470))
        if query.strip():
            xbmc.executebuiltin('Container.Update('+router.url(action='global_search',pid=portal['id'],q=query[:200])+')')
        return
    reader=Reader(portal['id'])
    incomplete=False
    from catalog_sync import request
    from library_index import IndexReadError,sync_state
    for section in LABELS:
        request(portal,section,portal.get('start_group_id','') if section=='live' else '',priority=5)
    xbmcplugin.setPluginCategory(router._handle,'XCMate · '+query[:200])
    xbmcplugin.setContent(router._handle,'files')
    kind=router._params.get('kind')
    if kind not in LABELS:
        for section,label_id in LABELS.items():
            label=tr(label_id)
            try:
                _,total=reader.page(section,query,limit=1)
                state=reader.state(section);jobs=sync_state(portal['id'],section)
                status=str(total)+tr(32606 if total==1 else 32471) if state else tr(32472)
                if jobs and jobs[0]['code']=='FAILED':
                    status+=' · '+tr(32614);incomplete=True
                elif not state or (jobs and jobs[0]['code']=='INDEXING'):
                    status+=' · '+tr(32613);incomplete=True
            except IndexReadError:
                status=tr(32614);incomplete=True
            router._add_dir(label+' · '+status,router.url(action='search_section',pid=portal['id'],kind=section,q=query))
    else:
        offset=page_offset(router)
        query_failed=False
        try: rows,total=reader.page(kind,query,offset=offset,limit=48)
        except IndexReadError:
            query_failed=True
            rows,total=[],0
            router._add_dir(tr(32614),router.url(action='search_section',pid=portal['id'],kind=kind,q=query))
        for item in rows: add_index_item(router,portal,kind,item)
        paging(router,total,offset,action='search_section',kind=kind,q=query)
        if not rows and not query_failed:
            router._add_dir(tr(32473) if reader.state(kind) else tr(32474),
                            router.url(action='global_search',pid=portal['id'],q=query))
    if incomplete:
        router._add_dir(tr(32615),router.url(action='global_search',pid=portal['id'],q=query))
    _end(router)


def page_offset(router):
    try: return min(9223372036854775807,max(0,int(router._params.get('offset','0'))))
    except (TypeError,ValueError): return 0


def paging(router,total,offset,**params):
    for label,target in ((tr(32475),offset-48),(tr(32476),offset+48)):
        if 0<=target<total:
            router._add_dir(tr(32477).format(label,total),router.url(pid=router._params['pid'],offset=target,**params))


def add_index_item(router,portal,kind,item,epg=None,recent=False,widget=False):
    if widget:
        from widget_items45 import describe,item as native_item
        import xbmcplugin
        info=None
        if epg:
            info=dict(now=epg.get('Now',''),next=epg.get('Next',''),start=epg.get('Start',0),stop=epg.get('Stop',0),progress=epg.get('Progress') if isinstance(epg.get('Progress'),(int,float)) else None,now_time='',next_time='',description='',_plot45=epg.get('plot',''))
        if epg and isinstance(epg.get('_event46'),dict):
            info=dict(epg['_event46']);info['_plot45']=epg.get('plot','')
        value=describe(portal,kind,item,getattr(router,'_widget_art44',{}),info,
            assets47=getattr(router,'_widget_assets47',{}).get(str(item['sid'])))
        from widget_diagnostics47 import counts as widget_counts47
        counters=getattr(router,'_widget_counts47',{})
        for key,count in widget_counts47([value]).items():counters[key]=counters.get(key,0)+count
        router._widget_counts47=counters
        xbmcplugin.addDirectoryItem(router._handle,value['url'],native_item(value),isFolder=False)
        return
    import os,xbmcaddon,xbmcgui,xbmcplugin
    from media_art import local_art
    li=xbmcgui.ListItem(item['name'])
    from theme_render import snapshot
    from theme_store import asset
    theme=snapshot()
    if widget:
        from widget_art44 import art as widget_art
        art=widget_art(item,getattr(router,'_widget_art44',{}))
    else:art=local_art(item,theme)
    if widget:
        li.setProperty('XCMate.WidgetKind41',kind)
        if kind=='live':
            li.setProperty('XCMate.LogoScale41','0.5')
            from widget_focus41 import token
            li.setProperty('XCMate.WidgetToken41',token(portal,item))
    if widget and theme:
        if art['landscape'].startswith(str(theme['folder'])+'/') or art['landscape']==os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media',{'live':'tv','series':'series'}.get(kind,'vod')+'.png'):
            art['landscape']=asset('widget.live' if kind=='live' else 'widget.series' if kind=='series' else 'widget.movie',art['landscape'],snapshot=theme)
        art['banner']=asset('widget.header',snapshot=theme)
    li.setArt(art)
    li.setInfo('video',{'title':item['name'],'plot':(epg or {}).get('plot') or item.get('plot') or '',
                        'mediatype':{'vod':'movie','series':'tvshow','live':'video'}[kind]})
    if epg:
        for name,value in epg.items(): li.setProperty('XtreamMate.'+name,str(value))
        progress=epg.get('Progress')
        li.setProperty('XCMate.EpgPercent41',str(round(max(0,min(1,float(progress)))*100)) if isinstance(progress,(int,float)) else '')
    li.setProperty('XCMate.PortalId',str(portal['id']))
    li.setProperty('XCMate.MediaId',item['sid'])
    li.setProperty('XCMate.Account',portal.get('name',''))
    if recent:
        from media_data import recent_label
        from utils import setting_int
        label=recent_label(item,setting_int('recent_days',10))
        li.setProperty('XCMate.AddedStatus',label)
        li.setInfo('video',{'plot':label+'\n'+str(item.get('plot') or '')})
    if kind=='live':
        li.setProperty('IsPlayable','true')
        url=router.url(action='play_live' if portal.get('type')=='xtream' else 'source_play',pid=portal['id'],sid=item['sid'],name=item['name'])
    else:
        url=router.url(action='media_detail',pid=portal['id'],kind=kind,sid=item['sid'])
    if kind!='live':li.setProperty('IsPlayable','false')
    if widget:li.setProperty('XCMate.ClickTarget44',url)
    xbmcplugin.addDirectoryItem(router._handle,url,li,isFolder=False)


def widget(router,portal,action):
    import xbmcplugin
    from widget_data41 import snapshot
    kind='live' if action=='widget_live_start_group' else 'vod' if action=='widget_recent_vod' else 'series'
    rows,code=snapshot(portal,kind)
    from widget_diagnostics47 import note as widget_note47
    widget_note47(portal['id'],kind,'SELECT',code,selected=len(rows))
    router._widget_counts47={}
    from widget_art44 import read as read_widget_art
    router._widget_art44=read_widget_art(portal['id'])
    if kind in ('vod','series'):
        from media_overrides43 import apply_many
        rows=apply_many(portal['id'],rows)
    if kind in ('live','vod'):
        from programme_assets47 import read_many
        router._widget_assets47=read_many(portal['id'],kind,rows)
    if action=='widget_live_start_group':
        from epg_sources import configuration
        from local_epg import now_next
        mappings=configuration(portal['id'])['mappings']
        # Existing widget routes, no skin mutation or full-cache hydration.
        from widget_group46 import infos as group_infos46
        from widget_focus41 import publish
        xbmcplugin.setContent(router._handle,'videos')
        for offset46 in range(0,len(rows),16):
            from programme_read47 import session as read_session47
            with read_session47():
                batch46=rows[offset46:offset46+16]
                info46=group_infos46(portal,batch46)
                if offset46==0:publish(portal,rows,info46)
                for row in batch46:
                    info=info46[row['sid']]
                    add_index_item(router,portal,'live',row,dict(Now=info['now'],Next=info['next'],
                        Start=info['start'],Stop=info['stop'],Progress=info['progress'] if info['progress'] is not None else '',
                        plot=guide_plot(info),_event46=info),widget=True)
        # Complete group; Kodi's native container scrolls horizontally and
        # requests textures as needed. EPG IO uses batches of sixteen.
        if not rows:
            router._add_dir(tr(35853) if code not in ('READY','CACHE') else tr(32479),
                            router.url(action='settings_section',pid=portal['id'],section='maintenance'))
    else:
        kind='vod' if action=='widget_recent_vod' else 'series'
        xbmcplugin.setContent(router._handle,'movies' if kind=='vod' else 'tvshows')
        for row in rows: add_index_item(router,portal,kind,row,recent=True,widget=True)
        if not rows and kind=='vod':
            # An unavailable/empty directory is not a dummy XCMate movie tile.
            xbmcplugin.setPluginCategory(router._handle,tr(36200) if code in ('READY','CACHE') else tr(36201))
        elif not rows and code not in ('READY','CACHE'):
            router._add_dir(tr(35853),
                            router.url(action='movies_home' if kind=='vod' else 'series_home',pid=portal['id']))
        # A poster row contains titles only. Old movies_home/series_home URLs
        # remain valid, but are not disguised as an extra film tile.
    widget_note47(portal['id'],kind,'ITEMS',code,**router._widget_counts47)
    _end(router)
    widget_note47(portal['id'],kind,'DIRECTORY',code,items=len(rows),directory_ok=1)


def guide_plot(info):
    """Localize the new widget without changing the frozen live resolver."""
    lines=[]
    if info.get('now'): lines.append(tr(32597,info.get('now_time',''),info['now']))
    if info.get('next'): lines.append(tr(32598,info.get('next_time',''),info['next']))
    if info.get('description'): lines.append(str(info['description']))
    return '\n'.join(lines) if lines else tr(32599)


def widget_instructions(router,portal):
    pid=portal['id'] if portal else ''
    lines=[tr(32483),
           tr(32484),
           tr(32485)]
    for title,action in ((tr(32401),'widget_live_start_group'),(tr(32486),'widget_recent_vod'),(tr(32487),'widget_recent_series')):
        lines+=['',title,router.url(action=action,pid=pid)]
    lines+=['',tr(32488),
            tr(32489),
            tr(32490)]
    return '\n'.join(lines)
