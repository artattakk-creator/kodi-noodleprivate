"""Fixed per-supplier outcomes; never include titles, IDs, URLs or errors."""
SOURCES=('xmltv','provider','tmdb','catalog','kodi','tvmaze','helper','injected')
CODES=frozenset(('FOUND','NO_CONFIRMED_IMAGE','DISABLED','CANCELLED','HTTP_AUTH','HTTP_RATE_LIMIT','HTTP_TIMEOUT','HTTP_NOT_FOUND','TIMEOUT','NETWORK_ERROR','DNS_ERROR','TLS_ERROR','TMDB_TOKEN_MISSING','TMDB_TOKEN_FILE_INVALID','HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE','HELPER_NOT_AVAILABLE','HELPER_VERSION_UNSUPPORTED','NO_UNIQUE_MATCH','NO_MATCH_AMBIGUOUS','NO_ARTWORK','REMOTE_ERROR'))
def label(fn,source):fn.source70=source;return fn
def clean(values):
 if not isinstance(values,list):return []
 return [dict(source=v['source'],code=v['code'] if v.get('code') in CODES else 'REMOTE_ERROR') for v in values[:8] if isinstance(v,dict) and v.get('source') in SOURCES]
def add(value,source,code):
 if source not in SOURCES:return
 value['sources70']=clean(value.get('sources70',[])+[dict(source=source,code=code)])
def settings():
 from utils import setting_bool
 return dict(own=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False),helper=setting_bool('programme_helper57',True),catalog=setting_bool('programme_catalog57',True),tvmaze=setting_bool('programme_tvmaze67',False))
