# -*- coding: utf-8 -*-
"""Noodle Private, independent Kodi 19+ video add-on (personal-use test build)."""
import concurrent.futures
import hashlib
import ipaddress
import os
import re
import sys
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources.lib.site import ROOT, UA, SiteError, fetch_html, listing_path, parse_detail, parse_listing, watch_url
from resources.lib.storage import Storage

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE = sys.argv[0]
ARGS = {key: values[-1] for key, values in urllib.parse.parse_qs(sys.argv[2].lstrip('?')).items()}
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
STORE = Storage(PROFILE)
ICON = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'icon.png')
FANART = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'fanart.png')


def build_url(action='', **params):
    values = {'action': action}
    values.update({k: v for k, v in params.items() if v is not None})
    return BASE + '?' + urllib.parse.urlencode(values, doseq=False)


def inform(message, heading='Noodle Private'):
    xbmcgui.Dialog().notification(heading, str(message)[:260], ICON, 5000)


def fail(error):
    xbmc.log('[Noodle Private] {}'.format(error), xbmc.LOGWARNING)
    inform(str(error))


def folder(label, action, icon=None, context=None, **params):
    item = xbmcgui.ListItem(label=label)
    item.setArt({'thumb': icon or ICON, 'icon': icon or ICON, 'fanart': FANART})
    if context:
        item.addContextMenuItems(context)
    xbmcplugin.addDirectoryItem(HANDLE, build_url(action, **params), item, isFolder=True)


def end(folder_type='videos', cache=False):
    xbmcplugin.setContent(HANDLE, folder_type)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=cache)


def confirm_adult():
    if STORE.prefs().get('confirmed_adult'):
        return True
    if xbmcgui.Dialog().yesno('Inhalte ab 18 Jahren',
             'Dieses Add-on zeigt externe Inhalte nur für Erwachsene. Bist du mindestens 18 Jahre alt und möchtest du die Anzeige aktivieren?'):
        STORE.update_prefs(confirmed_adult=True)
        return True
    return False


def _read_page(url, refresh=False):
    ttl = max(0, min(60, int(STORE.prefs().get('page_cache_minutes', 5)))) * 60
    if not refresh:
        cached = STORE.get_page(url, ttl)
        if cached is not None:
            return cached
    html = fetch_html(url)
    STORE.put_page(url, html)
    return html


def _thumb_file(item):
    """Optional local image cache to help skins that cannot load hotlinked artwork."""
    url = item.get('image', '')
    if not url:
        return ''
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        return ''
    try:
        ipaddress.ip_address(parsed.hostname)
        return ''
    except ValueError:
        pass
    folder_name = os.path.join(PROFILE, 'images')
    output = os.path.join(folder_name, hashlib.sha256(url.encode('utf-8')).hexdigest() + '.jpg')
    if os.path.isfile(output) and os.path.getsize(output) > 64:
        return output
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': ROOT + '/'})
        with urllib.request.urlopen(req, timeout=3) as response:
            if not response.headers.get('Content-Type', '').lower().startswith('image/'):
                return ''
            content = response.read(1_200_001)
            if len(content) > 1_200_000 or len(content) < 64:
                return ''
        os.makedirs(folder_name, exist_ok=True)
        with open(output, 'wb') as f:
            f.write(content)
        return output
    except (OSError, ValueError):
        return ''


def images_for(items):
    prefs = STORE.prefs()
    if not prefs.get('image_cache'):
        return items
    limit = max(1, min(int(prefs.get('max_images', 12)), 24))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        images = list(pool.map(_thumb_file, items[:limit]))
    for item, image in zip(items[:limit], images):
        if image:
            item['image'] = image
    return items


