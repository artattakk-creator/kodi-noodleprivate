"""Exact-scope, exact-edition local artwork admission during partial refresh.

No remote-URL lease extension. Only already verified files; no image/DB writes.
"""
import os,re

def retained(portal,kind,row,role,previous):
    from programme_assets47 import fingerprint
    from widget_cache79 import load,valid
    from widget_refs74 import revoked
    proof=previous.get('_provider80',{}).get(role,{})
    uri=proof.get('uri','')
    field='icon' if kind=='live' and role=='poster' else role
    if not uri or previous.get('art',{}).get(field)!=uri:return None
    # Reused IDs with changed editions must not inherit the old poster.
    if previous.get('info',{}).get('title')!=str(row.get('name','')):return None
    before=previous.get('info',{}).get('year');after=row.get('year')
    if before and after and str(before)!=str(after):return None
    record=load(portal,kind).get('refs',{}).get(str(row['sid']),{}).get(role,{})
    if record.get('file')==uri and proof.get('source')==fingerprint(record.get('source')) and not revoked(record.get('source')) and valid(record,record.get('source')):
        return dict(proof)
    match=re.fullmatch(r'render81-([0-9a-f]{64})-[0-9a-f]{64}\.(?:png|jpg)',os.path.basename(uri))
    if match:
        from render_cache81 import read
        record=read(match[1])
        if record and record['file']==uri:return dict(proof)
    return None

def apply(item,role,proof,kind):
    uri=proof['uri'];field='icon' if kind=='live' and role=='poster' else role
    item['art'][field]=uri;item.setdefault('_provider80',{})[role]=proof
    if role=='poster':
        item['art']['poster']=uri
        if kind=='live':item['props'].update({'XCMate.ProgrammeLogo46':uri,'channellogo':uri})
        else:
            item['art'].update(thumb=uri,icon=uri)
            if not item['art'].get('fanart'):item['art']['landscape']=uri
