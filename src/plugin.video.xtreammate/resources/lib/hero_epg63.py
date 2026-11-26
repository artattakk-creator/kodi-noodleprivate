"""RAM-only focus; the worker reads the existing exact event/art cache, never HTTP."""
import threading,time
_lock=threading.Lock();_focus=None;_selection=None;_art=None;_next=0;_last=None;_focused_at=0.;_labels=None

def _clear_focus():
    global _focus,_selection,_art
    if _focus is not None:
        with _lock:_focus=None;_selection=None;_art=None
        import xbmcgui
        xbmcgui.Window(10000).setProperty('XCMate.Hero86.Pending','')

def poll():
    global _focus,_selection,_art,_next,_last,_focused_at
    import xbmc,xbmcgui
    if time.monotonic()<_next:return
    _next=time.monotonic()+.1
    try:eligible=xbmc.getSkinDir()=='skin.titan.bingie.mod' and xbmcgui.getCurrentWindowId()==10000
    except (AttributeError,RuntimeError):return
    if not eligible:_clear_focus();return
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    label=lambda name:xbmc.getInfoLabel('ListItem.Property('+name+')')
    if label('XCMate.Home50')!='true' or label('XCMate.WidgetKind41') not in ('','live'):
        _clear_focus();return
    pid,sid,token=label('XCMate.PortalId'),label('XCMate.MediaId'),label('XCMate.WidgetToken41')
    if not pid or not sid or len(token)!=32:_clear_focus();return
    from epg_handoff63 import get,note,profile_scope,state
    from epg_views import guide_for_channel
    from live_text63 import apply
    from programme_events46 import visible
    from programme_requests68 import identity,request,result
    from programme_image69 import eligible as admit_art
    scope=profile_scope();current=(pid,sid,token,scope)
    info=get(pid,sid)
    intent68=visible(dict(id=pid),dict(sid=sid),info) if info and info.get('now') else None
    if intent68 and not intent68.get('title'):intent68=None
    selection=(current,identity(intent68)) if intent68 else None
    with _lock:
        changed=_focus!=current;_focus=current
        selection_changed=_selection!=selection
        if selection_changed:_selection=selection;_art=None
        art=dict(_art) if _art else {}
    if selection_changed:xbmcgui.Window(10000).setProperty('XCMate.Hero86.Pending','')
    if changed:_focused_at=time.monotonic();note('HOME_FOCUS',pid,sid)
    status482={}
    if intent68:
        status482=result(intent68,art)
        if not admit_art(status482,intent68):
            request(intent68,priority=True)
            status482=result(intent68)
        art=status482 if admit_art(status482,intent68) else {}
    if not info:
        from epg_row64 import valid as row_valid64
        fallback_window=xbmcgui.Window(10000)
        if row_valid64(label,fallback_window,pid,sid,scope):
            # Do not replace an already verified local row by a cache-miss label.
            # Native row fields remain current; no other sender/profile is read.
            if fallback_window.getProperty('XCMate.Hero63.Active'):fallback_window.setProperty('XCMate.Hero63.Active','')
            _last=None
            note('HOME_NOW_NEXT_READY',pid,sid,'READY',(time.monotonic()-_focused_at)*1000)
            return
    info=info or guide_for_channel({})
    neutral=''
    key=label('XCMate.ProgrammeKey47')
    props={'XCMate.Provisional85':label('XCMate.Provisional85'),'XCMate.ProgrammeKey47':key,'XCMate.ProgrammeImage46':label('XCMate.ProgrammeImage46') or neutral,
           'XCMate.ProgrammeArtSource57':label('XCMate.ProgrammeArtSource57'),
           'XCMate.ProgrammeImageScope57':label('XCMate.ProgrammeImageScope57'),
           'XCMate.FallbackLabel63':label('XCMate.FallbackLabel63'),'XCMate.ArtProof69':label('XCMate.ArtProof69')}
    props.update({'XCMate.PortalId':pid,'XCMate.MediaId':sid,'XCMate.ProgrammeLogo46':label('XCMate.ProgrammeLogo46'),
                  'XCMate.LogoProof88':label('XCMate.LogoProof88'),'XCMate.LogoSource88':label('XCMate.LogoSource88'),'XCMate.LogoProof84':label('XCMate.LogoProof84'),'XCMate.LogoProof86':label('XCMate.LogoProof86')})
    if intent68 and intent68.get('_agent_event104'):
        from programme_image69 import unpack
        proof=unpack(props['XCMate.ArtProof69'],intent68)
        if proof.get('scope69')!=selection[1]:
            for name in ('ProgrammeImage46','ProgrammeArtSource57','ProgrammeImageScope57','ArtProof69','Provisional85'):
                props['XCMate.'+name]=''
    labels=(label('XCMate.NoEpg63'),label('XCMate.RemainingFormat63'))
    if not all(labels):labels=_labels
    if not labels:return  # Static native ListItem remains usable until the worker warms labels.
    apply(dict(props=props),dict(id=pid),dict(sid=sid),info,event=intent68,labels=labels)
    event_key=info.get('programme_key47','')
    if art.get('key')==event_key and admit_art(art,intent68):
        props['XCMate.Provisional85']='true' if art.get('provisional85') or art.get('match')=='PROVISIONAL_TV85' else ''
        if props['XCMate.Provisional85']=='true' and not props['XCMate.ProgrammeDescription46'].startswith('Bildvorschlag – Zuordnung nicht bestätigt'):props['XCMate.ProgrammeDescription46']='Bildvorschlag – Zuordnung nicht bestätigt.\n'+props['XCMate.ProgrammeDescription46']
        props['XCMate.ProgrammeImage46']=props['XCMate.HeroImage63']=art['image'];props['XCMate.ProgrammeArtSource57']=props['XCMate.HeroArtSource63']=art.get('source','')
        if art.get('image_scope57')=='series_fallback' and props.get('XCMate.FallbackLabel63'):
            note63=props['XCMate.FallbackLabel63']
            if not props['XCMate.ProgrammeDescription46'].startswith(note63):props['XCMate.ProgrammeDescription46']=note63+'\n'+props['XCMate.ProgrammeDescription46']
    values=dict(Title=props['XCMate.ProgrammeTitle46'],Times=props['XCMate.ProgrammeTimes46'],
        Next=props['XCMate.ProgrammeNext46'],NextTimes=props['XCMate.ProgrammeNextTimes48'],
        Description=props['XCMate.ProgrammeDescription46'],Remaining=props['XCMate.ProgrammeRemaining63'],
        Subtitle=props['XCMate.ProgrammeSubtitle63'] or (label('XCMate.ProgrammeSubtitle63') if key==event_key else ''),
        Percent=props['XCMate.ProgrammePercent46'],Image=props.get('XCMate.HeroImage63',neutral),
        ArtSource=props.get('XCMate.HeroArtSource63',''),Facts=props.get('XCMate.ProgrammeFacts75',''),LongTitle='true' if len(props['XCMate.ProgrammeTitle46'])>26 else 'false')
    values['Provisional85']=props.get('XCMate.Provisional85','')
    # The existing description binding already reaches installed Home skins.
    # Keep status event-bound, without a new skin install or a new renderer.
    from programme_state482 import code as state_code482,text as state_text482
    values['ArtStatus']=state_code482(status482) if intent68 else ''
    values['ArtStatusText']=state_text482(status482) if intent68 else ''
    if values['ArtStatusText']:values['Description']=values['ArtStatusText']+'\n'+values['Description']
    values['Rating88']=__import__('programme_actions88').rating(art)
    # .86 typed/hysteretic commit; pending textures never blank a current bank.
    if xbmcgui.Window(10000).getProperty('XCMate.Home86.IdentityReady')=='true':
        values=__import__('hero_render86').choose(intent68,art,values,xbmcgui.Window(10000))
    else:
        # Keep a previously displayed local texture behind an atomic same-event
        # upgrade. Never carry it across channel, mapping, edition or opt-out.
        from event_art81 import key as event_identity81,allowed as source_allowed81
        event81=event_identity81(intent68) if intent68 else ''
        active81=xbmcgui.Window(10000);bank81=active81.getProperty('XCMate.Hero63.Active')
        prefix81='XCMate.Hero63.'+bank81+'.'
        same81=bool(event81 and active81.getProperty('XCMate.Hero81.Event')==event81)
        prior_image81=active81.getProperty(prefix81+'Image');prior_source81=active81.getProperty(prefix81+'ArtSource')
        if same81 and prior_image81.startswith('/') and source_allowed81(dict(source=prior_source81)):
            if not values['Image']:values['Image']=prior_image81;values['ArtSource']=prior_source81;values['Provisional85']=active81.getProperty(prefix81+'Provisional85')
            elif values['Image']!=prior_image81 and active81.getProperty('XCMate.Hero81.PreviousImage')!=prior_image81:active81.setProperty('XCMate.Hero81.PreviousImage',prior_image81)
        elif active81.getProperty('XCMate.Hero81.PreviousImage'):active81.setProperty('XCMate.Hero81.PreviousImage','')
        if active81.getProperty('XCMate.Hero81.Event')!=event81:active81.setProperty('XCMate.Hero81.Event',event81)

    signature=(current,tuple(values.items()),selection)
    if signature==_last:return
    if (label('XCMate.PortalId'),label('XCMate.MediaId'),label('XCMate.WidgetToken41'))!=current[:3]:return
    previous=_last
    window=xbmcgui.Window(10000)
    bank='B' if window.getProperty('XCMate.Hero63.Active')=='A' else 'A'
    # Double-buffer the entire presentation. Switch only after all fields and
    # identity are ready; no blank frame or previous station's mixed text.
    prefix='XCMate.Hero63.'+bank+'.'
    # Kodi21 GetInt does not support Window.Property info labels. Send a
    # numeric message to the inactive own progress control before bank commit.
    try:__import__('home_runtime77').control(window,296301 if bank=='A' else 296302).setPercent(float(values['Percent']))
    except (AttributeError,RuntimeError,ValueError):
        # A missing optional progress control must not discard an otherwise
        # coherent text/image bank. The skin may use a property-based fallback.
        values['ProgressControl']='UNAVAILABLE'
    else:values['ProgressControl']='READY'
    for name,value in values.items():window.setProperty(prefix+name,str(value))
    window.setProperty(prefix+'Profile',scope)
    window.setProperty(prefix+'Identity',token)
    from home_runtime77 import publish as render77
    render77(window,dict(intent68,key=event_key) if intent68 else None,values['Image'])
    window.setProperty('XCMate.Hero63.Active',bank)
    if intent68:__import__('art_trace81').note(intent68,'BANK_SWITCHED','TEXT_AND_IMAGE_COMMITTED',
        source=values['ArtSource'],role=art.get('role81') if art.get('image')==values['Image'] else '')
    _last=signature
    if changed or previous is None or previous[1][0]!=signature[1][0]:
        note('HOME_NOW_NEXT_READY',pid,sid,'READY' if info.get('now') else state(pid,sid),(time.monotonic()-_focused_at)*1000,facts=info)

