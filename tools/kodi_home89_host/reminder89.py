"""Native Linux two-button/remote proof. This is NOT Android acceptance."""
import json,threading,time
from pathlib import Path

def run(portal,rows,pump,capture,cold,check,home):
 import xbmc,xbmcgui,reminder_ui89 as ui,reminder_runtime89 as runtime
 from guide_timers import db
 failures=[];result={};done=threading.Event()
 def data89(fn):
  def work():
   try:
    # Separate positive-capacity fixture phase. The inherited 27MiB test and
    # the real 32MiB timer reserve remain unchanged and already deny writes.
    # Only this synthetic profile's timer/bookmark worker sees 218MiB here.
    import shutil
    from types import SimpleNamespace
    from utils import addon_data_dir
    original=shutil.disk_usage
    def measured(path):
     value=original(path)
     return SimpleNamespace(total=4034297856,used=4034297856-228114432,free=228114432) if Path(path)==Path(addon_data_dir()) else value
    shutil.disk_usage=measured
    try:fn()
    finally:shutil.disk_usage=original
   except Exception as exc:failures.append(type(exc).__name__)
   finally:done.set()
  done.clear();lane=threading.Thread(target=work);lane.start();end=time.monotonic()+8
  while not done.is_set() and time.monotonic()<end:xbmc.sleep(25)
  check(done.is_set() and not failures,('REMINDER89_WORKER_FAILED',failures));lane.join(.1)
 if cold:
  data89(lambda:runtime.worker())
  check(not runtime.read('Ready'),'REMINDER89_REPLAY_AFTER_RESTART')
  return dict(status='PASS',restart_no_duplicate=True,android='ANDROID_NOT_TESTED')
 event=dict(pid=str(portal['id']),sid=str(rows[0]['sid']),title='Native reminder fixture',start=int(time.time())+600,stop=int(time.time())+1800)
 def prepare():
  from programme_actions88 import toggle
  toggle(event);runtime.worker(now=event['start']-299)
 data89(prepare);ready=runtime.read('Ready');check(bool(ready.get('nonce')),'REMINDER89_READY_MISSING')
 ui.poll();end=time.monotonic()+8
 while time.monotonic()<end:
  xbmc.sleep(50)
  if ui._dialog and ui._dialog.native89 is not None:break
 check(ui._dialog is not None and ui._dialog.getFocusId()==611,'REMINDER89_DEFAULT_DISMISS_MISSING')
 labels=[ui._dialog.getControl(cid).getLabel() for cid in (610,611)]
 check(all(labels) and len(set(labels))==2,('REMINDER89_BUTTON_LABELS_MISSING',labels))
 picture,_=capture('visible84-reminder89-two-actions')
 xbmc.executebuiltin('Action(Select)',wait=False);end=time.monotonic()+5
 while time.monotonic()<end:
  ui.poll();xbmc.sleep(25)
  if runtime.read('Choice'):break
 check(runtime.read('Choice').get('choice')=='dismiss','REMINDER89_REMOTE_DISMISS_FAILED')
 data89(lambda:runtime.worker(now=event['start']-298));ui.poll()
 check(ui._dialog is None and ui._tune is None,'REMINDER89_UNWANTED_TUNE_OR_DIALOG')
 def verify():
  conn=db()
  try:result['state']=conn.execute('SELECT state FROM timers WHERE id=?',(ready['id'],)).fetchone()[0]
  finally:conn.close()
  from guide_bookmarks import entries
  result['bookmark_retained']=any(str(v['sid'])==event['sid'] and v['start']==event['start'] for v in entries(event['pid']))
 data89(verify);check(result['state']=='dismissed' and result['bookmark_retained'],'REMINDER89_DURABLE_DISMISS_MISSING')
 result.update(status='PASS',exactly_two_actions=labels,default_focus=611,native_remote_select=True,screenshot=picture.name,selected_free_injection=228114432,timer_reserve=32*1024**2,android='ANDROID_NOT_TESTED')
 Path('/root/reminder89.json').write_text(json.dumps(result));print('REMINDER89_RECEIPT '+json.dumps(result),flush=True)
 return result
