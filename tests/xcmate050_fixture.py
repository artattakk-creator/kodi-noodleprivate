"""Official BINGIE 2.2.3 XML and a synthetic saved Skinshortcuts profile."""
import importlib,importlib.util,json,sys,types,zipfile
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ROOT,ListItem

class Fixture50(Fixture):
    def setUp(self):
        super().setUp();self.skin=self.folder/'skin';self.skin.mkdir();self.profile=self.folder/'profile'
        self.native=self.profile/'addon_data/script.skinshortcuts';self.native.mkdir(parents=True)
        with zipfile.ZipFile(ROOT/'tests/fixtures/bingie223_reference50.zip') as z:
            for name in z.namelist():
                p=self.skin/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
        self.menu=self.native/'skin.titan.bingie.mod-mainmenu.DATA.xml';self.menu.write_bytes((self.skin/'shortcuts/mainmenu.DATA.xml').read_bytes())
        self.prop=self.native/'skin.titan.bingie.mod.properties'
        self.saved=[['mainmenu','10000','widget','Addon'],['mainmenu','10000','widgetName','My films'],['mainmenu','10000','widgetType','movies'],['mainmenu','10000','widgetTarget','videos'],['mainmenu','10000','widgetPath','plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=p&reload=keep-movies'],['mainmenu','10000','widget.1','Addon'],['mainmenu','10000','widgetName.1','My series'],['mainmenu','10000','widgetPath.1','plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=p&reload=keep-series'],['mainmenu','10000','widgetPath.2',''],['mainmenu','10000','widgetstyle.2','poster'],['mainmenu','movies','widgetPath','plugin://foreign.addon/?q=private-test'],['othermenu','named','custom','Keep Unicode ÄÖÜ']]
        self.prop.write_text(repr(self.saved).replace('],','],\n'))
        self.binding=importlib.import_module('widget_binding50');self.skinmod=importlib.import_module('widget_skin50');self.tx=importlib.import_module('widget_transaction50')

    def ctx(self):return self.binding.context(self.profile,self.skin)
    def bind_plan(self,kind='live',slot=2):return self.binding.prepare(self.ctx(),kind,'p',slot,dict(live='Live-TV',vod='Filme',series='Serien')[kind])
    def skin_bytes(self):return {name:(self.skin/name).read_bytes() for name in self.skinmod.FILES}
    def native_reference(self):
        spec=importlib.util.spec_from_file_location('native_shortcuts210',ROOT/'tests/fixtures/skinshortcuts210_reference50.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.SKINPATH=str(self.skin/'shortcuts');module.ADDONID='script.skinshortcuts';module.KODIVERSION='21';module.log=lambda *a:None;module.xbmc=types.SimpleNamespace(getSkinDir=lambda:'skin.titan.bingie.mod')
        class File:
            def __init__(self,path):self.path=Path(path)
            def read(self):return self.path.read_text()
            def close(self):pass
        module.xbmcvfs=types.SimpleNamespace(exists=lambda path:Path(path).exists(),File=File)
        return module
    def native_properties(self):
        import xml.etree.ElementTree as E
        module=self.native_reference();reader=module.DataFunctions();reader.currentProperties=None;reader.defaultProperties=None
        reader.slugify=lambda label,*a,**kw:label;reader.labelIDList=[]
        reader._get_overrides_skin=lambda:E.ElementTree(E.parse(self.skin/'shortcuts/overrides.xml').getroot());reader._save_hash=lambda *a:None
        reader.local=lambda text:[text,text,text,text];reader._getWidgetNameAndType=lambda text:None;reader._getBackgroundName=lambda text:None
        return reader.checkAdditionalProperties('mainmenu','10000','10000',True,str(self.profile))
