"""GUI-only native control evidence; missing controls are negatively cached.

No skin files, SQL, HTTP or false texture success. All image/text publication
continues even when the optional adapter/progress control is missing.
"""
import json,time
_missing={}
KEY='XCMate.Home77.Render'
def control(window,ident):
    from epg_handoff63 import profile_scope
    key=(profile_scope(),ident);now=time.monotonic()
    if now<_missing.get(key,0):raise RuntimeError('CONTROL_MISSING_CACHED77')
    try:value=window.getControl(ident)
    except (RuntimeError,AttributeError):
        _missing[key]=now+5
        while len(_missing)>64:_missing.pop(next(iter(_missing)))
        raise
    _missing.pop(key,None);return value

def publish(window,event=None,image='',control_id=296751):
    import xbmc
    if control_id==296751:
        try:
            if xbmc.getCondVisibility('Control.IsVisible(296784)'):control_id=296784
            elif xbmc.getCondVisibility('Control.IsVisible(296783)'):control_id=296783
        except (AttributeError,RuntimeError,KeyError):pass
    result=dict(control=control_id,code='CONTROL_MISSING',image_bound=False,visible=False)
    try:
        obj=control(window,control_id)
        x,y=obj.getPosition();result.update(x=x,y=y,width=obj.getWidth(),height=obj.getHeight(),code='CONTROL_READY',image_bound=bool(image),visible=bool(xbmc.getCondVisibility('Control.IsVisible('+str(control_id)+')')))
    except (AttributeError,RuntimeError,ValueError):pass
    window.setProperty(KEY,json.dumps(result,separators=(',',':')))
    if event:
        from programme_pipeline77 import note
        note(event,'BINGIE_SKIN_PROPERTY','BOUND' if image else 'SOURCE_MISSING')
        note(event,'RENDER_CONTROL','IMAGE_REQUESTED' if result['code']=='CONTROL_READY' and image else 'CONTROL_MISSING' if result['code']=='CONTROL_MISSING' else 'SOURCE_MISSING',control=control_id,visible=result['visible'])
    return result
