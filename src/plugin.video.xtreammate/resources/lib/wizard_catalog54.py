"""Restartable private group imports on the existing catalog's atomic heads.

No whole staging-DB deletion. Receipts prove schema/account/group, actual head,
row digest/count and age; only completed matching generations can be skipped.
"""
import hashlib,json,os,sqlite3,time
KINDS=('live','vod','series')
LABELS=dict(live='Live-TV',vod='Filme',series='Serien')


def digest_rows(db,pid,kind,cid,generation):
    h=hashlib.sha256();count=0
    for row in db.execute('SELECT sid,ordinal,title,search,added,payload FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=? ORDER BY sid',(pid,kind,cid,generation)):
        h.update(json.dumps(tuple(row),ensure_ascii=False,separators=(',',':')).encode());h.update(b'\n');count+=1
    return count,h.hexdigest()


def fingerprint(draft,kind,group):
    account=[draft.data.get(k,'') for k in ('type','xc_host','xc_user','stb_url','stb_mac','m3u_url')]
    return hashlib.sha256(json.dumps([1,account,kind,str(group['category_id']),str(group['category_name'])],sort_keys=True).encode()).hexdigest()


def open_db(draft):
    from library_index import connect
    db=connect(draft.index,write=True)
    db.execute('CREATE TABLE IF NOT EXISTS wizard_units54(pid TEXT,kind TEXT,cid TEXT,fingerprint TEXT,generation TEXT,rows INTEGER,digest TEXT,completed REAL,PRIMARY KEY(pid,kind,cid))');db.commit()
    db.execute('CREATE TABLE IF NOT EXISTS wizard_attempts54(pid TEXT,kind TEXT,cid TEXT,state TEXT,received INTEGER,updated REAL,PRIMARY KEY(pid,kind,cid))');db.commit()
    os.chmod(draft.index,0o600)
    if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':db.close();raise ValueError('staging catalogue requires verification')
    if getattr(draft,'_trusted_legacy54',False):adopt_legacy(db,draft)
    return db


def adopt_legacy(db,draft):
    """Owned .53 atomic heads prove complete import even if EPG later failed.

    Revalidate the exact account-owned generation, original selection, category
    label, age, every normalized payload and SQLite before recording a digest.
    No provider request and no published user database is changed.
    """
    for kind in KINDS:
        original=getattr(draft,'_legacy_selected54',{}).get(kind,set())
        for group in draft.categories[kind]:
            cid=str(group['category_id'])
            if cid not in draft.selected[kind] or cid not in original:continue
            if db.execute('SELECT 1 FROM wizard_units54 WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,cid)).fetchone():continue
            row=db.execute('SELECT h.generation,h.updated,g.title FROM heads h JOIN groups g USING(pid,kind,cid) WHERE h.pid=? AND h.kind=? AND h.cid=?',(draft.pid,kind,cid)).fetchone()
            if not row or row[2]!=str(group['category_name']) or not 0<=time.time()-row[1]<86400:continue
            valid=True
            for item in db.execute('SELECT sid,payload FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=?',(draft.pid,kind,cid,row[0])):
                try:value=json.loads(item[1])
                except (ValueError,TypeError):valid=False;break
                if not isinstance(value,dict) or value.get('sid')!=item[0] or value.get('category_id')!=cid or value.get('kind')!=kind or not value.get('name'):valid=False;break
            if not valid:continue
            count,sha=digest_rows(db,draft.pid,kind,cid,row[0])
            if count:
                with db:db.execute('INSERT INTO wizard_units54 VALUES(?,?,?,?,?,?,?,?)',(draft.pid,kind,cid,fingerprint(draft,kind,group),row[0],count,sha,row[1]))


def checkpoint(draft):
    session=getattr(draft,'resume53',None)
    if session and not session.checkpoint(draft,'groups'):raise OSError('DRAFT_CHECKPOINT_FAILED')


def valid(db,draft,kind,group):
    cid=str(group['category_id']);row=db.execute('SELECT fingerprint,generation,rows,digest,completed FROM wizard_units54 WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,cid)).fetchone()
    if row is None or row[0]!=fingerprint(draft,kind,group) or not 0<=time.time()-row[4]<86400:return None
    head=db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,cid)).fetchone()
    if head is not None and head[0]!=row[1]:return None
    count,sha=digest_rows(db,draft.pid,kind,cid,row[1])
    if (count,sha)!=(row[2],row[3]):return None
    if count and head is None:
        with db:db.execute('INSERT INTO heads VALUES(?,?,?,?,?)',(draft.pid,kind,cid,row[1],row[4]))
    return count


