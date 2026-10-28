"""Opt-in four-file BINGIE 2.2.3 Home integration, with exact source guards.

No generated layout, Skin.String, existing binding or foreign skin is rewritten.
The native Skinshortcuts rebuild is requested only after an approved commit.
"""
import copy,html,json,re
from pathlib import Path
from xml.parsers import expat
import xml.etree.ElementTree as ET
from widget_transaction50 import read,sha
from widget_binding50 import xml,source
FILES=('xml/IncludesHomeWidgets.xml','xml/IncludesHomeBingie.xml','shortcuts/overrides.xml','shortcuts/template.xml')
OWN='ControlGroup(77777).HasFocus() + String.IsEqual(ListItem.Property(XCMate.Home50),true)'


def reference():
    return json.loads(read(Path(__file__).parents[1]/'bingie50_reference.json'))


def spans(data):
    parser=expat.ParserCreate();stack=[];nodes=[]
    def start(tag,attrs):
        index=parser.CurrentByteIndex;node=dict(tag=tag,attrs=attrs,start=index,open=data.index(b'>',index)+1,children=[],text='')
        if stack:stack[-1]['children'].append(node)
        nodes.append(node);stack.append(node)
    def end(tag):
        node=stack.pop();node['end']=parser.CurrentByteIndex
    def text(value):
        if stack:stack[-1]['text']+=value
    parser.StartElementHandler=start;parser.EndElementHandler=end;parser.CharacterDataHandler=text
    parser.StartDoctypeDeclHandler=lambda *a:(_ for _ in ()).throw(ValueError('UNSAFE_XML'))
    parser.Parse(data,True);return nodes


def edit(data,changes):
    for start,stop,value in sorted(changes,reverse=True):data=data[:start]+value+data[stop:]
    xml(data);return data


def patch(path,data):
    expected=reference()['files'][path]
    if sha(data) not in expected:raise ValueError('UNVERIFIED_SKIN_FILE')
    if path=='shortcuts/template.xml':
        matches=list(re.finditer(rb'<include content="widget_base"\s+condition="[^"]*">.*?</include>',data,re.S))
        if len(matches)!=8:raise ValueError('UNVERIFIED_TEMPLATE')
        changes=[]
        for number,m in enumerate(matches,1):
            raw=m.group();element=xml(raw);condition=element.get('condition')
            if '$PYTHON' not in condition or element.find("param[@name='widgetPath']").get('value')!='$SKINSHORTCUTS[widgetPath'+str(number)+']':raise ValueError('UNVERIFIED_TEMPLATE')
            var='$SKINSHORTCUTS[widgetPath'+str(number)+']'
            own='String.StartsWith('+var+',plugin://plugin.video.xtreammate/) + String.Contains('+var+',action=widget_live_start_group) + String.Contains('+var+',&home50=1&)'
            def changed(value,content=None):
                result=re.sub(rb'condition="[^"]*"',b'condition="'+html.escape(value,quote=True).encode()+b'"',raw,count=1)
                return result.replace(b'content="widget_base"',b'content="'+content+b'"',1) if content else result
            original=changed('['+condition+'] + !['+own+']')
            live=changed('['+condition+'] + ['+own+']',b'XCMate50.LiveRow')
            changes.append((m.start(),m.end(),original+b'\n'+live))
        return edit(data,changes)
    if path=='shortcuts/overrides.xml':
        root=ET.Element('includes')
        for kind,label in (('live','Live-TV'),('vod','Filme'),('series','Serien')):
            url=source(kind,'ACTIVE')
            url=url.replace('&pid=ACTIVE','')  # Native picker uses current active account; direct XCMate links pin pid.
            if kind!='live':url+='&clock50=$INFO[System.Time(hh:mm)]'
            e=ET.SubElement(root,'widget',label='XCMate · '+label,name=label,type={'live':'videos','vod':'movies','series':'tvshows'}[kind],target='videos',path=url)
            e.text='xcmate50.'+kind
        addition=b'\n'.join(ET.tostring(n,encoding='utf-8') for n in root)
        index=data.rfind(b'</overrides>')
        if index<0:raise ValueError('UNVERIFIED_OVERRIDES')
        return edit(data,[(index,index,addition+b'\n')])
    if path=='xml/IncludesHomeWidgets.xml':
        root=xml(read(Path(__file__).parents[1]/'bingie50/IncludesXCMate50.xml'))
        index=data.rfind(b'</includes>')
        return edit(data,[(index,index,b'\n'+b'\n'.join(ET.tostring(n,encoding='utf-8') for n in root)+b'\n')])
    if path=='xml/IncludesHomeBingie.xml':
        nodes=spans(data);parent=next(n for n in nodes if n['tag']=='control' and n['attrs'].get('id')=='9000')
        controls=[n for n in nodes if n['tag']=='control' and n['attrs'].get('type')=='group']
        details=[n for n in parent['children'] if n['tag']=='control' and any(c['tag']=='width' and c['text']=='1920' for c in n['children']) and any(c['tag']=='height' and c['text']=='525' for c in n['children'])]
        if len(details)!=1:raise ValueError('UNVERIFIED_HERO_REGION')
        frames=[n for n in controls if any(c['tag']=='include' and (c['attrs'].get('content','') or c['text']).startswith('Bingie_Screens_Fixed_Focus_Frame') for c in n['children'])]
        changes=[(parent['end'],parent['end'],b'\n<include>XCMate50.Hero</include>\n')]
        for n in details+frames:
            visible=[c for c in n['children'] if c['tag']=='visible']
            if visible:
                for v in visible:changes.append((v['open'],v['end'],html.escape('['+v['text']+'] + !['+OWN+']').encode()))
            else:changes.append((n['open'],n['open'],('<visible>!['+html.escape(OWN)+']</visible>').encode()))
        return edit(data,changes)
    raise ValueError('UNSAFE_TARGET')


