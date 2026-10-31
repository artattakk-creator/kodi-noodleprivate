"""Pre-resolved event image URLs in the existing programme/artwork index.

Only producers enqueue. Home, focus and programme details perform local reads.
No image archive, new database, guide writes or TV-Spielfilm scraping. Public
image hosts require explicit approval; Kodi redirects are disabled at rendering.
"""
from collections import OrderedDict
import ipaddress,re,threading,time
from urllib.parse import urlsplit,unquote

_lock=threading.Lock();_queue=OrderedDict();_pending=set();_thread=None
_stop=threading.Event();_wake=threading.Event();_revisions={}
_observed56={}
OPTIONS='|redirect-limit=0&connection-timeout=3&failonerror=true'


def hosts():
    from utils import setting
    values={'image.tmdb.org'}
    for host in str(setting('programme_image_hosts55','')).lower().split(',')[:20]:
        host=host.strip()
        if re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?',host) and '.' in host:
            values.add(host)
    return values


def safe(url):
    """Pure validation only: no DNS, IO, normalization or discovery in readers."""
    if not isinstance(url,str) or not 1<len(url)<=2048:return False
    if any(ord(c)<33 or ord(c)>126 for c in url) or any(c in url for c in ('\\','|')):return False
    try:
        p=urlsplit(url)
        if (p.scheme!='https' or p.port not in (None,443) or p.username is not None or
                p.password is not None or p.query or p.fragment or p.hostname not in hosts()):return False
        if p.hostname.endswith(('.local','.localhost','.internal','.invalid')) or p.hostname=='localhost':return False
        try:
            ipaddress.ip_address(p.hostname)
            return False  # Literal IPs are never an approved image CDN.
        except ValueError:pass
        decoded=unquote(p.path)
        if any(ord(c)<32 for c in decoded) or any(c in decoded for c in ('\\','|','@')):return False
        if any(part in ('.','..') for part in decoded.split('/')):return False
        if p.hostname=='image.tmdb.org' and not re.fullmatch(r'/t/p/(?:w\d{2,4}|original)/[A-Za-z0-9_-]+\.(?:jpg|png)',p.path):return False
        return bool(p.path and p.path!='/')
    except (ValueError,TypeError,AttributeError):return False


def binding(event):
    from programme_store46 import title_hash
    return [str(event.get(k,'')) for k in ('pid','sid','canonical','source_key46','epg_source46','start','stop')]+[title_hash(event.get('title',''))]


def profile():
    import hashlib
    from programme_index46 import path
    return hashlib.sha256(path().encode()).hexdigest()


def display(event,value):
    """A persisted URL is not proof that Android displayed the right picture."""
    if not isinstance(value,dict) or value.get('url_version55')!=1:return None
    from programme_art46 import fingerprint
    if value.get('fingerprint')!=fingerprint(event):return None
    if value.get('hosts55')!=sorted(hosts()) or value.get('profile55')!=profile():return None
    if value.get('binding55')!=binding(event) or value.get('key')!=event.get('key'):return None
    until=value.get('until',0)
    if not isinstance(until,(int,float)) or not time.time()<until<time.time()+8*86400:return None
    if value.get('source')=='placeholder':return dict(value,image=event['placeholder'])
    url=value.get('source_url','')
    from programme_sources57 import PROOFS,policy
    if value.get('source')=='tmdb_helper' and not policy()[0]:return None
    if value.get('source') in ('xcmate_catalog','kodi_library') and not policy()[1]:return None
    if not safe(url) or value.get('match') not in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS:return None
    return dict(value,image=url+OPTIONS,thumbnail=url+OPTIONS)


def probe(url,cancel=lambda:False):
    """Bounded credentialless preflight, pinned public DNS/TLS, no redirects.

    Validates response type and header dimensions without archiving image bytes.
    Kodi performs the actual rendering download later; a later 404 is harmless.
    """
    from media_sources43 import SourceError
    from download_redirect import addresses,_connect
    from media_art import dimensions,MAX_PIXELS
    response=None
    try:
        if cancel():raise SourceError('CANCELLED')
        response=_connect(url,addresses(url),{'User-Agent':'XCMate programme image preflight','Accept':'image/jpeg,image/png','Accept-Encoding':'identity'})
        code=response.status
        if code in (404,410):raise SourceError('HTTP_NOT_FOUND')
        if code!=200:raise SourceError('REDIRECT_BLOCKED' if 300<=code<400 else 'HTTP_CLIENT')
        if response.headers.get('Content-Type','').partition(';')[0].lower() not in ('image/jpeg','image/png'):raise SourceError('CONTENT_TYPE')
        if response.headers.get('Content-Encoding','identity').lower() not in ('identity',''):raise SourceError('CONTENT_ENCODING')
        data=b'';deadline=time.monotonic()+3
        while len(data)<65536:
            if cancel():raise SourceError('CANCELLED')
            if time.monotonic()>deadline:raise SourceError('TIMEOUT')
            part=response.read(min(4096,65536-len(data)))
            if not part:break
            data+=part
            try:
                width,height=dimensions(data)
                if not 0<width<=4096 or not 0<height<=4096 or width*height>MAX_PIXELS:raise SourceError('IMAGE_LIMIT')
                return
            except (ValueError,IndexError):pass
        raise SourceError('INVALID_IMAGE')
    except SourceError:raise
    except Exception:
        # Private host, TLS error text and connection credentials never escape.
        raise SourceError('IMAGE_PREFLIGHT_FAILED') from None
    finally:
        if response is not None:response.close()


