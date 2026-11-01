"""Read-only category pages on the media worker; explicit bounded job controls."""
import json,os,sqlite3,time
PAGE=40
def snapshot(portal,kind,offset=0):
 from library_index import connect
 from group_selection import _read,_state,enabled_ids
 state=_state(_read(),portal['id'],kind);db=None;groups={};evidence={};jobs={}
 try:
  db=connect(timeout=.05)
  if db is not None:
   db.execute('PRAGMA query_only=ON');deadline=time.monotonic()+.5;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
   groups={str(row['cid']):dict(row) for row in db.execute('SELECT cid,title,ordinal FROM groups WHERE pid=? AND kind=? ORDER BY ordinal,cid',(str(portal['id']),kind))}
   try:
    evidence={cid:json.loads(raw) for cid,raw in db.execute('SELECT cid,data FROM catalog_evidence65 WHERE pid=? AND kind=?',(str(portal['id']),kind)) if len(raw)<4096}
   except sqlite3.OperationalError:pass
  for cid in sorted((state or {}).get('known',set())):groups.setdefault(cid,dict(cid=cid,title=cid,ordinal=len(groups)))
  allowed=enabled_ids(portal['id'],kind,[dict(category_id=cid) for cid in groups])
  try:
   from catalog_delta import states
   jobs={v['cid']:v for v in states(portal['id'],kind)}
  except (OSError,ValueError,sqlite3.Error):pass
  rows=[];ordered=list(groups.values())
  for group in ordered[max(0,offset):max(0,offset)+PAGE]:
   cid=group['cid'];count=None;generation=None;updated=None
   if db is not None:
    try:
     count=db.execute('SELECT count(DISTINCT sid) FROM readable_titles WHERE pid=? AND kind=? AND cid=?',(str(portal['id']),kind,cid)).fetchone()[0]
     head=db.execute('SELECT generation,updated FROM heads WHERE pid=? AND kind=? AND cid=?',(str(portal['id']),kind,cid)).fetchone()
     if head:generation,updated=head
    except sqlite3.Error:pass
   proof=evidence.get(cid,{})
   rows.append(dict(cid=cid,name=str(group.get('title') or cid)[:256],enabled=bool(portal.get('include_'+kind,True) and cid in allowed),local_count=count,generation=generation,updated=updated,evidence=proof,job=jobs.get(cid,{})))
  return dict(rows=rows,total=len(ordered),offset=max(0,offset),code='READY' if db is not None else 'INDEX_MISSING')
 except (OSError,sqlite3.Error,ValueError):
  return dict(rows=[],total=len(groups),offset=max(0,offset),code='READ_UNAVAILABLE')
 finally:
  if db is not None:db.close()
def cancel_one(pid,kind,cid):
 from catalog_delta import _read,_save
 from profile_transaction import writing
 with writing(timeout=.1):
  value=_read()
  for row in value['jobs'].values():
   if (row['pid'],row['kind'],row['cid'])!=(str(pid),kind,str(cid)):continue
   if row['code']=='RUNNING':row['cancel_requested']=True
   elif row['code'] in ('PENDING','FAILED'):row.update(code='CANCELLED',attempts=3,updated=time.time())
  _save(value)
def acceptance66(row):
 if not row.get('enabled'):return 'DISABLED'
 proof=row.get('evidence',{});job=row.get('job',{});code=proof.get('code')
 if code in ('SOURCE_EMPTY','SOURCE_FILTERED'):return code
 if proof.get('transport')=='LOCAL_CACHE' or code=='CACHED':return 'CACHED'
 if job.get('code')=='FAILED' or code=='FAILED':return 'FAILED'
 expected=proof.get('stored');local=row.get('local_count')
 if proof.get('transport')=='REMOTE' and code=='READY' and type(expected) is int and type(local) is int:
  return 'INDEX_INCOMPLETE' if local<expected else 'READY'
 return job.get('code') if job.get('code') in ('PENDING','RUNNING','CANCELLED') else 'NOT_VERIFIED'

