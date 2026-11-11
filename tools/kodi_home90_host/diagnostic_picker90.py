"""Fail-only disposable native experiments. Never turns a failed gate into PASS.
No production configuration or saved WidgetPath is touched; original skin bytes
are restored. A useful experiment requires a separate product fix + clean run.
"""
from pathlib import Path
import json,time,xml.etree.ElementTree as E
import xbmc,xbmcgui
from PIL import Image
import io

def run(reason,pump):
 path=Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/IncludesHomeWidgets.xml');original=path.read_bytes();results=[]
 try:
  for stage in ('params','self','bounds','combined','flat'):
   root=E.fromstring(original);row=root.find("include[@name='XCMate80.MediaRow']/control");normal=root.find("include[@name='XCMate80.MediaNormal']/control");inner=row.find("control[@type='group']")
   if stage in ('self','combined'):
    factory=root.find("include[@name='XCMate80.BaseBingie']/include[@content='Fixed_Focus_Navigation_Factory']")
    factory.attrib.pop('condition',None)
   if stage in ('bounds','combined'):
    for field,value in (('width','1920'),('height','214')):
     n=inner.find(field)
     if n is None:n=E.SubElement(inner,field)
     n.text=value
   if stage=='flat':
    call=inner.find('include');inner.remove(call);row.remove(inner);row.append(call)
   if stage=='params':
    for owner,cid in (('XCMate80.MediaRow','296910'),('XCMate80.NativeMediaBase','296911'),('XCMate80.MediaNormal','296912')):
     label=E.SubElement(root.find("include[@name='"+owner+"']"),'control',type='label',id=cid)
     for key,value in (('left','-100'),('top','-100'),('width','1'),('height','1'),('font','Reg18'),('label','TYPE=$PARAM[containerType];ID=$PARAM[widgetid];MENU=$PARAM[submenuid];VIS=$PARAM[visibility]')):E.SubElement(label,key).text=value
   path.write_bytes(E.tostring(root,encoding='utf-8'));xbmc.executebuiltin('ReloadSkin()',wait=False);xbmc.sleep(1200)
   result={'stage':stage,'status':'DIAGNOSTIC_ONLY','rows':{},'labels':{}}
   end=time.monotonic()+12;chosen=False
   while time.monotonic()<end:
    pump()
    if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999):
     home=xbmcgui.Window(10000)
     if not chosen:
      labels=[xbmc.getInfoLabel('Container(900).ListItemAbsolute('+str(i)+').Label') for i in range(int(xbmc.getInfoLabel('Container(900).NumItems') or 0))]
      positions=[i for i,v in enumerate(labels) if v.strip().casefold() in ('home','startseite')]
      if len(positions)==1:
       home.setFocusId(900);home.getControl(900).selectItem(positions[0]);xbmc.executebuiltin('Action(Right)',wait=False);chosen=True
     result['rows']={str(cid):dict(count=xbmc.getInfoLabel('Container('+str(cid)+').NumItems'),visible=xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')')) for cid in (2510,2520,2530)}
     result['labels']={str(cid):xbmc.getInfoLabel('Control.GetLabel('+str(cid)+')') for cid in (296910,296911,296912)}
     if chosen and result['rows']['2530']['count']=='24':
      home.setFocusId(2510);xbmc.executebuiltin('Action(Down)',wait=False);xbmc.sleep(300);xbmc.executebuiltin('Action(Down)',wait=False);xbmc.sleep(600);break
    xbmc.sleep(100)
   image='/root/picker90-experiment-'+stage+'.png';xbmc.executebuiltin('TakeScreenshot('+image+')',wait=False);xbmc.sleep(300);result['screenshot']=Path(image).name
   try:
    with Image.open(io.BytesIO(Path(image).read_bytes())) as picture:rgb=picture.convert('RGB').resize((1920,1080))
    result['rail_pixels']=sum(max(abs(a-b) for a,b in zip(pixel,(100,60,180)))<=8 for pixel in rgb.crop((260,640,1890,1040)).getdata())
    result['all_pixels']=sum(max(abs(a-b) for a,b in zip(pixel,(100,60,180)))<=8 for pixel in rgb.getdata())
   except (OSError,ValueError):result['rail_pixels']=-1
   result['focus']=xbmcgui.Window(10000).getFocusId()
   result['parent']={key:xbmc.getInfoLabel(key) for key in ('Container(77777).CurrentItem','Container(77777).NumItems','Window(Home).Property(CurrentWidgetID)','Window(Home).Property(CurrentWidgetPos)','Window(Home).Property(PrevWidgetPos)')}
   results.append(result)
   Path('/root/picker90-experiments.json').write_text(json.dumps(dict(original_gate=str(reason),experiments=results,verdict='FAIL: clean unmodified product run still required',android='ANDROID_NOT_TESTED'),indent=2))
 finally:path.write_bytes(original)
