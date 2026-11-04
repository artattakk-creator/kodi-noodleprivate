"""Category-specific cold evidence, never an unrelated group's oldest status."""
import time


def ensure_category(portal, kind, cid, reader):
    if not cid or portal.get('type') != 'xtream' or not hasattr(reader, '_query'): return
    heads=reader._query('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?', (str(portal['id']),kind,str(cid)))
    if heads: return
    # Older intact profiles can publish legacy title rows without V2 heads.
    # Their readable category is not a missing import and must not be rescanned.
    if reader._query('SELECT 1 AS present FROM titles WHERE pid=? AND kind=? AND cid=? LIMIT 1',
                     (str(portal['id']),kind,str(cid))):return
    from catalog_jobs73 import jobs
    if any(r['pid']==str(portal['id']) and kind in r['kinds'] and r.get('resume') for r in jobs()): return
    from catalog_delta import request_many
    # Completed EMPTY_SOURCE stays explicit until the user requests a retry.
    request_many(portal,kind,[str(cid)],missing=True)


def selected_status(pid, kind, cid, reader, rows):
    scoped=[dict(r) for r in rows if str(r.get('cid',''))==str(cid)]
    from catalog_jobs73 import jobs
    for job in jobs():
        if job['pid']!=str(pid) or kind not in job['kinds']: continue
        if job.get('units'):
            if not any(k==kind and str(g['category_id'])==str(cid) for k,g in job['units']): continue
        code=job['state']
        if job.get('units'):
            unit=next((i for i,(k,g) in enumerate(job['units']) if k==kind and str(g['category_id'])==str(cid)),None)
            if unit is not None and unit<job['cursor']:
                code='EMPTY_SOURCE' if [kind,str(cid)] in job.get('empty',[]) else 'READY'
            elif unit is not None and unit!=job['cursor'] and code=='RUNNING':code='WAITING'
        scoped.append(dict(cid=cid,code=code,updated=job['updated'],stored=job.get('group_stored',0),received=job.get('group_read',0)))
    scoped.sort(key=lambda r:r.get('updated',0),reverse=True)
    if cid and hasattr(reader,'_query'):
        heads=reader._query('SELECT updated FROM heads WHERE pid=? AND kind=? AND cid=?',(str(pid),kind,str(cid)))
        if heads and (not scoped or heads[0]['updated']>=scoped[0].get('updated',0)):
            return [dict(code='READY',updated=heads[0]['updated'],cid=cid)]
    return scoped[:1]
