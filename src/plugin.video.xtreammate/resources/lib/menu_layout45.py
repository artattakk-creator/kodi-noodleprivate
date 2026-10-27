"""Decorate only XCMate-owned XML; preserve IDs, hit rectangles and navigation."""
import xml.etree.ElementTree as ET
FILES={'XCMateMedia.xml','XCMateGuide.xml','XCMateGuideGrid.xml','XCMateArtwork43.xml','XCMateSetup.xml','XCMatePlaylistEditor.xml','XCMatePopupTest.xml'}

def apply(tree,filename):
 root=tree.getroot()
 if filename not in FILES:return
 for node in root.iter('control'):
  if node.get('type') not in ('list','panel','wraplist','fixedlist'):continue
  cid=node.get('id')
  wanted=filename=='XCMateMedia.xml' and cid in ('200','300','330','810') or filename=='XCMateGuide.xml' and cid in ('200','220') or filename=='XCMateGuideGrid.xml' and cid=='200' or filename=='XCMatePlaylistEditor.xml' and cid=='100'
  if not wanted:continue
  for layout in node:
   if layout.tag not in ('itemlayout','focusedlayout'):continue
   # Theme may already supply a functional icon; normalize its placement.
   for image in list(layout.findall("control[@type='image']")):
    if image.findtext('texture')=='$INFO[ListItem.Art(icon)]':layout.remove(image)
   height=int(layout.get('height','48'));size=16
   image=ET.SubElement(layout,'control',{'type':'image','xcmate-menu45':'true'})
   for tag,text in dict(left=12,top=max(0,(height-size)//2),width=size,height=size,texture='$INFO[ListItem.Art(icon)]',aspectratio='keep').items():ET.SubElement(image,tag).text=str(text)
   for label in layout.findall("control[@type='label']"):
    left=label.find('left');width=label.find('width')
    if left is not None and width is not None:
     previous=int(left.text);left.text=str(max(38,previous));width.text=str(max(1,int(width.text)-(int(left.text)-previous)))

 # Static action glyphs are decorative siblings, never independent focus stops.
 from menu_icons45 import icon
 maps={'XCMateMedia.xml':{'120':'list','400':'search','700':'tv','701':'movie','702':'series','820':'image'},'XCMateArtwork43.xml':{'401':'tv','402':'info','403':'image','404':'drive','405':'back','501':'image','502':'image','503':'check','504':'check','505':'back','506':'refresh','507':'info','508':'back'},'XCMateGuideGrid.xml':{'310':'back','311':'calendar','312':'calendar','313':'clock','314':'list','315':'search'},'XCMateGuide.xml':{'310':'back','311':'calendar','312':'activity'}}
 maps['XCMateSetup.xml']={'10':'tv','11':'movie','12':'series','13':'check','14':'back','15':'database','16':'image','17':'check','18':'back'}
 maps['XCMatePlaylistEditor.xml']={'10':'search','11':'list','12':'plus','13':'link','14':'download','16':'back','17':'play','18':'back'}
 fallback='wand' if filename=='XCMateSetup.xml' else 'list' if filename=='XCMatePlaylistEditor.xml' else 'activity'
 parents={child:parent for parent in root.iter() for child in parent}
 for button in list(root.iter('control')):
  if button.get('type')!='button':continue
  cid=button.get('id');role=maps.get(filename,{}).get(cid,fallback)
  if filename=='XCMateMedia.xml' and cid not in maps[filename]:continue
  # Keep exactly the existing hit rectangle and links.
  x=int(button.findtext('left','0'));y=int(button.findtext('top','0'));h=int(button.findtext('height','40'))
  image=ET.SubElement(parents[button],'control',{'type':'image','xcmate-menu45':'true'})
  for tag,text in dict(left=x+10,top=y+max(0,(h-16)//2),width=16,height=16,texture=icon(role,full=True),aspectratio='keep',visible='Control.IsVisible('+str(cid)+')').items():ET.SubElement(image,tag).text=str(text)
  offset=button.find('textoffsetx')
  if offset is None:offset=ET.SubElement(button,'textoffsetx')
  offset.text='34'