def resolve(event,cancel=lambda:False,allow_lookup=False,check=None,match=None,local_image63=False):
    """Worker-only URL mode or explicit bounded materialization in the existing cache."""
    from programme_index46 import art,event as save_event
    from programme_art46 import fingerprint,remember
    from media_sources43 import SourceError
    from programme_sources57 import PROOFS,policy,attempts,trace as source_trace
    from helper_rpc57 import Error as HelperError
    old=art(event)
    if old and not old.get('url_version55') and (local_image63 or old.get('source') in ('tmdb_movie','tmdb_episode')) and old.get('source')!='placeholder' and old.get('fingerprint')==fingerprint(event) and old.get('until',0)>time.time():
        from programme_art46 import indexed
        local60=indexed(event,verify=True)
        if local60:return local60
    current=display(event,old)
    from programme_refresh63 import retry as retry63
    explicit63=allow_lookup and retry63(event,old)
    if current and not (local_image63 and current.get('source')!='placeholder') and not explicit63 and not (allow_lookup and current.get('source')=='placeholder' and
            (current.get('code')=='AWAITING_BACKGROUND_REFRESH' or not current.get('matching_policy57') or current.get('source_policy57')!=policy())):return current
    if cancel():return None
    now=time.time()
    value=dict(key=event['key'],fingerprint=fingerprint(event),binding55=binding(event),url_version55=1,
               code='NO_IMAGE',source='placeholder',match='NONE',image=event['placeholder'],
               resolved_at55=now,until=now+300,tvspielfilm55='BLOCKED_NO_AUTHORIZED_API')
    value.update(hosts55=sorted(hosts()),profile55=profile())
    value['matching_policy56']=1
    value.update(matching_policy57=1,source_policy57=policy())
    candidates=[dict(url=event[field],source=source,match='EXACT_EVENT',attribution=credit)
                for field,source,credit in (('xmltv_image','xmltv_event','XMLTV – konfigurierte Eventquelle'),
                    ('provider_image','provider_event','Anbieter – konfigurierte Eventquelle')) if event.get(field)]
    if old and old.get('source_url') and old.get('source') in ('xmltv_event','provider_event','tmdb_movie','tmdb_episode','tmdb_helper','xcmate_catalog','kodi_library'):
        source=old.get('source')
        enabled=source!='tmdb_helper' or policy()[0]
        enabled=enabled and (source not in ('xcmate_catalog','kodi_library') or policy()[1])
        if enabled:candidates.append(dict(url=old['source_url'],source=source,match=old.get('match','NONE'),attribution=old.get('attribution',''),
            **{k:old[k] for k in ('image_scope57','helper_version57','matched_year56','provider_id') if k in old}))
    def failed(reason):
        if value['code']=='NO_IMAGE':value['code']=reason
        else:value['lookup_code56']=reason
        source_trace(event,reason)
    def supplied():
        yield from candidates
        if not allow_lookup:return
        deferred=[]
        steps=[lambda:match(event,cancel=cancel)] if match else attempts(event,cancel)
        for find in steps:
            if cancel():return
            started=time.monotonic()
            try:found=find()
            except (SourceError,HelperError) as exc:
                failed(exc.code);continue
            if found:
                if found.get('source')=='tmdb_helper':source_trace(event,'HELPER_LOOKUP_OK',duration_ms=(time.monotonic()-started)*1000)
                fallback=found.get('series_fallback57')
                if isinstance(fallback,dict):deferred.append(fallback)
                if event.get('season') and event.get('episode') and found.get('image_scope57')=='series_fallback':
                    deferred.append(found);continue
                yield found
                for alternate in found.get('alternate_urls57',[])[:2]:yield dict(found,url=alternate)
        for found in deferred:  # generic series art never masks an exact still
            yield found
            for alternate in found.get('alternate_urls57',[])[:2]:yield dict(found,url=alternate)
        from programme_match46 import diagnose
        if value['code']=='NO_IMAGE':failed(diagnose(event))
        elif 'lookup_code56' not in value:value['lookup_code56']=diagnose(event)
    for candidate in supplied():
        if cancel():return None
        if candidate.get('match') not in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS:continue
        url=candidate.get('url','')
        if not safe(url):value['code']='BLOCKED_IMAGE_HOST_OR_URL';continue
        from portals import get_by_id
        portal=get_by_id(str(event.get('pid',''))) or {}
        path=unquote(urlsplit(url).path)
        secrets=[str(portal.get(k) or '') for k in ('xc_user','xc_pass')]
        if any(secret and (secret in path.split('/') or len(secret)>=4 and secret in path) for secret in secrets):
            value['code']='BLOCKED_CREDENTIAL_URL';continue
        if local_image63 or candidate.get('source') in ('tmdb_movie','tmdb_episode'):
            from programme_art46 import prepare as materialize60
            return materialize60(event,cancel=cancel,resolved60=candidate)
        try:(check or probe)(url,cancel=cancel)
        except SourceError as exc:value['code']=exc.code;continue
        if cancel():return None
        value.update(code='READY',source=candidate['source'],match=candidate['match'],
            source_url=url,image=url+OPTIONS,thumbnail=url+OPTIONS,
            attribution=candidate.get('attribution',''),until=min(now+86400,max(now+300,event['stop']+3600)))
        if candidate.get('matched_year56'):value['matched_year56']=candidate['matched_year56']
        if candidate.get('remote_id') or candidate.get('provider_id'):value['provider_id']=candidate.get('remote_id') or candidate['provider_id']
        for field in ('image_scope57','helper_version57'):
            if candidate.get(field):value[field]=candidate[field]
        source_trace(event,'IMAGE_URL_VERIFIED')
        break
    if not candidates and not allow_lookup:value['code']='AWAITING_BACKGROUND_REFRESH'
    if cancel():return None
    # A transient network failure may never extend or bless an expired URL.
    save_event(event,write=True)
    saved=art(event,value)
    if saved is not None and value.get('code')=='READY':source_trace(event,'IMAGE_SHARED_EVENT')
    if saved is not None:remember(event['key'],value,verified47=True)
    return value if saved is not None else dict(value,code='PROGRAMME_DB_UNAVAILABLE',image=event['placeholder'],source='placeholder')


