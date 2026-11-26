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
    from epg_binding48 import commit_verified
    commit_verified(portal,sid,cid,source)
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
        if source == 'agent':
            from epg_events import deduplicate
            from programme_snapshot47 import identify
            origin = self.original['origin']
            start = origin + offset * 3 * 3600
            cid = candidate['id']
            events, detail = cold.agent_windows(self.portal, cid, [
                (origin, origin + 10800, 96), (start, start + 2 * 86400, 96)], cancel)
            sid = self.channel['sid']
            clean = identify(self.portal['id'], sid, cid, deduplicate(events, channel=cid))
            rows = [dict(row, events=clean, epg_id=cid, mapping='PREVIEW_RAM53')
                    if str(row['channel']['sid']) == str(sid) else row for row in self.original['rows']]
            return dict(rows=rows, details53=detail)
        from epg_sources import configuration
        from epg_binding48 import preview
        from guide_grid_data import page
        from local_epg import window
        mappings = preview(configuration(self.portal['id'])['mappings'], self.channel['sid'], candidate['id'], source)
        value = page(self.portal, self.original['offset'], self.original['origin'], self.original['category'], None, mappings48=mappings)
        start = self.original['origin'] + offset * 3 * 3600
        detail = window(self.portal['id'], [self.channel], mappings, start, start + 2 * 86400, limit=96, provider_fallback=False)
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

    def prepare_saved(self, candidate, source):
        from guide_grid_data import page
        from epg_binding48 import MappingSaveError
        value=page(self.portal,self.original['offset'],self.original['origin'],self.original['category'],strict48=True)
        row=next((r for r in value['rows'] if str(r['channel']['sid'])==str(self.channel['sid'])),None)
        if value.get('code')!='OK' or row is None or row['mapping']!='MANUAL' or row['epg_id']!=candidate['id']:
            raise MappingSaveError('MAPPING_RELOAD_FAILED')
        return value

    def apply_saved(self, value):
        parent=self.parent
        if parent._closed:raise RuntimeError('MAPPING_PARENT_CLOSED')
        parent.rows=value['rows'];parent.total=value['total'];parent.groups=value['groups']
        parent.row=min(self.original['row'],max(0,len(parent.rows)-1))
        parent._loading=False;parent._render();parent.setFocusId(self.focus)
        self._applied474=True

    def finish(self, saved):
        if saved and getattr(self,'_applied474',False):return
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
        start = self.origin + offset * 3 * 3600
        if source == 'agent':
            events, details = cold.agent_windows(self.portal, candidate['id'], [
                (self.origin, self.origin + 2 * 86400, 96), (start, start + 2 * 86400, 96)], cancel)
        else:
            mappings = preview(configuration(self.portal['id'])['mappings'], self.channel['sid'], candidate['id'], source)
            # Always include NOW in the Mini column; the dialog can page details.
            detail = window(self.portal['id'], [self.channel], mappings, self.origin, start + 2 * 86400, limit=256, provider_fallback=False)
            events = list((detail or {}).get(candidate['id'], []))
            if not events:
                events = cold.programmes(self.portal, source, candidate['id'], cancel)
            events = [dict(e, source_key46=source) for e in events if (e.get('source_key46') or e.get('epg_source46') or source) == source]
            details = [e for e in events if e['start_timestamp'] < start + 2 * 86400 and e['stop_timestamp'] > start][:96]
        clean = identify(self.portal['id'], self.channel['sid'], candidate['id'], deduplicate(events, channel=candidate['id']))
        info = guide_for_channel({candidate['id']: events}, candidate['id'], now=self.origin)
        info.update(epg_id=candidate['id'], canonical46=candidate['id'], mapping='PREVIEW_RAM96', loading68=False,
                    programme_events=clean, preview_epoch96=self.epoch)
        info = bind(self.portal['id'], self.channel, info)
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

    def prepare_saved(self, candidate, source):
        from epg_sources import configuration
        from local_epg import window
        from epg_views import resolve_guide
        from epg_status import revision
        from epg_binding48 import MappingSaveError
        from programme_snapshot47 import bind
        now=time.time();mappings=configuration(self.portal['id'])['mappings']
        view=window(self.portal['id'],[self.channel],mappings,now,now+2*86400,strict48=True)
        if view is None:raise MappingSaveError('MAPPING_RELOAD_FAILED')
        info=resolve_guide(view,candidate['id'],self.channel['sid'],now,mappings=mappings)
        if info['mapping']!='MANUAL' or info['epg_id']!=candidate['id']:raise MappingSaveError('MAPPING_RELOAD_FAILED')
        info.update(canonical46=candidate['id'],loading68=False,snapshot_revision=getattr(view,'revision',None))
        return dict(info=bind(self.portal['id'],self.channel,info),mappings=mappings,revision=revision(self.portal['id']))

    def apply_saved(self,value):
        parent=self.parent;guide=parent._guide;sid=str(self.channel['sid'])
        if parent._closed:raise RuntimeError('MAPPING_PARENT_CLOSED')
        with guide._lock:
            self._prior474=guide._values.get(sid)
            guide._preview96.pop(sid,None);guide._seeded63.pop(sid,None)
            guide._values[sid]=value['info'];guide._mappings=value['mappings'];guide._revision=value['revision']
            guide._request_generation+=1;guide.generation+=1;guide._wake.set()
        for key,old in self.original.items():setattr(parent,key,dict(old) if key=='_highlight' else old)
        parent._mini.signature=None;parent._render(focus=False);parent.setFocusId(self.focus)
        self._applied474=True

    def restore_saved(self):
        guide=self.parent._guide;sid=str(self.channel['sid'])
        with guide._lock:
            if hasattr(self,'_prior474'):
                if self._prior474 is None:guide._values.pop(sid,None)
                else:guide._values[sid]=self._prior474
            guide._revision=None;guide._request_generation+=1;guide._wake.set()
        try:self.finish(False)
        finally:self.epoch=guide.begin_preview96(sid)

    def finish(self, saved):
        if saved and getattr(self,'_applied474',False):return
        parent = self.parent
        parent._guide.clear_preview96(self.channel['sid'], self.epoch, refresh=saved)
        if parent._closed:
            return
        for key, value in self.original.items():
            setattr(parent, key, dict(value) if key == '_highlight' else value)
        parent._mini.signature = None
        parent._render(focus=False)
        parent.setFocusId(self.focus)
