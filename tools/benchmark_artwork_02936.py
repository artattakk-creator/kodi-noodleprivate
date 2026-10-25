"""Reproduce pre-fix artwork failures and a real local-HTTP fixture pipeline.

No private inputs, real-provider downloads or Android acceptance. Run from the
source checkout with tests/dependencies available, never on the user's profile.
"""
import argparse
import ast
import importlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import types
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'src/plugin.video.xtreammate/resources/lib')]
from test_xcmate_artwork_02936 import Artwork36
BASE='656be1e73aff1c16b877880bde52f2384792677a'


def old_function(name,module):
    text=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':src/plugin.video.xtreammate/resources/lib/art_store.py'],text=True)
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    scope=dict(module.__dict__)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'previous_art_store','exec'),scope)
    return scope[name]


def case():
    value=Artwork36(methodName='runTest');value.setUp();return value


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=dict(baseline=BASE,platform=platform.platform(),python=platform.python_version(),
                android='NOT_TESTED',private_logs_or_profiles_used=False,cases={})
    c=case()
    try:
        old=old_function('enqueue',c.store);usage=types.SimpleNamespace(free=512*1048576,total=2*1024**3)
        with mock.patch.object(c.policy.shutil,'disk_usage',return_value=usage):
            try:old(['https://fixture.invalid/one'])
            except OSError:pass
            before=dict(database_created=Path(c.m.health.path()).exists(),durable_jobs=0)
            c.store.enqueue(['https://fixture.invalid/one']);c.store.run_one()
            after=dict(durable_jobs=1,job_status=c.m.row('https://fixture.invalid/one')['status'],
                       storage_result=c.store.status()['storage_result'],network_calls=c.m.http.call_count)
        result['cases']['simulated_512_mib_free']=dict(simulated_not_device=True,free_bytes=usage.free,total_bytes=usage.total,
                    configured_image_reserve=c.policy.reserve(),before=before,after=after)
    finally:c.doCleanups()
    c=case()
    try:
        c.m.portal['include_series']=False
        records=[dict(stream_id=str(i),category_id='a',name='Fixture '+str(i),stream_icon='https://fixture.invalid/'+str(i)) for i in range(3)]
        c.m.index.replace_catalog('p','vod',records,c.m.catalogs['get_vod_categories'])
        old=old_function('prefetch_selected',c.store);old()
        db=c.store.connect();before=dict(scan_complete=db.execute('SELECT offset FROM scan').fetchone()[0]<0,
                                        durable_jobs=db.execute('SELECT count(*) FROM jobs').fetchone()[0]);db.close()
        c.store.prefetch_selected()
        db=c.store.connect();after=dict(scan_complete=db.execute('SELECT offset FROM scan').fetchone()[0]<0,
                                      durable_jobs=db.execute('SELECT count(*) FROM jobs').fetchone()[0],
                                      persistence_acknowledged=db.execute('SELECT revision FROM scan').fetchone()[0].endswith('|persisted36'));db.close()
        result['cases']['old_completed_empty_queue']=dict(before=before,after=after,network_calls=c.m.http.call_count)
    finally:c.doCleanups()
    test=Artwork36('test_real_local_http_three_movies_two_series_two_logos_repaint_and_survive_reload')
    run=unittest.TestResult();test.run(run)
    if not run.wasSuccessful():raise AssertionError(str(run.errors+run.failures))
    result['cases']['real_local_http_fixture']=test.metrics
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
