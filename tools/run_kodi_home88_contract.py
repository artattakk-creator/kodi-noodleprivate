#!/usr/bin/env python3
"""Native .86 typed large Hero pixels with 27MiB XCMate-observed pressure, two restarts."""
import argparse,os,subprocess,json,zipfile,hashlib,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_kodi_home74_contract import SKIN_SHA,SKIN_URL

def main():
 p=argparse.ArgumentParser();p.add_argument('--report-dir',type=Path,required=True);p.add_argument('--skin-archive',type=Path);p.add_argument('--resolution',default='1920x1080',choices=('1920x1080','1280x720'));a=p.parse_args()
 root=Path(__file__).resolve().parents[1];report=a.report_dir.resolve();report.mkdir(parents=True,exist_ok=True)
 archive=a.skin_archive or report/'skin.zip'
 if not archive.exists():
  import urllib.request
  with urllib.request.urlopen(SKIN_URL,timeout=60) as response:archive.write_bytes(response.read(100*1024*1024))
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==SKIN_SHA
 pristine=report/'pristine'
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(pristine)
 candidate=report/'candidate';subprocess.run([sys.executable,str(root/'tools/build_bingie87_review.py'),'--skin',str(pristine/'skin.titan.bingie.mod'),'--output',str(candidate)],check=True)
 env=dict(os.environ,BUILDX_CONFIG=str(report/'buildx'))
 for key in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(key,None)
 docker=['docker','--host=unix:///var/run/docker.sock'];name='xcmate-visible87-'+uuid.uuid4().hex[:10]
 def run(*args,**kw):return subprocess.run(docker+list(args),env=env,check=True,**kw)
 with (report/'build.log').open('w') as log:run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t','xcmate-kodi21-helper57-contract',str(root/'tools/kodi_helper57_host'),stdout=log,stderr=subprocess.STDOUT)
 start=(root/'tools/kodi_home74_host/start.sh').read_text().replace('cp /work/fixture66.py /root/.kodi/addons/plugin.video.xtreammate/','cp /fixture84.py /root/.kodi/addons/plugin.video.xtreammate/fixture66.py')
 start=start.replace('Xvfb :99', 'python3 /setup87.py\nXvfb :99')
 (report/'start.sh').write_text(start)
 base=root/'tools/kodi_home84_host'
 mounts=[(root/'tools/kodi_home74_host','/work'),(root/'src/plugin.video.xtreammate','/xcmate'),(pristine/'skin.titan.bingie.mod','/skin'),(candidate,'/candidate'),(root/'tools/kodi_home86_host/fixture86.py','/fixture84.py'),(base/'fixture84.py','/base_fixture84.py'),(root/'tools/kodi_home88_host/gui88.py','/work/gui66.py'),(root/'tools/kodi_home86_host/gui86.py','/base_gui86.py'),(root/'tools/kodi_home87_host/spec87.py','/spec87.py'),(root/'tools/kodi_home87_host/setup87.py','/setup87.py'),(root/'tools/kodi_home87_host/foreign87.py','/foreign87.py'),(base/'gui84.py','/base_gui84.py'),(root/'tools/kodi_home87_host/probe87.py','/work/probe.py'),(base/'probe84.py','/base_probe84.py'),(root/'tools/kodi_home86_host/tls86.py','/work/tls69.py'),(base/'skin84.py','/work/skin_fixture66.py'),(root/'tools/kodi_home74_host/skin_fixture66.py','/base_skin78.py'),(root/'tools/kodi_home78_host/skin_fixture78.py','/skin78.py'),(report/'start.sh','/work/start.sh')]
 mounts.extend([(root/'tools/kodi_home86_host/icons86.py','/icons86.py'),(root/'tools/kodi_home86_host/navigation86.py','/navigation86.py')])
 cmd=['run','-d','--name',name]
 for source,target in mounts:cmd+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
 cmd+=['-e','XCMATE_RES74='+a.resolution,'xcmate-kodi21-helper57-contract','sh','/work/start.sh']
 def copy(source,target):run('cp',name+':'+source,str(report/target))
 try:
  run(*cmd,stdout=subprocess.DEVNULL);print(name,flush=True)
  with (report/'probe.log').open('w') as log:run('exec',name,'python3','/work/probe.py',stdout=log,stderr=subprocess.STDOUT)
  copy('/root/visible84.json','visible84.json');copy('/root/foreign87.json','foreign87.json')
  run('cp',str(root/'tools/kodi_home88_host/gui88.py'),name+':/root/post75.py');run('cp',str(root/'tools/kodi_home75_host/restart75.py'),name+':/root/restart75.py')
  run('exec',name,'touch','/root/tls79-off')
  for i in (1,2):
   run('exec',name,'rm','-f','/root/foreign87.json')
   if i==2:run('exec',name,'rm','/root/post75.json')
   with (report/('restart'+str(i)+'.log')).open('w') as log:run('exec','-e','XCMATE_GUI_RESTART_TIMEOUT87=240',name,'python3','/root/restart75.py',stdout=log,stderr=subprocess.STDOUT)
   with (report/('foreign-restart'+str(i)+'.log')).open('w') as log:run('exec',name,'python3','-c',"import json,time;from pathlib import Path;end=time.monotonic()+160\nwhile time.monotonic()<end:\n if Path('/root/post75-error.txt').exists():raise RuntimeError(Path('/root/post75-error.txt').read_text())\n if Path('/root/foreign87.json').exists():assert json.loads(Path('/root/foreign87.json').read_text())['status']=='PASS';break\n time.sleep(.1)\nelse:raise RuntimeError('FOREIGN87_RESTART_TIMEOUT')",stdout=log,stderr=subprocess.STDOUT)
   copy('/root/post75.json','restart'+str(i)+'.json');copy('/root/foreign87.json','foreign-restart'+str(i)+'.json')
 finally:
  try:
   files=json.loads(run('exec',name,'python3','-c',"import json;from pathlib import Path;print(json.dumps([str(p) for p in Path('/root').glob('visible84-*.png')]))",capture_output=True,text=True).stdout)
   for file in files:copy(file,Path(file).name)
  except (ValueError,subprocess.CalledProcessError):pass
  for file in ('gui66-error.txt','post75-error.txt','tls69-requests.jsonl','visible84.json','texture84-debug.json','poster86-value.json','poster86-state.json','navigation86.json','icons86.json'):
   subprocess.run(docker+['cp',name+':/root/'+file,str(report/file)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  subprocess.run(docker+['cp',name+':/root/.kodi/temp/kodi.log',str(report/'synthetic-kodi.log')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for evidence86 in ('poster86-value.json','poster86-state.json','navigation86.json','icons86.json'):
   target86=report/evidence86
   if target86.is_file():print(evidence86+' '+target86.read_text()[:6000],flush=True)
  synthetic86=report/'synthetic-kodi.log'
  if synthetic86.is_file():
   for line86 in synthetic86.read_text(errors='replace').splitlines():
    if 'HERO86_RECEIVER ' in line86 or 'HERO86_FAILED_FRAME ' in line86:print(line86[:4000],flush=True)
  # Emit synthetic fixture failures in Actions logs as well as the artifact.
  for evidence85 in ('gui66-error.txt','probe.log','post75-error.txt','restart1.log','restart2.log','foreign-restart1.log','foreign-restart2.log'):
   target85=report/evidence85
   if target85.is_file():print(evidence85+'\n'+target85.read_text(errors='replace')[-12000:],flush=True)
  if synthetic86.is_file():print('SYNTHETIC87_KODI_TAIL\n'+'\n'.join(synthetic86.read_text(errors='replace').splitlines()[-80:]),flush=True)
  # Synthetic screenshots only: make two actual native PNGs recoverable for
  # human review even when signed Actions artifact downloads are unavailable.
  import base64
  for picture87 in ('visible84-hero86-final.png','visible84-foreign87-warm-1-7.png'):
   path87=report/picture87
   if path87.is_file() and path87.stat().st_size<=512*1024:
    raw87=path87.read_bytes();print('PNG87 '+picture87+' '+hashlib.sha256(raw87).hexdigest()+' '+base64.b64encode(raw87).decode(),flush=True)
  subprocess.run(docker+['rm','-f',name],env=env,stdout=subprocess.DEVNULL)
if __name__=='__main__':main()
