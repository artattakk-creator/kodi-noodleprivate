"""One EPG artwork configuration; existing IDs/values remain authoritative."""
def state():
 from utils import setting_bool
 from tmdb_token61 import status
 token=status()
 if token=='FILE_MISSING':
  from utils import setting
  if setting('tmdb_read_token43','').strip():token='FILE_VALID'
 guide=setting_bool('programme_tmdb46',False);access=setting_bool('tmdb_research43',False)
 return dict(token='TOKEN_PRESENT' if token=='FILE_VALID' else token,
             lookup='TMDB_LOOKUP_ENABLED' if guide and access else 'TMDB_LOOKUP_DISABLED',
             programme_enabled=guide,token_access_enabled=access,
             helper=setting_bool('programme_helper57',True),
             catalog=setting_bool('programme_catalog57',True),tvmaze=setting_bool('programme_tvmaze67',False))

def show():
 import json,xbmcaddon,xbmcgui
 from menu_icons45 import select
 from localization import tr
 addon=xbmcaddon.Addon();dialog=xbmcgui.Dialog()
 while True:
  value=state()
  entries=['Status: '+value['token']+' / '+value['lookup'],
           'Privater TMDB-Zugang: Import / bestehende Werte',
           'TMDB-Verbindung testen',
           'Eigene TMDB-Sendungsbildsuche erlauben',
           'Eigene TMDB-Sendungsbildsuche deaktivieren',
           'Optionaler TMDB-Helper: '+('AN' if value['helper'] else 'AUS'),
           'Lokaler Medienkatalog: '+('AN' if value['catalog'] else 'AUS'),
           'Optionaler TVmaze-Abgleich: '+('AN' if value['tvmaze'] else 'AUS'),
           'Internes Sendungsbild-Budget',
           'Speicherdiagnose (nur lesen)',
           'Lizenzen und Bildquellen',
           'Zurück']
  choice=select(dialog,'XCMate – EPG / Sendungsbilder',entries,default='settings')
  if not isinstance(choice,int) or not 0<=choice<len(entries) or choice==11:return
  if choice==0:dialog.ok('XCMate',json.dumps(value,ensure_ascii=False,indent=2)+'\nToken vorhanden und Verbindung OK bestätigen noch kein Sendungsbild.')
  elif choice==1:
   from tmdb_access61 import show as tokens
   tokens()
  elif choice==2:
   from tmdb_connection60 import launch
   launch()
  elif choice==3:
   if dialog.yesno('XCMate','Sendungstitel und vorhandene Jahr-/Episodendaten für die Bildsuche an TMDB senden? Der bestehende private Token bleibt unverändert.',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
    from tmdb_access61 import activate
    activate(addon)
  elif choice==4:
   if dialog.yesno('XCMate','Eigene TMDB-Sendungsbildsuche deaktivieren?',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
    addon.setSetting('programme_tmdb46','false');addon.setSetting('tmdb_research43','false')
  elif choice in (5,6,7):
   key=('programme_helper57','programme_catalog57','programme_tvmaze67')[choice-5]
   enabled=value[('helper','catalog','tvmaze')[choice-5]]
   if dialog.yesno('XCMate',entries[choice]+' – '+('deaktivieren?' if enabled else 'aktivieren? Externe Abfragen bleiben auf diese gewählte Quelle begrenzt.'),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):
    addon.setSetting(key,'false' if enabled else 'true')
    from programme_refresh63 import request
    request()
  elif choice==8:
   selected=select(dialog,'Sendungsbilder: Budget (MiB)',['32','64','128','256'],default='settings')
   if selected in (0,1,2,3):addon.setSetting('programme_art_budget46',str(selected))
  elif choice==9:
   from programme_storage68 import inspect
   dialog.ok('XCMate – Speicherdiagnose',json.dumps(inspect(),ensure_ascii=False,indent=2)+'\nKeine Dateien gelöscht; keine Budgets automatisch erhöht.')
  elif choice==10:
   from credits67 import show as credits
   credits('Sendungsbilder: TMDB / konfigurierte EPG-Quellen. Ein vorhandener Token belegt keine erfolgreiche Bildsuche.')
