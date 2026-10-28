"""One explicit Home slot in Skinshortcuts 2.1.0's existing .properties file.

Only already saved BINGIE profiles are accepted; defaults are never materialised
or guessed. Old rows remain byte-for-byte except the user's selected empty slot
or an explicitly selected own Live binding. No movie/series binding is replaced.
"""
import ast,copy,json,re
from pathlib import Path
from urllib.parse import urlencode,urlsplit,parse_qs
import xml.etree.ElementTree as ET
from widget_transaction50 import read,sha
SKIN='skin.titan.bingie.mod'
ROUTES={'live':'widget_live_start_group','vod':'widget_recent_vod','series':'widget_recent_series'}
CORE=('widget','widgetName','widgetType','widgetTarget','widgetPath')


def xml(data):
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:raise ValueError('UNSAFE_XML')
    return ET.fromstring(data)


def context(profile,skin):
    profile=Path(profile).resolve();skin=Path(skin).resolve()
    meta=xml(read(skin/'addon.xml'))
    if meta.get('id')!=SKIN or meta.get('version')!='2.2.3':raise ValueError('UNVERIFIED_SKIN_VERSION')
    overrides=xml(read(skin/'shortcuts/overrides.xml'))
    if overrides.find('doNotShareMenu') is None:raise ValueError('UNVERIFIED_MENU_SHARING')
    base=profile/'addon_data/script.skinshortcuts';menu=base/(SKIN+'-mainmenu.DATA.xml');prop=base/(SKIN+'.properties')
    if not menu.is_file() or not prop.is_file():raise ValueError('NO_SAVED_BINGIE_PROFILE')
    menu_data=read(menu)
    if len(menu_data)>256*1024:raise ValueError('PROFILE_BUDGET')
    tree=xml(menu_data)
    homes=[n for n in tree.findall('shortcut') if n.findtext('label')=='10000' and
           (n.findtext('action') or '').lower().replace(' ','').replace('"','')=='activatewindow(home,return)' and n.findtext('disabled')!='True']
    if len(homes)!=1:raise ValueError('HOME_ID_UNVERIFIED')
    data=read(prop)
    if len(data)>512*1024:raise ValueError('PROFILE_BUDGET')
    try:rows=ast.literal_eval(data.decode('utf-8'))
    except (SyntaxError,ValueError,RecursionError):raise ValueError('INVALID_PROPERTIES') from None
    if not isinstance(rows,list) or len(rows)>10000 or any(not isinstance(r,list) or len(r)!=4 or any(not isinstance(v,str) for v in r) for r in rows):raise ValueError('INVALID_PROPERTIES')
    keys=[tuple(r[:3]) for r in rows]
    if len(set(keys))!=len(keys):raise ValueError('DUPLICATE_PROPERTIES')
    if any(r[:3]==['mainmenu','10000','multiwidget'] and r[3] in ('single','single2') for r in rows):raise ValueError('SINGLE_WIDGET_HOME')
    # A saved Home widget proves the native profile already uses this labelID.
    if not any(r[:2]==['mainmenu','10000'] and r[2].startswith('widgetPath') and r[3] for r in rows):raise ValueError('HOME_ID_UNVERIFIED')
    return dict(profile=str(profile),skin=str(skin),target=str(prop),menu=str(menu),menu_sha=sha(menu_data),meta_sha=sha(read(skin/'addon.xml')),data=data,rows=rows)


def own(url,kind,pid):
    p=urlsplit(url);q=parse_qs(p.query)
    return p.scheme=='plugin' and p.netloc=='plugin.video.xtreammate' and q.get('action')==[ROUTES[kind]] and q.get('pid')==[str(pid)]


def legacy_live(url,pid):
    p=urlsplit(url);q=parse_qs(p.query)
    return p.scheme=='plugin' and p.netloc=='plugin.video.xtreammate' and q.get('pid')==[str(pid)] and q.get('action') in (['home_live'],['live_groups'],['widget_groups'])


def options(ctx,kind,pid):
    values={r[2]:r[3] for r in ctx['rows'] if r[:2]==['mainmenu','10000']};result=[]
    for slot in range(8):
        suffix='.'+str(slot) if slot else '';path=values.get('widgetPath'+suffix,'')
        if path and own(path,kind,pid):
            if kind!='live' or parse_qs(urlsplit(path).query).get('home50')==['1']:
                result.append(dict(slot=slot,state='ALREADY_LINKED'))
            else:result.append(dict(slot=slot,state='UPGRADE_OWN_LIVE'))
        elif kind=='live' and path and legacy_live(path,pid):result.append(dict(slot=slot,state='UPGRADE_OWN_LIVE'))
        elif not any(values.get(k+suffix,'') for k in CORE):result.append(dict(slot=slot,state='FREE'))
    return result