def details(row):
 proof=row['evidence'];source=proof.get('transport')
 remote=str(proof.get('stored',0)) if source=='REMOTE' and proof.get('code')=='READY' else '0' if source=='REMOTE' and proof.get('code')=='SOURCE_EMPTY' else 'nicht ermittelt'
 stamp=time.strftime('%d.%m.%Y %H:%M',time.localtime(row['updated'])) if row['updated'] else 'noch kein erfolgreicher Gruppenimport'
 count=str(row['local_count']) if row['local_count'] is not None else 'nicht lesbar'
 return '\n\n'.join([row['name'],'Prüfstatus: '+acceptance66(row),'Gruppe: '+('Aktiv' if row['enabled'] else 'Deaktiviert'),'Provider-Titelzahl: '+remote,'Lokal gespeichert: '+count,'Letzter erfolgreicher Import: '+stamp,'Letzte veröffentlichte Generation: '+str(row.get('generation') or 'unbekannt')[:32],'Quelle/Ergebnis: '+str(source or 'unbekannt')+' / '+str(proof.get('code','nicht geprüft')),'Empfangen / gespeichert / verworfen: '+str(proof.get('received','?'))+' / '+str(proof.get('stored','?'))+' / '+str(proof.get('discarded','?')),'Importauftrag: '+str(row['job'].get('code','kein Auftrag')),'Fehlergrund: '+str(proof.get('error_code','nicht ermittelt')),'Lokaler Cache oder letzter guter Bestand beweist keine aktuelle Provider-Verfügbarkeit. Bei SOURCE_FILTERED passt die Antwort nicht zur angeforderten Kategorie.'])
def manage(portal,kind,data):
 import xbmcgui
 from menu_icons45 import select
 from localization import tr
 dialog=xbmcgui.Dialog();rows=data['rows']
 if data['code']=='READ_UNAVAILABLE':dialog.ok('XCMate',tr(36710));return
 if not rows:dialog.ok('XCMate','Noch keine bekannten Gruppen. Bitte die gewünschten Gruppen zuerst in der vorhandenen Gruppenverwaltung auswählen.');return
 labels=[('Aktiv · ' if row['enabled'] else 'Deaktiviert · ')+row['name']+' · Lokal '+str(row['local_count'] if row['local_count'] is not None else '?') for row in rows]
 commands=[]
 if data['offset']:commands.append(('Vorherige Gruppen','previous'))
 if data['offset']+len(rows)<data['total']:commands.append(('Weitere Gruppen','next'))
 commands.append(('Zurück','back'))
 labels += [v[0] for v in commands]
 chosen=select(dialog,tr(36701)+' · '+str(data['offset']+1)+'–'+str(data['offset']+len(rows))+' / '+str(data['total']),labels,default='list')
 if not isinstance(chosen,int) or chosen<0:return
 if chosen>=len(rows):
  action=commands[chosen-len(rows)][1] if chosen-len(rows)<len(commands) else 'back'
  return max(0,data['offset']-PAGE) if action=='previous' else data['offset']+PAGE if action=='next' else None
 row=rows[chosen];dialog.textviewer(row['name'],details(row))
 action=select(dialog,tr(36701),[tr(36706) if row['enabled'] and portal.get('type')=='xtream' else 'Gruppe ist deaktiviert – Auswahl zuerst ausdrücklich ändern',tr(36707),tr(36708)],default='list')
 try:
  if action==0 and row['enabled'] and portal.get('type')=='xtream':
   from catalog_delta import request_many
   request_many(portal,kind,[row['cid']],retry=True,missing=True)
  elif action==1:cancel_one(portal['id'],kind,row['cid'])
 except (OSError,ValueError,sqlite3.Error):dialog.ok('XCMate',tr(36710))
 return data['offset'] if action in (0,1) else None
