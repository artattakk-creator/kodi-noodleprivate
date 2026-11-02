"""Pure exact negative-cache scope, including source, profile and consent."""
import hashlib,json
def negative_scope(event):
 from epg_handoff63 import profile_scope
 from tmdb_token61 import token_fingerprint
 from utils import setting_bool
 keys=('pid','sid','canonical','source_key46','fact_revision46','epg_source46','start','stop','title','year','season','episode','revision')
 flags=[setting_bool(k,d) for k,d in (('programme_tmdb46',False),('tmdb_research43',False),('programme_helper57',True),('programme_catalog57',True),('programme_tvmaze67',False))]
 from programme_urls55 import hosts
 from utils import setting_int
 value=[profile_scope(),[event.get(k) for k in keys],flags,token_fingerprint(),sorted(hosts()),setting_int('programme_art_budget46',1),setting_int('media_art_reserve_mb',1024),setting_int('media_art_budget_mb',0)]
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