def video(item, collection_id=None):
    url = item.get('url', '')
    if not url:
        return
    label = item.get('title') or 'Video'
    li = xbmcgui.ListItem(label=label, path=build_url('play', url=url, title=label, image=item.get('image', ''), duration=item.get('duration', 0)))
    artwork = item.get('image') or ICON
    li.setArt({'thumb': artwork, 'poster': artwork, 'icon': artwork, 'fanart': artwork if item.get('image') else FANART, 'landscape': artwork})
    li.setInfo('video', {'title': label, 'plot': label,
                         'duration': int(item.get('duration') or 0), 'mediatype': 'video'})
    li.setProperty('IsPlayable', 'true')
    context_params = dict(url=url, title=label, image=item.get('image', ''),
                          duration=item.get('duration', 0))
    ctx = [
        ('Zu Favoritenliste hinzufügen ...', 'RunPlugin({})'.format(
            build_url('collection_add', **context_params))),
    ]
    if collection_id:
        ctx.append(('Aus dieser Liste entfernen', 'RunPlugin({})'.format(
            build_url('collection_remove', collection_id=collection_id, url=url))))
    ctx.append(('Ähnliche Videos', 'Container.Update({})'.format(build_url('related', url=url))))
    li.addContextMenuItems(ctx)
    xbmcplugin.addDirectoryItem(HANDLE, li.getPath(), li, isFolder=False)


def root():
    if not confirm_adult():
        folder('Zugang für Erwachsene bestätigen', 'unlock')
        end('files')
        return
    choices = [
        ('Beliebt', 'popular'), ('Neu hinzugefügt', 'recent'), ('Trending', 'trending'),
        ('Gerade angesehen', 'now'), ('Nur HD', 'hd'), ('Kurzvideos', 'short'), ('Lange Videos', 'long')
    ]
    folder('Suche', 'search_prompt')
    for label, key in choices:
        folder(label, 'list', section=key)
    folder('Meine Favoritenlisten', 'favorites')
    folder('Zuletzt gestartet', 'recently_played')
    folder('Letzte Suchen', 'past_searches')
    folder('Filter & Qualität', 'settings')
    folder('Widget-Hilfe / BINGIE MOD', 'help')
    end('files')


def listing(section, query='', page=0, refresh=False):
    prefs = STORE.prefs()
    url = listing_path(section, query, page, hd='1' if section == 'hd' else '0',
                       sort=prefs.get('sort', '0'), duration=prefs.get('duration_filter', 'any'))
    try:
        markup = _read_page(url, refresh)
        items, next_page = parse_listing(markup)
        if section == 'search':
            folder('Neue Suche starten', 'search_prompt')
        if not items:
            folder('Keine Treffer – ggf. Zugriffsbeschränkung oder Seitenänderung', 'help')
        for item in images_for(items):
            video(item)
        if next_page is not None and int(next_page) > int(page):
            folder('Weitere Ergebnisse (Seite {})'.format(int(next_page) + 1),
                   'list', section=section, query=query, page=next_page)
    except (SiteError, ValueError, OSError) as error:
        fail(error)
        folder('Seite nicht verfügbar – Infos öffnen', 'help')
    end(cache=False)


def collections_page():
    folder('Neue Favoritenliste erstellen', 'collection_create')
    collections = STORE.collections()
    for ident, entry in collections.items():
        label = '{} ({} Videos)'.format(entry.get('name', 'Favoriten'), len(entry.get('items', {})))
        context = [
            ('Liste umbenennen', 'RunPlugin({})'.format(
                build_url('collection_rename', collection_id=ident))),
            ('Liste löschen', 'RunPlugin({})'.format(
                build_url('collection_delete', collection_id=ident))),
        ]
        folder(label, 'collection_view', collection_id=ident, context=context)
    if not collections:
        folder('Noch keine Listen vorhanden – erstelle eine neue', 'collection_create')
    end('files')


def collection_view(ident):
    try:
        entry = STORE.get_collection(ident)
        for item in reversed(list(entry.get('items', {}).values())):
            video(item, collection_id=ident)
        if not entry.get('items'):
            folder('Diese Liste ist leer – über das Video-Kontextmenü befüllen', 'help')
    except ValueError as error:
        fail(error)
    end()


