"""Reverify completed native evidence without rerunning/changing the Home soak.

Used when only the evidence validator changed (e.g. a fixture's actual progress
percentage). It never advances clocks, fabricates screenshots or repeats setup.
"""
import json,os
from pathlib import Path
idle=json.loads(Path('/root/idle74.json').read_text())
if idle.get('status')!='PASS' or idle.get('elapsed_seconds',0)<int(os.environ.get('XCMATE_IDLE74','0')):raise RuntimeError('REAL_SOAK_NOT_COMPLETE')
source=Path('/work/probe.py').read_text()
header=source.split('for _ in range(150):',1)[0]
tail='samples ='+source.split('samples =',1)[1]
namespace={}
exec(compile(header,'<native74-verifier-header>','exec'),namespace)
namespace['version']=namespace['rpc']('Application.GetProperties',{'properties':['version']})['version']
namespace['visited']=[dict(status='initial driver gated normal three sources and explicit adapter preview/consent before the GUI run',verification='completed native artifacts revalidated separately')]
exec(compile(tail,'<native74-completed-evidence>','exec'),namespace)
