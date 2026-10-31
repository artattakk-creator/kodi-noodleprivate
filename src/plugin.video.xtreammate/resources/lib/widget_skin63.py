"""Exact known .60/.62 adapter to full-bleed .63; no arbitrary skin rewrites."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

def candidate(path,data,previous):
    from widget_transaction50 import read,sha
    from widget_skin50 import spans,edit
    root=Path(__file__).parents[1]
    prior=json.loads(read(root/'bingie63_previous.json'))['files']
    if sha(data)!=prior.get(path):data=previous(path,data)
    if path!='xml/IncludesHomeWidgets.xml':return data
    definitions=ET.fromstring(read(root/'bingie63/IncludesXCMate63.xml'))
    nodes=spans(data);changes=[]
    # The LiveRow include is intentionally not replaced: keep accepted sizing,
    # focus, paging, navigation and native content/click behavior byte-identical.
    for definition in definitions:
        if definition.tag=='include' and definition.get('name')=='XCMate50.Hero':
            matches=[n for n in nodes if n['tag']=='include' and n['attrs'].get('name')=='XCMate50.Hero']
            if len(matches)!=1:raise ValueError('UNVERIFIED_HERO_REGION')
            old=matches[0];changes.append((old['start'],old['end']+len(b'</include>'),ET.tostring(definition,encoding='utf-8')))
        elif definition.tag=='variable':
            if any(n['tag']=='variable' and n['attrs'].get('name')==definition.get('name') for n in nodes):raise ValueError('UNVERIFIED_HERO_REGION')
            end=data.rfind(b'</includes>');changes.append((end,end,ET.tostring(definition,encoding='utf-8')+b'\n'))
    return edit(data,changes)

def previous_candidate(path,data):
    from widget_skin60 import candidate as old
    from widget_skin50 import legacy_patch60
    return old(path,data,legacy_patch60)

def previously_applied(skin):
    from widget_skin50 import FILES,guard
    from widget_transaction50 import folder,load,read,sha
    try:
        paths=guard(skin)
        for entry in folder().iterdir():
            if not entry.is_dir() or len(entry.name)!=32:continue
            try:
                plan=load(entry.name,'skin')
                state=json.loads(read(entry/'state.json')).get('state')
                if state!='APPLIED' or [str(p.resolve()) for p in paths]!=[e['target'] for e in plan['entries']]:continue
                if all(sha(read(p))==e['after'] and previous_candidate(name,read(entry/('original.'+str(i))))==read(p) for i,(name,p,e) in enumerate(zip(FILES,paths,plan['entries']))):return True
            except (OSError,ValueError,KeyError,TypeError):continue
    except (OSError,ValueError,ET.ParseError):pass
    return False