def saved_list(kind):
    if kind == 'favorites':
        return collections_page()
    items = STORE.state().get('recent', [])
    for item in items:
        video(item)
    if not items:
        folder('Noch keine gespeicherten Videos', 'help')
    end()


def prompt_search():
    """Return the search result as *this* directory. Avoid racing Container.Update
    against endOfDirectory: Titan BINGIE MOD sometimes showed an empty page.
    """
    query = xbmcgui.Dialog().input('NoodleMagazine durchsuchen', type=xbmcgui.INPUT_ALPHANUM)
    if query and query.strip():
        query = query.strip()
        STORE.remember_search(query)
        listing('search', query=query, refresh=True)
    else:
        folder('Neue Suche starten', 'search_prompt')
        folder('Bisherige Suchbegriffe', 'past_searches')
        end('files')


def saved_searches():
    folder('Neue Suche starten', 'search_prompt')
    for query in STORE.state().get('searches', []):
        folder(query, 'list', section='search', query=query)
    end('files')


def _video_args(args):
    url = watch_url(args.get('url', ''))
    return {'url': url, 'title': args.get('title', 'Video'),
            'image': args.get('image', ''), 'duration': int(args.get('duration') or 0)}


def fav_toggle(args):
    # Backwards-compatible route in case a v0.1 context action is still cached.
    try:
        added = STORE.toggle_favorite(_video_args(args))
        inform('Favorit gespeichert' if added else 'Favorit entfernt')
        xbmc.executebuiltin('Container.Refresh')
    except (SiteError, ValueError) as error:
        fail(error)


def collection_create(return_page=True):
    name = xbmcgui.Dialog().input('Name der neuen Favoritenliste', type=xbmcgui.INPUT_ALPHANUM)
    if name and name.strip():
        try:
            STORE.create_collection(name)
            inform('Favoritenliste erstellt: {}'.format(' '.join(name.split())))
        except ValueError as error:
            fail(error)
    if return_page:
        collections_page()


def collection_add(args):
    """Used from video context menu. Choose a named list or create one."""
    try:
        item = _video_args(args)
        collections = list(STORE.collections().items())
        labels = ['+ Neue Favoritenliste erstellen'] + [
            ('✓ ' if item['url'] in data.get('items', {}) else '') + data['name']
            for _ident, data in collections
        ]
        choice = xbmcgui.Dialog().select('Video in welche Liste aufnehmen?', labels)
        if choice < 0:
            return
        if choice == 0:
            name = xbmcgui.Dialog().input('Name der neuen Favoritenliste', type=xbmcgui.INPUT_ALPHANUM)
            if not name or not name.strip():
                return
            ident = STORE.create_collection(name)
        else:
            ident = collections[choice-1][0]
        added = STORE.add_to_collection(ident, item)
        name = STORE.get_collection(ident)['name']
        inform('In „{}“ gespeichert'.format(name) if added else 'Bereits in „{}“ vorhanden'.format(name))
        xbmc.executebuiltin('Container.Refresh')
    except (SiteError, ValueError) as error:
        fail(error)


def collection_remove(args):
    try:
        url = watch_url(args.get('url', ''))
        ident = args.get('collection_id', '')
        if STORE.remove_from_collection(ident, url):
            inform('Video aus Liste entfernt')
            xbmc.executebuiltin('Container.Refresh')
    except (ValueError, SiteError) as error:
        fail(error)


def collection_rename(args):
    try:
        ident = args.get('collection_id', '')
        current = STORE.get_collection(ident)['name']
        name = xbmcgui.Dialog().input('Favoritenliste umbenennen', defaultt=current,
                                       type=xbmcgui.INPUT_ALPHANUM)
        if name and name.strip() and name.strip() != current:
            name = STORE.rename_collection(ident, name)
            inform('Liste heißt jetzt „{}“'.format(name))
            xbmc.executebuiltin('Container.Refresh')
    except ValueError as error:
        fail(error)


