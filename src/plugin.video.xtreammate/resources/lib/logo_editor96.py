"""EPG-independent group/station browser and explicit persistent logo editor."""
import hashlib
import time


def groups(portal):
    from library_index import Reader
    return Reader(str(portal['id'])).groups('live')


def stations(portal, category, offset=0):
    from library_index import Reader
    return Reader(str(portal['id'])).page('live', category=str(category), offset=offset, limit=100)


def edit(portal, row):
    import xbmcgui
    from artwork_ui import job, _render
    import logo_overrides96 as overrides
    dialog = xbmcgui.Dialog()
    while True:
        choice = __import__('menu_icons45').select(dialog, row.get('name', 'Sender'),
            ['Provider-Original ansehen', 'Logo ersetzen', 'Original wiederherstellen', 'Zurück', 'Aktives Logo ansehen'])
        if choice < 0 or choice == 3:return
        try:
            if choice in (0, 4):
                value = job(lambda cancel, progress:__import__('logo_manifest86').read(
                    portal, [row], with_overrides=choice == 4, with_agent=choice == 4))
                uri = value.get(str(row['sid']), '') if value else ''
                if uri:_render(uri)
                else:dialog.ok('Senderlogos', 'Kein verifiziertes Provider-Logo verfügbar.')
            elif choice == 1:
                source = __import__('menu_icons45').select(dialog, 'Logo auswählen', ['Lokale PNG/JPEG-Datei', 'SMB PNG/JPEG-Datei'])
                if source not in (0,1):continue
                uri = dialog.browseSingle(1, 'Senderlogo auswählen', 'files', mask='.png|.jpg|.jpeg',
                                          defaultt='smb://' if source == 1 else '')
                if not uri:continue
                # SMB access only follows this explicit choice and exact selection.
                if uri.startswith('smb://') and source != 1:continue
                body = job(lambda cancel, progress:overrides.selection(uri, smb_selected=source == 1))
                if not body:continue
                # Existing bounded RAM server previews bytes without saving a choice.
                tag = 'logo-preview96-' + hashlib.sha256(body).hexdigest()
                preview = job(lambda cancel, progress:__import__('decoded_assets88').put(tag, body, time.time()+300, kind='logo'))
                if preview and _render(preview['uri']) and dialog.yesno('Senderlogo speichern',
                        'Dieses Logo dauerhaft nur für diesen Sender und dieses Konto speichern?'):
                    job(lambda cancel, progress:overrides.save(portal, row, body, confirmed=True))
                    __import__('xbmc').executebuiltin('Container.Refresh')
            elif choice == 2 and dialog.yesno('Original wiederherstellen', 'Nur die Logo-Auswahl dieses Senders zurücksetzen?'):
                job(lambda cancel, progress:overrides.reset(portal, row, confirmed=True))
                __import__('xbmc').executebuiltin('Container.Refresh')
        except (OSError, ValueError, TypeError, TimeoutError, __import__('media_sources43').SourceError):
            dialog.ok('Senderlogos', 'Logo konnte nicht verifiziert oder gespeichert werden.')


def manage():
    import xbmcgui
    from artwork_ui import job
    from portals import get_active
    dialog = xbmcgui.Dialog()
    portals = get_active()
    if not portals:return
    index = __import__('menu_icons45').select(dialog, 'Senderlogos verwalten', [p.get('name','Konto') for p in portals]) if len(portals)>1 else 0
    if not 0 <= index < len(portals):return
    portal = portals[index]
    while True:
        try:values = job(lambda cancel, progress:groups(portal))
        except (OSError, ValueError, RuntimeError, __import__('sqlite3').Error):
            dialog.ok('Senderlogos', 'Lokaler Senderkatalog noch nicht verfügbar.');return
        if not values:return
        index = __import__('menu_icons45').select(dialog, 'Sendergruppe', [g['title'] for g in values])
        if not 0 <= index < len(values):return
        cid = values[index]['cid'];offset = 0
        while True:
            try:page = job(lambda cancel, progress:stations(portal, cid, offset))
            except (OSError, ValueError, RuntimeError, __import__('sqlite3').Error):
                dialog.ok('Senderlogos', 'Lokaler Senderkatalog vorübergehend nicht verfügbar.');break
            if not page:break
            rows, total = page;labels = [r.get('name','Sender') for r in rows]
            more = offset+len(rows)<total;back = offset>0
            if more:labels.append('Nächste Sender')
            if back:labels.append('Vorherige Sender')
            index = __import__('menu_icons45').select(dialog, 'Sender auswählen', labels)
            if index < 0:break
            if index < len(rows):edit(portal, rows[index])
            elif more and index == len(rows):offset += 100
            elif back:offset = max(0, offset-100)
