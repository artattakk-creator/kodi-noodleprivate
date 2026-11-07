"""Repair only generated own directory consumers, not saved user shortcuts.

Literal original paths, order, labels, foreign consumers remain byte-identical.
The generated cache is privately backed up before a guarded atomic edit.
"""
import html,os,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs

def candidate(data):
    from widget_skin50 import spans,edit
    from navigation_builtin78 import uri
    from widget_hooks45 import ROUTES
    changes=[]
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
    original=read(target);changed=candidate(original)
    if changed==original:return False
    snapshot(profile,skin)
    replace(target,changed,sha(original),target.stat().st_mode&0o777)
    return True