def collection_delete(args):
    try:
        ident = args.get('collection_id', '')
        entry = STORE.get_collection(ident)
        count = len(entry.get('items', {}))
        if xbmcgui.Dialog().yesno('Favoritenliste löschen?',
                                  '„{}“ mit {} Einträgen löschen? Die Videos selbst bleiben online.'.format(entry['name'], count)):
            STORE.delete_collection(ident)
            inform('Liste gelöscht')
            xbmc.executebuiltin('Container.Refresh')
    except ValueError as error:
        fail(error)


def _pick_source(sources):
    prefs = STORE.prefs()
    preference = prefs.get('preferred_quality', 'best')
    if preference == 'ask' and len(sources) > 1:
        index = xbmcgui.Dialog().select('Wiedergabequalität', [s['label'] or ('HLS' if s['hls'] else 'Video') for s in sources])
        return sources[index] if index >= 0 else None
    if preference != 'best':
        limit = int(preference)
        for s in sources:
            match = re.search(r'\d+', s['label'])
            if match and int(match.group(0)) <= limit:
                return s
    return sources[0]


def play(args):
    try:
        url = watch_url(args.get('url', ''))
        doc = fetch_html(url)
        data = parse_detail(doc)
        chosen = _pick_source(data['sources'])
        if not chosen:
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
            return
        title = args.get('title') or data['title']
        img = args.get('image') or data['image'] or ICON
        source = chosen['url']
        ref_headers = {'User-Agent': UA, 'Referer': ROOT + '/'}
        if chosen['hls'] and xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)'):
            li = xbmcgui.ListItem(label=title, path=source)
            li.setMimeType('application/vnd.apple.mpegurl')
            li.setContentLookup(False)
            li.setProperty('inputstream', 'inputstream.adaptive')
            encoded = urllib.parse.urlencode(ref_headers)
            li.setProperty('inputstream.adaptive.manifest_headers', encoded)
            li.setProperty('inputstream.adaptive.stream_headers', encoded)
            li.setProperty('inputstream.adaptive.common_headers', encoded)
        else:
            # Kodi's direct HTTP player accepts appended request headers for MP4.
            # The native HLS fallback is less reliable than InputStream Adaptive.
            li = xbmcgui.ListItem(label=title, path=source + '|' + urllib.parse.urlencode(ref_headers))
        li.setArt({'thumb': img, 'icon': img, 'fanart': img})
        li.setInfo('video', {'title': title, 'plot': data.get('description') or title,
                             'duration': int(args.get('duration') or 0), 'mediatype':'video'})
        STORE.remember_play({'url': url, 'title': title, 'image': img,
                             'duration': int(args.get('duration') or 0)})
        xbmcplugin.setResolvedUrl(HANDLE, True, li)
    except (SiteError, ValueError, OSError) as error:
        fail(error)
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())


def related(url):
    try:
        doc = _read_page(watch_url(url))
        items, _page = parse_listing(doc)
        for item in images_for(items):
            video(item)
    except SiteError as error:
        fail(error)
    end()


