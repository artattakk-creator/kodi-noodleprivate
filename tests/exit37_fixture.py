"""Deterministic service worker pump; never invoked by a native callback."""
import importlib


def drain_stop():
    jobs=importlib.import_module('exit_jobs');value=jobs.state()
    if value and value['phase']=='pending':
        value['not_before']=0;jobs.save(value);jobs.poll()
    worker=jobs._thread
    if worker is not None:worker.join(2)
    process_native_live_stop()


def process_native_live_stop():
    """Model Kodi's ordered builtin queue; never call from a GUI callback."""
    jobs=importlib.import_module('exit_jobs');value=jobs.state()
    if value and value.get('native_posted') and not value.get('worker_done'):
        import xbmc,xbmcgui
        # The model applies the queued native Stop, then the FIFO barrier.
        xbmc.Player().stop()
        from native_stop41 import ACK
        xbmcgui.Window(10000).setProperty(ACK,value['native_ack'])
        jobs.poll()
