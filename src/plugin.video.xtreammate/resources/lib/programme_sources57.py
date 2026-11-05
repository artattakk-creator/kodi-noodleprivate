"""Ordered worker-only suppliers for the ONE existing event URL resolver."""
from helper_rpc57 import Error
import time
_backoff={}

PROOFS=('EXACT_HELPER_MOVIE57','EXACT_HELPER_EPISODE57','EXACT_HELPER_SERIES57',
        'EXACT_CATALOG_MOVIE57','EXACT_CATALOG_EPISODE57','EXACT_CATALOG_SERIES57',
        'EXACT_TV_TITLE_YEAR66','EXACT_UNIQUE_TV_TITLE66','EXACT_TVMAZE_ID67')


def policy():
    from utils import setting_bool
    return [setting_bool('programme_helper57',True),setting_bool('programme_catalog57',True)]


def unsuitable69(event):
    genre=str(event.get('genre','')).casefold()
    title=' '.join(str(event.get('title','')).casefold().split())
    return any(word in genre for word in ('nachricht','news','sport','wetter','teleshopping','talk')) or title in ('sendepause','programmhinweis','nachrichten','news','wetter','tagesschau','heute journal') or any(title.startswith(prefix) for prefix in ('live ','live:','live -','live –','live |','uefa ','bundesliga ','formel 1','sky sport news','sportstudio','tagesschau ','talkshow'))

def attempts(event,cancel=lambda:False):
    if unsuitable69(event):return
    from programme_catalog57 import xcmate,kodi
    from programme_helper57 import lookup
    from programme_match46 import candidate
    helper,catalog=policy()
    from programme_outcomes70 import label
    from utils import setting_bool
    own67=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
    if own67:yield label(lambda:candidate(event,cancel),'tmdb')
    if catalog:
        yield label(lambda:xcmate(event,cancel),'catalog')
        yield label(lambda:kodi(event,cancel),'kodi')
    from programme_tvmaze67 import candidate as maze67
    yield label(lambda:maze67(event,cancel),'tvmaze')
    if helper:
        def helper_lookup():
            from programme_urls55 import profile
            key=profile();prior=_backoff.get(key)
            if prior and time.monotonic()<prior[0]:raise Error(prior[1])
            try:result=lookup(event,cancel)
            except Error as exc:
                if exc.code in ('HELPER_NOT_AVAILABLE','HELPER_VERSION_UNSUPPORTED','HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE'):
                    attempts74=min(4,(prior[2]+1) if prior and len(prior)>2 else 1)
                    _backoff[key]=(time.monotonic()+min(900,60*2**(attempts74-1)),exc.code,attempts74)
                    if len(_backoff)>8:_backoff.pop(next(iter(_backoff)))
                raise
            _backoff.pop(key,None)
            return result
        yield label(helper_lookup,'helper')
    if not own67:yield label(lambda:candidate(event,cancel),'tmdb')


def trace(event,code,duration_ms=0):
    from programme_flow48 import trace as fixed
    fixed('IMAGE',event,code,duration_ms=duration_ms)
