"""New routes only. Legacy provider/player entry points remain compatible."""

ACTIONS=('xcmate_home','settings_home','settings_section','account_select','home_start','home_live',
         'movies_home','series_home','media_detail','media_favourites','global_search','search_section',
         'widget_live_start_group','widget_recent_vod','widget_recent_series','widget_setup',
         'recording_folder','recording_capabilities','about_xcmate','guide_browser','media_play','guide_timers','guide_status')
LABELS={'live':'LIVE-TV','vod':'FILME','series':'SERIEN'}


def portal_for(router):
    from portals import get_active
    from home_menu import active_portal
    active=get_active();requested=router._params.get('pid','')
    if requested: return next((p for p in active if str(p['id'])==requested),None)
    return active_portal(active)


def _end(router,ok=True):
    import xbmcplugin
    xbmcplugin.endOfDirectory(router._handle,ok,cacheToDisc=False)


def dispatch(router):
    import xbmc,xbmcgui,xbmcaddon
    from home_menu import settings,show,recording_folder
    action=router._params.get('action','xcmate_home')
    portal=portal_for(router)
    if action in ('settings_home','settings_section'):
        settings(router,portal,router._params.get('section','') if action=='settings_section' else '')
        return
    if action=='account_select':
        from portals import get_active
        rows=get_active()
        selected=router._params.get('selected','')
        _end(router,False)
        if not selected:
            i=xbmcgui.Dialog().select('XCMate · Aktiven Account wählen',[p.get('name','Account') for p in rows])
            if i<0 or i>=len(rows): return
            selected=str(rows[i]['id'])
        if selected not in {str(p['id']) for p in rows}: return
        xbmcaddon.Addon().setSetting('active_portal_id',selected)
        xbmc.executebuiltin('Container.Update('+router.url(action='xcmate_home',pid=selected)+')')
        return
    if action=='recording_folder':
        _end(router,False); recording_folder(router._params.get('check')=='1'); return
    if action=='guide_timers':
        _end(router,False)
        if portal:
            from guide_timers import manage
            manage(portal['id'])
        return
    if action=='guide_status':
        _end(router,False)
        if portal:
            from guide_store import status_lines
            xbmcgui.Dialog().textviewer('XCMate · Langzeit-EPG','\n'.join(status_lines(portal)))
        return
    if action in ('about_xcmate','recording_capabilities','widget_setup'):
        _end(router,False)
        if action=='about_xcmate':
            text='XCMate '+xbmcaddon.Addon().getAddonInfo('version')+'\nKodi-ID: plugin.video.xtreammate\nGPL-Fork: mr-evil1 TiViMate Kodi. Herkunft/Lizenzen bleiben erhalten; siehe Projekt-Lizenzdateien.'
        elif action=='recording_capabilities':
            from recording_probe import report
            text=report()
        else:
            text=widget_instructions(router,portal)
        xbmcgui.Dialog().textviewer('XCMate',text)
        return
    if not portal:
        _end(router,False)
        xbmcgui.Dialog().ok('XCMate','Bitte zuerst unter Einstellungen einen Account einrichten.')
        return
    router._params['pid']=portal['id']
    if action=='xcmate_home': show(router,portal)
    elif action=='home_start':
        _end(router,False)
        sid=str(portal.get('start_stream_id') or '')
        xc=router._xc(portal) if portal.get('type')=='xtream' else None
        streams=xc.get_cached_catalog('get_live_streams') if xc else None
        if not sid or not any(isinstance(s,dict) and str(s.get('stream_id'))==sid for s in (streams or [])):
            if xbmcgui.Dialog().yesno('XCMate','Kein gültiger Startkanal im lokalen Katalog. Startkanal & Startgruppe auswählen?'):
                xbmc.executebuiltin('Container.Update('+router.url(action='startup_settings',pid=portal['id'])+')')
            return
        router._play_start_direct()
    elif action=='home_live': router._live_groups()
    elif action in ('global_search','search_section'): search(router,portal)
    elif action.startswith('widget_'): widget(router,portal,action)
    elif action in ('movies_home','series_home','media_detail','media_favourites'):
        kind=router._params.get('kind','series' if action=='series_home' else 'vod')
        if kind not in ('vod','series'):
            _end(router,False);return
        if not portal.get('include_vod' if kind=='vod' else 'include_series',True):
            _end(router,False)
            xbmcgui.Dialog().ok('XCMate','Dieser Medienbereich ist für den Account deaktiviert. Einstellungen → Accounts & Portale.')
            return
        if portal.get('type')!='xtream':
            _end(router,False)
            xbmcgui.Dialog().ok('XCMate','Die neue Medienoberfläche benötigt den lokalen Xtream-Katalog. Die bisherige Medienliste dieses Portaltyps bleibt verfügbar.')
            route=('m3u_movies' if kind=='vod' else 'm3u_series') if portal.get('type')=='m3u' else ('vod_categories' if kind=='vod' else 'series_categories')
            xbmc.executebuiltin('Container.Update('+router.url(action=route,pid=portal['id'])+')')
            return
        _end(router,False)
        from media_window import open_media
        open_media(router,portal,kind,router._params.get('sid',''),favourites=action=='media_favourites')
    elif action=='guide_browser':
        _end(router,False)
        from guide_window import open_guide
        open_guide(router,portal)
    elif action=='media_play':
        from media_progress import play
        play(router,portal)