def scan(draft,cancel,status,include_epg=True):
    from library_index import import_group,Reader
    groups=[(kind,g) for kind in KINDS for g in draft.categories[kind] if str(g['category_id']) in draft.selected[kind]]
    if not groups:raise ValueError('select at least one category')
    draft.scanned=False;draft._scan_signature=None
    draft.report=dict(groups=len(groups),live=0,vod=0,series=0,epg=0,sources=[],warnings=[])
    db=open_db(draft)
    try:
        with db:
            for kind in KINDS:
                # Hide only deselected heads in this new portal's private stage.
                for cid, in db.execute('SELECT cid FROM heads WHERE pid=? AND kind=?',(draft.pid,kind)).fetchall():
                    if cid not in draft.selected[kind]:db.execute('DELETE FROM heads WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,cid))
                db.executemany('INSERT OR REPLACE INTO groups VALUES(?,?,?,?,?)',[(draft.pid,kind,str(g['category_id']),str(g['category_name']),i) for i,g in enumerate(draft.categories[kind])])
        totals={k:sum(kind==k for kind,g in groups) for k in KINDS};positions={k:0 for k in KINDS}
        for kind,group in groups:
            if cancel():raise InterruptedError('catalogue cancelled')
            positions[kind]+=1;cid=str(group['category_id']);prefix=LABELS[kind]+': Gruppe '+str(positions[kind])+' von '+str(totals[kind])+' · '+str(group['category_name'])[:160]
            retained=valid(db,draft,kind,group)
            if retained is not None:
                status(None,prefix+' · geprüft fortgesetzt · '+str(retained)+' Einträge');continue
            with db:db.execute('INSERT OR REPLACE INTO wizard_attempts54 VALUES(?,?,?,?,?,?)',(draft.pid,kind,cid,'RUNNING',0,time.time()))
            state={'done':False,'received':0}
            def rows():
                for row in draft.adapter.entries(kind,cid,cancel,allowed=draft.selected[kind]):
                    state['received']+=1;yield row
                state['done']=True
            def progress(received,stored,discarded):status(None,prefix+'\n'+str(received)+' Einträge verarbeitet · '+str(stored)+' gespeichert')
            status(None,prefix+' · Inhalte werden geladen')
            try:
                result=import_group(draft.pid,kind,cid,rows(),filename=draft.index,cancel=cancel,progress=progress,allowed=draft.selected[kind])
                touched=result['categories']
            except ValueError as error:
                if not state['done'] or state['received'] or str(error)!='category response contains no usable entries':raise
                if db.execute('SELECT 1 FROM heads WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,cid)).fetchone():raise
                touched=[];draft.report['warnings'].append(LABELS[kind]+': leere ausgewählte Kategorie')
            if cancel():raise InterruptedError('catalogue cancelled')
            for actual in set(touched)|{cid}:
                match=next((g for g in draft.categories[kind] if str(g['category_id'])==actual),None)
                if match is None:continue
                head=db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(draft.pid,kind,actual)).fetchone()
                generation=head[0] if head else ''
                count,sha=digest_rows(db,draft.pid,kind,actual,generation)
                with db:db.execute('INSERT OR REPLACE INTO wizard_units54 VALUES(?,?,?,?,?,?,?,?)',(draft.pid,kind,actual,fingerprint(draft,kind,match),generation,count,sha,time.time()))
            with db:db.execute('UPDATE wizard_attempts54 SET state=?,received=?,updated=? WHERE pid=? AND kind=? AND cid=?',('COMPLETE',state['received'],time.time(),draft.pid,kind,cid))
            checkpoint(draft);status(None,prefix+' fertig · '+str(state['received'])+' Einträge verarbeitet')
        reader=Reader(draft.pid,draft.index)
        for kind in KINDS:draft.report[kind]=reader.page(kind,limit=1)[1]
        if not sum(draft.report[k] for k in KINDS):raise ValueError('no selected content imported')
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('staging catalogue requires verification')
        if include_epg:draft._scan_epg(cancel,status)
        draft._scan_signature=draft._signature();draft.scanned=True;checkpoint(draft)
        status(100,'Katalog vollständig geprüft. Portal kann jetzt sicher gespeichert werden.')
        return draft.report
    except BaseException:
        with db:db.execute("UPDATE wizard_attempts54 SET state='PARTIAL',updated=? WHERE pid=? AND state='RUNNING'",(time.time(),draft.pid))
        raise
    finally:db.close()
