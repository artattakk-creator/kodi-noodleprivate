"""VOD origin stays in its native owner; only opaque intent crosses interpreters.

No URL/query/row serialization, profile writes or root/directory reload. The
owner pump re-shows the same live WindowXML after asynchronous Stop completes.
Foreign playback/dialogs and a replaced origin always fail closed.
"""
import copy,json,time
KEY='XCMate.MediaOrigin39'
FIELDS=('mode','kind','category','offset','rows','total','selected','groups','_previous',
        '_grid_return','_return_focus','episodes','next_episode','season','seasons',
        '_positions','_mode_focus','_search_kind','_search_offset','_search_selected',
        '_search_query','_search_rows','_search_detail','_season_cursor','_episode_cursor')


def marker():
    import xbmcgui
    return xbmcgui.Window(10000)


def read():
    try:
        raw=marker().getProperty(KEY);value=json.loads(raw) if raw and len(raw)<2048 else None
        if isinstance(value,dict) and 0<=time.time()-value.get('at',0)<86400:return value
    except (ValueError,TypeError,RuntimeError):pass
    return None


def capture(view,nonce):
    from window_lifecycle import capture as native_reference
    positions={}
    for cid in (110,111,112,200,210,300,330,710):
        try:positions[cid]=view.getControl(cid).getSelectedPosition()
        except (AttributeError,RuntimeError,KeyError):pass
    view._playback_origin39=dict(values={k:copy.deepcopy(getattr(view,k)) for k in FIELDS if hasattr(view,k)},
                                 positions=positions,focus=view.getFocusId(),native=native_reference(view))
    value=dict(pid=str(view.portal['id']),nonce=nonce,owner=view._native_owner,at=time.time(),requested=False)
    marker().setProperty(KEY,json.dumps(value))


def request(token):
    if not token or token[0]!='media':return False
    value=read();session=token[1]
    if not value or value['pid']!=session['pid'] or value['nonce'] not in (session['nonce'],session.get('autoplay_chain')):return False
    import xbmc
    from stream_details import own
    player=xbmc.Player()
    try:
        if getattr(player,'isPlaying',player.isPlayingVideo)() and not own(player,token):return False
    except (AttributeError,RuntimeError):return False
    value['requested']=True;value['not_before']=time.monotonic()+.15
    marker().setProperty(KEY,json.dumps(value));return True


def restore(view,natural=False):
    origin=getattr(view,'_playback_origin39',None);value=read()
    if not origin or not value or value.get('owner')!=view._native_owner or value.get('pid')!=str(view.portal['id']):return False
    if not natural and not value.get('requested'):return False
    if time.monotonic()<value.get('not_before',0):return False
    import xbmc,xbmcgui
    player=xbmc.Player()
    try:
        if getattr(player,'isPlaying',player.isPlayingVideo)():
            from playback_exit import identity
            token=identity(player)
            if not token or token[0]!='media' or token[1].get('pid')!=value['pid'] or value['nonce'] not in (token[1]['nonce'],token[1].get('autoplay_chain')):
                discard(view)
            return False
        from window_lifecycle import state,OWNER_PROPERTY,active
        native=state()
        if native['modal']:
            if xbmcgui.Window(native['dialog']).getProperty(OWNER_PROPERTY)!=view._native_owner:return False
    except (AttributeError,RuntimeError,ValueError,TypeError):return False
    from exit_jobs import state as exit_state
    stop=exit_state()
    if stop and stop['phase'] in ('pending','running'):return False
    for key,record in origin['values'].items():setattr(view,key,record)
    view._playback_waiting=False;view._playback_seen=False;view._playback_origin39=None
    marker().clearProperty(KEY)
    view._returning39=True
    try:
        # Reuse the exact native object on its owning Python thread.
        if not active(origin['native'],native):view.show()
        view._show(view.mode)
        if view.mode=='search' and getattr(view,'_search_data',None):view._search_ready(view._search_data,resume=True)
        else:view._refresh_art()
        for cid,pos in origin['positions'].items():view.getControl(cid).selectItem(pos)
        view.setFocusId(origin['focus'])
        if view.mode=='episodes':view._sync_episode_next()
    finally:view._returning39=False
    return True


def discard(view):
    value=read()
    if value and value.get('owner')==view._native_owner:marker().clearProperty(KEY)
    view._playback_origin39=None
