"""Actual Kodi runtime with synthetic provider; no real Helper/image claim."""
import json,sys,time,urllib.request,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/xcmate-lib')
from programme_helper57 import identity,image,same_title
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))  # container loopback only
def rpc(method,params=None):
    req=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=57,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
    with opener.open(req,timeout=15) as response:value=json.loads(response.read(512*1024))
    assert 'error' not in value,(method,value.get('error',{}).get('code'))
    return value['result']
for attempt in range(100):
    try:version=rpc('Application.GetProperties',{'properties':['version']})['version'];break
    except Exception:time.sleep(.2)
else:raise RuntimeError('LOCAL_TEST_KODI_UNAVAILABLE')
assert version['major']==21
addon=rpc('Addons.GetAddonDetails',{'addonid':'plugin.video.xcmate.contract57','properties':['version','enabled','installed']})['addon']
assert addon['installed'] is True
rpc('Addons.SetAddonEnabled',{'addonid':'plugin.video.xcmate.contract57','enabled':True})
before=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
def directory(suffix=''):
    value=rpc('Files.GetDirectory',dict(directory='plugin://plugin.video.xcmate.contract57/?info=details'+suffix,media='video',
        properties=['title','originaltitle','year','art','uniqueid','season','episode','showtitle','customproperties'],limits=dict(start=0,end=24)))
    assert value['limits']['total']==1
    return value['files'][0]
movie=directory();assert identity(movie)==('movie',672);assert movie['year']==2002
assert same_title('Harry Potter und die Kammer des Schreckens',movie)
expected='https://image.tmdb.org/t/p/w500/SYNTHETIC_CONTRACT_ONLY.jpg'
assert image(movie,check=lambda url:url==expected)==expected
with concurrent.futures.ThreadPoolExecutor(1) as pool:
    start=time.monotonic();future=pool.submit(directory,'&slow=true');time.sleep(.2)
    assert rpc('JSONRPC.Ping')=='pong';ping_ms=round((time.monotonic()-start)*1000)
    assert ping_ms<1500
    slow=future.result(8)
assert slow['customproperties']['h57.dialogid']==movie['customproperties']['h57.dialogid']
internal=directory('&internal=true')
assert internal['customproperties']['h57.internalworkerpassed']=='True'
assert internal['customproperties']['h57.dialogid']==movie['customproperties']['h57.dialogid']
episode=directory('&episode=3');assert identity(episode)==('tv',1399)
assert episode['season']==2 and episode['episode']==3 and episode['showtitle']=='Test Series'
assert episode['uniqueid']['tmdb']=='999001'  # distinct from parent SERIES id
assert rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})==before
assert rpc('Player.GetActivePlayers')==[]
report=dict(purpose='REAL_KODI_SYNTHETIC_PLUGIN_TRANSPORT_ONLY',kodi={k:version.get(k) for k in ('major','minor','revision','tag')},
    rpc_directory='PASS',native_movie_id_year='PASS',native_image_wrapper_roundtrip='PASS',nested_python_worker_rpc='PASS',
    distinct_series_episode_ids='PASS',concurrent_ping_ms=ping_ms,gui_and_dialog_unchanged='PASS',no_player_start='PASS',
    actual_tmdb_helper='NOT_TESTED',real_image_download='NOT_TESTED',android='BLOCKED_DEVICE_ACCESS')
print(json.dumps(report,indent=2))
