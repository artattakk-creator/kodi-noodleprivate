"""Repair only generated own directory consumers, not saved user shortcuts.

Literal original paths, order, labels, foreign consumers remain byte-identical.
The generated cache is privately backed up before a guarded atomic edit.
"""
import html,os,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs

def candidate(data,layout80=False):
    from widget_skin50 import spans,edit
    from navigation_builtin78 import uri
    from widget_hooks45 import ROUTES
    changes=[]
    if layout80:
        for node80 in spans(data):
            if node80['tag']!='include' or node80['attrs'].get('content')!='widget_base':continue
            params80={n['attrs'].get('name'):n['attrs'].get('value','') for n in node80['children'] if n['tag']=='param'}
            try:parsed80=urlsplit(uri(params80.get('widgetPath','')));kind80=ROUTES.get(parse_qs(parsed80.query).get('action',[''])[0])
            except ValueError:continue
            if kind80 not in ('vod','series') or params80.get('contentStyle')!='normal' or params80.get('widgetTarget')!='videos':continue
            start80,end80=node80['start'],node80['open'];old80=data[start80:end80]
            changes.append((start80,end80,old80.replace(b'content="widget_base"',b'content="XCMate80.MediaRow"',1)))
    for node in spans(data):
        tag=node['tag'];attrs=node['attrs']
        if tag=='content':raw=node['text']
        elif tag=='param' and attrs.get('name')=='widgetPath':raw=attrs.get('value','')
        else:continue
        try:url=uri(raw)
        except ValueError:continue
        query=parse_qs(urlsplit(url).query);actions=query.get('action',[])
        if len(actions)!=1 or actions[0] not in ROUTES:continue
        kind=ROUTES[actions[0]]
        # Existing declared hooks are respected, never doubled/replaced.
        if not any('$INFO[' in v or '$VAR[' in v for k in ('reload','xcmate_reload45','widgetreload') for v in query.get(k,[])):
            url+='&xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.'+kind+')]'
        if url==raw:continue
        if tag=='content':changes.append((node['open'],node['end'],html.escape(url).encode()))
        else:
            start,end=node['start'],node['open'];old=data[start:end]
            new,count=re.subn(rb'\bvalue="[^"]*"',lambda m:('value="'+html.escape(url,quote=True)+'"').encode(),old,count=1)
            if count!=1:raise ValueError('UNVERIFIED_TEMPLATE')
            changes.append((start,end,new))
    return edit(data,changes) if changes else data

def repair(profile,skin):
    from widget_transaction50 import read,replace,sha
    from home_inventory78 import snapshot
    target=Path(skin)/'xml/script-skinshortcuts-includes.xml'
    if not target.exists():return False
    original=read(target)
    marker80=Path(skin)/'xml/IncludesVariables.xml'
    changed=candidate(original,layout80=marker80.is_file() and b'XCMate80.Contract' in read(marker80))
    if changed==original:return False
    snapshot(profile,skin)
    replace(target,changed,sha(original),target.stat().st_mode&0o777)
    return True
