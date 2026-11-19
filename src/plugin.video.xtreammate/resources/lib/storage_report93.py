"""Human-readable storage evidence; never adds overlapping categories together."""
from localization import tr

def amount(n):
    if type(n) not in (int,float):return tr(38733)
    for unit in ('B','KiB','MiB','GiB','TiB'):
        if abs(n)<1024 or unit=='TiB':return ('%.1f'%n if unit!='B' else str(int(n)))+' '+unit
        n/=1024

def report(value):
    if value is True:return tr(38757)+'\n\n'+tr(38755)
    if not isinstance(value,dict):return tr(38734)
    rows=value.get('categories')
    if isinstance(rows,list):
        lines=[tr(38735),'']
        for row in rows:
            label=tr(CATEGORIES.get(row.get('category'),38736))
            status=tr(38737 if row.get('complete') else 38738)
            if row.get('scan_status')=='UNREADABLE':status=tr(38739)
            elif row.get('complete') and not row.get('files'):status=tr(38740)
            lines.extend([label+' · '+status,
                          tr(38741,amount(row.get('bytes')),row.get('files',0))])
            v=row.get('volume',{})
            if v.get('error'):lines.append(tr(38742))
            else:
                lines.append(tr(38743,amount(v.get('available')),amount(v.get('total')),amount(v.get('reserve'))))
                lines.append(tr(38744,str(v.get('volume','?')),str(v.get('mount_key','?')),str(v.get('fs','?'))))
            if row.get('wal_bytes') is not None:lines.append(tr(38745,amount(row['wal_bytes']),amount(row.get('shm_bytes',0))))
            db=row.get('sqlite',{})
            if db.get('page_size'):
                lines.append(tr(38746,amount(db.get('freelist_count',0)*db['page_size'])))
            lines.append('')
        lines.append(tr(38747));return '\n'.join(lines)
    # Action receipts are intentionally not a raw dump of profile/paths/URLs.
    state=str(value.get('state') or value.get('code') or '')
    labels={'DONE':38757,'RUNNING':38781,'PAUSED':38758,'CANCELLED':38759,'ACTIVE_MIGRATION_PROTECTED':38780,'REFERENCE_PROOF_BLOCKED':38780}
    lines=[tr(38748),tr(38749,tr(labels.get(state,38733)))]
    if 'free_before' in value:
        lines.append(tr(38750,amount(value['free_before']),amount(value.get('free_after'))))
        lines.append(tr(38751,amount(value.get('observed_free_change'))))
    for item in value.get('databases',[]):
        lines.append(tr(38752,item.get('rows',0),amount(item.get('observed_file_delta'))))
    if isinstance(value.get('temp'),dict):lines.append(tr(38753,amount(value['temp'].get('bytes'))))
    if value.get('epg_cleanup93'):lines.append(tr(38754,amount(value['epg_cleanup93'].get('deleted_bytes',0))))
    lines.append(tr(38755));return '\n'.join(lines)

CATEGORIES={name:38760+i for i,name in enumerate(('COVERS','PROGRAMME_EXTERNAL','PROGRAMME_IMAGES','LOGOS','TEMP_ARTWORK','NORMALIZED_CACHE','GUIDE_BACKUPS','RESTORE_PLANS','EPG_DB','EPG_METADATA','PROGRAMME_DB','MIGRATION_JOURNAL','KODI_THUMBNAILS','KODI_DATABASES','KODI_PACKAGES','KODI_TEMP','SELECTED_NORMALIZED_CACHE','ACTIVE_MEDIA','ACTIVE_LOGOS','ACTIVE_PROGRAMMES'))}
