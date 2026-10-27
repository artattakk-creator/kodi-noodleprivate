"""Optional verified BINGIE XML patch; never invoked by worker or startup.

Stored shortcut URLs stay unchanged. Only generated literal XCMate widget source
URLs receive a scoped runtime reload parameter. Explicit PIN + confirmation,
verified private backup, atomic replace, hash-guarded restore; no other edits.
"""
import hashlib,json,os,stat,tempfile,time,uuid
from pathlib import Path
from widget_hooks45 import sources,LIMIT

def sha(data):return hashlib.sha256(data).hexdigest()

def patch(data):
 text=data.decode('utf-8');rows=sources(text);count=0
 for row in reversed(rows):
  if row['hooks']:continue
  suffix='&amp;xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.'+row['kind']+')]'
  text=text[:row['stop']]+suffix+text[row['stop']:];count+=1
 result=text.encode('utf-8');sources(text)
 return result,count

def guard(target,skin_root,version):
 target=Path(target);root=Path(skin_root).resolve()
 if version!='2.2.3':raise ValueError('UNVERIFIED_SKIN_VERSION')
 if target.is_symlink() or target.resolve().parent.name not in ('xml','1080i','720p') or target.name!='script-skinshortcuts-includes.xml':raise ValueError('UNSAFE_TARGET')
 target=target.resolve()
 if root not in target.parents:raise ValueError('FOREIGN_TARGET')
 import xml.etree.ElementTree as ET
 meta=ET.parse(root/'addon.xml').getroot()
 if meta.get('id')!='skin.titan.bingie.mod' or meta.get('version')!=version:raise ValueError('SKIN_METADATA_MISMATCH')
 if not target.is_file() or target.stat().st_size>LIMIT:raise ValueError('LAYOUT_LIMIT')
 return target

def folder():
 from utils import addon_data_dir
 root=Path(addon_data_dir())/'widget_adapter45';root.mkdir(mode=0o700,exist_ok=True)
 if root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
 return root

def save_private(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())

def prepare(target,skin_root,version):
 target=guard(target,skin_root,version);old=target.read_bytes();new,count=patch(old)
 if not count:return dict(code='NO_PATCH_NEEDED',count=0)
 token=uuid.uuid4().hex;root=folder();backup=root/(token+'.original.xml');candidate=root/(token+'.candidate.xml')
 save_private(backup,old);save_private(candidate,new)
 if sha(backup.read_bytes())!=sha(old) or sha(candidate.read_bytes())!=sha(new):raise ValueError('BACKUP_VERIFY_FAILED')
 plan=dict(code='PREPARED_NOT_APPLIED',target=str(target),skin_root=str(Path(skin_root).resolve()),version=version,backup=backup.name,candidate=candidate.name,before=sha(old),after=sha(new),count=count,mode=stat.S_IMODE(target.stat().st_mode),at=time.time())
 manifest=root/(token+'.json');save_private(manifest,json.dumps(plan).encode());plan['manifest']=manifest.name
 return plan

def replace(target,data,mode,expected):
 fd,temp=tempfile.mkstemp(prefix='.xcmate-widget45-',dir=str(target.parent))
 try:
  os.fchmod(fd,mode)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  if sha(target.read_bytes())!=expected:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
  os.replace(temp,target)
 finally:
  if os.path.exists(temp):os.unlink(temp)

def apply(plan,*,confirmed=False,restore=False):
 if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
 target=guard(plan['target'],plan['skin_root'],plan['version']);root=folder()
 if any(Path(plan[k]).name!=plan[k] for k in ('backup','candidate')):raise ValueError('UNSAFE_PLAN')
 old=(root/plan['backup']).read_bytes();new=(root/plan['candidate']).read_bytes()
 if sha(old)!=plan['before'] or sha(new)!=plan['after'] or patch(old)[0]!=new:raise ValueError('BACKUP_VERIFY_FAILED')
 expected=plan['after'] if restore else plan['before']
 if sha(target.read_bytes())!=expected:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
 content=old if restore else new
 replace(target,content,plan['mode'],expected)
 if sha(target.read_bytes())!=sha(content):raise ValueError('TARGET_VERIFY_FAILED')
 return dict(code='RESTORED' if restore else 'APPLIED',sha256=sha(content),count=plan['count'])

