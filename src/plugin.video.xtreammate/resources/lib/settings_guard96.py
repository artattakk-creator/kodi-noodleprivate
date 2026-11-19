"""Bounded native Kodi-settings health, verified writes and explicit recovery.

Only sanitized codes escape this adapter. Backups stay private in the profile;
no tokens/paths/settings payloads are logged or sent to diagnostics.
"""
import hashlib,os,stat,tempfile,threading,time,xml.etree.ElementTree as E
_lock=threading.RLock();_cache={};_defaults={};LIMIT=262144

class SettingsError(OSError):
 def __init__(self,code):self.code=code;super().__init__(code)

def path():
 import xbmcvfs
 return xbmcvfs.translatePath('special://profile/addon_data/plugin.video.xtreammate/settings.xml')

def parse(raw):
 if len(raw)>LIMIT or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise SettingsError('SETTINGS_XML_INVALID')
 try:root=E.fromstring(raw)
 except (E.ParseError,UnicodeError):raise SettingsError('SETTINGS_XML_INVALID') from None
 if root.tag!='settings':raise SettingsError('SETTINGS_XML_INVALID')
 values={};off=set()
 for n in root.iter('setting'):
  key=n.get('id')
  if not key or key in values:raise SettingsError('SETTINGS_XML_INVALID')
  values[key]=n.text if n.text is not None else n.get('value','')
  if n.get('default')!='true' and values[key].strip().lower()=='false':off.add(key)
 return values,off

def snapshot():
 filename=path()
 try:
  st=os.stat(filename,follow_symlinks=False)
  if not stat.S_ISREG(st.st_mode):raise SettingsError('SETTINGS_UNREADABLE')
  key=(filename,st.st_dev,st.st_ino,st.st_mtime_ns,st.st_size)
  with _lock:
   if key in _cache:return dict(_cache[key])
  with open(filename,'rb') as stream:raw=stream.read(LIMIT+1)
  values,off=parse(raw);result=dict(code='READY',values=values,explicit_off=off,revision=hashlib.sha256(raw).hexdigest())
  with _lock:
   _cache[key]=result
   while len(_cache)>8:_cache.pop(next(iter(_cache)))
  return dict(result)
 except FileNotFoundError:return dict(code='NOT_CREATED',values={},explicit_off=set())
 except SettingsError as exc:return dict(code=exc.code,values={},explicit_off=set())
 except OSError:return dict(code='SETTINGS_UNREADABLE',values={},explicit_off=set())

def require():
 result=snapshot()
 if result['code'] not in ('READY','NOT_CREATED'):raise SettingsError(result['code'])
 return result

def rebuild_pending():
 from settings_rebuild99 import pending
 return pending(os.path.dirname(path()))

def value(key,addon,default=''):
 state=require()
 if key in state['values']:return state['values'][key] or default
 if state['code']=='READY':
  try:
   resource=os.path.join(addon.getAddonInfo('path'),'resources/settings.xml')
   if resource not in _defaults:
    nodes=E.parse(resource).getroot().iter('setting')
    _defaults[resource]={n.get('id'):n.get('default','') for n in nodes}
   return _defaults[resource].get(key,default)
  except (OSError,TypeError,E.ParseError,AttributeError):return default
 try:return addon.getSetting(key) or default
 except (RuntimeError,OSError):raise SettingsError('SETTINGS_API_UNAVAILABLE') from None

def _atomic(filename,raw):
 folder=os.path.dirname(filename);os.makedirs(folder,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.settings96-',dir=folder)
 try:
  os.fchmod(fd,0o600)
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  with open(tmp,'rb') as f:
   if f.read(LIMIT+1)!=raw:raise SettingsError('SETTINGS_READBACK_FAILED')
  os.replace(tmp,filename)
  d=os.open(folder,os.O_RDONLY)
  try:os.fsync(d)
  finally:os.close(d)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def backup():
 require();filename=path()
 if not os.path.exists(filename):return False
 with open(filename,'rb') as f:raw=f.read(LIMIT+1)
 parse(raw);_atomic(os.path.join(os.path.dirname(filename),'settings96.lastgood.xml'),raw);return True

def write(changes,addon=None):
 """Explicit edits only. Never acknowledge a RAM-only setSetting result."""
 import xbmcaddon
 from profile_transaction import writing
 addon=addon or xbmcaddon.Addon()
 with writing():
  if rebuild_pending():raise SettingsError('RESTART_REQUIRED')
  before=require();backup()
  try:
   with open(path(),'rb') as f:before_raw=f.read(LIMIT+1)
  except FileNotFoundError:before_raw=None
  try:
   return _write_values(changes,addon,before)
  except (SettingsError,OSError,RuntimeError):
   # This is rollback of an explicitly requested edit, not automatic repair
   # of an unknown profile. Preserve the rejected bytes before restoration.
   if before_raw is not None:
    if os.path.isfile(path()) and not os.path.islink(path()):os.replace(path(),os.path.join(os.path.dirname(path()),'settings96.rejected.'+str(time.time_ns())+'.xml'))
    _atomic(path(),before_raw)
    with _lock:_cache.clear()
   raise

def _write_values(changes,addon,before):
  for key,v in changes.items():
   if not isinstance(key,str) or not isinstance(v,str):raise SettingsError('SETTINGS_VALUE_INVALID')
   addon.setSetting(key,v)
  with _lock:_cache.clear()
  after=require()
  if any(after['values'].get(k)!=v for k,v in changes.items()):raise SettingsError('SETTINGS_READBACK_FAILED')
  # Native Kodi can append default-valued entries. Existing explicit token and
  # account values must survive; only the requested IDs are allowed to change.
  if any(k not in changes and after['values'].get(k)!=v for k,v in before['values'].items()):raise SettingsError('SETTINGS_UNRELATED_CHANGED')
  backup();return after['revision']

def repair():
 """UI-confirmed recovery from our last validated copy; preserve corrupt bytes."""
 from profile_transaction import writing
 with writing():
  if rebuild_pending():raise SettingsError('RESTART_REQUIRED')
  filename=path();folder=os.path.dirname(filename);saved=os.path.join(folder,'settings96.lastgood.xml')
  try:
   if os.path.islink(saved) or os.path.islink(filename):raise SettingsError('SETTINGS_UNREADABLE')
   with open(saved,'rb') as f:raw=f.read(LIMIT+1)
   parse(raw)
  except FileNotFoundError:raise SettingsError('SETTINGS_BACKUP_MISSING') from None
  if os.path.isfile(filename):
   with open(filename,'rb') as f:old=f.read(LIMIT+1)
   if len(old)>LIMIT:raise SettingsError('SETTINGS_REPAIR_REQUIRES_EXTERNAL_BACKUP')
   _atomic(os.path.join(folder,'settings96.corrupt.'+str(time.time_ns())+'.xml'),old)
  _atomic(filename,raw)
  with _lock:_cache.clear()
  state=require()
  if state.get('revision')!=hashlib.sha256(raw).hexdigest():raise SettingsError('SETTINGS_READBACK_FAILED')
  return state['revision']
