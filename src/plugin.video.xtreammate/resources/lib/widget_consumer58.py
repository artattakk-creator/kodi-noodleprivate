"""Read-only saved-binding/generated-consumer/live-Home evidence.

No rebuild, binding edit, refresh, raw path/URL output, or pixel-success claim.
The actual active profile is selected by Kodi, never guessed from userdata.
"""
import ast
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
SKIN='skin.titan.bingie.mod'
ROUTES={'widget_live_start_group':'live','widget_recent_vod':'vod','widget_recent_series':'series'}


def identity(uri,pid):
    try:
        p=urlsplit(uri);q=parse_qs(p.query)
        if p.scheme!='plugin' or p.netloc!='plugin.video.xtreammate' or q.get('pid')!=[str(pid)]:return None
        action=q.get('action',[])
        return ROUTES.get(action[0]) if len(action)==1 else None
    except (ValueError,TypeError):return None


def bounded(path,limit):
    path=Path(path)
    if path.is_symlink():raise ValueError('UNSAFE_PROFILE')
    with path.open('rb') as stream:raw=stream.read(limit+1)
    if len(raw)>limit:raise ValueError('PROFILE_BUDGET')
    return raw


def inspect(profile,skin,generated,pid,probe=None):
    prop=Path(profile)/'addon_data/script.skinshortcuts'/(SKIN+'.properties')
    raw=bounded(prop,512*1024)
    rows=ast.literal_eval(raw.decode('utf-8'))
    if not isinstance(rows,list) or len(rows)>10000 or any(not isinstance(r,list) or len(r)!=4 or not all(isinstance(v,str) for v in r) for r in rows):raise ValueError('INVALID_PROPERTIES')
    text=bounded(generated,8*1024*1024)
    if b'<!DOCTYPE' in text or b'<!ENTITY' in text:raise ValueError('UNSAFE_LAYOUT')
    root=ET.fromstring(text)
    parents={child:node for node in root.iter() for child in node}
    consumers={kind:[] for kind in ROUTES.values()}
    for node in root.iter('content'):
        kind=identity(node.text or '',pid)
        if not kind:continue
        ancestor=parents.get(node)
        while ancestor is not None and not (ancestor.tag=='control' and ancestor.get('id','').isdigit()):ancestor=parents.get(ancestor)
        if ancestor is not None:consumers[kind].append(int(ancestor.get('id')))
    # Stock BINGIE 2.2.3 keeps DirectoryProvider in an external parametric
    # include. A literal <content> scan alone misses the real Home consumers.
    declarations={kind:0 for kind in ROUTES.values()}
    references=[n for n in root.iter('include') if n.get('content')=='widget_base']
    pipeline=False
    if references:
        try:
            layout=bounded(Path(skin)/'xml/IncludesHomeWidgets.xml',2*1024*1024)
            if b'<!DOCTYPE' in layout or b'<!ENTITY' in layout:raise ValueError('UNSAFE_LAYOUT')
            tree=ET.fromstring(layout)
            definitions={n.get('name'):n for n in tree.findall('include')}
            normal=definitions.get('widget_base_normal')
            content=definitions.get('widget_base_content_normal')
            base=definitions.get('widget_base')
            pipeline=bool(base is not None and normal is not None and content is not None
                and any(n.get('content')=='widget_base_normal' for n in base.iter('include'))
                and any(n.get('id')=='$PARAM[widgetid]' for n in normal.iter('control'))
                and any(n.get('content')=='widget_base_content_$PARAM[contentStyle]' for n in normal.iter('include'))
                and any(n.text=='$PARAM[widgetPath]' for n in content.iter('content')))
        except (OSError,ValueError,ET.ParseError):pass
    for node in references:
        params={n.get('name'):n.get('value',n.text or '') for n in node.findall('param')}
        kind=identity(params.get('widgetPath',''),pid)
        if not kind:continue
        declarations[kind]+=1
        cid=params.get('widgetid','')
        if pipeline and cid.isdigit() and params.get('contentStyle')=='normal' and params.get('widgetTarget')=='videos':consumers[kind].append(int(cid))
    result={}
    for kind in ROUTES.values():
        saved=[]
        for row in rows:
            if re.fullmatch(r'widgetPath(?:\.[1-7])?',row[2]) and identity(row[3],pid)==kind:
                suffix=row[2][len('widgetPath'):]
                values={r[2]:r[3] for r in rows if r[:2]==row[:2]}
                required=('widget','widgetName','widgetType','widgetTarget')
                saved.append(all(values.get(key+suffix) for key in required) and values.get('widgetType'+suffix)=={'live':'videos','vod':'movies','series':'tvshows'}[kind] and values.get('widgetTarget'+suffix)=='videos')
        ids=sorted(set(consumers[kind]));state=dict(binding='BINDING_PRESENT' if saved and all(saved) else 'BINDING_INVALID' if saved else 'BINDING_NOT_FOUND',saved_slots=len(saved),generated_consumers=len(ids),include_declarations=declarations[kind],consumer='SKIN_CONSUMER_UNVERIFIED',home='NOT_OBSERVED',pixels='NOT_TESTED')
        if saved and not ids and not declarations[kind]:state['consumer']='SKIN_CONSUMER_MISSING'
        elif ids:state['consumer']='GENERATED_CONSUMER_PRESENT'
        if ids and probe is not None:
            values=[probe(cid) for cid in ids]
            known=[v for v in values if v is not None]
            if known:
                state['home']='SKIN_CONSUMER_HIDDEN' if not any(v['visible'] for v in known) else 'HOME_ITEMS_PRESENT' if any(v['items']>0 and v['visible'] for v in known) else 'HOME_DIRECTORY_EMPTY'
                state['home_items']=sum(max(0,v['items']) for v in known)
        result[kind]=state
    return dict(code='READ_ONLY',profile_fingerprint=hashlib.sha256(str(Path(profile).resolve()).encode()).hexdigest()[:12],properties_sha256=hashlib.sha256(raw).hexdigest(),generated_sha256=hashlib.sha256(text).hexdigest(),kinds=result)


def status(pid):
    try:
        import xbmc,xbmcvfs
        if xbmc.getSkinDir()!=SKIN:return dict(code='UNSUPPORTED_SKIN')
        profile=xbmcvfs.translatePath('special://profile/')
        skin=xbmcvfs.translatePath('special://skin/')
        generated=next((Path(skin)/p/'script-skinshortcuts-includes.xml' for p in ('xml','1080i','720p') if (Path(skin)/p/'script-skinshortcuts-includes.xml').is_file()),None)
        if generated is None:return dict(code='NO_GENERATED_LAYOUT')
        # A diagnostic opened as a dialog must not evaluate Home controls in
        # that dialog's context. Runtime visibility remains unknown in that case.
        import xbmcgui
        probe=None
        if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999):
            def probe(cid):
                count=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
                if not str(count).isdigit():return None
                return dict(visible=bool(xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')')),items=int(count))
        return inspect(profile,skin,generated,pid,probe)
    except (OSError,ValueError,SyntaxError,RecursionError,ET.ParseError,ImportError,AttributeError,RuntimeError):return dict(code='PROFILE_UNVERIFIED')