def source(kind,pid):
    if kind not in ROUTES or not pid or len(str(pid))>128:raise ValueError('INVALID_SOURCE')
    params=dict(action=ROUTES[kind],pid=str(pid))
    if kind=='live':params['home50']='1'
    url='plugin://plugin.video.xtreammate/?'+urlencode(params)
    url+='&reload=$INFO[Window(Home).Property(XCMate.Widget45.Reload.'+kind+')]'
    if kind=='live':url+='&clock50=$INFO[System.Time(hh:mm)]'
    return url


def candidate(ctx,kind,pid,slot,label):
    choice=next((v for v in options(ctx,kind,pid) if v['slot']==slot),None)
    if not choice:raise ValueError('OCCUPIED_SLOT')
    if choice['state']=='ALREADY_LINKED':return ctx['data'],choice
    suffix='.'+str(slot) if slot else ''
    desired=dict(widget='Addon',widgetName=label,widgetType={'live':'videos','vod':'movies','series':'tvshows'}[kind],widgetTarget='videos',widgetPath=source(kind,pid))
    if choice['state']=='UPGRADE_OWN_LIVE':
        previous=next((r[3] for r in ctx['rows'] if r[:3]==['mainmenu','10000','widgetName'+suffix]),'')
        if previous:desired['widgetName']=previous
    raw=ctx['data'];bom=3 if raw.startswith(b'\xef\xbb\xbf') else 0;body=raw[bom:];lines=body.splitlines(keepends=True)
    tree=ast.parse(body.decode('utf-8'),mode='eval');edits=[];found=set();expected=copy.deepcopy(ctx['rows'])
    for i,node in enumerate(tree.body.elts):
        row=ctx['rows'][i]
        for key,value in desired.items():
            if row[:3]==['mainmenu','10000',key+suffix]:
                literal=node.elts[3];start=sum(map(len,lines[:literal.lineno-1]))+literal.col_offset;stop=sum(map(len,lines[:literal.end_lineno-1]))+literal.end_col_offset
                edits.append((start,stop,repr(value).encode()));found.add(key);expected[i][3]=value
    extra=[['mainmenu','10000',key+suffix,value] for key,value in desired.items() if key not in found]
    end=len(body.rstrip())-1
    if body[end:end+1]!=b']':raise ValueError('INVALID_PROPERTIES')
    prefix=b'' if not ctx['rows'] or body[:end].rstrip().endswith(b',') else b','
    if extra:edits.append((end,end,prefix+b'\n'+repr(extra)[1:-1].encode()+b'\n'))
    for start,stop,value in sorted(edits,reverse=True):body=body[:start]+value+body[stop:]
    output=raw[:bom]+body
    if ast.literal_eval(output.decode('utf-8'))!=expected+extra:raise ValueError('CANDIDATE_VERIFY_FAILED')
    return output,choice


def prepare(ctx,kind,pid,slot,label):
    from widget_transaction50 import prepare as transaction
    data,choice=candidate(ctx,kind,pid,slot,label)
    if choice['state']=='ALREADY_LINKED':return dict(code='ALREADY_LINKED',slot=slot)
    if read(ctx['target'])!=ctx['data'] or sha(read(ctx['menu']))!=ctx['menu_sha']:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
    metadata={k:ctx[k] for k in ('profile','skin','menu','menu_sha','meta_sha')}
    metadata.update(kind=kind,pid=str(pid),slot=slot,label=label,state=choice['state'])
    return transaction('binding',[(ctx['target'],data)],metadata)


def apply(token,profile,skin,*,confirmed=False,restore=False):
    from widget_transaction50 import load,apply as transaction
    plan=load(token,'binding');ctx=context(profile,skin);m=plan['metadata']
    if any(ctx[k]!=m[k] for k in ('profile','skin','menu','menu_sha','meta_sha')):raise ValueError('PROFILE_CHANGED')
    root=__import__('widget_transaction50').folder()/token;old=read(root/'original.0');new=read(root/'candidate.0')
    verify=dict(ctx,data=old,rows=ast.literal_eval(old.decode('utf-8')))
    if candidate(verify,m['kind'],m['pid'],m['slot'],m['label'])[0]!=new:raise ValueError('CANDIDATE_VERIFY_FAILED')
    return transaction(token,'binding',[ctx['target']],confirmed=confirmed,restore=restore)
