"""RAM-only focus; the worker reads the existing exact event/art cache, never HTTP."""
import os,threading,time
_lock=threading.Lock();_focus=None;_art=None;_next=0;_last=None;_focused_at=0.;_labels=None

def poll():
    global _focus,_next,_last,_focused_at
    import xbmc,xbmcgui,xbmcaddon
    if time.monotonic()<_next:return
    _next=time.monotonic()+.1
    try:eligible=xbmc.getSkinDir()=='skin.titan.bingie.mod' and xbmcgui.getCurrentWindowId()==10000
    except (AttributeError,RuntimeError):return
    if not eligible:return
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    label=lambda name:xbmc.getInfoLabel('ListItem.Property('+name+')')
    if label('XCMate.Home50')!='true':return
    pid,sid,token=label('XCMate.PortalId'),label('XCMate.MediaId'),label('XCMate.WidgetToken41')
    if not pid or not sid or len(token)!=32:return
    from epg_handoff63 import get,note,profile_scope,state
    from epg_views import guide_for_channel
    from live_text63 import apply,local_image
    scope=profile_scope();current=(pid,sid,token,scope)
    with _lock:
        changed=_focus!=current;_focus=current;art=dict(_art) if _art else {}
    if changed:_focused_at=time.monotonic();note('HOME_FOCUS',pid,sid)
    info=get(pid,sid) or guide_for_channel({})
    neutral=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','programme46','neutral.png')
    key=label('XCMate.ProgrammeKey47')
    props={'XCMate.ProgrammeKey47':key,'XCMate.ProgrammeImage46':label('XCMate.ProgrammeImage46') or neutral,
           'XCMate.ProgrammeArtSource57':label('XCMate.ProgrammeArtSource57'),
           'XCMate.ProgrammeImageScope57':label('XCMate.ProgrammeImageScope57'),
           'XCMate.FallbackLabel63':label('XCMate.FallbackLabel63')}
    labels=(label('XCMate.NoEpg63'),label('XCMate.RemainingFormat63'))
    if not all(labels):labels=_labels
    if not labels:return  # Static native ListItem remains usable until the worker warms labels.
    apply(dict(props=props),dict(id=pid),dict(sid=sid),info,labels=labels)
    event_key=info.get('programme_key47','')
    if art.get('profile63')==scope and art.get('key')==event_key and art.get('code') in ('READY','READY_STALE') and art.get('source')!='placeholder' and local_image(art.get('image','')):
        props['XCMate.ProgrammeImage46']=art['image'];props['XCMate.ProgrammeArtSource57']=art.get('source','')
        if art.get('image_scope57')=='series_fallback' and props.get('XCMate.FallbackLabel63'):
            note63=props['XCMate.FallbackLabel63']
            if not props['XCMate.ProgrammeDescription46'].startswith(note63):props['XCMate.ProgrammeDescription46']=note63+'\n'+props['XCMate.ProgrammeDescription46']
    values=dict(Title=props['XCMate.ProgrammeTitle46'],Times=props['XCMate.ProgrammeTimes46'],
        Next=props['XCMate.ProgrammeNext46'],NextTimes=props['XCMate.ProgrammeNextTimes48'],
        Description=props['XCMate.ProgrammeDescription46'],Remaining=props['XCMate.ProgrammeRemaining63'],
        Subtitle=label('XCMate.ProgrammeSubtitle63') if key==event_key else '',
        Percent=props['XCMate.ProgrammePercent46'],Image=props.get('XCMate.ProgrammeImage46',neutral),
        ArtSource=props.get('XCMate.ProgrammeArtSource57',''))
    signature=(current,tuple(values.items()))
    if signature==_last:return
    previous=_last
    window=xbmcgui.Window(10000)
    bank='B' if window.getProperty('XCMate.Hero63.Active')=='A' else 'A'
    # Double-buffer the entire presentation. Switch only after all fields and
    # identity are ready; no blank frame or previous station's mixed text.
    prefix='XCMate.Hero63.'+bank+'.'
    # Kodi21 GetInt does not support Window.Property info labels. Send a
    # numeric message to the inactive own progress control before bank commit.
    try:window.getControl(296301 if bank=='A' else 296302).setPercent(float(values['Percent']))
    except (AttributeError,RuntimeError,ValueError):return  # Layout is not ready; retry next UI tick.
    for name,value in values.items():window.setProperty(prefix+name,str(value))
    window.setProperty(prefix+'Profile',scope)
    window.setProperty(prefix+'Identity',token)
    window.setProperty('XCMate.Hero63.Active',bank)
    _last=signature
    if changed or previous is None or previous[1][0]!=signature[1][0]:
        note('HOME_NOW_NEXT_READY',pid,sid,'READY' if info.get('now') else state(pid,sid),(time.monotonic()-_focused_at)*1000,facts=info)

def prepare(pid):
    global _art,_labels
    from localization import tr
    _labels=(tr(36102),tr(36668,'{0}'))
    with _lock:focus=_focus
    if not focus or focus[0]!=str(pid):return
    from epg_handoff63 import get
    info=get(pid,focus[1])
    if not info or not info.get('now'):return
    from programme_events46 import from_info
    from programme_art46 import cached
    event=from_info(dict(id=str(pid)),dict(sid=focus[1]),info)
    art=cached(event)
    with _lock:
        if _focus==focus:_art=dict(art,key=event['key'],profile63=focus[3])
