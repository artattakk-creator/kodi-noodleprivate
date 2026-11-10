"""Private read-only inventory of every saved widget, including foreign addons.

No repair/default generation and no URI output in public diagnostics. Unsupported
properties fail closed before any skin write. Existing backup contains raw bytes.
"""
import ast,hashlib,json
from pathlib import Path
MAX=4*1024*1024

def widgets(profile):
 root=Path(profile)/'addon_data/script.skinshortcuts'
 if root.is_symlink():raise ValueError('SKIN_MIGRATION_BLOCKED')
 result=[]
 if not root.exists():return result
 for path in sorted(root.glob('*.properties')):
  if path.is_symlink() or path.stat().st_size>MAX:raise ValueError('SKIN_MIGRATION_BLOCKED')
  try:rows=ast.literal_eval(path.read_text(encoding='utf-8'))
  except (ValueError,SyntaxError,RecursionError):raise ValueError('SKIN_MIGRATION_BLOCKED') from None
  if not isinstance(rows,list) or len(rows)>16000:raise ValueError('SKIN_MIGRATION_BLOCKED')
  groups={}
  for position,row in enumerate(rows):
   if not isinstance(row,(list,tuple)) or len(row)!=4 or not all(isinstance(v,str) for v in row):raise ValueError('SKIN_MIGRATION_BLOCKED')
   menu,ident,name,value=row
   if not name.startswith('widget'):continue
   prefix,_,suffix=name.partition('.')
   key=(menu,ident,suffix);record=groups.setdefault(key,dict(file=path.name,menu=menu,identity=ident,slot=suffix,order=position,properties=[]))
   record['properties'].append([name,value])
  for record in groups.values():
   values={name.partition('.')[0]:value for name,value in record['properties']};path=values.get('widgetPath','')
   if not path:continue
   record.update(name=values.get('widgetName',''),path=path,external=not path.startswith('plugin://plugin.video.xtreammate/'))
   result.append(record)
 return result

def fingerprint(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def collect(profile,skin):
 from widget_skin78 import FILES
 from widget_transaction50 import read,sha
 skin=Path(skin);rows=widgets(profile)
 return dict(format=1,profile=str(Path(profile).resolve()),widgets=rows,sha256=fingerprint(rows),skin={name:sha(read(skin/name)) for name in ('addon.xml',)+FILES})
def compare(profile,receipt):
 if receipt.get('profile')!=str(Path(profile).resolve()):raise ValueError('SKIN_MIGRATION_BLOCKED')
 current=widgets(profile)
 if fingerprint(current)!=receipt.get('sha256') or current!=receipt.get('widgets'):raise ValueError('SKIN_MIGRATION_BLOCKED')
 return True
