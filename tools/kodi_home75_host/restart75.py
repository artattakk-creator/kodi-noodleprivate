"""Disposable native Kodi process restart; never connects to a user's device."""
import hashlib,json,os,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
    payload=dict(jsonrpc='2.0',id=75,method=method,params=params or {})
    request=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(payload).encode(),{'Content-Type':'application/json'})
    with opener.open(request,timeout=15) as response:result=json.load(response)
    if 'error' in result:raise RuntimeError(str(result['error']))
    return result['result']
def protected():
    root=Path('/root/.kodi');files=[root/'userdata/addon_data/plugin.video.xtreammate/portals.json']
    files.extend(sorted((root/'userdata/addon_data/script.skinshortcuts').glob('*')))
    files.extend(sorted((root/'addons/skin.titan.bingie.mod/xml').glob('Includes*.xml')))
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
before=protected()
if 'userdata/addon_data/plugin.video.xtreammate/portals.json' not in before:raise RuntimeError('POST75_NO_PORTAL_BASELINE')
def kodi_pids():
    result=set()
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:command=(path/'cmdline').read_bytes().split(b'\0')[0]
        except OSError:continue
        if command==b'/usr/lib/x86_64-linux-gnu/kodi/kodi.bin':result.add(int(path.name))
    return result
# The renderer report is written before runpy unwinds its native WindowXML
# objects. Await the fixture's explicit return/GC receipt before Kodi Quit.
receipt87=Path('/root/native-fixture-returned87')
for _ in range(100):
    if receipt87.exists():break
    time.sleep(.05)
else:raise RuntimeError('POST87_INITIAL_SCRIPT_NOT_RETURNED')
receipt87.unlink()
old_pids=kodi_pids()
if not old_pids:raise RuntimeError('POST75_NO_INITIAL_KODI_PROCESS')
# Only this synthetic test script changes; all add-on/profile/skin files remain.
main=Path('/root/.kodi/addons/script.xcmate.guicontract59/main.py')
main.write_text("import runpy,traceback,gc\nfrom pathlib import Path\ntry:\n runpy.run_path('/root/post75.py')\n gc.collect()\n Path('/root/native-fixture-returned87').write_text('RETURNED')\nexcept Exception:\n Path('/root/post75-error.txt').write_text(traceback.format_exc(),encoding='utf-8')\n raise\n")
rpc('Application.Quit')
for _ in range(600):
    if not kodi_pids().intersection(old_pids):break
    time.sleep(.1)
else:raise RuntimeError('POST75_OLD_KODI_NOT_EXITED')
for _ in range(150):
    try:
        if not kodi_pids():raise RuntimeError('POST75_NEW_PROCESS_PENDING')
        rpc('JSONRPC.Ping');break
    except Exception:time.sleep(.2)
else:raise RuntimeError('POST75_RESTART_NO_KODI')
rpc('GUI.ActivateWindow',{'window':'home'});time.sleep(2)
rpc('Addons.ExecuteAddon',{'addonid':'script.xcmate.guicontract59'})
# .87 replays three media/hero cases plus thirteen independent rows; the
# legacy .79 cold probe covered two cached pictures only. This bounded test
# harness budget never changes any packaged Save/Stop/UI production timeout.
gui_budget87=max(120,min(240,int(os.environ.get('XCMATE_GUI_RESTART_TIMEOUT87','120'))))
for _ in range(gui_budget87*10):
    if Path('/root/post75-error.txt').exists():raise RuntimeError(Path('/root/post75-error.txt').read_text(encoding='utf-8'))
    if Path('/root/post75.json').exists():break
    time.sleep(.1)
else:raise RuntimeError('POST75_GUI_TIMEOUT')
if protected()!=before:raise RuntimeError('POST75_PROTECTED_FILES_CHANGED')
result=json.loads(Path('/root/post75.json').read_text())
result.update(protected_files=len(before),protected_sha256='PASS',restart='native Application.Quit + supervised Kodi restart',old_pids=sorted(old_pids),new_pids=sorted(kodi_pids()))
Path('/root/post75.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
