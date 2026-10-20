"""Private playlist working copy and durable overrides, never the original.

Stream parsing uses bounded chunks/lines. Remote refresh atomically changes a
base generation; edits/custom stations survive. Source URLs live only here.
"""
import codecs
import html
import hashlib
import json
import os
import sqlite3
import time
import uuid
from urllib.parse import urlsplit,urlunsplit,urljoin,parse_qsl,urlencode
from contextlib import contextmanager

KINDS=('live','vod','series')
EDIT_FIELDS=('name','gid','logo','epg','enabled','ordinal','deleted')


def group_id(name): return hashlib.sha256(str(name).encode()).hexdigest()[:24]


def path(pid):
    from utils import addon_data_dir
    if not str(pid) or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in str(pid)):
        raise ValueError('invalid private playlist ID')
    folder=os.path.join(addon_data_dir(),'playlists');os.makedirs(folder,exist_ok=True)
    return os.path.join(folder,str(pid)+'.sqlite')


def connect(filename):
    db=sqlite3.connect(filename,timeout=.2);db.row_factory=sqlite3.Row
    db.executescript('''CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v TEXT);
      CREATE TABLE IF NOT EXISTS groups(gid TEXT PRIMARY KEY,name TEXT,kind TEXT);
      CREATE TABLE IF NOT EXISTS base(sid TEXT,generation TEXT,name TEXT,gid TEXT,url TEXT,
        logo TEXT,epg TEXT,ordinal INTEGER,attrs TEXT,PRIMARY KEY(generation,sid));
      CREATE INDEX IF NOT EXISTS m3u_group ON base(generation,gid,ordinal);
      CREATE INDEX IF NOT EXISTS m3u_url ON base(url);
      CREATE TABLE IF NOT EXISTS custom(sid TEXT PRIMARY KEY,name TEXT,gid TEXT,url TEXT,
        logo TEXT,epg TEXT,ordinal INTEGER,attrs TEXT);
      CREATE TABLE IF NOT EXISTS edits(sid TEXT PRIMARY KEY,name TEXT,gid TEXT,logo TEXT,
        epg TEXT,enabled INTEGER,ordinal INTEGER,deleted INTEGER);''')
    return db


@contextmanager
def source(uri,cancel=lambda:False):
    if urlsplit(uri).scheme in ('http','https'):
        from utils import http_stream
        with http_stream(uri,cancel=cancel) as stream: yield stream
    else:
        import xbmcvfs
        file=xbmcvfs.File(uri)
        class Reader:
            def read(self,n):
                if cancel(): raise InterruptedError('playlist cancelled')
                return bytes(file.readBytes(min(n,32768)))
        try: yield Reader()
        finally: file.close()


def lines(stream,cancel=lambda:False):
    raw=stream.read(32768)
    encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
    decoder=codecs.getincrementaldecoder(encoding)('surrogateescape' if encoding!='utf-16' else 'strict')
    pending=''
    while True:
        if cancel(): raise InterruptedError('playlist cancelled')
        pending+=decoder.decode(raw,final=not raw)
        while '\n' in pending:
            line,pending=pending.split('\n',1)
            if len(line)>262144: raise ValueError('playlist line budget exceeded')
            if encoding!='utf-16':
                binary=line.encode('utf-8','surrogateescape')
                try: line=binary.decode('utf-8')
                except UnicodeDecodeError: line=binary.decode('cp1252',errors='replace')
            yield line.rstrip('\r')
        if len(pending)>262144: raise ValueError('playlist line budget exceeded')
        if not raw:
            if pending:
                if encoding!='utf-16':
                    raw_line=pending.encode('utf-8','surrogateescape')
                    try: pending=raw_line.decode('utf-8')
                    except UnicodeDecodeError: pending=raw_line.decode('cp1252',errors='replace')
                yield pending.rstrip('\r')
            return
        raw=stream.read(32768)


