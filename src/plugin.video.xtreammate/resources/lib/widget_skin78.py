"""Complete BINGIE include graph, explicit variable registry and runtime gate.

Only own reviewed adapter nodes change; saved rows/settings are not targets.
An installed file contract never implies that Kodi reloaded its controls.
"""
from pathlib import Path
import xml.etree.ElementTree as E
from widget_transaction50 import read,sha
FILES=('xml/IncludesHomeWidgets.xml','xml/IncludesHomeBingie.xml','shortcuts/overrides.xml','shortcuts/template.xml','xml/IncludesBingie.xml','xml/IncludesVariables.xml','xml/Includes.xml','xml/Home.xml')
CONTRACT='XCMate78.Contract'
READY='XCMate78_READY'

def supported(skin):
    return all((Path(skin)/name).is_file() for name in FILES)

def _nodes(data,tag):
    from widget_skin50 import spans
    return [n for n in spans(data) if n['tag']==tag]

def parse(data):
    # Stock BINGIE's variable registry contains bare '&' in labels. Kodi's
    # TinyXML reader accepts those. Normalize only the parser's view; preserve
    # every original byte in the actual skin and its backup.
    import re
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:raise ValueError('UNSAFE_XML')
    view=re.sub(rb'&(?!amp;|lt;|gt;|apos;|quot;|#[0-9]+;|#x[0-9A-Fa-f]+;)',b'&amp;',data)
    return E.fromstring(view)

def _append(data,closing,addition):
    at=data.rfind(closing)
    if at<0:raise ValueError('UNVERIFIED_SKIN_FILE')
    result=data[:at]+addition+data[at:];parse(result);return result

def build(original):
    if b'XCMate88.Contract' in original['xml/IncludesVariables.xml']:
        __import__('widget_skin88').verify(original);return __import__('widget_skin90').upgrade(original)
    from widget_skin77 import candidate as previous
    from widget_skin75 import navigation_candidate
    from widget_skin50 import edit
    if CONTRACT.encode() in original['xml/IncludesVariables.xml']:
        verify(original);return __import__('widget_skin90').upgrade(__import__('widget_skin88').upgrade(__import__('widget_skin87').upgrade(__import__('widget_skin81').upgrade(__import__('widget_skin80').upgrade(original)))))
    result=dict(original)
    for name in FILES[:4]:result[name]=previous(name,original[name])
    result[FILES[4]]=navigation_candidate(original[FILES[4]])
    variables=[]
    for name in (FILES[0],FILES[4]):
        data=result[name];changes=[]
        for node in _nodes(data,'variable'):
            if not node['attrs'].get('name','').startswith(('XCMate63.','XCMate75.')):continue
            end=node['end']+len(b'</variable>');variables.append(data[node['start']:end]);changes.append((node['start'],end,b''))
        result[name]=edit(data,changes)
    names=[E.fromstring(raw).get('name') for raw in variables]
    if len(names)!=16 or len(set(names))!=16:raise ValueError('UNVERIFIED_VARIABLES')
    existing={n.get('name') for n in parse(result[FILES[5]]).findall('variable')}
    if existing.intersection(names):raise ValueError('UNVERIFIED_VARIABLES')
    registry=b'\n'.join(variables)+b'\n<variable name="XCMate78.Contract"><value>XCMate78_READY</value></variable>\n'
    result[FILES[5]]=_append(result[FILES[5]],b'</includes>',registry)
    # Explicit root include is independent of SkinShortcuts and menu focus.
    marker=b'<include name="XCMate78.Runtime"><control type="label" id="296780"><left>-100</left><top>-100</top><width>1</width><height>1</height><label>$VAR[XCMate78.Contract]</label></control></include>\n'
    result[FILES[0]]=_append(result[FILES[0]],b'</includes>',marker)
    data=result[FILES[0]];changes=[]
    for node in _nodes(data,'control'):
        for child in node['children']:
            if child['tag']=='label' and child['text'] in ('$VAR[XCMate75.Title]','$VAR[XCMate75.Description]'):
                ident='296781' if child['text'].endswith('Title]') else '296782'
                if 'id' in node['attrs']:raise ValueError('UNVERIFIED_HERO_REGION')
                changes.append((node['start'],node['open'],data[node['start']:node['open']-1]+(' id="'+ident+'">').encode()))
    result[FILES[0]]=edit(data,changes)
    home=result[FILES[7]]
    if b'XCMate78.Runtime' in home:raise ValueError('UNVERIFIED_HOME_HOOK')
    result[FILES[7]]=_append(home,b'</controls>',b'<include>XCMate78.Runtime</include>\n')
    result=__import__('widget_skin81').upgrade(__import__('widget_skin80').upgrade(result))
    verify(result)
    return __import__('widget_skin90').upgrade(__import__('widget_skin88').upgrade(__import__('widget_skin87').upgrade(result)))