def settings():
    labels = ['Wiedergabequalität', 'Sortierung', 'Laufzeitfilter',
              'Bildvorschauen lokal zwischenspeichern', 'Seiten-Cache leeren']
    sel = xbmcgui.Dialog().select('Noodle Private – Einstellungen', labels)
    prefs = STORE.prefs()
    if sel == 0:
        opts = [('Höchste verfügbare', 'best'), ('Bis 1080p', '1080'), ('Bis 720p', '720'),
                ('Bis 480p', '480'), ('Immer nachfragen', 'ask')]
        v = xbmcgui.Dialog().select('Wiedergabequalität', [x[0] for x in opts])
        if v >= 0:
            STORE.update_prefs(preferred_quality=opts[v][1])
    elif sel == 1:
        opts = [('Hinzugefügt', '0'), ('Laufzeit', '1'), ('Relevanz', '2')]
        v = xbmcgui.Dialog().select('Sortierung', [x[0] for x in opts])
        if v >= 0:
            STORE.update_prefs(sort=opts[v][1])
    elif sel == 2:
        opts = [('Beliebig', 'any'), ('Kurz', 'short'), ('Lang', 'long')]
        v = xbmcgui.Dialog().select('Laufzeitfilter', [x[0] for x in opts])
        if v >= 0:
            STORE.update_prefs(duration_filter=opts[v][1])
    elif sel == 3:
        new_value = not bool(prefs.get('image_cache'))
        STORE.update_prefs(image_cache=new_value)
        inform('Lokaler Bildcache: ' + ('An' if new_value else 'Aus'))
    elif sel == 4:
        STORE.clear_cache()
        inform('Seiten-Cache geleert')


def help_page():
    lines = [
        'Kodi-Widgets / Titan BINGIE MOD:',
        '',
        'Beliebt: plugin://plugin.video.noodleprivate/?action=list&section=popular',
        'Neu: plugin://plugin.video.noodleprivate/?action=list&section=recent',
        'Trending: plugin://plugin.video.noodleprivate/?action=list&section=trending',
        'HD: plugin://plugin.video.noodleprivate/?action=list&section=hd',
        'Favoritenlisten: plugin://plugin.video.noodleprivate/?action=favorites',
        'Einzelne Liste: plugin://plugin.video.noodleprivate/?action=collection_view&collection_id=default',
        '',
        'In BINGIE MOD unter Startmenü/Widgets eine Add-on-Liste wählen.',
        'Video lange drücken / rechte Maustaste: Zu Favoritenliste hinzufügen.',
        'Liste lange drücken: Umbenennen / Löschen.',
        'TMDb Helper ist nicht notwendig.',
        'Für HLS wird InputStream Adaptive empfohlen.',
        'Bei HTTP 403 lässt sich der Zugriff nicht durch das Add-on erzwingen.'
    ]
    xbmcgui.Dialog().textviewer('Noodle Private – Hilfe', '\n'.join(lines))
    end('files')


def run():
    action = ARGS.get('action', '')
    if action == 'unlock':
        if confirm_adult():
            xbmc.executebuiltin('Container.Update({})'.format(BASE))
        end('files')
        return
    if action not in ('root', '') and not STORE.prefs().get('confirmed_adult'):
        folder('Inhalte erst im Add-on freischalten', 'unlock')
        end('files')
        return
    if action in ('', 'root'):
        root()
    elif action == 'list':
        listing(ARGS.get('section', 'popular'), ARGS.get('query', ''),
                int(ARGS.get('page', '0')), ARGS.get('refresh') == '1')
    elif action == 'search_prompt':
        prompt_search()
    elif action == 'favorites':
        saved_list('favorites')
    elif action == 'collection_view':
        collection_view(ARGS.get('collection_id', ''))
    elif action == 'collection_create':
        collection_create()
    elif action == 'collection_add':
        collection_add(ARGS)
    elif action == 'collection_remove':
        collection_remove(ARGS)
    elif action == 'collection_rename':
        collection_rename(ARGS)
    elif action == 'collection_delete':
        collection_delete(ARGS)
    elif action == 'recently_played':
        saved_list('recent')
    elif action == 'past_searches':
        saved_searches()
    elif action == 'favorite':
        fav_toggle(ARGS)
    elif action == 'play':
        play(ARGS)
    elif action == 'related':
        related(ARGS.get('url', ''))
    elif action == 'settings':
        settings()
        end('files')
    elif action == 'help':
        help_page()
    else:
        root()


if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        fail('Unerwarteter Fehler: {}'.format(exc))
        xbmc.log('[Noodle Private] exception: {}'.format(repr(exc)), xbmc.LOGERROR)
        if ARGS.get('action') != 'play':
            end('files')
        else:
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
