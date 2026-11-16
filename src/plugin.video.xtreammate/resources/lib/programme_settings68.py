"""One EPG artwork configuration; existing IDs/values remain authoritative."""
def state():
 from utils import setting_bool
 from tmdb_token61 import status
 token=status()
 if token=='FILE_MISSING':
  from utils import setting
  if setting('tmdb_read_token43','').strip():token='FILE_VALID'
 guide=setting_bool('programme_tmdb46',False);access=setting_bool('tmdb_research43',False)
 from settings_guard96 import snapshot
 return dict(settings_health=snapshot()['code'],token='TOKEN_PRESENT' if token=='FILE_VALID' else token,
             lookup='TMDB_LOOKUP_ENABLED' if guide and access else 'TMDB_LOOKUP_DISABLED',
             programme_enabled=guide,token_access_enabled=access,
             helper=setting_bool('programme_helper57',True),
             catalog=setting_bool('programme_catalog57',True),tvmaze=setting_bool('programme_tvmaze67',False),local_cache=setting_bool('programme_art_local69',False))

def show():
 from artwork_hub96 import show as hub
 hub()
