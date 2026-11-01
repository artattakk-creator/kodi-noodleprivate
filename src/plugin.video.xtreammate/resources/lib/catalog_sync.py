"""Durable category intents: leases and process death never consume work."""
import sqlite3,time
from catalog_delta52 import serial_worker
def request(portal,kind,preferred='',priority=10,force=False):
 from library_index import request_sync
 try:request_sync(portal,kind,preferred,priority,force)
 except (OSError,RuntimeError,sqlite3.Error) as exc:
  from utils import warn
  from artwork_db import classify
  warn('Catalogue request: code='+classify(exc)+' sqlite='+str(getattr(exc,'sqlite_errorcode',0)&255)+' error='+type(exc).__name__)
@serial_worker
def run_next(cancel=lambda:False):
 from library_index import connect,sync_kind
 from portals import get_by_id
 from xtream import XtreamClient
 if cancel():return False
 db=connect(write=True)
 try:
  row=db.execute('SELECT r.* FROM sync_requests r LEFT JOIN sync_leases l USING(pid,kind) WHERE l.pid IS NULL OR l.until<=? ORDER BY r.priority,r.requested LIMIT 1',(time.time(),)).fetchone()
  if not row:return False
  job=dict(row)  # Keep the durable intent while network/import work is running.
 finally:db.close()
 portal=get_by_id(job['pid']);more=False
 if portal and portal.get('enabled',True) and portal.get('type') in ('xtream','m3u','stb'):
  if portal['type']=='xtream':
   client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
   more=sync_kind(portal,client,job['kind'],job['preferred'],bool(job['force']),cancel,max_groups=1,requested_at=job['requested'])
  else:
   from source_sync import sync_kind as sync_source
   sync_source(portal,job['kind'],bool(job['force']),cancel,job['requested'])
 if not more and not cancel():
  db=connect(write=True)
  try:
   with db:db.execute('DELETE FROM sync_requests WHERE pid=? AND kind=? AND priority=? AND preferred=? AND force=? AND requested=?',tuple(job[k] for k in ('pid','kind','priority','preferred','force','requested')))
  finally:db.close()
 return True
