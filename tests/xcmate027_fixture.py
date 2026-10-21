"""Strict XML-window native callback model, with a manually drained job queue."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import time
import types
from concurrent.futures import Future
from unittest import mock
import urllib.parse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ADDON=ROOT/'src/plugin.video.xtreammate'
LIB=ADDON/'resources/lib'


class ListItem:
    def __init__(self,label='',label2='',path='',offscreen=False):
        self.label,self.path=label,path;self.art={};self.props={};self.info={}
    def setArt(self,dictionary): self.art.update(dictionary)
    def setInfo(self,type,infoLabels): self.info.update(infoLabels)
    def setProperty(self,key,value): self.props[key]=value
    def getProperty(self,key): return self.props.get(key,'')


class Control:
    def __init__(self,node):
        self.kind=node.get('type');self.node=node;self.visible=True;self.enabled=True
        self.items=[];self.selected=0;self.label=node.findtext('label','')
        self.width=int(node.findtext('width','0'));self.x=int(node.findtext('left','0'));self.y=int(node.findtext('top','0'))
    def reset(self): self.items=[];self.selected=0
    def addItems(self,items): self.items=[ListItem(i) if isinstance(i,str) else i for i in items]
    def getListItem(self,index): return self.items[index]
    def getSelectedPosition(self): return self.selected
    def selectItem(self,item): self.selected=max(0,min(item,len(self.items)-1))
    def setVisible(self,visible): self.visible=visible
    def isVisible(self): return self.visible
    def setEnabled(self,enabled): self.enabled=enabled
    def size(self):return len(self.items)
    def setNavigation(self,up,down,left,right):
        for key,control in zip(('up','down','left','right'),(up,down,left,right)):
            node=self.node.find('on'+key)
            if node is None:node=ET.SubElement(self.node,'on'+key)
            node.text=control.node.get('id')
    def setLabel(self,label='',font=None,textColor=None,disabledColor=None,shadowColor=None,focusedColor=None,label2=''): self.label=label
    def setText(self,text): self.text=text
    def setWidth(self,width): self.width=width
    def setPosition(self,x,y): self.x,self.y=x,y
    def setImage(self,imageFilename,useCache=True): self.image=imageFilename


class WindowXML:
    def __init__(self,xmlFilename,scriptPath,defaultSkin='Default',defaultRes='720p',isMedia=False):
        self.tree=ET.parse(Path(scriptPath)/'resources/skins'/defaultSkin/defaultRes/xmlFilename).getroot()
        self.controls={int(n.get('id')):Control(n) for n in self.tree.findall('./controls/control') if n.get('id')}
        self.focus=int(self.tree.findtext('defaultcontrol'));self.shown=False;self._window_properties={}
    def setProperty(self,key,value): self._window_properties[key]=value
    def getProperty(self,key): return self._window_properties.get(key,'')
    def show(self):
        self.shown=True
        sys.modules['xbmc']._focus_window=self
        self.onInit()
    def getControl(self,controlId): return self.controls[controlId]
    def setFocusId(self,iControlId):
        assert self.controls[iControlId].visible, ('focus on hidden control',iControlId)
        assert self.controls[iControlId].kind in ('button','list','panel'),('focus on noninteractive control',iControlId)
        self.focus=iControlId
    def getFocusId(self): return self.focus
    def doModal(self):
        self.shown=True
        sys.modules['xbmc']._focus_window=self
        self.onInit()  # Real WindowXML callback, NOT WindowDialog's absent onInit.
    def close(self): self.shown=False
    def native(self,key):
        sys.modules['xbmc']._focus_window=self
        focus=self.focus;c=self.controls[focus]
        if key==7: self.onClick(focus)
        elif key in (1,2,3,4):
            direction={1:'left',2:'right',3:'up',4:'down'}[key]
            horizontal=c.node.findtext('orientation')=='horizontal'
            step={1:-1,2:1,3:-1,4:1}[key]
            moves=c.kind in ('list','panel') and (c.kind=='panel' or (key in (1,2))==horizontal)
            if moves and c.items:
                if c.kind=='panel' and key in (3,4): step*=c.width//190
                target=c.selected+step
                if 0<=target<len(c.items): c.selected=target
            else:
                target=int(c.node.findtext('on'+direction,str(focus)))
                if target in self.controls and self.controls[target].visible: WindowXML.setFocusId(self,target)
        self.onAction(types.SimpleNamespace(getId=lambda:key,getButtonCode=lambda:0))


class StrictFuture(Future):
    def _invoke_callbacks(self):
        # Real Future logs callback errors; tests must FAIL on a native API
        # or rendering exception instead of silently returning a green result.
        for callback in self._done_callbacks: callback(self)


class QueuedPool:
    def __init__(self,max_workers=1): self.jobs=[]
    def submit(self,fn):
        future=StrictFuture();self.jobs.append((future,fn));return future
    def drain(self):
        for _ in range(40):
            if not self.jobs: return
            future,fn=self.jobs.pop(0)
            if future.cancelled(): continue
            try: future.set_result(fn())
            except BaseException as exc:
                if not future.done(): future.set_exception(exc)
                else: raise
        raise AssertionError('unbounded jobs')
    def shutdown(self,wait=True,cancel_futures=False):
        if cancel_futures:
            for future,_ in self.jobs: future.cancel()


class Fixture:
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.folder=Path(temp.name);self.options={};self.properties={};self.added=[];self.ends=[];self.builtins=[]
        self.ui_locale='de_de'
        self.portal=dict(id='p',name='Demo',type='xtream',enabled=True,xc_host='https://provider.invalid',xc_user='user',xc_pass='SECRET',start_stream_id='1',start_group_id='b')
        self.portals=[self.portal];self.now=int(time.time())
        categories=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
        self.catalogs={'get_live_categories':categories,'get_vod_categories':categories,'get_series_categories':categories,
            'get_live_streams':[dict(stream_id=str(i),category_id='a',name='House of Dragon TV' if i==1 else 'Channel '+str(i),epg_channel_id='xml') for i in range(1,4)],
            'get_vod_streams':[dict(stream_id=str(i),category_id='a',name='House of Dragon '+str(i),added=self.now-i,stream_icon='https://image.invalid/'+str(i),duration_secs=2700,rating='8.0') for i in range(1,101)],
            'get_series':[dict(series_id=str(i),category_id='a',name='House of Dragon series '+str(i),added=self.now-i) for i in range(1,4)]}
        self.details={'get_vod_info':{'info':{'plot':'Actual plot','duration_secs':2700,'rating':'8.5','youtube_trailer':'abcdefghijk'}},
                      'get_series_info':{'info':{'plot':'Series plot'},'episodes':{'2':[dict(id='21',episode_num=1,title='Second season')],
                       '1':[dict(id='12',episode_num=2,title='Two'),dict(id='11',episode_num=1,title='One')]}}}
        self.client=types.SimpleNamespace(get_cached_catalog=lambda a:self.catalogs.get(a),
            _cache_key=lambda a,extra=None:a+json.dumps(extra or {},sort_keys=True),
            _get_json=mock.Mock(side_effect=lambda action,**kw:self.details.get(action,{}) if kw.get('cached_only') else (_ for _ in ()).throw(AssertionError('HTTP on GUI'))),
            vod_stream_url=lambda sid,ext:'https://provider.invalid/movie/user/SECRET/'+sid+'.'+ext,
            series_episode_url=lambda sid,ext:'https://provider.invalid/series/user/SECRET/'+sid+'.'+ext)
        utils=types.ModuleType('utils')
        for name in ('info','warn','debug','error','notify','cache_clear','toggle_favourite','load_favourites','is_favourite','apply_lang_sort'):
            setattr(utils,name,lambda *a,**kw:None)
        utils._L=lambda n:str(n)
        utils.addon_data_dir=lambda:str(self.folder)
        utils.setting=lambda k,default='':self.options.get(k,default)
        utils.setting_int=lambda k,default=0:int(self.options.get(k,default))
        utils.setting_bool=lambda k,default=False:self.options.get(k,default)
        utils.cache_dir=utils._private_cache_dir=lambda:str(self.folder)
        utils.http_get=mock.Mock(side_effect=AssertionError('unexpected HTTP'))
        utils.cache_set=mock.Mock(return_value=True)
        addon=types.ModuleType('xbmcaddon')
        addon.Addon=lambda *args:types.SimpleNamespace(getAddonInfo=lambda k: {'path':str(ADDON),'id':'plugin.video.xtreammate','version':'0.1.27'}.get(k,''),
            setSetting=lambda k,v:self.options.__setitem__(k,v),
            getLocalizedString=lambda ident:self.translations.get(self.ui_locale,{}).get(ident,''))
        gui=types.ModuleType('xbmcgui');gui.WindowXML=WindowXML;gui.ListItem=ListItem
        gui.Window=lambda n:types.SimpleNamespace(getProperty=lambda k:self.properties.get(k,''),setProperty=self.properties.__setitem__,clearProperty=lambda k:self.properties.pop(k,None))
        self.dialog=types.SimpleNamespace(input=mock.Mock(return_value=''),select=mock.Mock(return_value=-1),
            yesno=mock.Mock(return_value=False),ok=mock.Mock(),notification=mock.Mock(),textviewer=mock.Mock())
        gui.Dialog=lambda:self.dialog
        xbmc=types.ModuleType('xbmc');self.current_folder='plugin://plugin.video.xtreammate/?action=xcmate_home&pid=p'
        def builtin(command):
            self.builtins.append(command)
            if command.startswith('Container.Update('):
                self.current_folder=command[len('Container.Update('):-1].removesuffix(',replace')
            elif command.startswith('ActivateWindow(Videos,'):
                self.current_folder=command[len('ActivateWindow(Videos,'):-1].removesuffix(',return')
        xbmc.executebuiltin=builtin
        xbmc.getInfoLabel=lambda label:self.current_folder if label=='Container.FolderPath' else ''
        xbmc.Monitor=lambda:types.SimpleNamespace(waitForAbort=lambda n:False)
        xbmc.Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:False)
        def condition(c):
            if c.startswith('Control.IsEnabled('):
                w=getattr(xbmc,'_focus_window',None);cid=int(c[len('Control.IsEnabled('):-1])
                return w.controls[cid].enabled if w else True
            return c=='System.HasAddon(plugin.video.youtube)' or c=='Player.SeekEnabled'
        xbmc.getCondVisibility=condition
        plugin=types.ModuleType('xbmcplugin');plugin.setContent=mock.Mock();plugin.setPluginCategory=mock.Mock()
        plugin.endOfDirectory=lambda *a,**kw:self.ends.append((a,kw))
        plugin.addDirectoryItem=lambda handle,url,listitem,isFolder=True:self.added.append((url,listitem,isFolder))
        plugin.setResolvedUrl=mock.Mock()
        portals=types.ModuleType('portals');portals.get_active=lambda:[p for p in self.portals if p.get('enabled',True)]
        portals.get_by_id=lambda pid:next((p for p in self.portals if p['id']==pid),None)
        portals.import_from_settings=lambda:None;portals.load_all=lambda:self.portals
        epg=types.ModuleType('epg');self.cache={};epg.load_cache=lambda pid:self.cache
        epg._disk_ck=lambda pid:utils.cache_key('epg2_'+pid)
        epg._mem_clear=lambda pid=None:None
        sources=types.ModuleType('epg_sources');sources.configuration=lambda pid:{'mappings':{},'sources':[]}
        status=types.ModuleType('epg_status');status.revision=lambda pid:'r1';status.read=lambda pid:{}
        patch_path=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch_path.start();self.addCleanup(patch_path.stop)
        from localization import read_catalog
        self.translations={locale:read_catalog(ADDON/'resources/language'/('resource.language.'+locale)/'strings.po')
                           for locale in ('de_de','en_gb')}
        patch=mock.patch.dict(sys.modules,utils=utils,xbmc=xbmc,xbmcgui=gui,xbmcplugin=plugin,xbmcaddon=addon,
            portals=portals,epg=epg,epg_sources=sources,epg_status=status,xbmcvfs=types.ModuleType('xbmcvfs'))
        patch.start();self.addCleanup(patch.stop)
        for name in ('library_index','group_selection','latest_media','home_menu','app_routes','media_art','media_state',
                     'owner_dispatch','window_navigation','media_data','media_progress','media_window','guide_store','guide_window','guide_timers'):
            sys.modules.pop(name,None)
        self.index=importlib.import_module('library_index');self.routes=importlib.import_module('app_routes')
        self.media=importlib.import_module('media_window');self.guide=importlib.import_module('guide_window')
        self.state=importlib.import_module('media_state')
        self.index.refresh(self.portal,self.client)
        for module in (self.media,self.guide):
            p=mock.patch.object(module,'ThreadPoolExecutor',QueuedPool);p.start();self.addCleanup(p.stop)
        p=mock.patch.object(self.media.MediaWindow,'_art_loop',lambda self:None);p.start();self.addCleanup(p.stop)
        # HTTP prefetch is a separate daemon in production; key callbacks only
        # enqueue work. Keep native UI tests independent of that worker.
        p=mock.patch.object(importlib.import_module('media_art'),'request');p.start();self.addCleanup(p.stop)
        p=mock.patch.object(importlib.import_module('media_art'),'ensure_worker');p.start();self.addCleanup(p.stop)
        self.router=types.SimpleNamespace(_params={'pid':'p'},_handle=7,_xc=lambda p:self.client,
            url=lambda **kw:'plugin://plugin.video.xtreammate/?'+urllib.parse.urlencode({k:v for k,v in kw.items() if v is not None}),
            _add_dir=lambda label,url,**kw:self.added.append((url,ListItem(label),True)),
            _play_youtube_id=mock.Mock())

    def media_window(self,kind='vod'):
        w=self.media.MediaWindow('XCMateMedia.xml',str(ADDON),'Default','720p')
        w.configure(self.router,self.portal,kind)
        self.addCleanup(w.close);w.doModal();self.settle(w);return w

    def guide_window(self):
        w=self.guide.GuideWindow('XCMateGuide.xml',str(ADDON),'Default','720p')
        w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.doModal();self.settle(w);return w

    def settle(self,window):
        # Complete queued data work, then explicitly deliver on the GUI owner.
        for _ in range(40):
            window._pool.drain();window.pump()
            if not window._pool.jobs: return
        raise AssertionError('unbounded owner jobs')