def build103(original):
    from widget_skin103 import MARKER, VARIABLES, upgrade
    return upgrade(original if MARKER in original[VARIABLES] else build(original))

def verify(files):
    roots={name:parse(files[name]) for name in FILES}
    registry=roots[FILES[5]];definitions={n.get('name') for n in registry.findall('variable')}
    referenced=set()
    import re
    for name in (FILES[0],FILES[1],FILES[4]):
        referenced.update(re.findall(r'\$VAR\[(XCMate(?:63|75)\.[^\]]+)\]',files[name].decode()))
    if not referenced<=definitions or registry.findtext("variable[@name='XCMate78.Contract']/value")!=READY:raise ValueError('UNVERIFIED_VARIABLES')
    includes=[n.get('file') for n in roots[FILES[6]].findall('include') if n.get('file')]
    required=('IncludesVariables.xml','IncludesBingie.xml','IncludesHomeWidgets.xml','IncludesHomeBingie.xml')
    if any(includes.count(name)!=1 for name in required):raise ValueError('UNVERIFIED_INCLUDE_GRAPH')
    if includes.index('IncludesVariables.xml')>min(includes.index(n) for n in required[1:]):raise ValueError('UNVERIFIED_INCLUDE_GRAPH')
    home=roots[FILES[7]]
    if home.find("controls/include[.='XCMate78.Runtime']") is None or home.find("controls/include[.='HomeBingie']") is None:raise ValueError('UNVERIFIED_HOME_HOOK')
    own=roots[FILES[0]]
    ids=[n.get('id') for n in own.findall('.//control')]
    for ident in ('296301','296302','296751','296780','296781','296782'):
        if ids.count(ident)!=1:raise ValueError('UNVERIFIED_HERO_REGION')
    parent=roots[FILES[1]].find(".//control[@id='9000']")
    if parent is None or parent.find("include[.='XCMate50.Hero']") is None:raise ValueError('UNVERIFIED_HOME_HOOK')
    return True

def installed(skin):
    try:
        from widget_skin103 import MARKER, VARIABLES, upgrade
        files88={name:read(Path(skin)/name) for name in FILES};verify(files88)
        if MARKER in files88[VARIABLES]:return upgrade(files88)==files88
        if __import__('widget_skin88').previous_owned(skin):return False
        if not __import__('widget_skin90').verify(files88):return False
        return True
    except (OSError,ValueError,E.ParseError,KeyError):return False

def previous_owned(skin):
    """Only exact released .77 own hooks qualify for authorized repair."""
    if __import__('widget_skin90').previous_owned(skin):return True
    from widget_skin77 import known,NEW,OLD,BLUE,RED
    reference=known()
    try:
        for name in FILES[:4]:
            raw=read(Path(skin)/name)
            if name=='xml/IncludesHomeBingie.xml':raw=raw.replace(NEW,OLD).replace(BLUE,RED)
            if sha(raw)!=reference['current'][name]:return False
        return sha(read(Path(skin)/FILES[4]))==reference['navigation']
    except (OSError,ValueError,KeyError):return False

