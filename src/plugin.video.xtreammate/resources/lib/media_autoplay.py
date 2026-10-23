"""Service-owned episode chain. Callbacks enqueue identities; owner alone starts.

No playback-gap inference, URLs, credentials or persistent settings. A root ID
binds cancellation across resolver interpreters and each successor gets a nonce.
"""
import json
import math
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

STATE='XCMate.AutoplayState'
CANCEL='XCMate.AutoplayCancelled'
SWITCH='XCMate.AutoplaySwitch'
_ACTIVE=frozenset(('PLAYING','PREPARING','ENDED_PENDING','STARTING'))
_runtime=None


def _read(key):
    from media_intent import _read
    value=_read(key)
    return value if isinstance(value,dict) else {}


def cancelled(root,pid):
    value=_read(CANCEL)
    try:return any(root and e.get('root')==root and e.get('pid')==str(pid)
                   and 0<=time.time()-float(e.get('at',0))<86400 for e in value.get('entries',[]))
    except (ValueError,TypeError,OverflowError):return True


def view(root='',pid=''):
    value=_read(STATE)
    try:
        if not (value.get('phase') in _ACTIVE and 0<=time.time()-float(value.get('at',0))<5):return {}
    except (ValueError,TypeError,OverflowError):return {}
    if root and value.get('root')!=root or pid and value.get('pid')!=str(pid):return {}
    if cancelled(value.get('root'),value.get('pid')):return {}
    command=_read(SWITCH)
    if command.get('root')==value.get('root') and command.get('pid')==value.get('pid'):
        at=command.get('at',0)
        if isinstance(at,(float,int)) and at>value.get('command_at',0):value['enabled']=bool(command.get('enabled'))
    return value


def request_cancel(root,pid):
    """Publish Stop first, including during an unresolved next-episode launch."""
    if not root:return
    import xbmcgui
    entries=[e for e in _read(CANCEL).get('entries',[]) if isinstance(e,dict) and e.get('root')!=root][-7:]
    entries.append(dict(root=str(root),pid=str(pid),at=time.time()))
    xbmcgui.Window(10000).setProperty(CANCEL,json.dumps(dict(entries=entries)))
    value=_read(STATE)
    if value.get('root')==root and value.get('pid')==str(pid):
        from media_intent import cancel
        cancel(pid,value.get('nonce',''))


def toggle(root,pid):
    value=view(root,pid)
    if not value:return False
    # Disable cancels an already queued successor too; re-enable applies to a
    # still-playing verified episode only, never resurrects a stopped chain.
    import xbmcgui
    enabled=not value.get('enabled',True)
    command=dict(root=root,pid=str(pid),enabled=enabled,at=time.time())
    xbmcgui.Window(10000).setProperty(SWITCH,json.dumps(command))
    if not enabled and value['phase']!='PLAYING':request_cancel(root,pid)
    return enabled


def load_episodes(session):
    """Worker-only local snapshot, bound to the same active portal and series."""
    from portals import get_by_id
    from library_index import Reader
    from media_sequence import records
    portal=get_by_id(session['pid'])
    if not portal or not portal.get('enabled',True) or portal.get('type') not in ('xtream','stb'):raise ValueError('SOURCE_UNAVAILABLE')
    if not Reader(session['pid']).get('series',session['series_id']):raise ValueError('SERIES_UNAVAILABLE')
    if portal['type']=='xtream':
        from xtream import XtreamClient
        client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    else:
        from source_adapters import for_portal
        client=for_portal(portal)
    data=client._get_json('get_series_info',extra={'series_id':session['series_id']},cached_only=True) or {}
    rows=records(data,session['pid'],session['series_id'])
    if not rows:raise ValueError('EPISODES_UNAVAILABLE')
    return rows


class Events:
    """Bounded, locked callback inbox; never touches SQLite or starts playback."""
    def __init__(self):
        self.lock=threading.RLock();self.items=deque(maxlen=32);self.active=None;self.closed=False;self.overflow=False

    def av_started(self,player):
        from playback_exit import identity
        try:token=identity(player)
        except (RuntimeError,AttributeError,TypeError,ValueError):token=None
        with self.lock:
            if self.closed:return
            self.active=dict(token[1]) if token and token[0]=='media' else None
            if len(self.items)==self.items.maxlen:self.overflow=True
            self.items.append(('start',self.active))

    def terminal(self,kind,player):
        with self.lock:
            if self.closed or not self.active:return
            session=self.active
            # A duplicate terminal callback after a successor's AVStart cannot
            # end that now-playing item. Unidentified/dropped events fail closed.
            try:
                if player.isPlayingVideo():return
            except (AttributeError,RuntimeError):return
            if len(self.items)==self.items.maxlen:self.overflow=True
            self.items.append((kind,dict(session)))
            # Keep the snapshot until AVStart so Stop after Ended wins too.

    def drain(self):
        with self.lock:
            items=list(self.items);self.items.clear();return items


