"""Read-only source status and real programme previews, independent of playback."""
import time
from epg_views import resolve_guide, _as_int


def safe_name(value, fallback='Quelle'):
    value = str(value or '').replace('\n',' ').replace('\r',' ')[:120]
    return fallback if '://' in value or '@' in value else value or fallback


def programme_lines(info):
    lines = ['Zuordnung: {} | EPG-ID: {} | Quelle: {}'.format(
        info.get('mapping',''), safe_name(info.get('epg_id'), 'keine'),
        'Xtream Kurz-EPG' if info.get('source_index') == -1 else
        '[{}]'.format(info['source_index']) if info.get('source_index') else 'Anbieter / Cache')]
    if not info.get('now'):
        lines.append('Für diesen Sender keine aktuellen EPG-Daten verfügbar: '+info.get('reason','NO_DATA'))
    if info.get('now'):
        lines.append('JETZT {}-{}: {}'.format(info['now_time'], info['now_end_time'], info['now']))
        lines.append('{} / {} Min. | Noch {} Min.'.format(int(info['elapsed']//60),
            int((info['stop']-info['start'])//60), max(1,int((info['remaining']+59)//60))))
    if info.get('next'):
        lines.append('DANACH ab {}: {}'.format(info['next_time'],info['next']))
    lines.append('')
    for event in info.get('events', []):
        lines.append('{} - {}  {}'.format(time.strftime('%d.%m. %H:%M',time.localtime(event['start'])),
            time.strftime('%H:%M',time.localtime(event['stop'])),event['title']))
        if event.get('description'): lines.append(event['description'][:1500])
    return lines


def cached_streams(portal, client):
    from group_selection import load
    enabled = load(portal['id']) if portal.get('type') == 'xtream' else None
    streams = (client.get_cached_catalog('get_live_streams') or []) if client else []
    return [s for s in streams if isinstance(s,dict) and
            (enabled is None or str(s.get('category_id','')) in enabled)]


def status_lines(portal, cache, streams, config, state):
    from epg_status import source_key
    lines = ['EPG-Status & Vorschau (lokaler Cache; Öffnen startet keinen Download)', '']
    sources = [('provider', 'Anbieter-XMLTV', True), ('cache', 'Persistenter EPG-Cache', True)]
    sources += [(source_key(s), '[{}] {}'.format(i,safe_name(s.get('name'))),
                 s.get('enabled',True)) for i,s in enumerate(config['sources'],1)]
    for key,name,enabled in sources:
        entry = state.get(key,{})
        code = entry.get('code','WAITING') if enabled else 'DISABLED'
        if entry.get('running') and time.time()-entry.get('at',0)>120:
            code = 'UNTERBROCHEN / Status veraltet'
        lines.append('{}: {}'.format(name,code))
        if entry.get('at'): lines.append('  Stand: '+time.strftime('%d.%m.%Y %H:%M:%S',time.localtime(entry['at'])))
        success = entry.get('last_success')
        lines.append('  Letzter Erfolg: '+(time.strftime('%d.%m.%Y %H:%M:%S',time.localtime(success)) if success else 'noch keiner bestätigt'))
        keys = ('failure_stage','exception_class','failure_code','limit_kind','limit_value',
                'http_status','bytes','channels','programmes','last_channels','last_programmes')
        lines.append('  '+', '.join('{}={}'.format(k,entry[k]) for k in keys if k in entry))
    matched = manual = automatic = 0
    for stream in streams:
        sid, eid = str(stream.get('stream_id','')), str(stream.get('epg_channel_id') or '')
        mapped = config['mappings'].get(sid)
        found = bool(cache.get(mapped)) if mapped else bool(cache.get(sid) or cache.get(eid))
        matched += found
        manual += bool(mapped and found)
        automatic += bool(not mapped and cache.get(sid) and not cache.get(eid))
    valid = set()
    now = time.time()
    for key,events in cache.items():
        if not isinstance(events,list): continue
        for e in events:
            if not isinstance(e,dict): continue
            start,stop = _as_int(e.get('start_timestamp')), _as_int(e.get('stop_timestamp'))
            if stop>max(start,now) and start<now+48*3600:
                valid.add((e.get('channel') or key,start,stop,e.get('name','')))
    lines += ['', 'Cache-IDs (inkl. Senderaliase): {}'.format(len(cache)),
              'Gültige Programme bis +48 Stunden (ohne Aliase): {}'.format(len(valid)),
              'Aktivierte Xtream-Sender: {}'.format(len(streams)),
              'XMLTV-Zuordnung: {}/{} ({:.1f}%)'.format(matched,len(streams),100*matched/max(1,len(streams))),
              'Manuell: {} | automatisch über Namen: {} | Anbieter-ID: {} | ohne XMLTV: {}'.format(
                  manual,automatic,matched-manual-automatic,len(streams)-matched),
              'Kurz-EPG wird senderweise in der Vorschau geprüft; nicht in XMLTV-Quote enthalten.']
    return lines


def show(portal, preview_first=False):
    import xbmcgui
    from epg import load_cache, request_refresh
    from epg_sources import configuration
    from epg_status import read
    client = None
    if portal.get('type') == 'xtream':
        from xtream import XtreamClient
        client = XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    cache, config = load_cache(portal['id']), configuration(portal['id'])
    streams = cached_streams(portal,client)
    dialog = xbmcgui.Dialog()
    if not preview_first:
        dialog.textviewer('XCMate - EPG-Status & Vorschau', '\n'.join(status_lines(
            portal,cache,streams,config,read(portal['id']))))
    while True:
        option = dialog.select('XCMate - Programmvorschau',
            ['Sender suchen', 'Sender auswählen (erste 200)', 'Aktualisierung im Hintergrund anfordern',
             'Lokalen Status / Cache neu einlesen', 'Zurück'])
        if option not in (0,1,2,3): return
        if option == 3:
            from epg import _mem_clear
            _mem_clear(portal['id'])
            cache,config=load_cache(portal['id']),configuration(portal['id'])
            streams=cached_streams(portal,client)
            dialog.textviewer('XCMate - EPG-Status & Vorschau','\n'.join(status_lines(
                portal,cache,streams,config,read(portal['id']))))
            continue
        if option == 2:
            request_refresh(portal['id'],portal,force=True)
            dialog.notification('XCMate EPG','Anforderung gesendet; Import noch nicht bestätigt.')
            continue
        query = dialog.input('Sendername') if option == 0 else ''
        if option == 0 and not query: continue
        choices = [s for s in streams if query.casefold() in str(s.get('name','')).casefold()][:200]
        # Non-Xtream sources can still preview XMLTV channels without a player.
        if not client:
            choices = [dict(name=k,epg_channel_id=k) for k in cache if query.casefold() in k.casefold()][:200]
        if not choices:
            dialog.ok('XCMate EPG','Kein passender Sender im lokalen Katalog. Katalog zuerst laden.')
            continue
        selected = dialog.select('Sender (max. 200; Suche zum Eingrenzen)',
                                 [str(s.get('name','')) for s in choices])
        if 0 <= selected < len(choices):
            s = choices[selected]
            info = resolve_guide(cache,str(s.get('epg_channel_id') or ''),str(s.get('stream_id') or ''),
                                 client=client,mappings=config['mappings'])
            dialog.textviewer('XCMate - '+str(s.get('name','')), '\n'.join(programme_lines(info)))
