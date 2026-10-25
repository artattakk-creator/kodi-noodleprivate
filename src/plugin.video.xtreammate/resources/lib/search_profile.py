"""Bounded search phases: random generation/owner, monotonic times, numbers only."""
import time
import uuid
from contextlib import contextmanager

PHASES=frozenset(('QUERY_ACCEPTED','TAB_LIVE_SELECTED','LIVE_CURSOR_INIT_BEGIN','LIVE_CURSOR_INIT_END',
    'INDEX_QUERY_BEGIN','INDEX_QUERY_END','MAPPING_BEGIN','MAPPING_END','EPG_NOW_SQL_BEGIN','EPG_NOW_SQL_END',
    'SHORT_EPG_CACHE_BEGIN','SHORT_EPG_CACHE_END','SLICE_BEGIN','SLICE_END',
    'FIRST_NAME_MATCH','FIRST_PROGRAMME_MATCH','FIRST_LIVE_ROW_RENDERED','SCAN_FINAL',
    'QUERY_CHANGED','STALE_CANCEL','WORKER_QUEUED','WORKER_BEGIN','ROW_RENDER_BEGIN','ROW_RENDER_END'))
FREQUENT=frozenset(('WORKER_QUEUED','WORKER_BEGIN','ROW_RENDER_BEGIN','ROW_RENDER_END'))
FIELDS=frozenset(('events','duration_ms','queue_ms','rows','scanned','channels','name_hits','programme_hits','slices','cached','cancelled'))


def token(value):
    return value if isinstance(value,str) and len(value)==32 and all(c in '0123456789abcdef' for c in value) else ''


class SearchProfile:
    def __init__(self,generation='',owner=''):
        self.generation=token(generation) or uuid.uuid4().hex;self.owner=token(owner)
        self.started=time.monotonic_ns();self.seen=set();self.last={};self.pending={}

    def emit(self,phase,once=False,force=False,**values):
        if phase not in PHASES or once and phase in self.seen:return
        now=time.monotonic_ns()
        if phase=='SCAN_FINAL':self.flush()
        if phase in FREQUENT and not force:
            pending=self.pending.setdefault(phase,dict(events=0,duration_ms=0,queue_ms=0))
            pending['events']+=1
            for name in ('duration_ms','queue_ms'):
                value=values.get(name,0)
                if isinstance(value,(int,float,bool)):
                    try:pending[name]+=max(0,int(value))
                    except (ValueError,OverflowError):pass
            if phase in self.last and now-self.last[phase]<1000000000:return
            self.last[phase]=now;values=dict(values,**pending);self.pending.pop(phase,None)
        self.seen.add(phase)
        fields=['[XCMate][SEARCH_PERF] phase='+phase,'generation='+self.generation,'owner='+self.owner,
                'ms='+str(max(0,(time.monotonic_ns()-self.started)//1000000))]
        for key,value in values.items():
            if key in FIELDS and isinstance(value,(int,float,bool)):
                try:fields.append(key+'='+str(max(0,min(int(value),10**12))))
                except (ValueError,OverflowError):pass
        try:
            import xbmc
            xbmc.log(' '.join(fields),xbmc.LOGINFO)
        except (ImportError,AttributeError,RuntimeError,TypeError):pass

    def flush(self):
        pending=self.pending;self.pending={}
        for phase,values in pending.items():self.emit(phase,force=True,**values)

    @contextmanager
    def span(self,name,**values):
        start=time.monotonic_ns();self.emit(name+'_BEGIN',**values)
        try:yield
        finally:self.emit(name+'_END',duration_ms=(time.monotonic_ns()-start)//1000000,**values)
