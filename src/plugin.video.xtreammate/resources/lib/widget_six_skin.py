"""Additional owned rows; native/foreign definitions and saved shortcuts stay exact.

Called only by the existing guarded skin plan. Unknown edits to these private
nodes fail closed, with the existing backup/rollback transaction unchanged.
"""
import copy
import xml.etree.ElementTree as E
PREFIX='XCMate.SixRows.'
MARKER='XCMate.SixRows.Contract'

def definitions(files):
 from widget_skin78 import parse
 root=parse(files['xml/IncludesHomeWidgets.xml'])
 row=copy.deepcopy(root.find("include[@name='XCMate80.MediaRow']"));row.set('name',PREFIX+'Row')
 group=row.find('control')
 base_visibility=group.find('visible').text
 expanded='String.IsEqual(Window(Home).Property(XCMate.SixRows.$PARAM[xcmateKind].Expanded),true)'
 group.find('visible').text='['+base_visibility+'] + '+expanded
 # Empty/waiting rows retain their real heading, but cannot reserve 244px
 # and make Kodi scroll the final populated row out of the viewport. The
 # expanded native consumer is admitted BEFORE starting its DirectoryProvider.
 compact=E.Element('control',type='group',id='76$PARAM[widgetid]')
 for tag,text in (('height','26'),('width','1920'),('left','140'),('visible','['+base_visibility+'] + !'+expanded)):E.SubElement(compact,tag).text=text
 heading=copy.deepcopy(group.find("control[@type='grouplist']"))
 for node in heading.iter('control'):
  ident=node.get('id')
  if ident:node.set('id',str(int(ident.split('$')[0])+10)+'$PARAM[widgetid]')
 compact.append(heading);row.append(compact)
 # Same measured title and original animated spinner for all six kinds.
 for label in list(group.findall("control[@type='label']")):group.remove(label)
 status=E.SubElement(group,'control',type='label')
 for tag,text in (('left','900'),('top','2'),('width','860'),('height','24'),('font','Reg18'),('textcolor','FFBCC7D2'),('label','$INFO[Window(Home).Property(XCMate.SixRows.$PARAM[xcmateKind].Text)]')):E.SubElement(status,tag).text=text
 compact.append(copy.deepcopy(status))
 call=group.find("control[@type='group']/include");call.set('content',PREFIX+'Base')
 base=copy.deepcopy(root.find("include[@name='XCMate80.NativeMediaBase']"));base.set('name',PREFIX+'Base')
 for inc in base.findall('include'):inc.set('content',PREFIX+'Normal')
 normal=copy.deepcopy(root.find("include[@name='XCMate80.MediaNormal']"));normal.set('name',PREFIX+'Normal')
 for inc in normal.findall('.//include'):
  if inc.get('content')=='XCMate81.PosterRow':inc.set('content',PREFIX+'Cards')
 # A blank delayed source has no provider. It cannot fall through to Kodi's
 # library or issue unbounded concurrent source calls during Live startup.
 content=normal.find("control/include[@content='widget_base_content_$PARAM[contentStyle]']")
 normal.find('control').remove(content)
 E.SubElement(normal.find('control'),'content',target='$PARAM[widgetTarget]',limit='$PARAM[widgetLimit]').text='$INFO[Window(Home).Property(XCMate.SixRows.$PARAM[xcmateKind].Path)]'
 # xcmateKind must traverse the two legacy plain includes explicitly.
 for parent in (call,)+tuple(base.findall('include')):
  E.SubElement(parent,'param',name='xcmateKind',value='$PARAM[xcmateKind]')
 cards=copy.deepcopy(root.find("include[@name='XCMate81.PosterRow']"));cards.set('name',PREFIX+'Cards')
 for layout in ('itemlayout','focusedlayout'):
  images=cards.find(layout).findall("control[@type='image']")
  picture=next(n for n in images if n.findtext('texture')=='$INFO[ListItem.Art(poster)]')
  picture.find('texture').text='$VAR[XCMate.SixRows.Image]';picture.find('visible').text='!String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(thumb)) | !String.IsEmpty(ListItem.Icon)'
 return [row,base,normal,cards]

def variables():
 marker=E.Element('variable',name=MARKER);E.SubElement(marker,'value').text='READY'
 image=E.Element('variable',name='XCMate.SixRows.Image')
 for field in ('ListItem.Art(poster)','ListItem.Art(thumb)','ListItem.Icon'):
  E.SubElement(image,'value',condition='!String.IsEmpty('+field+')').text='$INFO['+field+']'
 E.SubElement(image,'value').text=''
 return [marker,image]

def upgrade(files):
 from widget_skin78 import parse
 from widget_skin80 import digest
 result=dict(files)
 for name,expected in (('xml/IncludesHomeWidgets.xml',definitions(files)),('xml/IncludesVariables.xml',variables())):
  root=parse(result[name]);add=[]
  for node in expected:
   existing=root.findall(node.tag+"[@name='"+node.get('name')+"']")
   if existing:
    if len(existing)!=1 or digest(existing[0])!=digest(node):raise ValueError('SIX_ROWS_UNVERIFIED')
   else:add.append(E.tostring(node,encoding='utf-8'))
  if add:
   at=result[name].rfind(b'</includes>');result[name]=result[name][:at]+b'\n'.join(add)+result[name][at:]
 return result
