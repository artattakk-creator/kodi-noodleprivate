"""New routes only. Legacy provider/player entry points remain compatible."""
from localization import tr

ACTIONS=('live_guide','search_continue','download_target_test','stability_test','download_folder','download_capabilities','theme_manager','branding_status','xcmate_licenses','guide_grid','playlist_editor','source_live','source_play','source_start','art_status','art_retry','art_db_health','ui_language','appearance_settings','xcmate_home','settings_home','settings_section','account_select','home_start','home_live',
         'movies_home','series_home','media_detail','media_favourites','global_search','search_section',
         'widget_live_start_group','widget_recent_vod','widget_recent_series','widget_setup',
         'record_now','recordings_manage','recording_folder','recording_capabilities','about_xcmate','guide_browser','media_play','guide_timers','guide_status')
LABELS={'live':32460,'vod':32461,'series':32462}


def portal_for(router):
    from portals import get_active
    from home_menu import active_portal
    active=get_active();requested=router._params.get('pid','')
    if requested: return next((p for p in active if str(p['id'])==requested),None)
    return active_portal(active)


def _end(router,ok=True):
    from boot_diagnostics import finish_directory
    finish_directory(router,ok,cacheToDisc=False)


def dispatch(router):
    import xbmc,xbmcgui,xbmcaddon
    from home_menu import settings,show,recording_folder
    action=router._params.get('action','xcmate_home')
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
    portal=portal_for(router)
    if action in ('guide_timers','guide_status','widget_setup') and not portal:
        _end(router,False)
        xbmcgui.Dialog().notification('XCMate',tr(32466));return
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
        for name in ('ORIGIN_AND_CHANGES.txt','LICENSE','THIRD_PARTY_SMB.txt'):
            text+=name+'\n'+(root/name).read_text(encoding='utf-8')+'\n\n'
        xbmcgui.Dialog().textviewer(tr(33406),text);return
    if action=='art_db_health':
        _end(router)
        from artwork_health_ui import manage
        manage();return
    if action in ('art_status','art_retry'):
        _end(router)
        from art_store import status,retry
        if action=='art_retry': retry()
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
            i=xbmcgui.Dialog().select(tr(32463),[p.get('name',tr(32417)) for p in rows])
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
        if portal.get('type') in ('m3u','stb'):
            if router._handle>=0:
                from window_navigation import _anchor_home
                import uuid
                if not _anchor_home(router,portal,uuid.uuid4().hex):return
            from source_live import play
            play(router,portal,direct=True);return
        sid=str(portal.get('start_stream_id') or '')
        xc=router._xc(portal) if portal.get('type')=='xtream' else None
        streams=xc.get_cached_catalog('get_live_streams') if xc else None
        if not sid or not any(isinstance(s,dict) and str(s.get('stream_id'))==sid for s in (streams or [])):
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
        play(router,portal)


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
    import xbmcgui,xbmcplugin
    from media_art import local_art
    li=xbmcgui.ListItem(item['name'])
    from theme_render import snapshot
    from theme_store import asset
    theme=snapshot();art=local_art(item,theme)
    if widget and theme:
        if art['landscape'].startswith(str(theme['folder'])+'/'):
            art['landscape']=asset('widget.live' if kind=='live' else 'widget.series' if kind=='series' else 'widget.movie',art['landscape'],snapshot=theme)
        art['banner']=asset('widget.header',snapshot=theme)
    li.setArt(art)
    li.setInfo('video',{'title':item['name'],'plot':(epg or {}).get('plot') or item.get('plot') or '',
                        'mediatype':{'vod':'movie','series':'tvshow','live':'video'}[kind]})
    if epg:
        for name,value in epg.items(): li.setProperty('XtreamMate.'+name,str(value))
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
    xbmcplugin.addDirectoryItem(router._handle,url,li,isFolder=False)


def widget(router,portal,action):
    import xbmcplugin
    from library_index import Reader,initial_group
    reader=Reader(portal['id'],timeout=0.05,query_seconds=0.35)
    if action=='widget_live_start_group':
        start=reader.get('live',str(portal.get('start_stream_id') or ''))
        cid=initial_group(portal,reader.groups('live'),start)
        rows,total=reader.page('live',category=cid,offset=page_offset(router),limit=48,
                               pin=start['sid'] if start else None) if cid else ([],0)
        from epg import load_cache
        from epg_sources import configuration
        from epg_views import resolve_guide
        cache=load_cache(portal['id']); mappings=configuration(portal['id'])['mappings']
        xbmcplugin.setContent(router._handle,'videos')
        for row in rows:
            info=resolve_guide(cache,row.get('epg_channel_id',''),row['sid'],
                               client=router._xc(portal),mappings=mappings)
            add_index_item(router,portal,'live',row,dict(Now=info['now'],Next=info['next'],
                Start=info['start'],Stop=info['stop'],Progress=info['progress'] if info['progress'] is not None else '',
                plot=guide_plot(info)),widget=True)
        paging(router,total,page_offset(router),action=action)
        if not rows:
            router._add_dir(tr(32478) if not reader.state('live')
                            else tr(32479),
                            router.url(action='settings_section',pid=portal['id'],section='maintenance'))
    else:
        kind='vod' if action=='widget_recent_vod' else 'series'
        xbmcplugin.setContent(router._handle,'movies' if kind=='vod' else 'tvshows')
        from utils import setting_int
        rows,total=reader.rail(kind,limit=24,keep=setting_int('recent_keep',100))
        for row in rows: add_index_item(router,portal,kind,row,recent=True,widget=True)
        if not rows and not reader.state(kind):
            router._add_dir(tr(32480),
                            router.url(action='movies_home' if kind=='vod' else 'series_home',pid=portal['id']))
        router._add_dir(tr(32481)+(' · '+str(total)+tr(32482) if total else ''),
                        router.url(action='movies_home' if kind=='vod' else 'series_home',pid=portal['id']))
    _end(router)


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