def runtime():
    import xbmc,xbmcgui
    if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return dict(code='HOME_NOT_ACTIVE')
    try:
        window=xbmcgui.Window(10000)
        if xbmc.getInfoLabel('Control.GetLabel(296780)')!=READY:return dict(code='VARIABLES_NOT_LOADED')
        from home_runtime77 import control
        ids=(296301,296302,296751,296780,296781,296782)
        if xbmc.getInfoLabel('$VAR[XCMate103.Contract]')=='READY':ids+=(296903,)
        for ident in ids:control(window,ident)
        return dict(code='RUNTIME_READY',controls=len(ids),variables=True)
    except (AttributeError,RuntimeError,ValueError):return dict(code='RENDER_CONTROLS_NOT_LOADED')

def prepare(skin):
    from widget_skin50 import guard
    from widget_transaction50 import prepare as transaction
    from home_inventory78 import snapshot
    from skin_patch103 import active_profile,phase
    with phase('profile'):
        profile=active_profile()
    with phase('layout'):
        guard(skin);root=Path(skin).resolve()
        paths=[root/name for name in FILES]
        if any(path.parent.is_symlink() for path in paths):raise ValueError('UNSAFE_TARGET')
        original={name:read(path) for name,path in zip(FILES,paths)}
        candidate=build(original)
        meta_sha=sha(read(root/'addon.xml'))
    with phase('inventory'):
        inventory=snapshot(profile,root)
    with phase('journal'):
        changes=[(path,candidate[name]) for name,path in zip(FILES,paths)]
        return transaction('skin',changes,dict(skin=str(root),meta_sha=meta_sha,contract78=1,
                           inventory78=inventory,profile=str(profile)),originals=tuple(original.values()))

def apply(token,skin,confirmed=False,restore=False):
    from widget_transaction50 import load,folder,apply as transaction
    from widget_skin50 import guard
    from skin_patch103 import active_profile,phase
    if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
    with phase('profile'):
        profile=active_profile()
    with phase('layout'):
        guard(skin);root=Path(skin).resolve()
        if any((root/name).parent.is_symlink() for name in FILES):raise ValueError('UNSAFE_TARGET')
        meta_sha=sha(read(root/'addon.xml'))
    with phase('journal'):
        metadata=load(token,'skin')['metadata'];backup=folder()/token
        if metadata.get('skin')!=str(root) or metadata.get('meta_sha')!=meta_sha or metadata.get('contract78')!=1:
            raise ValueError('SKIN_CHANGED')
        if 'profile' in metadata and metadata['profile']!=str(profile):raise ValueError('PROFILE_CHANGED')
        original={name:read(backup/('original.'+str(i))) for i,name in enumerate(FILES)}
        expected=build(original)
        for i,name in enumerate(FILES):
            if expected[name]!=read(backup/('candidate.'+str(i))):raise ValueError('CANDIDATE_VERIFY_FAILED')
    # Revalidate the complete saved widget inventory before activating own
    # XML, not only the three XCMate paths. The snapshot is private/local.
    if not restore or 'profile' not in metadata:
        with phase('inventory'):
            from home_inventory78 import receipt
            inventory87=metadata.get('inventory78')
            receipt87=receipt(inventory87) if inventory87 else None
            if receipt87 is not None:
                if not isinstance(receipt87,dict):raise ValueError('BACKUP_VERIFY_FAILED')
                if receipt87.get('profile')!=str(profile):raise ValueError('PROFILE_CHANGED')
                if not restore:
                    from widget_inventory87 import InventoryChanged,compare
                    try:compare(profile,receipt87)
                    except InventoryChanged:raise ValueError('WIDGET_INVENTORY_CHANGED') from None
            elif 'profile' in metadata:raise ValueError('BACKUP_VERIFY_FAILED')
    result=transaction(token,'skin',[root/name for name in FILES],confirmed=confirmed,restore=restore)
    import xbmcaddon,xbmcgui
    xbmcaddon.Addon().setSetting('home78_repair_optout','true' if restore else 'false')
    if restore:xbmcgui.Window(10000).clearProperty('XCMate.Home78.Activation')
    if not restore:
        if not installed(root):raise ValueError('TARGET_VERIFY_FAILED')
        from home_activation78 import request
        request(token,consumers_changed=b'XCMate80.Contract' in expected['xml/IncludesVariables.xml'])
    return result
