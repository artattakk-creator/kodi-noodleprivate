"""Authorized .80 repair of the exact installed own adapter, worker only."""
import time
_next=0

def prepare():
 global _next
 if time.monotonic()<_next:return
 _next=time.monotonic()+60
 import xbmc,xbmcgui,xbmcvfs
 from utils import setting_bool
 if xbmc.getSkinDir()!='skin.titan.bingie.mod' or setting_bool('home78_repair_optout',False):return
 if xbmc.getCondVisibility('Player.HasMedia') or xbmc.getCondVisibility('System.HasActiveModalDialog') or xbmcgui.Window(10000).getProperty('skinshortcuts-isrunning').lower()=='true':return
 from pathlib import Path
 skin=Path(xbmcvfs.translatePath('special://skin/'))
 from widget_skin78 import installed,prepare as plan,apply
 from widget_skin80 import MARKER
 try:
  if not installed(skin) or MARKER in (skin/'xml/IncludesVariables.xml').read_bytes():return
  candidate=plan(skin);apply(candidate['id'],skin,confirmed=True)
  __import__('home_activation78').request(candidate['id'],consumers_changed=True)
 except (OSError,ValueError,RuntimeError,KeyError):return
