"""Background-only RAM reload notification when snapshot publication is denied.

Existing native widget paths/hooks are reused. No skin/profile/cache writes,
new route, shared snapshot or lock-free publication into another writer's file.
"""
import hashlib,json,time
PREFIX84='XCMate.ReadonlyPrepared84.'


def _slot84(portal,kind):
    from widget_data41 import policy
    return PREFIX84+policy(portal,kind)


def proof84(portal,kind,rows):
    import xbmcgui
    from home_publication74 import source_refs
    try:
        raw=xbmcgui.Window(10000).getProperty(_slot84(portal,kind));value=json.loads(raw) if raw and len(raw)<65536 else {}
        selected=rows[:24]
        if value.get('ids')!=[str(r['sid']) for r in selected] or value.get('sources')!=source_refs(selected) or not 0<=time.time()-value.get('at',0)<5:return None
        return {k:value[k] for k in ('signature','count','images','fallbacks')}
    except (ValueError,TypeError,AttributeError,KeyError):return None


def publish(portal,kind,rows):
    from widget_render47 import values
    from widget_art44 import read
    from widget_notice46 import prepare
    digest=hashlib.sha256();approved=read(portal['id'],kind);count=0;images84=0
    for offset in range(0,len(rows),16):
        for value in values(portal,kind,rows[offset:offset+16],approved):
            value.pop('_programme46',None)
            images84+=int(__import__('widget_assets69').renderable(value.get('art',{}).get('poster')))
            digest.update(json.dumps(value,sort_keys=True).encode());count+=1
    if kind in ('vod','series'):
        import xbmcgui
        from home_publication74 import source_refs
        record=dict(at=time.time(),ids=[str(r['sid']) for r in rows[:24]],sources=source_refs(rows[:24]),signature=digest.hexdigest(),count=count,images=images84,fallbacks=count-images84)
        raw=json.dumps(record,separators=(',',':'))
        if len(raw)<65536:xbmcgui.Window(10000).setProperty(_slot84(portal,kind),raw)
    prepare(portal,kind,digest.hexdigest(),count,art_count84=images84)
    from widget_diagnostics47 import note
    note(portal['id'],kind,'DIRECTORY','READ_ONLY_RELOAD',items=count)
    return True
