"""One widget management entry; existing shortcut URLs never rewritten here."""
from localization import tr

def manage(router,portal):
 import xbmcgui
 from menu_icons45 import select
 from widget_hooks45 import probe
 dialog=xbmcgui.Dialog()
 while True:
  choice=select(dialog,tr(32443),['Status vorhandener Widgetverknüpfungen','Widgetquellen für einmalige Einrichtung anzeigen','TEST – optionaler BINGIE-Adapter (PIN)','Zurück'],actions=['info','grid','flask-lock','back'])
  if choice<0 or choice==3:return
  if choice==0:
   try:
    result=probe();rows=result.get('bindings',[])
    text='Status: '+result['code']+'\n'+str(len(rows))+' erkannte XCMate-Quellen; '+str(sum(bool(r['hooks']) for r in rows))+' mit vorhandenem Aktualisierungsauslöser.\n'
    text+='Bestehende Widgets nicht neu einrichten. Ohne Aktualisierungsauslöser bleibt automatischer sichtbarer Refresh blockiert. Ein optionaler Adapter erfordert PIN und gesonderte Freigabe; keine automatische Skinänderung.'
   except Exception:text='Status: READ_ERROR'
   dialog.textviewer('XCMate Widgets',text)
  elif choice==1:
   from app_routes import widget_instructions
   dialog.textviewer('XCMate Widgets',widget_instructions(router,portal))
  else:
   from experimental45 import run
   from widget_adapter45 import show
   run(show)
