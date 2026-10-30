"""Seven canonical sections; old directory URLs remain safe aliases."""
from localization import tr
SECTIONS=((36000,'accounts'),(36001,'live'),(36002,'epg'),(36003,'media'),(36004,'appearance'),(36005,'system'),(36006,'experimental'))
ALIASES={'startup':'live','groups':'live','remote':'appearance','player':'media','storage':'system','maintenance':'system','about':'system','designs':'appearance'}
ROWS={
'accounts':[(32416,'account_select',{}),(32419,'portal_manager',{}),(32420,'setup_wizard',{}),(36015,'native_options45',{'group':'accounts'})],
'live':[(32421,'startup_settings',{}),(32430,'groups_manager',{}),(32431,'favourites',{}),(36016,'native_options45',{'group':'live'})],
'epg':[(32423,'guide_browser',{}),(32424,'epg_sources',{}),(32426,'guide_status',{}),(35960,'guide_backup44',{}),(32428,'refresh_epg',{}),(36017,'native_options45',{'group':'epg'})],
'media':[(36018,'native_options45',{'group':'media'}),(32432,'media_favourites',{'kind':'vod'}),(32433,'media_favourites',{'kind':'series'})],
'appearance':[(33813,'theme_manager',{}),(32620,'ui_language',{}),(32622,'appearance_settings',{}),(32436,'remote_setup',{}),(36019,'native_options45',{'group':'appearance'})],
'system':[(35200,'artwork_manage',{}),(32661,'art_status',{}),(36020,'native_options45',{'group':'system'}),(32414,'settings_section',{'section':'information'}),(32429,'settings',{})],
'information':[(35300,'device_info',{}),(33701,'branding_status',{}),(32454,'about_xcmate',{}),(33405,'xcmate_licenses',{})]}
EXPERIMENTAL={
'experimental':[(36681,'tvmaze_experiment59',{}),(36111,'widget_adapter46',{}),(32443,'widget_adapter45',{}),(36021,'settings_section',{'section':'downloads'}),(36022,'settings_section',{'section':'recordings'}),(36023,'settings_section',{'section':'diagnostics'}),(36024,'native_options45',{'group':'experimental'})],
'downloads':[(34202,'downloads_manage45',{}),(34700,'download_folder',{}),(34701,'download_capabilities',{}),(35007,'download_target_test',{})],
'recordings':[(34013,'record_now',{}),(34008,'recordings_manage',{}),(32427,'guide_timers',{}),(32438,'recording_folder',{}),(32441,'recording_capabilities',{})],
'diagnostics':[(34800,'stability_test',{}),(32449,'remote_diagnostics',{}),(32450,'service_recover',{}),(32451,'popup_probe',{}),(32452,'clear_cache',{}),(32662,'art_retry',{}),(32900,'art_db_health',{}),(35503,'autoplay_diagnostic_mode',{}),(32435,'remote_learn',{}),(32439,'recording_folder',{'check':'1'})]}

def render(router,portal,section=''):
 import xbmcplugin
 from boot_diagnostics import finish_directory
 from window_navigation import add_action,WINDOW_ACTIONS,DIALOG_ACTIONS
 from menu_icons45 import icon
 from theme_render import lightweight_background
 pid=portal['id'] if portal else ''
 if section in EXPERIMENTAL:
  finish_directory(router,cacheToDisc=False)
  from experimental45 import run,open_menu
  run(lambda:open_menu(router,portal,section));return
 section=ALIASES.get(section,section)
 values=[(label,'settings_section',{'section':key}) for label,key in SECTIONS] if not section else list(ROWS.get(section,[]))
 if section=='live' and portal and portal.get('type')=='m3u':values.append((32746,'playlist_editor',{}))
 for label,action,params in values:
  url=router.url(action=action,pid=pid,**params);art=dict(icon=icon(action,params),fanart=lightweight_background())
  if action in WINDOW_ACTIONS|DIALOG_ACTIONS or action in ('native_options45','downloads_manage45') or action=='settings_section' and params.get('section')=='experimental':add_action(router,tr(label),url,**art)
  else:router._add_dir(tr(label),url,**art)
 finish_directory(router,cacheToDisc=False)