def observe(events):
    import xbmc
    class Observer(xbmc.Player):
        def onAVStarted(self):events.av_started(self)
        def onPlayBackEnded(self):events.terminal('ended',self)
        def onPlayBackStopped(self):events.terminal('stopped',self)
        def onPlayBackError(self):events.terminal('error',self)
    return Observer()


class Coordinator:
    def __init__(self,player,events=None,pool=None,loader=load_episodes,launch=None,abort=lambda:False,clock=time.monotonic):
        import xbmc
        self.player=player;self.events=events or Events();self.pool=pool or ThreadPoolExecutor(max_workers=1)
        self.loader=loader;self.launch=launch or xbmc.executebuiltin;self.abort=abort;self.clock=clock
        self.session=None;self.root='';self.phase='IDLE';self.enabled=True;self.future=None;self.rows=None
        self.consumed=set();self.sample=None;self.deadline=0;self.command_at=0;self.message='';self._last_publish=0;self.missing_since=None

    def _publish(self):
        if not self.session:return
        import xbmcgui
        s=self.session
        value={k:s[k] for k in ('pid','sid','series_id','season','episode','nonce') if k in s}
        value.update(root=self.root,phase=self.phase,enabled=self.enabled,at=time.time(),command_at=self.command_at)
        xbmcgui.Window(10000).setProperty(STATE,json.dumps(value));self._last_publish=self.clock()

    def finish(self,phase='CANCELLED',message=''):
        if phase=='CANCELLED' and self.session:request_cancel(self.root,self.session['pid'])
        self.phase=phase;self.message=message
        if self.future:self.future.cancel()
        self.future=None;self.rows=None;self._publish()
        if message:
            from localization import tr
            import xbmcgui
            xbmcgui.Dialog().notification('XCMate',tr(33505 if message=='SERIES_FINISHED' else 33506))

    def _start(self,session):
        if not session or session.get('kind')!='episode' or not session.get('autoplay') or not session.get('autoplay_chain'):
            if self.phase in _ACTIVE:self.finish()
            return
        from media_intent import cancelled as intent_cancelled
        if cancelled(session['autoplay_chain'],session['pid']) or intent_cancelled(session):self.finish();return
        continuing=self.root==session['autoplay_chain'] and self.phase in _ACTIVE
        if continuing and self.session and self.session['nonce']==session['nonce'] and self.phase=='PLAYING':return
        if self.future:self.future.cancel()
        self.session=dict(session);self.root=session['autoplay_chain'];self.phase='PLAYING';self.sample=None;self.missing_since=None
        if not continuing:self.enabled=True;self.consumed=set();self.command_at=0;self.rows=None
        if self.rows is None:
            snapshot=dict(session);self.future=self.pool.submit(lambda:self.loader(snapshot))
        self.deadline=self.clock()+20;self._publish()

    def _commands(self):
        value=_read(SWITCH)
        if value.get('root')==self.root and value.get('pid')==self.session['pid']:
            at=value.get('at',0)
            if isinstance(at,(float,int)) and at>self.command_at:
                self.command_at=at;self.enabled=bool(value.get('enabled'))
                if not self.enabled and self.phase in ('ENDED_PENDING','PREPARING','STARTING'):
                    request_cancel(self.root,self.session['pid']);self.finish()

    def _checkpoint(self):
        from media_progress import _current,_last
        import media_progress
        sample=self.sample
        if _current and _current.get('nonce')==self.session['nonce']:
            sample=_last or sample
            media_progress._current=media_progress._last=None
        if sample and math.isfinite(sample[1]) and sample[1]>=60:
            from media_state import save_progress
            save_progress(self.session,sample[1],sample[1])

    def tick(self):
        if self.abort():self.shutdown();return
        # Drain one complete batch. Terminal cancellation wins over Ended,
        # including the duplicate Ended/Stopped order in the same dispatch.
        batch=self.events.drain()
        for kind,session in batch:
            if kind=='start':self._start(session)
        if not self.session or self.phase not in _ACTIVE:return
        if self.events.overflow:self.events.overflow=False;self.finish();return
        self._commands()
        from media_intent import cancelled as intent_cancelled,_valid,REQUEST
        if cancelled(self.root,self.session['pid']) or intent_cancelled(self.session):self.finish();return
        if any(kind in ('stopped','error') and s and (s['nonce']==self.session['nonce'] or
                   self.phase in ('ENDED_PENDING','STARTING') and s.get('autoplay_chain')==self.root) for kind,s in batch):
            self.finish(message='PLAYBACK_FAILED' if any(k=='error' for k,s in batch) else '');return
        if self.phase not in _ACTIVE:return
        pending=_read(REQUEST)
        if _valid(pending) and pending.get('nonce')!=self.session['nonce']:self.finish();return
        from playback_exit import identity
        token=identity(self.player)
        if token:
            if token[0]!='media' or token[1]['nonce']!=self.session['nonce']:self.finish();return
            if self.phase=='PLAYING':
                try:
                    pos,dur=float(self.player.getTime()),float(self.player.getTotalTime())
                    if all(math.isfinite(v) and v>=0 for v in (pos,dur)):self.sample=pos,dur
                except (RuntimeError,TypeError,ValueError):pass
        if token:self.missing_since=None
        elif self.phase=='PLAYING':
            if self.missing_since is None:self.missing_since=self.clock()
            elif self.clock()-self.missing_since>3:
                self.finish();return  # missing terminal event never implies Ended
        if self.future and self.future.done():
            try:self.rows=self.future.result()
            except Exception:self.future=None;self.finish(message='SOURCE_UNAVAILABLE');return
            self.future=None
        ended=any(k=='ended' and s and s['nonce']==self.session['nonce'] for k,s in batch)
        if ended and self.session['nonce'] not in self.consumed and self.phase=='PLAYING':
            self.consumed.add(self.session['nonce'])
            # Keep at most the recent chain identities, regardless of length.
            if len(self.consumed)>64:self.consumed={self.session['nonce']}
            try:self._checkpoint()
            except Exception:self.finish(message='CHECKPOINT_FAILED');return
            if not self.enabled:self.finish('FINISHED');return
            self.phase='ENDED_PENDING';self.deadline=self.clock()+20;self._publish()
            return  # separate dispatch turn gives Stop priority during handoff
        if self.phase=='STARTING':
            if self.clock()>self.deadline:request_cancel(self.root,self.session['pid']);self.finish(message='START_FAILED')
        elif self.phase=='ENDED_PENDING':
            if self.clock()>self.deadline:self.finish(message='SOURCE_UNAVAILABLE');return
            if self.rows is None:return
            from media_sequence import successor
            target=successor(self.rows,self.session['pid'],self.session['series_id'],self.session)
            if target is None:self.finish('FINISHED','SERIES_FINISHED');return
            # Preparation is already complete and cache-only. Never replace a
            # foreign or manually requested player item during this small gap.
            if self.player.isPlaying() or self.abort() or cancelled(self.root,self.session['pid']):self.finish();return
            from media_intent import begin
            nonce=begin(self.session['pid'],'episode',target['sid'])
            self.session.update({k:str(target[k]) for k in ('sid','season','episode')})
            self.session.update(nonce=nonce,at=time.time());self.phase='STARTING';self.deadline=self.clock()+20;self._publish()
            if self.abort() or cancelled(self.root,self.session['pid']):request_cancel(self.root,self.session['pid']);self.finish();return
            params=dict(action='media_play',pid=self.session['pid'],kind='episode',sid=self.session['sid'],
                        series_id=self.session['series_id'],season=self.session['season'],episode=self.session['episode'],
                        intent=nonce,resume='0',autoplay='1',autoplay_chain=self.root)
            try:self.launch('PlayMedia(plugin://plugin.video.xtreammate/?'+urlencode(params)+')')
            except Exception:request_cancel(self.root,self.session['pid']);self.finish(message='START_FAILED')
        if self.phase in _ACTIVE and self.clock()-self._last_publish>=1:self._publish()

    def shutdown(self):
        with self.events.lock:self.events.closed=True;self.events.items.clear()
        if self.session:request_cancel(self.root,self.session['pid']);self.finish()
        self.pool.shutdown(wait=False,cancel_futures=True)


def poll():
    global _runtime
    if _runtime is None:
        import xbmc
        events=Events();player=observe(events);monitor=xbmc.Monitor()
        _runtime=Coordinator(player,events,abort=monitor.abortRequested)
    _runtime.tick()


def shutdown():
    global _runtime
    if _runtime:_runtime.shutdown();_runtime=None
