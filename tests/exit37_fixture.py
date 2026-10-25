"""Deterministic service worker pump; never invoked by a native callback."""
import importlib


def drain_stop():
    jobs=importlib.import_module('exit_jobs');value=jobs.state()
    if value and value['phase']=='pending':
        value['not_before']=0;jobs.save(value);jobs.poll()
    worker=jobs._thread
    if worker is not None:worker.join(2)
