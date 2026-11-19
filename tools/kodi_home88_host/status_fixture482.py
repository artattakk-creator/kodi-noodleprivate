"""Synthetic RAM event tied to the existing verified native guide snapshot."""


def build(pid,row,now,original):
    from epg_views import guide_for_channel
    from programme_snapshot47 import bind
    cid=str(original.get('canonical46') or original.get('epg_id') or row.get('epg_channel_id') or row['sid'])
    raw=dict(name='Native status482',descr='Native status projection; synthetic programme facts.',
             start_timestamp=int(now)-60,stop_timestamp=int(now)+1800,source_key46='provider')
    info=guide_for_channel({cid:[raw]},cid,now=now)
    # get() must retain its real revision guard. A made-up new revision is
    # rejected by design and cannot be used as a native rendering fixture.
    info.update(epg_id=cid,canonical46=cid,snapshot_revision=original['snapshot_revision'])
    return bind(pid,row,info)
