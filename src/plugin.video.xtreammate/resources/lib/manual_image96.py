"""Artwork Hub station picker, reusing local groups and the owned detail dialog."""
def manage():
 import xbmcgui
 from menu_icons45 import select
 from portals import get_active
 from logo_editor96 import groups,stations
 from artwork_ui import job
 from localization import tr
 portal_rows=get_active()
 if not portal_rows:return
 dialog=xbmcgui.Dialog();chosen=select(dialog,tr(39029),[p.get('name','XCMate') for p in portal_rows]) if len(portal_rows)>1 else 0
 if not 0<=chosen<len(portal_rows):return
 portal=portal_rows[chosen]
 try:
  categories=job(lambda cancel,progress:groups(portal)) or []
  chosen=select(dialog,tr(39030),[r['title'] for r in categories])
  if not 0<=chosen<len(categories):return
  cid=categories[chosen]['cid'];offset=0
  while True:
   page=job(lambda cancel,progress:stations(portal,cid,offset))
   if not page:return
   rows,total=page;more=offset+len(rows)<total
   labels=[r.get('name','') for r in rows]+([tr(39031)] if more else [])+([tr(39032)] if offset else [])
   chosen=select(dialog,tr(39029),labels)
   if chosen<0:return
   if chosen<len(rows):
    from programme_window46 import show
    show(portal,rows[chosen],manual96=True)
   elif more and chosen==len(rows):offset+=100
   elif offset:offset=max(0,offset-100)
 except (OSError,ValueError,__import__('sqlite3').Error):dialog.ok('XCMate',tr(39025))
