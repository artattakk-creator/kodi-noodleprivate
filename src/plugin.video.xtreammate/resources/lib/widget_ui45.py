"""One widget management entry; existing shortcut URLs never rewritten here."""
from localization import tr

def manage(router,portal):
 import xbmcgui
 from menu_icons45 import select
 from widget_hooks45 import probe
 dialog=xbmcgui.Dialog()
 while True:
  choice=select(dialog,tr(32443),['Status vorhandener Widgetverknüpfungen','Widgetquellen für einmalige Einrichtung anzeigen','TEST – optionaler BINGIE-Adapter (PIN)','Zurück','Live-TV: Senderleiste und große Vorschau (.48)'],actions=['info','grid','flask-lock','back','tv'])
  if choice<0 or choice==3:return
  if choice==4:
   from live_hero48 import launch
   launch(router,portal);return
  if choice==0:
   try:
    result=probe();rows=result.get('bindings',[])
    text='Status: '+result['code']+'\n'+str(len(rows))+' erkannte XCMate-Quellen; '+str(sum(bool(r['hooks']) for r in rows))+' mit vorhandenem Aktualisierungsauslöser.\n'
    text+='Bestehende Widgets nicht neu einrichten. Ohne Aktualisierungsauslöser bleibt automatischer sichtbarer Refresh blockiert. Ein optionaler Adapter erfordert PIN und gesonderte Freigabe; keine automatische Skinänderung.'
    from widget_capabilities46 import probe as programme_capabilities46
    capability=programme_capabilities46()
    text+='\n\nProgrammbild / Logo / Fokus: '+capability['code']
    text+='\nStatische Bindings sind keine Android-Darstellungsabnahme. Fehlende Darstellung bleibt gesperrt; ein Adapter wird hier nicht automatisch angewandt.'
    from programme_index46 import status as programme_status46
    local46=programme_status46()
    text+='\n\nLokale Sendungs-/Artwork-Datenbank: '+local46['code']+' · '+str(local46.get('bytes',0))+' Bytes. Ein Status READY bestätigt keine vollständigen20Tage oder Android-Abnahme.'
    if portal:
     import json
     from widget_diagnostics47 import status as widget_status47
     text+='\n\nDatenfluss .47 (−1 = nicht im Budget ermittelbar):\n'+json.dumps(widget_status47(portal['id']),ensure_ascii=False,indent=2)
     text+='\nBildreferenzen sind kein Beleg für Kodi-/EGL-Decodierung. Sichtbarkeit und echtes Dekodieren bleiben Geräteabnahme.'
   except Exception:text='Status: READ_ERROR'
   dialog.textviewer('XCMate Widgets',text)
  elif choice==1:
   from app_routes import widget_instructions
   dialog.textviewer('XCMate Widgets',widget_instructions(router,portal))
  else:
   from experimental45 import run
   from widget_adapter46 import show
   run(show)
