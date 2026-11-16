"""View adapters for the shared source/channel mapping dialog.

The controller owns search, detail text and explicit Save. Adapters read an
actual grid or Mini viewport and apply only a reversible in-memory preview.
Neither adapter owns or changes the player.
"""
import time


def mini_channel(parent):
    """Resolve only a real native sender row, excluding page links/programmes."""
    if getattr(parent, '_closed', False) or getattr(parent, '_leaving', False):
        return None
    if getattr(parent, 'mode', '') != 'channels' or getattr(getattr(parent, '_mini', None), 'focused', False):
        return None
    try:
        control = parent.control
        if parent.getFocusId() != control.getId():
            return None
        position = parent._page_start + control.getSelectedPosition() - parent._row_offset
        if not parent._page_start <= position < min(parent._page_start + 100, len(parent.visible_channels)):
            return None
        channel = parent.visible_channels[position]
        sid = str(channel.extra.get('stream_id') or '').strip()
        return channel if sid and sid != '0' else None
    except (AttributeError, IndexError, RuntimeError, TypeError, ValueError):
        return None


def save_verified(portal, sid, cid, source):
    """Only report success after a fresh configuration read proves the tuple."""
    from epg_binding48 import save, binding
    from epg_sources import configuration
    if not save(portal, sid, cid, source):
        return False
    selected = binding(configuration(portal['id'])['mappings'], sid)
    if selected != dict(channel=str(cid), source=str(source)):
        raise ValueError('MAPPING_READBACK_FAILED')
    return True


class GridAdapter:
    preview_label = 'Vorschau im Raster'

    def __init__(self, parent):
        self.parent = parent
        self.portal = parent.portal
        self.channel = dict(parent.rows[parent.row]['channel'])
        self.original = {k: getattr(parent, k) for k in ('rows', 'total', 'groups', 'row', 'offset', 'cursor', 'origin', 'category', '_focus_zone', '_header')}
        self.focus = parent.getFocusId()

    def load_preview(self, candidate, source, offset, cold, cancel):
        from epg_sources import configuration
        from epg_binding48 import preview
        from guide_grid_data import page
        from local_epg import window
        mappings = preview(configuration(self.portal['id'])['mappings'], self.channel['sid'], candidate['id'], source)
        value = page(self.portal, self.original['offset'], self.original['origin'], self.original['category'], None, mappings48=mappings)
        start = self.original['origin'] + offset * 3 * 3600
        detail = window(self.portal['id'], [self.channel], mappings, start, start + 2 * 86400, limit=96)
        value['details53'] = list((detail or {}).get(candidate['id'], []))
        selected = next((r for r in value['rows'] if str(r['channel']['sid']) == str(self.channel['sid'])), None)
        if selected is not None and not selected['events'] and not value['details53']:
            events = cold.programmes(self.portal, source, candidate['id'], cancel)
            from epg_events import deduplicate
            from programme_snapshot47 import identify
            selected['events'] = identify(self.portal['id'], self.channel['sid'], candidate['id'], deduplicate([e for e in events if e['start_timestamp'] < self.original['origin'] + 10800 and e['stop_timestamp'] > self.original['origin']], channel=candidate['id']))
            selected['epg_id'] = candidate['id']; selected['mapping'] = 'PREVIEW_RAM53'
            value['details53'] = [e for e in events if e['start_timestamp'] < start + 2 * 86400 and e['stop_timestamp'] > start][:96]
        return value

    def apply_preview(self, value, source, candidate):
        parent = self.parent
        if parent._closed:
            return None
        selected = next((row for row in value['rows'] if str(row['channel']['sid']) == str(self.channel['sid'])), None)
        if selected is None:
            return None
        parent.rows = [selected if str(row['channel']['sid']) == str(self.channel['sid']) else row for row in self.original['rows']]
        zone = parent._focus_zone; parent._focus_zone = 'preview48'; parent._preview53 = True
        try:
            parent._render()
        finally:
            parent._focus_zone = zone; parent._preview53 = False
        parent.getControl(102).setLabel('VORSCHAU · ' + source['name'] + ' · ' + candidate['id'] + ' · noch nicht gespeichert')
        return len(selected['events'])

    def finish(self, saved):
        if self.parent._closed:
            return
        if saved:
            self.parent._load(background=True)
        else:
            for key, value in self.original.items():
                setattr(self.parent, key, value)
            self.parent._render(); self.parent.setFocusId(self.focus)


class MiniAdapter:
    preview_label = 'Vorschau im Mini-EPG'

    def __init__(self, parent, channel):
        from programme_window46 import channel_row
        self.parent = parent; self.portal = parent.portal
        self.channel = channel_row(channel)
        self.focus = parent.getFocusId()
        # Capture only navigation fields the Mini parent actually owns.
        self.original = {key: getattr(parent, key) for key in ('mode', 'category_id', '_page_start', '_row_offset', '_scroll_to_current') if hasattr(parent, key)}
        self.original['_highlight'] = dict(parent._highlight)
        self.position = parent._page_start + parent.control.getSelectedPosition() - parent._row_offset
        self.epoch = parent._guide.begin_preview96(self.channel['sid'])
        self.origin = time.time()

    def load_preview(self, candidate, source, offset, cold, cancel):
        from epg_binding48 import preview
        from epg_sources import configuration
        from local_epg import window
        from epg_views import guide_for_channel
        from epg_events import deduplicate
        from programme_snapshot47 import bind, identify
        mappings = preview(configuration(self.portal['id'])['mappings'], self.channel['sid'], candidate['id'], source)
        start = self.origin + offset * 3 * 3600
        # Always include NOW in the Mini column; the dialog can page details.
        detail = window(self.portal['id'], [self.channel], mappings, self.origin, start + 2 * 86400, limit=256)
        events = list((detail or {}).get(candidate['id'], []))
        if not events:
            events = cold.programmes(self.portal, source, candidate['id'], cancel)
        events = [dict(e, source_key46=source) for e in events if (e.get('source_key46') or e.get('epg_source46') or source) == source]
        clean = identify(self.portal['id'], self.channel['sid'], candidate['id'], deduplicate(events, channel=candidate['id']))
        info = guide_for_channel({candidate['id']: events}, candidate['id'], now=self.origin)
        info.update(epg_id=candidate['id'], canonical46=candidate['id'], mapping='PREVIEW_RAM96', loading68=False,
                    programme_events=clean, preview_epoch96=self.epoch)
        info = bind(self.portal['id'], self.channel, info)
        details = [e for e in events if e['start_timestamp'] < start + 2 * 86400 and e['stop_timestamp'] > start][:96]
        return dict(info96=info, details53=details)

    def apply_preview(self, value, source, candidate):
        parent = self.parent
        if parent._closed or not parent._guide.set_preview96(self.channel['sid'], self.epoch, value['info96']):
            return None
        parent._highlight['channels'] = self.position
        if hasattr(parent, '_scroll_to_current'):parent._scroll_to_current = False
        parent._mini.signature = None
        parent._render(focus=False)
        return len(value['info96']['events'])

    def finish(self, saved):
        parent = self.parent
        parent._guide.clear_preview96(self.channel['sid'], self.epoch, refresh=saved)
        if parent._closed:
            return
        for key, value in self.original.items():
            setattr(parent, key, dict(value) if key == '_highlight' else value)
        parent._mini.signature = None
        parent._render(focus=False)
        parent.setFocusId(self.focus)
