"""Capability-gated VOD actions; future extensions receive verified IDs only."""
KINDS=frozenset(('vod','episode','series_item'))
ACTIONS=(('pause',33001,'transport'),('back',33002,'transport'),('forward',33003,'transport'),
         ('stop',33004,'transport'),('audio',33005,'transport'),('subtitles',33006,'transport'),
         ('subtitle_toggle',33007,'settings'),('video',33008,'settings'),
         ('audio_settings',33009,'settings'),('info',33010,'settings'))
_extensions={}


def register(name,label,handler,capability,kinds=KINDS):
    if name in {a[0] for a in ACTIONS} or not callable(handler) or not callable(capability):raise ValueError('action registration')
    if not frozenset(kinds)<=KINDS:raise ValueError('media kinds')
    _extensions[name]=(int(label),handler,capability,frozenset(kinds))


def media_ids(session):
    if session.get('kind') not in KINDS or not all(isinstance(session.get(k),str) and session[k] for k in ('pid','sid','nonce')):raise ValueError('unverified media IDs')
    return {k:session[k] for k in ('pid','kind','sid','series_id','season','episode') if k in session}


def available(session,caps):
    if session.get('kind') not in KINDS:return []
    result=[entry for entry in ACTIONS if caps.get(entry[0],False)]
    for name,(label,handler,capability,kinds) in _extensions.items():
        if session['kind'] in kinds and capability(media_ids(session)):result.append((name,label,'settings'))
    return result


def extension(name,session):
    label,handler,capability,kinds=_extensions[name]
    ids=media_ids(session)
    if session['kind'] in kinds and capability(ids):return handler(ids)
    return False
# No active download action is registered. Future download permission/target
# validation belongs to its own manager, before registering a capability.
