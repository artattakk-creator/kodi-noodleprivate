"""Actual local RailView pixels over native BINGIE; no personal skin edits."""
import hashlib,json,time
from pathlib import Path
import xbmc,xbmcgui
from PIL import Image
from nav_rail import RailView,icon

def run(capture):
 class Dialog(xbmcgui.WindowDialog):
  def __init__(self):
   super().__init__();self.finished=False;self.rail=RailView(self,'live',lambda action:None,lambda where:None)
  def onAction(self,action):
   command={1:'left',2:'right',3:'up',4:'down',9:'back',10:'back',92:'back'}.get(action.getId())
   if command:self.rail.command(command)
  def onControl(self,control):self.rail.click(control.getId())
 view=Dialog();view.show();rail=view.rail;rail.show(False);xbmc.sleep(500)
 scale_x=1920/view.getWidth();scale_y=1080/view.getHeight();wanted=('search','favourites','live','movies','series','settings','home');cases=[]
 try:
  for key in wanted:
   index=next(i for i,entry in enumerate(rail.items) if entry[0]==key)
   # Reach every entry through native D-pad actions.
   for _ in range((index-rail.position)%len(rail.items)):xbmc.executebuiltin('Action(Down)',wait=False);xbmc.sleep(40)
   assert rail.position==index,'ICON86_NATIVE_FOCUS'
   step=(rail.height-64)/len(rail.items);height=int(step)-4;y=int(32+index*step)+(height-32)//2
   box=(round(48*scale_x),round(y*scale_y),round(80*scale_x),round((y+32)*scale_y))
   path,rgb=capture('visible84-nav86-'+key)
   crop=rgb.crop(box);expected=Image.open(icon(rail.items[index][1],'focused')).getchannel('A').resize(crop.size,Image.Resampling.LANCZOS)
   actual=[p[0]>125 and p[1]>125 and p[2]>125 for p in crop.getdata()];mask=[p>100 for p in expected.getdata()]
   union=sum(a or b for a,b in zip(actual,mask));intersection=sum(a and b for a,b in zip(actual,mask));score=intersection/max(1,union)
   assert sum(actual)>8 and score>.25,('ICON86_PIXELS',key,score,box)
   cases.append(dict(key=key,mask_iou=round(score,3),pixels=sum(actual),screenshot=path.name,sha256=hashlib.sha256(crop.tobytes()).hexdigest()))
  assert len({c['sha256'] for c in cases})==7,'ICON86_DUPLICATE_RENDER'
  position=rail.position;xbmc.executebuiltin('Action(Left)',wait=False);xbmc.sleep(150)
  assert rail.expanded and rail.position==position,'ICON86_EXPAND_FOCUS'
  expanded,_=capture('visible84-nav86-expanded')
  xbmc.executebuiltin('Action(Back)',wait=False);xbmc.sleep(100)
  assert not rail.expanded and rail.position==position,'ICON86_COLLAPSE_FOCUS'
 finally:rail.hide();view.close();xbmc.sleep(100)
 result=dict(status='PASS',cases=cases,expanded=expanded.name,android='ANDROID_NOT_TESTED',personal_bingie_shortcuts='UNCHANGED')
 Path('/root/icons86.json').write_text(json.dumps(result,indent=2));print('ICONS86 '+json.dumps(result),flush=True)
