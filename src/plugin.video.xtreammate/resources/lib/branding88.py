"""Separate reversible HeaderLogo transaction, never an automatic skin write."""
from pathlib import Path
import xml.etree.ElementTree as E
OLD=('bingie_mod_logo.png','home/bingie_mod_logo.png')
NEW='special://home/addons/plugin.video.xtreammate/resources/media/hero88/xcmate_logo.png'
def candidate(raw):
 from widget_skin80 import _node
 from widget_skin50 import edit
 span,end,node=_node(raw,'include','name','HeaderLogo')
 textures=[n for n in node.iter('texture') if n.text in OLD]
 if len(textures)!=2:raise ValueError('BRANDING_UNVERIFIED')
 for n in textures:n.text=NEW
 for n in node.iter('colordiffuse'):n.text='FFFFFFFF'
 return edit(raw,[(span['start'],end,E.tostring(node,encoding='utf-8'))])
def prepare(skin):
 from widget_skin50 import guard
 from widget_transaction50 import prepare as transaction,read,sha
 guard(skin);target=Path(skin).resolve()/'xml/IncludesHeader.xml';raw=read(target)
 return transaction('skin',[(target,candidate(raw))],dict(branding88=True,skin=str(Path(skin).resolve()),meta_sha=sha(read(Path(skin)/'addon.xml'))))
def apply(token,skin,confirmed=False,restore=False):
 from widget_transaction50 import load,folder,read,apply as transaction,sha
 plan=load(token,'skin');root=Path(skin).resolve();target=root/'xml/IncludesHeader.xml'
 if plan.get('metadata')!=dict(branding88=True,skin=str(root),meta_sha=sha(read(root/'addon.xml'))):raise ValueError('BRANDING_UNVERIFIED')
 backup=folder()/token
 if candidate(read(backup/'original.0'))!=read(backup/'candidate.0'):raise ValueError('BRANDING_UNVERIFIED')
 return transaction(token,'skin',[target],confirmed=confirmed,restore=restore)
def menu():
 import xbmcgui
 from widget_manager50 import runtime,rebuild
 from widget_transaction50 import folder,load
 _,skin=runtime();dialog=xbmcgui.Dialog();choice=dialog.select('XCMate-Logo in BINGIE', ['Vorschau und anwenden','Letzte Logo-Änderung zurücknehmen'])
 if choice==0:
  plan=prepare(skin)
  if dialog.yesno('XCMate-Logo','Nur die zwei Header-Logotexturen werden ersetzt. Original, SHA256 und Rückrollplan sind gesichert. Jetzt anwenden?'):
   apply(plan['id'],skin,True);rebuild()
 elif choice==1:
  plans=[]
  for entry in folder().iterdir():
   try:
    plan=load(entry.name,'skin')
    if plan.get('metadata',{}).get('branding88'):plans.append(plan)
   except (OSError,ValueError,KeyError):pass
  if plans and dialog.yesno('XCMate-Logo','Gesicherte Original-Logos wiederherstellen?'):
   apply(max(plans,key=lambda p:p['at'])['id'],skin,True,True);rebuild()
