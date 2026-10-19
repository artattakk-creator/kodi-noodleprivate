"""Provider metadata normalization; explicit detail work runs off GUI callbacks."""
from localization import tr
import json
import math
import time


def recent_label(item,days=10,now=None):
    now=time.time() if now is None else now
    stamp=item.get('added_at')
    if not isinstance(stamp,(int,float)) or not math.isfinite(stamp):
        return tr(32535)
    date=time.strftime(tr(32583),time.localtime(stamp))
    return (tr(32536) if now-stamp<=max(1,min(days,30))*86400 else tr(32537).format(days))+date


def details(client,kind,sid):
    action='get_vod_info' if kind=='vod' else 'get_series_info'
    extra={'vod_id' if kind=='vod' else 'series_id':str(sid)}
    data=client._get_json(action,extra=extra,cached_only=True)
    if isinstance(data,dict) and data: return data
    from utils import http_get,cache_set
    raw,_=http_get(client._api_url(),params={**client._base_params(),'action':action,**extra},
                   timeout=5,max_seconds=10,max_bytes=2*1024*1024)
    data=json.loads(raw)
    if not isinstance(data,dict): raise ValueError('invalid details')
    if cache_set(client._cache_key(action,extra),data) is False:
        raise OSError('detail cache is not writable')
    return data


def video_info(item):
    from metadata_views import provider_plot
    result={'title':str(item.get('name') or item.get('title') or ''),'plot':provider_plot(item)}
    for key in ('genre','director','cast'):
        if item.get(key): result[key]=item[key]
    try:
        year=int(str(item.get('year') or item.get('releaseDate') or '')[:4])
        if 1880<=year<=2100: result['year']=year
    except (ValueError,TypeError): pass
    try:
        rating=float(item.get('rating')) if item.get('rating') not in (None,'') else float(item.get('rating_5based'))*2
        if math.isfinite(rating) and 0<=rating<=10: result['rating']=rating
    except (ValueError,TypeError): pass
    duration=0
    try:
        duration=int(item.get('duration_secs') or 0)
        text=item.get('duration')
        if not duration and isinstance(text,str) and text.count(':')==2:
            h,m,s=map(int,text.split(':'))
            if 0<=h<48 and 0<=m<60 and 0<=s<60: duration=h*3600+m*60+s
    except (ValueError,TypeError,OverflowError): pass
    if 0<duration<=172800: result['duration']=duration
    return result


def episode_records(data,series_id):
    episodes=data.get('episodes',{}) if isinstance(data,dict) else {}
    result=[]
    if not isinstance(episodes,dict): return result
    for season,rows in episodes.items():
        if not str(season).isdigit() or not isinstance(rows,list): continue
        for row in rows:
            if not isinstance(row,dict) or not row.get('id'): continue
            try: number=int(row.get('episode_num',0))
            except (ValueError,TypeError): number=0
            info=row.get('info') if isinstance(row.get('info'),dict) else {}
            result.append(dict(info,sid=str(row['id']),name=str(row.get('title') or tr(32605)),
                series_id=str(series_id),season=int(season),episode=number,
                container_extension=row.get('container_extension','mkv')))
    result.sort(key=lambda e:(e['season'],e['episode'],e['sid']))
    return result