def refreshed(pid,revision):
    """The first observation is a boot baseline, never a metadata lookup trigger."""
    key=(profile(),str(pid));previous=_revisions.get(key)
    # Existing background schedule may repair missing images even if no new
    # guide revision arrives. Initial startup stays quiet; neither Home nor
    # focus/detail readers call this scheduler or enqueue metadata lookups.
    now=time.monotonic()
    if previous is None:_observed56.pop(key,None)
    if revision is not None:_observed56.setdefault(key,now)
    periodic=revision is not None and now-_observed56.get(key,now)>=60
    eligible=bool(previous and previous[0] is not None and revision is not None and (previous[0]!=revision or previous[1] or periodic))
    _revisions[key]=(revision,eligible)
    if len(_revisions)>8:
        old=next(iter(_revisions));_revisions.pop(old);_observed56.pop(old,None)
    return eligible


def enqueue(event,allow_lookup=False,local_image63=False):
    """Called only by existing background producers, never by focus/details."""
    global _thread
    if _stop.is_set() or not event.get('title'):return False
    with _lock:
        key=event['key']
        if key in _pending or len(_pending)>=24:return False
        _pending.add(key);_queue[key]=(dict(event),allow_lookup,True) if local_image63 else (dict(event),allow_lookup)
        if _thread is None or not _thread.is_alive():
            _thread=threading.Thread(target=_run,name='XCMate-programme-URL55',daemon=True);_thread.start()
    _wake.set();return True


def _run():
    while not _stop.is_set():
        with _lock:pair=_queue.popitem(last=False) if _queue else None
        if pair is None:_wake.wait(.5);_wake.clear();continue
        key,job=pair;event,allow=job[:2];local63=len(job)>2 and job[2]
        try:
            try:
                if local63:resolve(event,cancel=_stop.is_set,allow_lookup=allow,local_image63=True)
                else:resolve(event,cancel=_stop.is_set,allow_lookup=allow)
            except Exception:pass  # No private exception text, keep worker alive.
        finally:
            with _lock:_pending.discard(key)


def shutdown():_stop.set();_wake.set()
