"""Read-only installed-skin capability report, never assumes Android rendering."""
import os,xml.etree.ElementTree as ET

def inspect_file(filename,version):
 if version!='2.2.3':return dict(code='BLOCKED_UNVERIFIED_SKIN',overlay=False,focus=False)
 try:
  if os.path.islink(filename) or os.path.getsize(filename)>2*1024*1024:raise ValueError()
  with open(filename,'rb') as f:data=f.read(2*1024*1024+1)
  if b'<!DOCTYPE' in data or b'<!ENTITY' in data:raise ValueError()
  tree=ET.fromstring(data);groups=tree.findall('.//control[@xcmate-programme46="true"]')
  overlays=[g for g in groups if 'XCMate.ProgrammeLogo46' in ET.tostring(g,encoding='unicode') and 'XCMate.ProgrammePercent46' in ET.tostring(g,encoding='unicode')]
  focus=[g for g in groups if 'XCMate.ProgrammeDescription46' in ET.tostring(g,encoding='unicode')]
  ready=len(overlays)==12 and len(focus)==8
  return dict(code='STATIC_BINDINGS_PRESENT_ANDROID_NOT_TESTED' if ready else 'BLOCKED_NO_OVERLAY_FOCUS_BINDING',overlay=len(overlays)==12,focus=len(focus)==8)
 except (OSError,ValueError,ET.ParseError):return dict(code='BLOCKED_LAYOUT_UNAVAILABLE',overlay=False,focus=False)

def probe():
 try:
  import xbmc,xbmcaddon
  if xbmc.getSkinDir()!='skin.titan.bingie.mod':return dict(code='BLOCKED_OTHER_SKIN',overlay=False,focus=False)
  skin=xbmcaddon.Addon('skin.titan.bingie.mod');return inspect_file(os.path.join(skin.getAddonInfo('path'),'xml','IncludesHomeWidgets.xml'),skin.getAddonInfo('version'))
 except (ImportError,AttributeError,RuntimeError):return dict(code='BLOCKED_LAYOUT_UNAVAILABLE',overlay=False,focus=False)
