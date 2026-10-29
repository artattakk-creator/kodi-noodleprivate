#!/usr/bin/env python3
"""Opt-in Box-B PUBLIC metadata probe. No install, GUI, playback or settings IO.

This verifies Helper RPC metadata, not actual EPG persistence or Android pixels.
Endpoint/auth never enter the report. Never run against productive Box A.
"""
import argparse,base64,hashlib,json,os,re,ssl,sys,time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler,HTTPSHandler

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0,str(LIB))
from helper_rpc57 import Error
from programme_helper57 import lookup


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise Error('HELPER_BACKGROUND_UNAVAILABLE')


def image_url(url):
    if not isinstance(url,str) or any(ord(c)<33 or ord(c)>126 for c in url):return False
    try:
        parsed=urlsplit(url)
        return bool(parsed.scheme=='https' and parsed.hostname=='image.tmdb.org' and parsed.port in (None,443)
            and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment
            and re.fullmatch(r'/t/p/(w\d{2,4}|original)/[A-Za-z0-9_-]+\.(jpg|png)',parsed.path))
    except ValueError:return False


class Endpoint:
    def __init__(self,url,ca_file=None):
        p=urlsplit(url)
        if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.query or p.fragment or p.path!='/jsonrpc':
            raise Error('INVALID_EXPLICIT_BOX_B_ENDPOINT')
        self.url=url;self.headers={'Content-Type':'application/json'};self.count=0
        user=os.environ.get('XCMATE_KODI_USERNAME','');password=os.environ.get('XCMATE_KODI_PASSWORD','')
        if user or password:self.headers['Authorization']='Basic '+base64.b64encode((user+':'+password).encode()).decode()
        # Preserve the caller's network/proxy policy. No redirect may forward
        # Kodi credentials to another endpoint. An authorized route is required.
        self.opener=build_opener(NoRedirect(),HTTPSHandler(context=ssl.create_default_context(cafile=ca_file)))

    def call(self,method,params=None,cancel=lambda:False):
        allowed={'Application.GetProperties','GUI.GetProperties','Player.GetActivePlayers','Addons.GetAddonDetails','Files.GetDirectory'}
        if method not in allowed or cancel():raise Error('HELPER_BACKGROUND_UNAVAILABLE')
        data=json.dumps(dict(jsonrpc='2.0',id=57,method=method,params=params or {})).encode()
        try:
            self.count+=1
            with self.opener.open(Request(self.url,data,self.headers),timeout=12) as response:raw=response.read(512*1024+1)
            if len(raw)>512*1024:raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            value=json.loads(raw)
            if value.get('id')!=57 or value.get('jsonrpc')!='2.0' or 'error' in value:raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            return value['result']
        except Error:raise
        except TimeoutError:raise Error('HELPER_TIMEOUT') from None
        except Exception:raise Error('BLOCKED_DEVICE_ACCESS') from None


def gui(endpoint):
    value=endpoint.call('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
    return {key:value.get(key,{}).get('id') for key in ('currentwindow','currentcontrol')}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--box-b',action='store_true',required=True,help='Confirm endpoint belongs to TEST Box B, never Box A')
    parser.add_argument('--endpoint',required=True,help='Explicit http(s)://BOX-B:PORT/jsonrpc; no credentials in URL')
    parser.add_argument('--title',default='Harry Potter und die Kammer des Schreckens')
    parser.add_argument('--year',type=int,default=2002)
    parser.add_argument('--season',type=int);parser.add_argument('--episode',type=int);parser.add_argument('--subtitle')
    parser.add_argument('--ca-file');parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.report.exists():parser.error('report already exists; choose a new file')
    report=dict(android='NOT_TESTED',device_access='BLOCKED_DEVICE_ACCESS',purpose='PUBLIC_HELPER_METADATA_PROBE_ONLY',
                real_epg_persistence='NOT_TESTED',image_pixels='NOT_TESTED',same_epg_hero_pixels='NOT_TESTED')
    event=dict(title=args.title,year=args.year,key=hashlib.sha256(args.title.encode()).hexdigest())
    if args.season is not None and args.episode is not None:event.update(season=args.season,episode=args.episode,subtitle=args.subtitle or '')
    started=time.monotonic()
    try:
        endpoint=Endpoint(args.endpoint,args.ca_file)
        version=endpoint.call('Application.GetProperties',{'properties':['version']}).get('version',{})
        report['device_access']='CONNECTED_BY_USER_ENDPOINT'
        report['kodi_version']={k:version.get(k) for k in ('major','minor','tag')}
        if version.get('major')!=21:raise Error('HELPER_VERSION_UNSUPPORTED')
        before=gui(endpoint);players=endpoint.call('Player.GetActivePlayers')
        value=lookup(event,rpc=endpoint.call,image_check=image_url)
        report.update(device_access='CONNECTED_BY_USER_ENDPOINT',code='HELPER_LOOKUP_OK',helper_version=value['helper_version57'],
            tmdb_id=value['remote_id'],matched_year=value['matched_year56'],image_scope=value['image_scope57'],
            validated_url_shape=True,image_url_sha256=hashlib.sha256(value['url'].encode()).hexdigest(),
            gui_unchanged=before==gui(endpoint),active_players_unchanged=players==endpoint.call('Player.GetActivePlayers'),
            rpc_calls=endpoint.count,personal_xcmate_token_used=False)
    except Error as exc:report['code']=exc.code
    except Exception:report['code']='HELPER_BACKGROUND_UNAVAILABLE'
    report['duration_ms']=round((time.monotonic()-started)*1000)
    # Refuse overwriting an older test result. No endpoint, raw response, title,
    # Kodi credentials, private source IDs or actual external image URL stored.
    with args.report.open('x',encoding='utf-8') as output:json.dump(report,output,indent=2);output.write('\n')
    os.chmod(args.report,0o600)
    print(json.dumps(report))
    return 0 if report.get('code')=='HELPER_LOOKUP_OK' else 2


if __name__=='__main__':raise SystemExit(main())
