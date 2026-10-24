"""First show storage classes, then actual Kodi sources/volumes, then folders."""
import json,os
import xbmc,xbmcgui
from localization import tr
from storage_diagnostics import mark,kind


def kodi_sources():
    result=[];seen=set()
    for media in ('files','video'):
        try:
            response=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=1,method='Files.GetSources',params=dict(media=media))))
            if len(response)>262144:continue
            values=json.loads(response).get('result',{}).get('sources',[])
        except (AttributeError,ValueError,RuntimeError,TypeError):continue
        for value in values[:256]:
            path=value.get('file','') if isinstance(value,dict) else ''
            if not isinstance(path,str) or path in seen:continue
            if path.startswith('smb://') or os.path.isabs(path):
                seen.add(path);result.append(dict(path=path,label=str(value.get('label') or tr(34907))[:160]))
    return result


def external_sources():
    values=[v for v in kodi_sources() if kind(v['path'])=='USB'];seen={v['path'] for v in values}
    for root in ('/storage','/mnt/media_rw','/media'):
        try:names=os.listdir(root)[:128]
        except OSError:continue
        for name in names:
            if name in ('emulated','self','sdcard','sdcard0') or name.startswith('.'):continue
            path=root+'/'+name
            if path not in seen and os.path.isdir(path):seen.add(path);values.append(dict(path=path,label=tr(34903)+' · '+name))
    return values


def choose(action='DOWNLOAD'):
    from capture_ui import work
    mark(action,'PICKER_ACTION');dialog=xbmcgui.Dialog()
    mark(action,'PICKER_ROOT_LISTED',count=3)
    category=dialog.select(tr(34900 if action=='DOWNLOAD' else 34901),[tr(34902),tr(34903),tr(34904)])
    if category not in (0,1,2):return None
    target=('LOCAL','USB','SMB')[category];mark(action,'SOURCE_CATEGORY',target)
    if category==0:
        values=[dict(label=tr(34908),path='special://profile/'),dict(label=tr(34909),path='/storage/emulated/0/'),dict(label=tr(34910),path='/')]
    elif category==1:
        values=work(external_sources) or []
        if not values:dialog.ok('XCMate',tr(34905))
        values.append(dict(label=tr(34911),path='/storage/'))
    else:
        values=work(lambda:[v for v in kodi_sources() if v['path'].startswith('smb://')]) or []
        if not values:dialog.ok('XCMate',tr(34906))
        values.append(dict(label=tr(34912),path='smb://'))
    index=dialog.select(tr(34900 if action=='DOWNLOAD' else 34901),[v['label'] for v in values])
    if not 0<=index<len(values):return None
    # Never initialize to the previous internal target. This root was just
    # selected explicitly from the relevant class/source list.
    selected=dialog.browseSingle(0,tr(34913),'files',defaultt=values[index]['path'])
    if not selected:return None
    mark(action,'TARGET_SELECTED',kind(selected));return selected
