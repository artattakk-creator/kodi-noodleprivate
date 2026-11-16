"""Exactly three source choices backed by existing Kodi flags and token store."""
FLAGS={
 'xmltv':{'programme_xmltv96':'true'},
 'tmdb':{'programme_tmdb46':'true','tmdb_research43':'true','programme_tmdb_optout77':'false'},
 'tvmaze':{'programme_tvmaze67':'true','programme_tvmaze_optout77':'false'},
}

def health():
 from settings_guard96 import snapshot
 return snapshot()['code']

def require():
 from settings_guard96 import require as check,SettingsError
 from media_sources43 import SourceError
 try:check()
 except SettingsError as exc:raise SourceError(exc.code) from None

def enabled(source):
 require()
 from utils import setting_bool
 if source=='xmltv':return setting_bool('programme_xmltv96',True)
 if source=='tmdb':return all(setting_bool(k,False) for k in ('programme_tmdb46','tmdb_research43')) and not setting_bool('programme_tmdb_optout77',False)
 if source=='tvmaze':return setting_bool('programme_tvmaze67',False) and not setting_bool('programme_tvmaze_optout77',False)
 return False

def token_valid():
 from tmdb_token61 import effective_tmdb_read_token,validate,TokenError
 try:
  token=effective_tmdb_read_token(force=True)
  if not token:return False
  validate(token.encode('utf-8'));return True
 except (TokenError,OSError,UnicodeError):return False

def changes(source,on):
 return {key:('true' if (on!=(key.endswith('_optout77'))) else 'false') for key in FLAGS[source]}

def choose(source,on):
 from settings_guard96 import write
 if source not in FLAGS:raise ValueError('SOURCE_UNKNOWN')
 if on and source=='tmdb' and not token_valid():raise OSError('TMDB_TOKEN_MISSING_OR_INVALID')
 result=write(changes(source,on))
 if on:
  # This is the same explicit image decision shown by the storage dialog, not
  # a hidden fourth switch. Never silently override it for another profile.
  from storage_policy92 import choose as policy
  policy('yes')
 from programme_refresh63 import request
 request();return result

def enroll_test_profile():
 from settings_guard96 import write
 if not token_valid():raise OSError('TMDB_TOKEN_MISSING_OR_INVALID')
 combined={}
 for source in FLAGS:combined.update(changes(source,True))
 write(combined)
 from storage_policy92 import choose,images_enabled
 choose('yes')
 if not images_enabled():raise OSError('SOURCE_POLICY_READBACK_FAILED')
 from programme_refresh63 import request
 request();return 'SOURCES_VERIFIED'

def status():
 from settings_guard96 import snapshot
 state=snapshot();result={'settings':state['code'],'token_valid':False}
 if state['code'] not in ('READY','NOT_CREATED'):return result
 result.update({key:enabled(key) for key in FLAGS});result['token_valid']=token_valid()
 from storage_policy92 import images_enabled
 result['images_enabled']=images_enabled()
 return result