def extinf(line):
    from iptv import _parse_attrs
    quoted=None
    for pos,c in enumerate(line):
        if c in ('"',"'"):
            if quoted==c: quoted=None
            elif quoted is None: quoted=c
        elif c==',' and quoted is None:
            attrs={k:html.unescape(v) for k,v in _parse_attrs(line[:pos]).items()};return attrs,line[pos+1:].strip()
    return {},''


def stable_url(uri):
    p=urlsplit(uri.partition('|')[0])
    query=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True)
           if k.lower() not in ('token','expires','auth','session')]
    return urlunsplit((p.scheme,p.netloc,p.path,urlencode(query),''))


def import_playlist(uri,filename,cancel=lambda:False,progress=None):
    from iptv import classify_group,_parse_attrs
    from import_budget import check_space
    generation=uuid.uuid4().hex;db=connect(filename);count=0;batch=[]
    # Duplicate occurrence numbers are held in SQLite, not an unbounded set.
    db.execute('CREATE TEMP TABLE seen(ident TEXT PRIMARY KEY,n INTEGER)')
    attrs={};name='';group='';header_epg=''
    def flush():
        if not batch: return
        check_space(filename,sum(len(r[4])+len(r[8]) for r in batch)*3)
        with db: db.executemany('INSERT INTO base VALUES(?,?,?,?,?,?,?,?,?)',batch)
        batch.clear()
        if progress: progress(count)
    try:
        with source(uri,cancel) as stream:
            for line in lines(stream,cancel):
                line=line.strip()
                if not line: continue
                if line.upper().startswith('#EXT-X-TARGETDURATION'):
                    raise ValueError('single HLS manifest is not an IPTV channel playlist')
                if line.upper().startswith('#EXTM3U'):
                    header=_parse_attrs(line);header_epg=header.get('x-tvg-url') or header.get('tvg-url') or ''
                elif line.upper().startswith('#EXTINF'):
                    attrs,name=extinf(line);group=attrs.get('group-title') or attrs.get('group') or ''
                elif line.upper().startswith('#EXTGRP:'): group=line[8:].strip()
                elif line.startswith('#'): continue
                else:
                    if '\x00' in line: raise ValueError('invalid playlist URI')
                    if not urlsplit(line.partition('|')[0]).scheme:
                        line=urljoin(uri,line) if urlsplit(uri).scheme in ('http','https') else os.path.normpath(os.path.join(os.path.dirname(uri),line))
                    if urlsplit(line.partition('|')[0]).scheme not in ('http','https','rtsp','rtmp','udp','rtp','smb','nfs','file','special',''):
                        attrs={};name='';continue
                    group=group or 'Unsortiert';gid=group_id(group)
                    kind={'movies':'vod'}.get(classify_group(group),classify_group(group))
                    ident=hashlib.sha256((attrs.get('tvg-id') or stable_url(line)).encode()).hexdigest()[:28]
                    seen=db.execute('SELECT n FROM seen WHERE ident=?',(ident,)).fetchone()
                    number=(seen[0]+1) if seen else 0
                    db.execute('INSERT OR REPLACE INTO seen VALUES(?,?)',(ident,number))
                    sid=ident+'-'+str(number)
                    db.execute('INSERT OR IGNORE INTO groups VALUES(?,?,?)',(gid,group,kind))
                    batch.append((sid,generation,name or attrs.get('tvg-name') or 'Unbenannter Eintrag',gid,line,
                        attrs.get('tvg-logo',''),attrs.get('tvg-id',''),count,json.dumps(attrs)))
                    count+=1;attrs={};name='';group=''
                    if len(batch)>=256: flush()
            flush()
        if not count: raise ValueError('empty playlist')
        if cancel(): raise InterruptedError('playlist cancelled')
        with db:
            db.execute("INSERT OR REPLACE INTO meta VALUES('active',?)",(generation,))
            db.execute("INSERT OR REPLACE INTO meta VALUES('updated',?)",(str(time.time()),))
            db.execute("INSERT OR REPLACE INTO meta VALUES('epg',?)",(header_epg,))
        # Old generations are no longer visible; bounded cleanup transactions.
        while True:
            with db: removed=db.execute('DELETE FROM base WHERE rowid IN (SELECT rowid FROM base WHERE generation!=? LIMIT 256)',(generation,)).rowcount
            if removed<256: break
        return dict(entries=count,epg_uri=header_epg)
    except BaseException:
        with db: db.execute('DELETE FROM base WHERE generation=?',(generation,))
        raise
    finally: db.close()


