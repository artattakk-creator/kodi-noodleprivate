"""Cancellation/deadline of existing owner-pool work, not another worker lane."""
import contextlib,threading,time
_local=threading.local()
def active():return callable(getattr(_local,'cancel',None))
def cancelled():return bool(active() and (_local.cancel() or time.monotonic()>=_local.deadline))
def check():
 if cancelled():raise InterruptedError('UI_JOB_CANCELLED86')
def policy(timeout,seconds,retries):
 if not active():return timeout,seconds,retries
 check();remaining=max(.01,_local.deadline-time.monotonic())
 return min(timeout,1.,remaining),min(seconds,remaining),0

def wait(seconds):
 end=time.monotonic()+max(0,seconds)
 while time.monotonic()<end:
  check();time.sleep(min(.05,max(0,end-time.monotonic())))
 check()

@contextlib.contextmanager
def scope(cancel,seconds=4):
 previous=(getattr(_local,'cancel',None),getattr(_local,'deadline',None))
 _local.cancel=cancel;_local.deadline=time.monotonic()+seconds
 try:check();yield;check()
 finally:_local.cancel,_local.deadline=previous

def run(view,generation,job):
 import xbmc
 monitor=xbmc.Monitor();abort=getattr(monitor,'abortRequested',lambda:False)
 cancel=lambda:getattr(view,'_closed',False) or getattr(view,'_generation',generation)!=generation or abort()
 with scope(cancel):return job()
