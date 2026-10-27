"""Conservative opt-in detail-only fallback; never runs on scrolling/focus."""
import collections,threading,time
_cache=collections.OrderedDict()
_lock=threading.Lock()
_next=0


def fallback(item,kind,failed=False):
    from utils import setting_bool
    from media_art import poster_candidates
    if kind not in ('vod','series') or not setting_bool('tmdb_fallback43',False):return item
    if not failed and poster_candidates(item):return item
    from library_index import normalized
    title=normalized(item.get('name',''));year=str(item.get('year') or item.get('releaseDate') or '')[:4]
    if not title or not year.isdigit() or not 1880<=int(year)<=2100:return item
    key=(kind,title,year)
    global _next
    with _lock:
        prior=_cache.get(key)
        if prior and prior[0]>time.monotonic():rows=prior[1]
        elif time.monotonic()<_next:return item
        else:rows=None;_next=time.monotonic()+2
    if rows is None:
        from media_sources43 import tmdb,SourceError
        try:rows=tmdb(str(item.get('name',''))[:200],kind)
        except SourceError as error:
            with _lock:
                _cache[key]=(time.monotonic()+60,[])
                _next=time.monotonic()+(300 if error.code in ('HTTP_AUTH','HTTP_RATE_LIMIT') else 15)
            return item
        rows=[r for r in rows if r.get('url') and r['role']=='poster' and r['media_type']==('movie' if kind=='vod' else 'tv')
              and normalized(r['title'])==title and r['year']==year]
        # Same title/year can still be ambiguous. Only ONE distinct work is safe.
        if len({r['remote_id'] for r in rows})!=1:rows=[]
        with _lock:
            _cache[key]=(time.monotonic()+(600 if rows else 60),rows)
            while len(_cache)>128:_cache.popitem(last=False)
    if not rows:return item
    row=rows[0];result=dict(item,cover=row['url'],_metadata_source43='TMDb')
    result['_provider43']=dict(item.get('_provider43',item))
    result['_fallback43']={'cover':row['url']}
    # Only fill absent descriptive data. IDs, title, portal and year remain
    # provider identity. Manual choices are reapplied AFTER this function.
    from metadata_views import provider_plot
    if not provider_plot(item) and row['metadata'].get('plot'):
        result['plot']=row['metadata']['plot'];result['_fallback43']['plot']=result['plot']
    return result