def prepare(pid):
    global _art,_labels
    from localization import tr
    _labels=(tr(36102),tr(36668,'{0}'))
    with _lock:focus=_focus;selection=_selection
    if not focus or not selection or focus[0]!=str(pid):return
    from epg_handoff63 import get
    info=get(pid,focus[1])
    if not info or not info.get('now'):return
    from programme_events46 import visible
    from programme_art46 import cached
    event=visible(dict(id=str(pid)),dict(sid=focus[1]),info)
    from programme_requests68 import identity,result
    if (focus,identity(event))!=selection:return
    def current():
        with _lock:return _selection==selection
    art=result(event,cached(event))
    durable81=__import__('event_art81').prior(event)
    if durable81 and (not __import__('programme_lastgood80').positive(event,art) or __import__('event_art81').rank(durable81)<__import__('event_art81').rank(art)):art=durable81
    __import__('hero_render86').prepare(event,art or {},still_current=current)
    with _lock:previous=_art if _selection==selection else None
    art=__import__('programme_lastgood80').choose(event,art,previous,check_file=True)
    with _lock:
        if _selection==selection:_art=art


def focused64(pid):
    from epg_handoff63 import profile_scope
    with _lock:focus=_focus
    return focus[1] if focus and focus[0]==str(pid) and focus[3]==profile_scope() else ''
