"""Repair only generated own directory consumers, not saved user shortcuts.

Literal original paths, order, labels, foreign consumers remain byte-identical.
The generated cache is privately backed up before a guarded atomic edit.
"""
import html,os,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs

def candidate(data,layout80=False,six_rows=False):
    from widget_skin50 import spans,edit
    from navigation_builtin78 import uri
    uri=directory_uri89
    from widget_hooks45 import ROUTES
    changes=[]
    if layout80:
        for node80 in spans(data):
            if node80['tag']!='include' or node80['attrs'].get('content') not in ('widget_base','XCMate80.MediaRow'):continue
            params80={n['attrs'].get('name'):n['attrs'].get('value','') for n in node80['children'] if n['tag']=='param'}
            try:parsed80=urlsplit(uri(params80.get('widgetPath','')));kind80=ROUTES.get(parse_qs(parsed80.query).get('action',[''])[0])
            except ValueError:continue
            if kind80 not in ('vod','series') or params80.get('contentStyle')!='normal' or params80.get('widgetTarget')!='videos':continue
            if node80['attrs'].get('content')=='widget_base':
                start80,end80=node80['start'],node80['open'];old80=data[start80:end80]
                changes.append((start80,end80,old80.replace(b'content="widget_base"',b'content="XCMate80.MediaRow"',1)))
            declared80=params80.get('xcmateKind')
            if declared80 is not None and declared80!=kind80:raise ValueError('UNVERIFIED_MEDIA_KIND')
            if declared80 is None:
                changes.append((node80['end'],node80['end'],('<param name="xcmateKind" value="'+kind80+'" />').encode()))
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
        # Preserve legacy/global parameters, but add a private own-row hook.
        # XCMate must not pulse the shared BINGIE hook used by foreign rows.
        if not any('XCMate.Widget45.Reload.' in v for k in ('reload','xcmate_reload45','widgetreload') for v in query.get(k,[])):
            url+='&xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.'+kind+')]'
        if url==raw:continue
        if tag=='content':changes.append((node['open'],node['end'],html.escape(url).encode()))
        else:
            start,end=node['start'],node['open'];old=data[start:end]
            new,count=re.subn(rb'\bvalue="[^"]*"',lambda m:('value="'+html.escape(url,quote=True)+'"').encode(),old,count=1)
            if count!=1:raise ValueError('UNVERIFIED_TEMPLATE')
            changes.append((start,end,new))
    result=edit(data,changes) if changes else data
    return __import__('widget_six_consumer').patch(result) if layout80 and six_rows else result

def repair(profile,skin):
    from widget_transaction50 import read,replace,sha
    from home_inventory78 import snapshot
    target=Path(skin)/'xml/script-skinshortcuts-includes.xml'
    if not target.exists():return False
    original=read(target)
    marker80=Path(skin)/'xml/IncludesVariables.xml'
    markers=read(marker80) if marker80.is_file() else b''
    changed=candidate(original,layout80=b'XCMate80.Contract' in markers,six_rows=b'XCMate.SixRows.Contract' in markers)
    if changed==original:return False
    snapshot(profile,skin)
    replace(target,changed,sha(original),target.stat().st_mode&0o777)
    return True


def directory_uri89(value):
    """Allow declared Home properties and the exact generated clock parameter.

    Never relax the executable ActivateWindow/builtin boundary. These URLs
    are written as escaped XML, not executed as Python or Kodi commands.
    """
    from navigation_builtin78 import uri
    from widget_hooks45 import HOOK
    if isinstance(value,str) and value.startswith('plugin://plugin.video.xtreammate/'):
        checked=HOOK.sub('runtime89',value)
        # Kodi's generated Home directory URLs contain this exact clock
        # info-label token for cache invalidation. Normalize it only for
        # strict URI validation; preserve the actual URL byte-for-byte.
        checked,count=re.subn(r'(?<=[?&])clock50=\$INFO\[System\.Time\(hh:mm\)\](?=&|$)',
                             'clock50=runtime89',checked)
        if count>1:raise ValueError('INVALID_NAVIGATION')
        if '$INFO[' in checked:raise ValueError('INVALID_NAVIGATION')
        uri(checked)
        return value
    return uri(value)