VIEW='''WITH b AS (SELECT sid,name,gid,url,logo,epg,ordinal,attrs FROM base
 WHERE generation=(SELECT v FROM meta WHERE k='active') UNION ALL SELECT * FROM custom)
 SELECT b.sid,coalesce(e.name,b.name) name,coalesce(e.gid,b.gid) gid,b.url,
 coalesce(e.logo,b.logo) logo,coalesce(e.epg,b.epg) epg,coalesce(e.ordinal,b.ordinal) ordinal,
 b.attrs,g.name group_name,g.kind,coalesce(e.enabled,1) enabled,coalesce(e.deleted,0) deleted
 FROM b LEFT JOIN edits e ON e.sid=b.sid JOIN groups g ON g.gid=coalesce(e.gid,b.gid)'''


def categories(filename,kind=None):
    db=connect(filename)
    try: return [dict(r) for r in db.execute('SELECT * FROM groups'+(' WHERE kind=?' if kind else '')+' ORDER BY name',(kind,) if kind else ())]
    finally: db.close()


def entries(filename,kind=None,gid=None,query='',include_disabled=False,offset=0,limit=None):
    db=connect(filename)
    sql='SELECT * FROM ('+VIEW+') WHERE deleted=0';args=[]
    if not include_disabled: sql+=' AND enabled=1'
    if kind: sql+=' AND kind=?';args.append(kind)
    if gid is not None: sql+=' AND gid=?';args.append(str(gid))
    if query: sql+=" AND name LIKE ? ESCAPE '\\'";args.append('%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
    try:
        sql+=' ORDER BY ordinal,sid'
        if limit is not None: sql+=' LIMIT ? OFFSET ?';args.extend((max(1,min(1000,int(limit))),max(0,int(offset))))
        cursor=db.execute(sql,args)
        while True:
            rows=cursor.fetchmany(100)
            if not rows: return
            yield from (dict(r) for r in rows)
    finally: db.close()


def get(filename,sid):
    db=connect(filename)
    try:
        row=db.execute('SELECT * FROM ('+VIEW+') WHERE sid=? AND deleted=0',(str(sid),)).fetchone()
        return dict(row) if row else None
    finally: db.close()


def edit(filename,sid,**values):
    if set(values)-set(EDIT_FIELDS): raise ValueError('unsupported playlist edit')
    if not get(filename,sid): raise ValueError('unknown playlist entry')
    for k,v in values.items():
        if isinstance(v,str) and ('\n' in v or '\r' in v or '\x00' in v or len(v)>8192): raise ValueError('invalid playlist field')
    if 'gid' in values and values['gid'] not in {g['gid'] for g in categories(filename)}: raise ValueError('unknown group')
    if any(k in values and values[k] not in (0,1,False,True) for k in ('enabled','deleted')): raise ValueError('invalid flag')
    db=connect(filename)
    try:
        with db:
            db.execute('INSERT OR IGNORE INTO edits(sid) VALUES(?)',(str(sid),))
            db.execute("INSERT OR REPLACE INTO meta VALUES('modified',?)",(str(time.time()),))
            db.execute('UPDATE edits SET '+','.join(k+'=?' for k in values)+' WHERE sid=?',list(values.values())+[str(sid)])
    finally: db.close()


def group(filename,name,kind='live',gid=None):
    if kind not in KINDS or not name.strip() or any(c in name for c in '\r\n\x00'): raise ValueError('invalid group')
    gid=gid or uuid.uuid4().hex
    db=connect(filename)
    try:
        with db:
            db.execute('INSERT OR REPLACE INTO groups VALUES(?,?,?)',(gid,name.strip(),kind))
            db.execute("INSERT OR REPLACE INTO meta VALUES('modified',?)",(str(time.time()),))
    finally: db.close()
    return gid


def add(filename,name,gid,url,logo='',epg=''):
    if not name.strip() or any(c in name+url+logo+epg for c in '\r\n\x00'): raise ValueError('invalid entry')
    if urlsplit(url.partition('|')[0]).scheme not in ('http','https','rtsp','rtmp','udp','rtp','smb','nfs','file','special'): raise ValueError('unsupported stream protocol')
    if gid not in {g['gid'] for g in categories(filename)}: raise ValueError('unknown group')
    sid='custom-'+uuid.uuid4().hex;db=connect(filename)
    try:
        with db:
            db.execute('INSERT INTO custom VALUES(?,?,?,?,?,?,?,?)',(sid,name,gid,url,logo,epg,2147483647,'{}'))
            db.execute("INSERT OR REPLACE INTO meta VALUES('modified',?)",(str(time.time()),))
    finally: db.close()
    return sid


def duplicates(filename):
    db=connect(filename)
    try:
        return [dict(r) for r in db.execute('SELECT url,min(name) name,count(*) n FROM ('+VIEW+') WHERE deleted=0 GROUP BY url HAVING count(*)>1')]
    finally: db.close()


def export_lines(filename,include_disabled=False):
    yield '#EXTM3U\n'
    def quoted(value): return html.escape(str(value),quote=True).replace('\r',' ').replace('\n',' ')
    for row in entries(filename,include_disabled=include_disabled):
        yield '#EXTINF:-1 tvg-id="{}" tvg-logo="{}" group-title="{}",{}\n'.format(
            quoted(row['epg']),quoted(row['logo']),quoted(row['group_name']),row['name'])
        yield row['url']+'\n'


def export(filename,target,allow_overwrite=False):
    import xbmcvfs
    if not target.lower().endswith(('.m3u','.m3u8')): raise ValueError('playlist export extension required')
    if xbmcvfs.exists(target) and not allow_overwrite: raise FileExistsError('explicit overwrite required')
    temporary=target+'.xcmate-'+uuid.uuid4().hex+'.tmp'
    try:
        file=xbmcvfs.File(temporary,'w')
        try:
            for text in export_lines(filename):
                if not file.write(text): raise OSError('playlist export failed')
        finally: file.close()
        # VFS rename must succeed without deleting the original target first.
        if not xbmcvfs.rename(temporary,target): raise OSError('atomic playlist export unavailable')
    finally:
        if xbmcvfs.exists(temporary): xbmcvfs.delete(temporary)


def reorder(filename,sid,step):
    """Renumber one group in bounded transactions; no list of all stations."""
    row=get(filename,sid)
    if not row: raise ValueError('unknown station')
    db=connect(filename)
    try:
        cursor=db.execute('SELECT sid FROM ('+VIEW+') WHERE gid=? AND deleted=0 ORDER BY ordinal,sid',(row['gid'],))
        batch=[];number=0
        while True:
            rows=cursor.fetchmany(256)
            if not rows: break
            for value in rows: batch.append((value['sid'],number));number+=1
            with db: db.executemany('INSERT INTO edits(sid,ordinal) VALUES(?,?) ON CONFLICT(sid) DO UPDATE SET ordinal=excluded.ordinal',batch)
            batch.clear()
        current=db.execute('SELECT ordinal FROM edits WHERE sid=?',(sid,)).fetchone()[0]
        neighbour=db.execute('SELECT e.sid FROM edits e JOIN ('+VIEW+') b ON b.sid=e.sid WHERE b.gid=? AND e.ordinal=? AND b.deleted=0',(row['gid'],current+step)).fetchone()
        if neighbour:
            with db:
                db.execute('UPDATE edits SET ordinal=? WHERE sid=?',(current+step,sid))
                db.execute('UPDATE edits SET ordinal=? WHERE sid=?',(current,neighbour[0]))
                db.execute("INSERT OR REPLACE INTO meta VALUES('modified',?)",(str(time.time()),))
    finally: db.close()