def guard(skin):
    root=Path(skin).resolve();meta=xml(read(root/'addon.xml'))
    if meta.get('id')!='skin.titan.bingie.mod' or meta.get('version')!='2.2.3':raise ValueError('UNVERIFIED_SKIN_VERSION')
    fonts={e.findtext('name') for e in xml(read(root/'xml/Font.xml')).iter('font')}
    if not {'Reg18','Bold22','Bold40'}<=fonts:raise ValueError('UNVERIFIED_FONTS')
    paths=[root/name for name in FILES]
    if any(p.is_symlink() or root not in p.resolve().parents for p in paths):raise ValueError('UNSAFE_TARGET')
    return paths


def prepare(skin):
    from widget_transaction50 import prepare as transaction
    paths=guard(skin);changes=[(p,patch(name,read(p))) for name,p in zip(FILES,paths)]
    return transaction('skin',changes,dict(skin=str(Path(skin).resolve()),meta_sha=sha(read(Path(skin)/'addon.xml'))))


def apply(token,skin,*,confirmed=False,restore=False):
    from widget_transaction50 import load,folder,apply as transaction
    plan=load(token,'skin');paths=guard(skin)
    if plan['metadata']!=dict(skin=str(Path(skin).resolve()),meta_sha=sha(read(Path(skin)/'addon.xml'))):raise ValueError('SKIN_CHANGED')
    for i,name in enumerate(FILES):
        root=folder()/token
        if patch(name,read(root/('original.'+str(i))))!=read(root/('candidate.'+str(i))):raise ValueError('CANDIDATE_VERIFY_FAILED')
    return transaction(token,'skin',paths,confirmed=confirmed,restore=restore)


def applied(skin):
    from widget_transaction50 import folder,load
    try:
        paths=guard(skin)
        for p in folder().iterdir():
            if not p.is_dir() or len(p.name)!=32:continue
            try:
                plan=load(p.name,'skin')
                if [str(t.resolve()) for t in paths]==[v['target'] for v in plan['entries']] and all(sha(read(t))==v['after'] for t,v in zip(paths,plan['entries'])):return True
            except (OSError,ValueError,KeyError):pass
    except (OSError,ValueError,ET.ParseError):pass
    return False
