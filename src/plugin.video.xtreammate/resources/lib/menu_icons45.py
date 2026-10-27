"""Central local menu glyph registry, shared by directories, lists and dialogs."""
import os
from urllib.parse import urlsplit,parse_qs
ROLES=('tv','movie','series','search','star','calendar','database','refresh','user','plus','pencil','link','list','play','speaker','cc','globe','remote','image','grid','palette','drive','shield','info','flask-lock','record','download','activity','clock','document','settings','trash','back','wand','check')
SECTIONS={'accounts':'user','live':'tv','epg':'calendar','media':'play','appearance':'palette','system':'drive','experimental':'flask-lock','downloads':'download','recordings':'record','diagnostics':'activity','about':'info','remote':'remote','storage':'drive','groups':'list','startup':'tv','player':'play','maintenance':'activity','designs':'palette'}
ACTIONS={
 'home_start':'tv','home_live':'tv','play_start':'tv','play_start_direct':'tv','source_start':'tv','source_live':'tv','play_live':'tv','source_play':'tv','root':'tv','xcmate_home':'tv','portal_home':'user',
 'movies_home':'movie','vod_categories':'movie','vod_list':'movie','m3u_movies':'movie','m3u_movie_list':'movie','series_home':'series','series_categories':'series','series_list':'series','series_seasons':'series','series_episodes':'series',
 'global_search':'search','search':'search','search_results':'search','search_section':'search','favourites':'star','media_favourites':'star','toggle_favourite':'star','favourite':'star','resume':'clock','restart':'refresh','continue_episode':'clock','next_episode':'series','seasons':'series','play':'play','trailer':'movie',
 'guide_grid':'calendar','guide_browser':'calendar','guide_timers':'clock','epg_sources':'database','epg_status':'activity','guide_status':'activity','guide_backup44':'shield','refresh_epg':'refresh','refresh_portal':'refresh','epg_now':'calendar','epg_channel':'calendar','catchup_list':'clock','play_catchup':'play',
 'account_select':'check','portal_manager':'user','xtream_account':'user','m3u_account':'user','stb_account':'user','add_portal_from_settings':'plus','setup_wizard':'wand','import_legacy_settings':'shield','groups_manager':'list','group_settings':'list','startup_settings':'tv','playlist_editor':'pencil',
 'settings_home':'settings','settings':'settings','native_options45':'settings','remote_setup':'remote','remote_learn':'remote','remote_diagnostics':'activity','service_recover':'refresh','popup_probe':'activity','stability_test':'activity','autoplay_diagnostic_mode':'activity','clear_cache':'trash',
 'artwork_manage':'image','art_status':'activity','art_retry':'refresh','art_db_health':'shield','theme_manager':'palette','appearance_settings':'palette','ui_language':'globe','widget_adapter45':'grid','widget_setup':'grid','widget_live_start_group':'grid','widget_recent_vod':'grid','widget_recent_series':'grid','device_info':'info','branding_status':'info','about_xcmate':'info','xcmate_licenses':'document',
 'record_now':'record','recordings_manage':'record','recording_folder':'drive','recording_capabilities':'info','download_folder':'drive','download_capabilities':'info','download_target_test':'activity','downloads_manage45':'download','experimental_options45':'flask-lock',
 'metadata':'info','image_search':'image','poster_retry':'refresh','download':'download','downloads':'download','back':'back','previous':'back','delete':'trash','remove':'trash','add':'plus','edit':'pencil','select':'check','audio':'speaker','language':'globe','subtitle':'cc','video':'tv','info':'info','episodes':'series'}

def role(action,params=None):
 params=params or {}
 if action in ROLES:return action
 if action in ('settings_section','native_options45'):return SECTIONS.get(params.get('section') or params.get('group'),'settings')
 if action=='media_detail':return 'series' if params.get('kind')=='series' else 'movie'
 if action in ACTIONS:return ACTIONS[action]
 for words,value in [(('download',),'download'),(('record',),'record'),(('epg','guide'),'calendar'),(('series','season','episode'),'series'),(('vod','movie','film'),'movie'),(('group','channel'),'list'),(('portal','account'),'user'),(('refresh','retry'),'refresh'),(('remote',),'remote'),(('play',),'play'),(('theme','appearance'),'palette'),(('diagnos','status','probe','test'),'activity'),(('setting',),'settings')]:
  if any(word in action for word in words):return value
 return 'info'

def icon(action='info',params=None,full=False):
 key=role(action,params)
 return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'resources','media','menu45',*(['full'] if full else []),key+'.png')

def for_url(url,existing=None):
 p={k:v[0] for k,v in parse_qs(urlsplit(url).query).items()};action=p.get('action','root')
 if existing and action in ('media_detail','play_live','play_vod','play_episode','source_play','play_stb_live','play_stb_vod','play_stb_episode'):return existing
 return icon(action,p)

def decorate(item,action='info',params=None,full=False):
 value=icon(action,params,full);item.setArt({'icon':value,'thumb':value});return item

def entries(labels,actions=None,default='info'):
 import xbmcgui
 result=[]
 for i,label in enumerate(labels):
  if not isinstance(label,str):result.append(label);continue
  action=actions[i] if actions and i<len(actions) else classify(label,default)
  result.append(decorate(xbmcgui.ListItem(label),action))
 return result

def classify(label,default):
 text=label.casefold()
 for words,key in [(('hinzufügen','add portal','add source'),'plus'),(('bearbeiten','edit'),'pencil'),(('löschen','entfernen','delete','remove'),'trash'),(('abbrechen','zurück','cancel','back'),'back'),(('speichern','übernehmen','save','apply'),'check'),(('aktualisier','erneut','refresh','retry'),'refresh'),(('zuordn','mapping'),'link'),(('sprache','language'),'globe'),(('untertitel','subtitle'),'cc'),(('audio','lautstärke','volume'),'speaker'),(('abspielen','ansehen','wiedergabe','play','watch'),'play'),(('fortsetzen','resume'),'clock'),(('favorit','favorite'),'star'),(('widget',),'grid'),(('diagnos','status','test'),'activity'),(('timer',),'clock'),(('cover','poster','bild','image','commons'),'image'),(('konto','portal','account'),'user'),(('quelle','source'),'database')]:
  if any(word in text for word in words):return key
 return default

def select(dialog,heading,labels,*args,actions=None,default='info',**kwargs):
 kwargs['useDetails']=True
 return dialog.select(heading,entries(labels,actions,default),*args,**kwargs)

def multiselect(dialog,heading,labels,*args,default='info',**kwargs):
 kwargs['useDetails']=True
 return dialog.multiselect(heading,entries(labels,default=default),*args,**kwargs)

def state_icon(selected):
 import xbmcaddon
 return os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','setup_checked.png' if selected else 'setup_unchecked.png')
