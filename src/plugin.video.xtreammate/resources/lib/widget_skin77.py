"""Recognize only the exact official Space-Blue logo/line substitutions.

The existing .75 source-hash guard still validates the complete normalized
file. Unknown skin changes remain blocked; original branded bytes are backed
up by the existing explicit preview/apply/restore transaction.
"""
OLD=b'home/bingie_mod_logo.png'
NEW=b'special://home/addons/script.gsmedia.xcmate.branding/resources/media/xcmate_logo.png'
RED=b'colordiffuse="ffE50914">bingie/line.png'
BLUE=b'colordiffuse="FF159FEA">bingie/line.png'
def known():
    import json
    from pathlib import Path
    from widget_transaction50 import read
    return json.loads(read(Path(__file__).parents[1]/'bingie77_previous.json'))

def _core(path,data):
    from widget_skin75 import candidate as previous
    from widget_transaction50 import sha
    reference=known()
    if sha(data)==reference.get('current',{}).get(path):return data
    if sha(data)!=reference['files'].get(path):data=previous(path,data)
    if path=='xml/IncludesHomeWidgets.xml':
        from widget_skin50 import spans,edit
        matches=[node for node in spans(data) if node['tag']=='control' and node['attrs'].get('id')=='296751']
        if len(matches)!=1:raise ValueError('UNVERIFIED_HERO_IMAGE')
        node=matches[0];ratios=[c for c in node['children'] if c['tag']=='aspectratio']
        if len(ratios)!=1 or ratios[0]['text']!='keep':raise ValueError('UNVERIFIED_HERO_IMAGE')
        ratio=ratios[0];data=edit(data,[(ratio['open'],ratio['end'],b'scale')])
    return data

def candidate(path,data):
    if path!='xml/IncludesHomeBingie.xml' or NEW not in data:return _core(path,data)
    if data.count(NEW)!=1 or OLD in data:raise ValueError('UNVERIFIED_SPACE_BLUE')
    normalized=data.replace(NEW,OLD)
    color=normalized.count(BLUE)
    if color>1:raise ValueError('UNVERIFIED_SPACE_BLUE')
    if color:normalized=normalized.replace(BLUE,RED)
    changed=_core(path,normalized)  # full-file guard; no fuzzy acceptance
    if changed.count(OLD)!=1:raise ValueError('UNVERIFIED_SPACE_BLUE')
    changed=changed.replace(OLD,NEW)
    if color:
        if changed.count(RED)!=1:raise ValueError('UNVERIFIED_SPACE_BLUE')
        changed=changed.replace(RED,BLUE)
    return changed

def existing_navigation(data):
    from widget_transaction50 import sha
    return sha(data)==known()['navigation']

def previously_applied(skin):
    from widget_skin50 import guard,FILES
    from widget_transaction50 import read,sha
    try:
        for name,path in zip(FILES,guard(skin)):
            data=read(path)
            if name=='xml/IncludesHomeBingie.xml':data=data.replace(NEW,OLD).replace(BLUE,RED)
            if sha(data)!=known()['files'][name]:return False
        return True
    except (OSError,ValueError,KeyError):return False


def inspect():
    from pathlib import Path
    import xbmcaddon
    from widget_skin50 import guard,FILES,applied,patch
    from widget_transaction50 import read
    try:
        skin=Path(xbmcaddon.Addon('skin.titan.bingie.mod').getAddonInfo('path'))
        paths=guard(skin)
        if applied(skin):return dict(code='ADAPTER_VERIFIED')
        for name,path in zip(FILES,paths):patch(name,read(path))
        from widget_skin75 import extra
        extra(skin)
        return dict(code='ADAPTER_APPROVAL_REQUIRED',space_blue=NEW in read(skin/'xml/IncludesHomeBingie.xml'))
    except (OSError,ValueError,KeyError,RuntimeError):return dict(code='ADAPTER_UNVERIFIED')
