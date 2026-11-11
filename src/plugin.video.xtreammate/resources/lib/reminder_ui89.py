"""Nonblocking two-action native reminder, pumped only by the service owner.

Worker persists choice before this window closes. No background dialog, Snooze,
auto-tune, player replacement, keymap edit or foreign-modal dismissal.
"""
import json,time
import xbmc,xbmcgui
from localization import tr
from reminder_runtime89 import read,put
_dialog=None;_tune=None;_verify=None
class ReminderDialog89(xbmcgui.WindowXMLDialog):
 def configure(self,row):self.row=dict(row);self.choice=None;self.sent=False;self.native89=None;self.opened=time.monotonic()
 def onInit(self):
  self.native89=xbmcgui.getCurrentWindowDialogId()
  self.getControl(601).setLabel(tr(37154));self.getControl(602).setLabel(str(self.row['channel'])[:160]);self.getControl(603).setText(str(self.row['title'])[:512]+'\n'+time.strftime('%H:%M',time.localtime(self.row['start'])))
  self.getControl(610).setLabel(tr(37152));self.getControl(611).setLabel(tr(37153));self.setFocusId(611)
 def onClick(self,cid):
  if self.choice is None and cid in (610,611):self.choice='switch' if cid==610 else 'dismiss'
 def onAction(self,action):
  if action.getId() in (9,10,92) and self.choice is None:self.choice='dismiss'
 def pump89(self):
  if self.choice is None and (time.monotonic()-self.opened>=120 or self.native89 is not None and xbmcgui.getCurrentWindowDialogId()!=self.native89):self.choice='dismiss'
  if self.choice is not None and not self.sent:
   put('Choice',dict(nonce=self.row['nonce'],choice=self.choice));self.sent=True
   try:self.getControl(604).setLabel(tr(37157));self.getControl(610).setEnabled(False);self.getControl(611).setEnabled(False)
   except (AttributeError,RuntimeError):pass

def poll():
 global _dialog,_tune,_verify
 if _verify:
  from live_overlay import session_from_property
  from reminder_runtime89 import window
  session=session_from_property(window().getProperty('XtreamMate.LiveSession'))
  if session and str(session.get('pid'))==_verify['pid'] and str(session.get('sid'))==_verify['sid']:_verify=None
  elif time.monotonic()>_verify['deadline']:
   xbmcgui.Dialog().notification('XCMate',tr(37156));_verify=None
 if _dialog is not None:
  _dialog.pump89();ack=read('Ack')
  if ack.get('nonce')!=_dialog.row['nonce']:return
  row=_dialog.row
  try:_dialog.close()
  except (AttributeError,RuntimeError):pass
  _dialog=None
  if ack.get('choice')=='switch' and ack.get('code')=='SWITCH_REQUESTED' and ack.get('pid')==str(row['pid']) and ack.get('sid')==str(row['sid']):_tune=dict(ack,after=time.monotonic()+.2,deadline=time.monotonic()+12)
  elif ack.get('code')=='CHANNEL_UNAVAILABLE':xbmcgui.Dialog().notification('XCMate',tr(37156))
  return
 if _tune:
  if time.monotonic()<_tune['after']:return
  from exit_jobs import blocked
  if blocked() or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('System.HasActiveModalDialog'):
   if time.monotonic()>_tune['deadline']:xbmcgui.Dialog().notification('XCMate',tr(37156));_tune=None
   return
  # Exact existing resolver route, as used by guide_playback. No stream URL,
  # credentials, separate player or implicit stop appears in the reminder.
  from urllib.parse import urlsplit,parse_qs
  value=_tune;_tune=None;p=urlsplit(value.get('url',''));q=parse_qs(p.query)
  if p.scheme=='plugin' and p.netloc=='plugin.video.xtreammate' and q.get('action') in (['play_live'],['source_play']) and q.get('pid')==[value['pid']] and q.get('sid')==[value['sid']]:
   xbmc.executebuiltin('PlayMedia('+value['url']+')',wait=False);_verify=dict(pid=value['pid'],sid=value['sid'],deadline=time.monotonic()+12)
  else:xbmcgui.Dialog().notification('XCMate',tr(37156))
  return
 row=read('Ready')
 if not row or not row.get('nonce'):return
 if row.get('stop',0)<=time.time():put('Choice',dict(nonce=row['nonce'],choice='dismiss'));return
 if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('System.HasActiveModalDialog'):return
 from exit_jobs import blocked
 if blocked():return
 import xbmcaddon
 dialog=ReminderDialog89('XCMateReminder89.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p');dialog.configure(row)
 _dialog=dialog
 try:dialog.show()
 except (AttributeError,RuntimeError):_dialog=None;put('Choice',dict(nonce=row['nonce'],choice='dismiss'))