def latest():
 root=folder()
 for file in sorted(root.glob('*.json'),reverse=True):
  try:
   plan=json.loads(file.read_text());plan['manifest']=file.name
   if sha(Path(plan['target']).read_bytes())==plan['after']:return plan
  except (OSError,ValueError,KeyError):continue
 return None

def show():
 import xbmc,xbmcaddon,xbmcgui,xbmcvfs
 from menu_icons45 import select
 from widget_hooks45 import probe
 if xbmc.getCondVisibility('Player.HasMedia'):
  xbmcgui.Dialog().ok('XCMate','Adapter nur ohne laufende Wiedergabe prüfen.');return
 dialog=xbmcgui.Dialog()
 choice=select(dialog,'TEST – optionaler BINGIE-Widgetadapter',['Abbrechen','Anpassung prüfen und vorbereiten','Gesicherte Originaldatei wiederherstellen'],actions=['back','grid','shield'],preselect=0)
 if choice not in (1,2):return
 try:
  if choice==1:
   state=probe()
   if state.get('version')!='2.2.3' or not state.get('uri'):raise ValueError('UNVERIFIED_SKIN_VERSION')
   root=xbmcaddon.Addon('skin.titan.bingie.mod').getAddonInfo('path')
   plan=prepare(xbmcvfs.translatePath(state['uri']),root,state['version'])
   if plan['code']=='NO_PATCH_NEEDED':dialog.ok('XCMate','Vorhandene Aktualisierungsauslöser sind bereits nutzbar.');return
   message='Verifizierte lokale Sicherung erstellt. Nur '+str(plan['count'])+' XCMate-Widgetquellen im generierten BINGIE-Layout erhalten einen Aktualisierungsauslöser. Gespeicherte Widget-URLs bleiben erhalten. Danach wird der Skin neu geladen. Jetzt ausdrücklich aktivieren?'
  else:
   plan=latest()
   if not plan:dialog.ok('XCMate','Keine unverändert wiederherstellbare Anpassung gefunden.');return
   message='Die verifizierte Originaldatei wird nur bei exakt unverändertem Adapterstand wiederhergestellt. Danach wird der Skin neu geladen. Jetzt ausdrücklich wiederherstellen?'
  dialog.ok('TEST – optionale Anpassung',message)
  if select(dialog,'Ausdrückliche Freigabe',['Abbrechen','Ja, diese Anpassung freigeben'],actions=['back','shield'],preselect=0)!=1:return
  result=apply(plan,confirmed=True,restore=choice==2)
  from widget_hooks45 import prepare as prepare_bindings
  import widget_hooks45
  widget_hooks45._next=0;prepare_bindings()
  dialog.notification('XCMate',result['code'])
  xbmc.executebuiltin('ReloadSkin()')
 except (OSError,ValueError,PermissionError,KeyError) as exc:
  # Fixed codes only, never paths or XML contents in public logs/UI.
  code=str(exc) if str(exc) in ('UNVERIFIED_SKIN_VERSION','UNSAFE_TARGET','FOREIGN_TARGET','SKIN_METADATA_MISMATCH','LAYOUT_LIMIT','BACKUP_VERIFY_FAILED','TARGET_CHANGED_NO_OVERWRITE','TARGET_VERIFY_FAILED','UNSAFE_BACKUP_FOLDER','UNSAFE_PLAN','EXPLICIT_APPROVAL_REQUIRED') else type(exc).__name__
  dialog.ok('XCMate','Adapter nicht angewendet: '+code)