def search(router,portal):
    import xbmc,xbmcgui,xbmcplugin
    from library_index import Reader
    query=router._params.get('q')
    if query is None:
        _end(router,False)
        query=xbmcgui.Dialog().input('XCMate · Live-TV, Filme und Serien suchen')
        if query.strip():
            xbmc.executebuiltin('Container.Update('+router.url(action='global_search',pid=portal['id'],q=query[:200])+')')
        return
    reader=Reader(portal['id'])
    xbmcplugin.setPluginCategory(router._handle,'XCMate · '+query[:200])
    xbmcplugin.setContent(router._handle,'files')
    kind=router._params.get('kind')
    if kind not in LABELS:
        for section,label in LABELS.items():
            _,total=reader.page(section,query,limit=1)
            status=str(total)+' Treffer' if reader.state(section) else 'Index wird geladen / Katalog nicht verfügbar'
            router._add_dir(label+' · '+status,router.url(action='search_section',pid=portal['id'],kind=section,q=query))
    else:
        offset=page_offset(router)
        rows,total=reader.page(kind,query,offset=offset,limit=48)
        for item in rows: add_index_item(router,portal,kind,item)
        paging(router,total,offset,action='search_section',kind=kind,q=query)
        if not rows:
            router._add_dir('Keine Treffer' if reader.state(kind) else 'Index wird geladen · später erneut öffnen',
                            router.url(action='global_search',pid=portal['id'],q=query))
    _end(router)


def page_offset(router):
    try: return min(1000000,max(0,int(router._params.get('offset','0'))))
    except (TypeError,ValueError): return 0


def paging(router,total,offset,**params):
    for label,target in (('Vorherige Seite',offset-48),('Weitere Ergebnisse',offset+48)):
        if 0<=target<total:
            router._add_dir('{} · {} insgesamt'.format(label,total),router.url(pid=router._params['pid'],offset=target,**params))


def add_index_item(router,portal,kind,item,epg=None,recent=False):
    import xbmcgui,xbmcplugin
    from media_art import local_art
    li=xbmcgui.ListItem(item['name'])
    art=local_art(item)
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
        url=router.url(action='play_live',pid=portal['id'],sid=item['sid'],name=item['name'])
    else:
        url=router.url(action='media_detail',pid=portal['id'],kind=kind,sid=item['sid'])
    xbmcplugin.addDirectoryItem(router._handle,url,li,isFolder=kind!='live')


def widget(router,portal,action):
    import xbmcplugin
    from library_index import Reader,initial_group
    reader=Reader(portal['id'])
    if action=='widget_live_start_group':
        start=reader.get('live',str(portal.get('start_stream_id') or ''))
        cid=initial_group(portal,reader.groups('live'),start)
        rows,total=reader.page('live',category=cid,offset=page_offset(router),limit=48,
                               pin=start['sid'] if start else None) if cid else ([],0)
        from epg import load_cache
        from epg_sources import configuration
        from epg_views import resolve_guide,programme_plot
        cache=load_cache(portal['id']); mappings=configuration(portal['id'])['mappings']
        xbmcplugin.setContent(router._handle,'videos')
        for row in rows:
            info=resolve_guide(cache,row.get('epg_channel_id',''),row['sid'],
                               client=router._xc(portal),mappings=mappings)
            add_index_item(router,portal,'live',row,dict(Now=info['now'],Next=info['next'],
                Start=info['start'],Stop=info['stop'],Progress=info['progress'] if info['progress'] is not None else '',
                plot=programme_plot(info)))
        paging(router,total,page_offset(router),action=action)
        if not rows:
            router._add_dir('Live-TV-Index wird geladen / kein aktiver Sender · Wartung öffnen' if not reader.state('live')
                            else 'Keine Sender in der aktiven Startkanalgruppe · Gruppen prüfen',
                            router.url(action='settings_section',pid=portal['id'],section='maintenance'))
    else:
        kind='vod' if action=='widget_recent_vod' else 'series'
        xbmcplugin.setContent(router._handle,'movies' if kind=='vod' else 'tvshows')
        from utils import setting_int
        rows,total=reader.rail(kind,limit=24,keep=setting_int('recent_keep',100))
        for row in rows: add_index_item(router,portal,kind,row,recent=True)
        if not rows and not reader.state(kind):
            router._add_dir('Katalog noch nicht lokal verfügbar · zum Laden öffnen',
                            router.url(action='movies_home' if kind=='vod' else 'series_home',pid=portal['id']))
        router._add_dir('Alle anzeigen'+(' · '+str(total)+' gespeicherte Titel' if total else ''),
                        router.url(action='movies_home' if kind=='vod' else 'series_home',pid=portal['id']))
    _end(router)


def widget_instructions(router,portal):
    pid=portal['id'] if portal else ''
    lines=['BINGIE MOD · freiwillige Widget-Einrichtung',
           'Skin-Einstellungen → Hauptmenü konfigurieren → gewünschten Menüpunkt → Widgets.',
           'Drei Widget-Reihen in dieser Reihenfolge hinzufügen (Bezeichnungen variieren je Skinversion):']
    for title,action in (('Live-TV','widget_live_start_group'),('Neueste Filme','widget_recent_vod'),('Neueste Serien','widget_recent_series')):
        lines+=['',title,router.url(action=action,pid=pid)]
    lines+=['','Als Quelle Video-Add-ons → XCMate → Einstellungen → Darstellung → Widget-Quellen nutzen.',
            'Live: Logo/Querformat; Filme/Serien: Poster 2:3. Vorhandene Widgets vorher notieren; nur neu angelegte Reihen zum Rückbau entfernen.',
            'Keine Skin-Dateien oder Nutzerkonfiguration werden automatisch verändert. Die tatsächlich installierte BINGIE-MOD-Version ist hier noch nicht am Gerät geprüft.']
    return '\n'.join(lines)
