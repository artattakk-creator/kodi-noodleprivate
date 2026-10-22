"""Local, read-only episode ordering. No playback, IO or watched-state policy."""
from collections import Counter


def _number(value):
    text=str(value)
    return int(text) if len(text)<=9 and text.isascii() and text.isdigit() else 0


def _belongs(row,pid,series_id):
    return all(str(row[key])==str(expected) for key,expected in
               (('pid',pid),('portal_id',pid),('series_id',series_id)) if key in row)


def records(data,pid,series_id):
    """Reject explicit foreign identities BEFORE the legacy normalizer binds IDs.

    Keep specials in the ordinary episode list; they are excluded only from Next.
    The response itself is bound to the selected portal/series detail request.
    """
    from media_data import episode_records
    raw=data.get('episodes',{}) if isinstance(data,dict) else {}
    clean={}
    if not str(pid) or not str(series_id) or not isinstance(raw,dict) or not _belongs(data,pid,series_id):return []
    for season,rows in raw.items():
        if not isinstance(rows,list):continue
        clean[season]=[]
        for row in rows:
            if not isinstance(row,dict):continue
            info=row.get('info') if isinstance(row.get('info'),dict) else {}
            if not _belongs(row,pid,series_id) or not _belongs(info,pid,series_id):continue
            valid=bool(_number(season) and _number(row.get('episode_num')))
            valid=valid and row.get('_sequence_valid') is not False and info.get('_sequence_valid') is not False
            valid=valid and all(_number(source['season'])==_number(season) for source in (row,info) if 'season' in source)
            clean[season].append(dict(row,info=dict(info,_sequence_valid=valid)))
    return [dict(row,pid=str(pid)) for row in episode_records({'episodes':clean},series_id)]


def ordered(episodes,pid,series_id):
    """Ambiguous IDs/positions and invalid numbers are never Next candidates."""
    rows=[]
    for row in episodes:
        if not isinstance(row,dict) or row.get('_sequence_valid') is False or not _belongs(row,pid,series_id):continue
        if str(row.get('series_id',''))!=str(series_id):continue
        sid=str(row.get('sid','')).strip()
        season,episode=_number(row.get('season')),_number(row.get('episode'))
        if not sid or sid in ('0','None') or not season or not episode:continue
        rows.append(dict(row,sid=sid,season=season,episode=episode))
    ids=Counter(row['sid'] for row in rows)
    positions=Counter((row['season'],row['episode']) for row in rows)
    return sorted((row for row in rows if ids[row['sid']]==1 and
                   positions[row['season'],row['episode']]==1),key=lambda row:(row['season'],row['episode']))


def match(episodes,pid,series_id,reference):
    if not isinstance(reference,dict) or not _belongs(reference,pid,series_id):return None
    if str(reference.get('pid',reference.get('portal_id','')))!=str(pid) or str(reference.get('series_id',''))!=str(series_id):return None
    key=(str(reference.get('sid','')),_number(reference.get('season')),_number(reference.get('episode')))
    return next((row for row in ordered(episodes,pid,series_id)
                 if (row['sid'],row['season'],row['episode'])==key),None)


def successor(episodes,pid,series_id,reference):
    anchor=match(episodes,pid,series_id,reference)
    if anchor is None:return None
    return next((row for row in ordered(episodes,pid,series_id)
                 if (row['season'],row['episode'])>(anchor['season'],anchor['episode'])),None)
