"""Explicit, bounded cold-source preview in RAM; persistence only after Save.

The ordinary guide remains strictly local. Only the mapping worker can read a
configured feed on demand. Whole XML/gzip validation is required before use.
No URL, exception value, programme or credential is logged.
"""
import gzip
import json
import uuid


class PreviewUnavailable(ValueError):
    pass


def source(portal,identity):
    from epg_sources import configuration
    from guide_publish44 import source_id
    if identity=='provider':
        if not portal.get('provider_epg_enabled',True):raise PreviewUnavailable('SOURCE_DISABLED')
        from source_adapters import for_portal
        uri=portal.get('epg_url') or for_portal(portal).get_xmltv_epg_url() or ''
        if not uri:raise PreviewUnavailable('SOURCE_MISSING')
        return dict(uri=uri,local=not uri.startswith(('https://','http://'))),0
    for rank,item in enumerate(configuration(portal['id'])['sources'],1):
        if source_id(item,rank)==identity and item.get('enabled',True):return item,rank
    raise PreviewUnavailable('SOURCE_MISSING')


class Limited:
    def __init__(self,stream,budget,cancel):self.stream=stream;self.left=budget;self.cancel=cancel
    def read(self,size=-1):
        if self.cancel():raise InterruptedError('PREVIEW_CANCELLED')
        if size==0:return b''
        value=self.stream.read(min(max(1,size),32768,self.left+1) if size>=0 else min(32768,self.left+1))
        self.left-=len(value)
        if self.left<0:raise PreviewUnavailable('PREVIEW_BYTE_BUDGET')
        return value


def scan(portal,identity,cid=None,cancel=lambda:False):
    from stream_epg import source_stream
    from xmltv_stream import parse,PrefixReader
    from programme_index46 import bounds
    selected,rank=source(portal,identity);left,right=bounds()
    names={};events=[];used=0
    def channel(ident,name):
        nonlocal used
        if cid is not None:return
        used+=len(ident.encode())+len(name.encode())+128
        if len(names)>=20000 or used>4*1024*1024:raise PreviewUnavailable('PREVIEW_CHANNEL_BUDGET')
        names[ident]=name
    def programme(event):
        nonlocal used
        if cid is None or event['channel']!=cid or event['stop_timestamp']<=left or event['start_timestamp']>=right:return
        event=dict(event,source_key46=identity,_source_index=rank,source=rank)
        used+=len(json.dumps(event,ensure_ascii=False).encode())+256
        if len(events)>=512 or used>4*1024*1024:raise PreviewUnavailable('PREVIEW_EVENT_BUDGET')
        events.append(event)
    with source_stream(selected,cancel=cancel) as stream:
        packed=PrefixReader(Limited(stream,64*1024*1024,cancel))
        decoded=gzip.GzipFile(fileobj=packed) if packed.prefix==b'\x1f\x8b' else packed
        try:parse(Limited(decoded,256*1024*1024,cancel),channel,programme,cancel,max_seconds=45)
        finally:
            if isinstance(decoded,gzip.GzipFile):decoded.close()
    if cancel():raise InterruptedError('PREVIEW_CANCELLED')
    return sorted(events,key=lambda e:(e['start_timestamp'],e['stop_timestamp'])) if cid is not None else [dict(id=k,name=v) for k,v in sorted(names.items())]


class Candidates:
    """At most one catalogue and one channel, scoped to the open dialog."""
    def __init__(self):self.catalogue=None;self.events=None
    def channels(self,portal,identity,query,offset,cancel):
        if self.catalogue is None or self.catalogue[0]!=identity:
            self.catalogue=(identity,scan(portal,identity,cancel=cancel))
        q=query.casefold()
        rows=[r for r in self.catalogue[1] if q in r['id'].casefold() or q in r['name'].casefold()]
        return rows[offset:offset+100]
    def programmes(self,portal,identity,cid,cancel):
        if self.events is None or self.events[:2]!=(identity,cid):
            self.events=(identity,cid,scan(portal,identity,cid,cancel))
        return self.events[2]
    def selected(self,identity,cid):
        return self.events[2] if self.events is not None and self.events[:2]==(identity,cid) else []


def publish(portal,identity,cid,name,events):
    """Save-only additive publication in the existing shared fact store.

    No automatic aliases or global priorities change. Re-read every exact fact
    before allowing the mapping write; a failed cache write is never success.
    """
    if not events:return
    from programme_store46 import Stage
    from programme_index46 import window
    _,rank=source(portal,identity)
    stage=Stage(portal['id'],'mapping53-'+uuid.uuid4().hex,rank,source_identity=identity)
    try:
        stage.channel48(cid,name)
        for event in events:
            if event['channel']!=cid or event.get('source_key46')!=identity:raise PreviewUnavailable('PREVIEW_IDENTITY')
            stage.add(event)
        stage.flush()
        if stage.failed or stage.facts46.failed:raise PreviewUnavailable('PREVIEW_WRITE_FAILED')
        stage.finish(True)
        for event in events:
            saved=window(portal['id'],cid,event['start_timestamp'],event['stop_timestamp'],limit=256,source48=identity)
            if not any(e['start_timestamp']==event['start_timestamp'] and e['stop_timestamp']==event['stop_timestamp'] and e['name']==event['name'] for e in saved):raise PreviewUnavailable('PREVIEW_VERIFY_FAILED')
    finally:stage.finish(False)
