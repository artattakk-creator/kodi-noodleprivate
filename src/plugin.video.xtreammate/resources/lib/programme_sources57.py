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


def attempts(event,cancel=lambda:False):
    from programme_catalog57 import xcmate,kodi
    from programme_helper57 import lookup
    from programme_match46 import candidate
    helper,catalog=policy()
    from utils import setting_bool
    own67=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
    if own67:yield lambda:candidate(event,cancel)
    if catalog:
        yield lambda:xcmate(event,cancel)
        yield lambda:kodi(event,cancel)
    if helper:
        def helper_lookup():
            from programme_urls55 import profile
            key=profile();prior=_backoff.get(key)
            if prior and time.monotonic()<prior[0]:raise Error(prior[1])
            try:result=lookup(event,cancel)
            except Error as exc:
                if exc.code in ('HELPER_NOT_AVAILABLE','HELPER_VERSION_UNSUPPORTED','HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE'):
                    _backoff[key]=(time.monotonic()+60,exc.code)
                    if len(_backoff)>8:_backoff.pop(next(iter(_backoff)))
                raise
            _backoff.pop(key,None)
            return result
        yield helper_lookup
    # Existing local catalogue/library and helper before optional own-token HTTP.
    if not own67:yield lambda:candidate(event,cancel)
    from programme_tvmaze67 import candidate as maze67
    yield lambda:maze67(event,cancel)


def trace(event,code,duration_ms=0):
    from programme_flow48 import trace as fixed
    fixed('IMAGE',event,code,duration_ms=duration_ms)
