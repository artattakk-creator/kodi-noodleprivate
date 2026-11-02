"""Native Kodi AV decoding against an isolated synthetic TS/HLS/504 provider."""
import argparse,json,os,subprocess,uuid
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--report-dir',type=Path,required=True);args=parser.parse_args()
report=args.report_dir.resolve();report.mkdir(parents=True,exist_ok=True);media=report/'media';media.mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc=size=320x180:rate=25','-f','lavfi','-i','sine=frequency=440','-t','18','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-g','25','-threads','1','-c:a','aac','-f','mpegts',str(media/'sample.ts')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(media/'sample.ts'),'-c','copy','-hls_time','2','-hls_list_size','0','-hls_playlist_type','vod','-hls_segment_filename',str(media/'segment%d.ts'),str(media/'playlist.m3u8')],check=True)
env=dict(os.environ)
for k in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):env.pop(k,None)
env['BUILDX_CONFIG']=str(report/'buildx')
docker=['docker','--host=unix:///var/run/docker.sock']
def run(*cmd,**kw):return subprocess.run(docker+list(cmd),env=env,check=True,**kw)
image='xcmate-kodi21-helper57-contract';name='xcmate-live67-'+uuid.uuid4().hex[:12]
with (report/'build.log').open('w') as log:run('build','--secret','id=system_ca,src=/etc/ssl/certs/ca-certificates.crt','-t',image,str(root/'tools/kodi_helper57_host'),stdout=log,stderr=subprocess.STDOUT)
try:
 run('run','-d','--name',name,'--mount','type=bind,src='+str(root/'tools/kodi_live67_host')+',dst=/work,readonly','--mount','type=bind,src='+str(root/'src/plugin.video.xtreammate')+',dst=/xcmate,readonly','--mount','type=bind,src='+str(media)+',dst=/root/media,readonly',image,'sh','/work/start.sh',stdout=subprocess.DEVNULL)
 with (report/'live.json').open('w') as out:run('exec',name,'python3','/work/probe.py',stdout=out,timeout=180)
 result=json.loads((report/'live.json').read_text());assert len(result['cases'])==5 and len(result['errors'])==2
 print('NATIVE67_AV_VERIFIED_JSON '+json.dumps(result,sort_keys=True))
except Exception:
 subprocess.run(docker+['logs',name],env=env,check=False)
 subprocess.run(docker+['inspect',name,'--format','{{json .State}}'],env=env,check=False)
 subprocess.run(docker+['cp',name+':/root/.kodi/temp/kodi.log',str(report/'synthetic-kodi.log')],env=env,check=False)
 log=report/'synthetic-kodi.log'
 if log.exists():print('SYNTHETIC67_FAILURE '+log.read_text(errors='replace')[-25000:])
 run('exec',name,'python3','-c',"from pathlib import Path; p=Path('/root/.kodi/temp/kodi.log'); print('SYNTHETIC67_ERRORS\\n'+'\\n'.join(v for v in p.read_text(errors='replace').splitlines() if any(k in v for k in ('error','Error','Exception','Traceback')))[-18000:])")
 raise
finally:subprocess.run(docker+['rm','-f',name],env=env,check=False,stdout=subprocess.DEVNULL)
