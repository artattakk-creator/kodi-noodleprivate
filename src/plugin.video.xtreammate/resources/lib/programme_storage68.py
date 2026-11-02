"""Read-only storage evidence. No retention, VACUUM, unlink or limit changes."""
import os,shutil,sqlite3
from urllib.parse import quote

def inspect(guide=None):
 from programme_index46 import path,MAX_BYTES
 filename=path(guide);db=None
 result=dict(code='NOT_CREATED',policy_bytes=MAX_BYTES,policy_max_pages=32768,
             page_count=None,page_size=None,freelist_count=None,db_bytes=0,wal_bytes=0,
             disk_free_bytes=None,write_probe='NOT_PERFORMED')
 try:
  parent=os.path.dirname(filename)
  result['disk_free_bytes']=shutil.disk_usage(parent).free
  from import_budget import RESERVE
  result['programme_db_reserve_bytes']=RESERVE
  from programme_art46 import root,limit
  result['programme_image_budget_bytes']=limit()
  try:
   from art_storage import capacity,explain
   cap=capacity(location=root())
   result['artwork_capacity']={k:cap[k] for k in ('free','total','reserve','budget','external','storage_availability') if k in cap}
   result['artwork_capacity']['reason']=explain(cap,3*1024*1024)
  except (OSError,ValueError,RuntimeError):result['artwork_capacity']=dict(reason='UNCONFIRMED')
  for suffix,field in (('','db_bytes'),('-wal','wal_bytes')):
   try:result[field]=os.stat(filename+suffix,follow_symlinks=False).st_size
   except FileNotFoundError:pass
  if not os.path.isfile(filename):return result
  if os.path.islink(filename):return dict(result,code='UNSAFE_PATH')
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.02)
  db.execute('PRAGMA query_only=ON')
  for field in ('page_count','page_size','freelist_count'):
   result[field]=int(db.execute('PRAGMA '+field).fetchone()[0])
  result['connection_max_page_count']=int(db.execute('PRAGMA max_page_count').fetchone()[0])
  result['logical_bytes']=result['page_count']*result['page_size']
  result['reusable_bytes']=result['freelist_count']*result['page_size']
  if result['disk_free_bytes']<65536:result['code']='FILESYSTEM_SPACE_LOW'
  elif result['logical_bytes']>=MAX_BYTES and result['reusable_bytes']<65536:result['code']='INTERNAL_DB_LIMIT'
  else:result['code']='READABLE_WRITE_CAPACITY_UNCONFIRMED'
  from programme_index46 import status
  result['last_writes']=status().get('last_write_failures',{}) if guide is None else {}
  return result
 except (OSError,sqlite3.Error,ValueError):return dict(result,code='STORAGE_DIAGNOSTIC_UNAVAILABLE')
 finally:
  if db is not None:db.close()
