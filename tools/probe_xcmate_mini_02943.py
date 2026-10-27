"""Host-only before/after native setter counts; does not simulate Kodi renderer."""
import importlib,json,subprocess,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from test_xcmate_kodi21_overlay import OverlayLifecycleTests
BASE='451f4cf0995cc09ada4b9eb4090906320d36a9fb'

def measure(source):
    fixture=OverlayLifecycleTests(methodName='runTest');fixture.setUp()
    try:
        owner=fixture.overlay;module=types.ModuleType('mini_probe');exec(compile(source,'mini_probe','exec'),module.__dict__)
        mini=module.MiniProgramme(owner);now=time.time()
        owner.visible_channels=owner.channels;owner._highlight['channels']=0
        owner._guide.get=lambda sid:dict(programme_events=[dict(title='Programme '+str(n),start=now-10+n*100,stop=now+90+n*100) for n in range(16)])
        calls=[];maxfocus=[0]
        for control in (mini.heading,mini.hint,mini.list,*[c for row in mini.rows for c in row]):
            for method in ('setVisible','setText','setLabel','reset','addItems','selectItem'):
                if not hasattr(control,method):continue
                fn=getattr(control,method)
                def observe(*a,_fn=fn,_method=method,**kw):
                    result=_fn(*a,**kw);calls.append(_method)
                    maxfocus[0]=max(maxfocus[0],sum(h.visible for h,_,_ in mini.rows));return result
                setattr(control,method,observe)
        mini.render();mini.focus();calls.clear()
        for _ in range(200):mini.render()
        return dict(identical_render_ticks=200,native_setter_calls=len(calls),list_reset_calls=calls.count('reset'),maximum_simultaneously_visible_focus_frames=maxfocus[0])
    finally:fixture.doCleanups()

if __name__=='__main__':
    old=subprocess.check_output(['git','show',BASE+':src/plugin.video.xtreammate/resources/lib/mini_epg.py'],cwd=ROOT).decode()
    new=(ROOT/'src/plugin.video.xtreammate/resources/lib/mini_epg.py').read_text()
    print(json.dumps(dict(base=BASE,host_model_only=True,kodi_gpu_or_android_proof=False,before=measure(old),after=measure(new)),indent=2))
