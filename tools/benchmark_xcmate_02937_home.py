#!/usr/bin/env python3
"""Cold Python-process Home submission; fake Kodi, real source/profile IO.

Run after host tests, without parallel builds. This does not measure Android
rendering, remote readiness or first video frame. No production profile used.
"""
import argparse,json,statistics,subprocess,sys
from pathlib import Path

CHILD=r'''
import sys,time,json
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'tests'))
from test_xcmate_0281_boot import BootTests
case=BootTests(methodName='runTest');case.setUp()
try:
 before=case.portal_file.read_bytes();start=time.perf_counter();case.entry.run();elapsed=(time.perf_counter()-start)*1000
 assert len(case.items)==6 and len(case.ends)==1
 assert case.portal_file.read_bytes()==before
 print(json.dumps(dict(ms=elapsed,items=len(case.items),completions=len(case.ends),logs=case.logs)))
finally:case.doCleanups()
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('output');p.add_argument('--samples',type=int,default=7);args=p.parse_args()
 rows={'baseline':[],'candidate':[]}
 for _ in range(args.samples):
  for name,root in [('baseline',args.baseline),('candidate',args.candidate)]:
   result=subprocess.run([sys.executable,'-c',CHILD,str(Path(root).resolve())],capture_output=True,text=True,check=True)
   rows[name].append(json.loads(result.stdout))
 summary={name:dict(median_ms=statistics.median(row['ms'] for row in values),min_ms=min(row['ms'] for row in values),max_ms=max(row['ms'] for row in values)) for name,values in rows.items()}
 data=dict(level='HOST modeled Kodi; actual source imports and temporary profile IO',python=sys.version,scope='new interpreter per sample, OS file cache warm; time run() to directory submission, not hardware IR/render or video',baseline_version='0.1.29.36',candidate_version='0.1.29.37',samples=args.samples,summary=summary,rows=rows)
 data['median_reduction_percent']=100*(1-summary['candidate']['median_ms']/summary['baseline']['median_ms'])
 Path(args.output).write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
