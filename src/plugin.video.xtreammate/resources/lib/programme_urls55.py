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
_urgent68=set();_burst68=0
_focus75=None
OPTIONS='|redirect-limit=0&connection-timeout=3&failonerror=true'


def hosts():
    from utils import setting
    values={'image.tmdb.org'}
    from utils import setting_bool
    if setting_bool('programme_tvmaze67',False):values.add('static.tvmaze.com')
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
                p.password is not None or not __import__('programme_url77').public_query(p.query) or p.fragment):return False
        if p.hostname not in hosts():
            from programme_origin75 import approved
            if not approved(url):return False
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
    if value.get('source','').startswith('agent_') and not __import__('agent_programme100').allowed(value['source']):return None
    if value.get('source')=='xmltv_event' and (not __import__('event_art81').allowed(value) or not __import__('xmltv_art96').display_allowed(value,event)):return None
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


def probe(url,cancel=lambda:False,*,qualified_origin=False):
    """Bounded credentialless preflight, pinned public DNS/TLS, bounded trusted redirects.

    Fully decodes bounded PNG/JPEG bytes without forcing an image archive.
    Kodi performs the actual rendering download later; a later 404 is harmless.
    """
    from programme_transport77 import verified
    fetch = lambda: verified(url,cancel,keep_data81=True)
    # An exact Agent event origin or a known public CDN can share decoded
    # bytes across roles. Other configured XMLTV origins keep their probes.
    parsed = urlsplit(url)
    if not qualified_origin and (parsed.hostname not in ('image.tmdb.org','static.tvmaze.com') or not safe(url)):
        return fetch()
    from widget_refs74 import revoked
    if revoked(url):
        return fetch()
    from artwork_request100 import images
    from epg_handoff63 import profile_scope
    from portals import get_active
    import hashlib, json
    from programme_policy68 import negative_scope
    credentials = [(p.get('xc_user'),p.get('xc_pass')) for p in get_active()[:16]]
    profile = hashlib.sha256(json.dumps(credentials).encode()).hexdigest()
    value = images.request((profile_scope(),profile,negative_scope({}),url),fetch,cancel,ttl=120)
    final = value.get('url',url)
    return fetch() if final!=url and (not safe(final) or revoked(final)) else value


def _contains_credentials(event, url):
    from portals import get_by_id

    portal = get_by_id(str(event.get('pid', ''))) or {}
    path = unquote(urlsplit(url).path)
    secrets = (str(portal.get(key) or '') for key in ('xc_user', 'xc_pass'))
    return any(secret and (secret in path.split('/') or len(secret) >= 4 and secret in path)
               for secret in secrets)


def _resolve_person(event, requested, cancel, check):
    import agent_programme100 as reference
    from epg_agent100_art import validator
    from media_sources43 import SourceError
    from programme_mapping85 import current, epoch
    from programme_policy68 import negative_scope
    from sticky_art88 import publish89

    if cancel():
        return None
    failure = dict(key=event['key'], code='NO_IMAGE', source='placeholder',
                   until=time.time() + 300, policy69=negative_scope({}))
    mapping = current(event)
    if mapping and mapping.get('hidden'):
        return failure
    mapping_epoch = epoch(event)
    prior = reference.read(event, requested)
    if prior:
        return prior
    candidates = reference.candidates(event, requested)
    if not candidates:
        return failure
    candidate = candidates[0]
    url = candidate['url']
    if not safe(url):
        return dict(failure, code='BLOCKED_IMAGE_HOST_OR_URL')
    if _contains_credentials(event, url):
        return dict(failure, code='BLOCKED_CREDENTIAL_URL')
    try:
        if candidate['source'] == 'agent_xmltv' and check is None:
            verified = probe(url, cancel=cancel, qualified_origin=True)
        else:
            verified = (check or probe)(url, cancel=cancel)
    except SourceError as error:
        return dict(failure, code=error.code)
    if cancel():
        return None
    role = candidate['role81']
    if not reference.image_shape(role, verified) or not verified.get('_body81'):
        return dict(failure, code='NO_ARTWORK')
    final = verified.get('url', url)
    final_source = validator()(final)
    if not safe(final) or not final_source or final_source['source'] != candidate['source']:
        return dict(failure, code='BLOCKED_IMAGE_HOST_OR_URL')
    if mapping_epoch != epoch(event) or reference.candidates(event, requested) != [candidate]:
        return failure
    value = dict(code='READY', source=candidate['source'], match='EXACT_EVENT', role81=role,
                 source_url=final, attribution=candidate['attribution'],
                 decoded77=True, image_width77=verified['width'], image_height77=verified['height'],
                 mapping_epoch85=mapping_epoch)
    value = publish89(event, value, verified['_body81'], shared=False)
    if not value.get('decoded88'):
        return dict(failure, code='FETCH_FAILED')
    reference.remember(event, requested, value)
    return value


def resolve(event,cancel=lambda:False,allow_lookup=False,check=None,match=None,local_image63=False,url_mode69=False):
    """Worker-only URL mode or explicit bounded materialization in the existing cache."""
    from programme_index46 import art,event as save_event
    from programme_art46 import fingerprint,remember
    from media_sources43 import SourceError
    from programme_sources57 import PROOFS,policy,attempts,trace as source_trace
    from helper_rpc57 import Error as HelperError
    import agent_programme100 as roles499
    view499=roles499.view(event)
    if view499 in roles499.PERSON_VIEWS:
        return _resolve_person(event, view499, cancel, check)
    typed499=roles499.typed(event)
    home86=__import__('home_schedule75').applicable() and view499=='hero'
    def usable86(v):
        if not v or not roles499.fits(v,view499):
            return False
        if typed499 and not roles499.manual(v):
            if not roles499.selected(v,view499):
                return False
        return not home86 or bool(__import__('hero_art86').classify(v))
    upgrade81=False;best86=None
    def retain86(v):
        nonlocal best86
        if home86 and v and usable86(v) and __import__('programme_image69').eligible(v,event) and __import__('event_art81').allowed(v):
            if best86 is None or __import__('hero_art86').classify(v)[1]<__import__('hero_art86').classify(best86)[1]:best86=dict(v)
    def upgrade86(v):
        return home86 and allow_lookup and __import__('event_art81').upgrade(event,v)
    mapping86=__import__('programme_mapping85').current(event)
    if mapping86 and mapping86.get('hidden'):
        return dict(key=event['key'],fingerprint=fingerprint(event),code='NO_IMAGE',source='placeholder',match='NONE',image=event['placeholder'],until=time.time()+3600,negative_scope68=__import__('programme_policy68').negative_scope(event),negative_scope77=__import__('programme_policy68').negative_scope(event),mapping_epoch85=__import__('programme_mapping85').epoch(event))
    invalid_manual96=False;fresh_xml96=[]
    if mapping86 and mapping86.get('source')=='xmltv_event' and __import__('artwork_sources96').enabled('xmltv'):
        try:
            invalid_manual96=__import__('xmltv_art96').checked_mapping(event,mapping86,cancel) is None
            if invalid_manual96:fresh_xml96=__import__('xmltv_art96').search(event,cancel)['rows']
        except SourceError as exc96:
            if exc96.code not in ('SQLITE_BUSY','EPG_READ_BUDGET'):raise
            # Short DB contention does not revoke the last confirmed image.
    held89=None if invalid_manual96 else __import__('programme_lock89').current(event,worker=True)
    if held89 and roles499.manual(held89):return held89
    local86=__import__('work_requests86').local_result(event)
    if local86:return local86
    if typed499 and not mapping86:
        role499=roles499.read(event,view499)
        if role499:return role499
    if held89 and (usable86(held89) or not typed499):return held89
    external89=None if invalid_manual96 else __import__('external_art89').recover_programme(event)
    if external89 and (usable86(external89) or not typed499):return external89
    temp85=None if invalid_manual96 else __import__('artwork_temp85').lookup(event)
    retain86(temp85)
    if temp85 and usable86(temp85):
        upgrade81=upgrade86(temp85)
        if not upgrade81:return temp85
    durable81=None if invalid_manual96 else __import__('event_art81').prior(event)
    retain86(durable81)
    if durable81 and not usable86(durable81):durable81=None
    upgrade81=upgrade81 or allow_lookup and __import__('event_art81').upgrade(event,durable81)
    if durable81 and not upgrade81:return durable81
    pressure84=__import__('artwork_display84').observe() or __import__('home_schedule75').applicable()
    if url_mode69 and pressure84 and not invalid_manual96:
        renewed84=__import__('sticky_art88').read(event) or __import__('event_cache88').recover(event) or __import__('programme_display84').recover(event) or __import__('programme_display84').renew(event)
        retain86(renewed84)
        if renewed84 and usable86(renewed84) and not upgrade81:
            upgrade81=upgrade86(renewed84)
        if renewed84 and usable86(renewed84) and not upgrade81:
            from programme_session69 import remember as remember84
            remember84(event,renewed84,update=True)
            return renewed84
    if url_mode69:
        from programme_session69 import get as session69
        prior69=None if invalid_manual96 else session69(event)
        retain86(prior69)
        if prior69 and usable86(prior69) and not upgrade81 and not (allow_lookup and __import__('programme_status70').retry(event,prior69)):return prior69
    old=None if invalid_manual96 else art(event)
    if old and (old.get('source')=='xmltv_event' or old.get('source','').startswith(('tmdb_','tvmaze'))) and not __import__('event_art81').allowed(old):old=None
    if not upgrade81 and old and (not typed499 or usable86(old)) and not old.get('url_version55') and (local_image63 or old.get('source') in ('tmdb_movie','tmdb_episode','tmdb_series','tvmaze_series','tvmaze_episode')) and old.get('source')!='placeholder' and old.get('fingerprint')==fingerprint(event) and old.get('until',0)>time.time():
        from programme_art46 import indexed
        local60=indexed(event,verify=True)
        if local60:
            if url_mode69:
                from programme_session69 import remember as local_session69
                local_session69(event,local60,persisted=True)
            return local60
    if old and not usable86(old):old=None
    current=display(event,old)
    legacy70=__import__('programme_status70').legacy_negative(old)
    if legacy70:current=None
    if url_mode69 and current and current.get('source')!='placeholder' and not current.get('url_verified69'):current=None
    from programme_refresh63 import retry as retry63
    from programme_refresh63 import retry67
    explicit63=allow_lookup and (__import__('programme_status70').retry(event,prior69 if url_mode69 and prior69 else old) or retry63(event,old) or retry67(event,old))
    from programme_policy68 import negative_scope
    negative68=negative_scope(event)
    if not typed499 and old and old.get('source')=='placeholder' and old.get('negative_scope68')==negative68 and old.get('until',0)>time.time() and not explicit63 and not legacy70:
        return dict(old,image=event['placeholder'])
    if current and not (typed499 and current.get('source')=='placeholder') and not upgrade81 and not (local_image63 and current.get('source')!='placeholder') and not explicit63 and not (allow_lookup and current.get('source')=='placeholder' and
            (current.get('code')=='AWAITING_BACKGROUND_REFRESH' or not current.get('matching_policy57') or current.get('source_policy57')!=policy())):return current
    if cancel():return None
    if best86:
        # Publish a verified current local fallback before optional network work.
        # This does not launch another job or pretend a renderer/Android ACK.
        __import__('programme_requests68').completed(event,best86)
    from programme_pipeline77 import note as trace77
    trace77(event,'EPG_EVENT','IDENTIFIED')
    trace77(event,'MATCHED_EVENT_FACTS','SOURCE_READY' if event.get('epg_source46') else 'SOURCE_MISSING')
    trace77(event,'EVENT_REVISION','BOUND')
    now=time.time()
    value=dict(key=event['key'],fingerprint=fingerprint(event),binding55=binding(event),url_version55=1,
               code='NO_IMAGE',source='placeholder',match='NONE',image=event['placeholder'],
               resolved_at55=now,until=now+300,tvspielfilm55='BLOCKED_NO_AUTHORIZED_API')
    value.update(hosts55=sorted(hosts()),profile55=profile())
    value['matching_policy56']=1
    value.update(matching_policy57=1,source_policy57=policy(),sources70=[],lookup70=__import__('programme_outcomes70').settings(),origin_policy75=1)
    candidates=[dict(url=event[field],source=source,match='EXACT_EVENT',attribution=credit)
                for field,source,credit in (('xmltv_image','xmltv_event','XMLTV – konfigurierte Eventquelle'),
                    ('provider_image','provider_event','Anbieter – konfigurierte Eventquelle')) if event.get(field) and (source!='xmltv_event' or __import__('artwork_sources96').enabled('xmltv'))]
    if invalid_manual96:candidates=fresh_xml96+[c for c in candidates if c.get('source')=='provider_event']
    agent100=roles499.candidates(event, requested=view499)
    if typed499:
        offered={row['url'] for row in agent100}
        candidates=[dict(row,role81='legacy_icon') for row in candidates if row['url'] not in offered]
    if old and old.get('source_url') and old.get('source') in ('xmltv_event','provider_event','tmdb_movie','tmdb_episode','tmdb_series','tmdb_helper','xcmate_catalog','kodi_library'):
        source=old.get('source')
        enabled=source!='tmdb_helper' or policy()[0]
        enabled=enabled and (source not in ('xcmate_catalog','kodi_library') or policy()[1])
        if enabled:candidates.append(dict(url=old['source_url'],source=source,match=old.get('match','NONE'),attribution=old.get('attribution',''),
            **{k:old[k] for k in ('image_scope57','helper_version57','matched_year56','provider_id') if k in old}))
    def failed(reason):
        if value['code']=='NO_IMAGE' or reason in ('NO_MATCH_AMBIGUOUS','NO_ARTWORK'):value['code']=reason
        else:value['lookup_code56']=reason
        source_trace(event,reason)
    def supplied():
        mapping85=__import__('programme_mapping85').current(event)
        if mapping85 and mapping85.get('hidden'):return
        if mapping85 and mapping85.get('id'):
            if mapping85.get('source')=='xmltv_event':
                chosen96=__import__('xmltv_art96').mapped(event,mapping85,cancel)
                if chosen96:yield chosen96
            elif mapping85.get('source') in ('tmdb','tvmaze') and __import__('programme_candidates85').enabled(mapping85['source']) and allow_lookup:
                try:manual85=__import__('programme_candidates85').candidate(event,cancel)
                except (SourceError,HelperError) as error85:
                    failed(error85.code);manual85=None
                if manual85:yield manual85
            # Optional remote permission and local exact-event XMLTV fallback
            # are separate. A disabled/failed TMDB mapping cannot erase it.
            yield from agent100
            yield from (c for c in candidates if c.get('source') in ('xmltv_event','provider_event') and c.get('match')=='EXACT_EVENT')
            return
        # The same verified event can have different images for different
        # views. Missing roles descend to the feed icon, then the UI fallback.
        if typed499:
            exact_role=roles499.VIEW_ROLE[view499]
            yield from (candidate for candidate in agent100 if candidate.get('role81')==exact_role)
        reference84=__import__('programme_reference84').get(event)
        if reference84 and reference84.get('candidate'):
            if home86:candidates.append(dict(reference84['candidate']))
            elif reference84['candidate'].get('source') not in ('xmltv_event','provider_event'):
                yield dict(reference84['candidate'])
        own81=[];attempted81=False
        if allow_lookup and not match and not __import__('programme_sources57').unsuitable69(event):
            from programme_match46 import candidate as own_candidate81
            from art_trace81 import own as own_trace81
            attempted81=True  # cache/backoff/consent skips also own this supplier
            try:
                def run_own81():
                    nonlocal attempted81
                    attempted81=True
                    return own_candidate81(event,cancel)
                found81=own_trace81(event,run_own81)
                if attempted81:__import__('programme_outcomes70').add(value,'tmdb','FOUND' if found81 else 'NO_CONFIRMED_IMAGE',event)
                if found81:own81.extend(__import__('cinematic_images96').alternatives(found81))
            except (SourceError,HelperError) as exc:
                __import__('programme_outcomes70').add(value,'tmdb',exc.code,event);failed(exc.code)
        if not own81:
            provisional85=__import__('programme_candidates85').suggestion(event)
            if provisional85:own81.append(provisional85)
        if home86:
            from hero_art86 import expand,ordered
            yield from ordered(expand(own81,event,cancel),[])
        else:
            yield from own81
        if not allow_lookup:
            if typed499:yield from (candidate for candidate in agent100 if candidate.get('role81')=='legacy_icon')
            yield from candidates
            return
        from programme_outcomes70 import add as outcome70

        def alternatives(found):
            yield found
            for alternate in found.get('alternate_urls57',[])[:2]:
                yield dict(found,url=alternate)

        def read_supplier(find,source70,deferred):
            started=time.monotonic()
            try:found=find()
            except (SourceError,HelperError) as exc:
                outcome70(value,source70,exc.code,event);failed(exc.code);return
            outcome70(value,source70,'FOUND' if found else 'DISABLED' if source70=='tmdb' and not value['lookup70']['own'] else 'NO_CONFIRMED_IMAGE',event)
            if not found:return
            if found.get('source')=='tmdb_helper':source_trace(event,'HELPER_LOOKUP_OK',duration_ms=(time.monotonic()-started)*1000)
            fallback=found.get('series_fallback57')
            if isinstance(fallback,dict):deferred.append(fallback)
            if event.get('season') and event.get('episode') and found.get('image_scope57')=='series_fallback':
                deferred.append(found);return
            yield from alternatives(found)

        deferred=[];fallback_sources=[]
        steps=[lambda:match(event,cancel=cancel)] if match else attempts(event,cancel,critical80=not bool(event.get('helper_explicit80')))
        for find in steps:
            if cancel():return
            source70=getattr(find,'source70','injected')
            if source70=='tmdb' and attempted81:continue
            if source70 in ('tmdb','tvmaze','injected'):
                yield from read_supplier(find,source70,deferred)
            else:
                fallback_sources.append((find,source70))
        for found in deferred:  # generic series art never masks an exact still
            yield from alternatives(found)
        if typed499:yield from (candidate for candidate in agent100 if candidate.get('role81')=='legacy_icon')
        yield from candidates
        deferred=[]
        for find,source70 in fallback_sources:
            if cancel():return
            yield from read_supplier(find,source70,deferred)
        for found in deferred:
            yield from alternatives(found)
        from programme_match46 import diagnose
        from programme_sources57 import unsuitable69
        if unsuitable69(event):failed('NO_UNIQUE_MATCH')
        elif value['code']=='NO_IMAGE':failed(diagnose(event))
        elif 'lookup_code56' not in value:value['lookup_code56']=diagnose(event)
    for candidate in supplied():
        if cancel():return None
        if candidate.get('match') not in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS:continue
        trace77(event,'IMAGE_SOURCE_SELECTION','SOURCE_SELECTED')
        trace77(event,'MATCH_CONFIDENCE','PROVISIONAL_SUGGESTION' if candidate.get('provisional85') else 'MANUAL_CONFIRMED' if candidate.get('manual85') else 'EXACT_MATCH')
        url=candidate.get('url','')
        if candidate.get('source')=='tmdb_episode':url=url.replace('https://image.tmdb.org/t/p/w500/','https://image.tmdb.org/t/p/original/',1)
        if candidate.get('source','').startswith('tmdb_') and candidate.get('role81')=='backdrop':url=url.replace('https://image.tmdb.org/t/p/w500/','https://image.tmdb.org/t/p/w1280/',1)
        if candidate.get('match')=='EXACT_EVENT':
            from image_reference78 import canonical
            url=canonical(url) or url
        from programme_origin75 import candidate as origin75,grant as grant75
        new_origin75=not safe(url) and candidate.get('match')=='EXACT_EVENT' and origin75(event,url,candidate.get('source'))
        if not safe(url) and not new_origin75:
            trace77(event,'URL_SECURITY','BLOCKED');value['code']='BLOCKED_IMAGE_HOST_OR_URL';continue
        trace77(event,'URL_SECURITY','APPROVED')
        if _contains_credentials(event,url):
            value['code']='BLOCKED_CREDENTIAL_URL';continue
        if home86 and not new_origin75:
            local86=__import__('hero_render86').recovered_candidate(event,candidate,url)
            if local86:
                retain86(local86)
                return best86 or local86
        verified77=None
        agent_origin499=candidate.get('source')=='agent_xmltv'
        if new_origin75:
            try:
                verified77=probe(url,cancel=cancel,qualified_origin=True) if agent_origin499 else probe(url,cancel=cancel)
            except SourceError as exc:value['code']=exc.code;continue
            if cancel():return None
            grant75(url)
            if isinstance(verified77,dict) and verified77.get('url'):
                url=verified77['url'];grant75(url)
        typed_choice499=typed499 and not roles499.manual(candidate)
        if not typed_choice499 and (local_image63 or not url_mode69 and candidate.get('source') in ('tmdb_movie','tmdb_episode','tmdb_series')):
            from programme_art46 import prepare as materialize60
            return materialize60(event,cancel=cancel,resolved60=dict(candidate,_local_only63=True) if local_image63 else candidate)
        try:
            if not new_origin75:
                if agent_origin499 and not check:
                    verified77=probe(url,cancel=cancel,qualified_origin=True)
                else:verified77=(check or probe)(url,cancel=cancel)
            if isinstance(verified77,dict) and verified77.get('url'):url=verified77['url']
        except SourceError as exc:value['code']=exc.code;continue
        if cancel():return None
        role=candidate.get('role81')
        if typed_choice499 and (role not in (roles499.VIEW_ROLE[view499],'legacy_icon') or
                                not roles499.image_shape(role,verified77)):
            failed('HERO_QUALITY_REJECTED');continue
        if home86:
            quality86=dict(candidate,image_width77=(verified77 or {}).get('width',0),image_height77=(verified77 or {}).get('height',0))
            if not __import__('hero_art86').classify(quality86):
                failed('HERO_QUALITY_REJECTED');continue
            trace77(event,'IMAGE_SOURCE_SELECTION','HERO_QUALITY_VERIFIED')
        if candidate.get('xmltv96'):value['xmltv96']=candidate['xmltv96']
        value['mapping_epoch85']=__import__('programme_mapping85').epoch(event)
        value.update(code='READY',source=candidate['source'],match=candidate['match'],
            source_url=url,image=url+OPTIONS,thumbnail=url+OPTIONS,
            attribution=candidate.get('attribution',''),until=min(now+86400,max(now+300,event['stop']+3600)))
        if candidate.get('matched_year56'):value['matched_year56']=candidate['matched_year56']
        if candidate.get('remote_id') or candidate.get('provider_id'):value['provider_id']=candidate.get('remote_id') or candidate['provider_id']
        for field in ('image_scope57','helper_version57','role81','provisional85','manual85','vote_average88','vote_count88'):
            if candidate.get(field):value[field]=candidate[field]
        if url_mode69 or typed_choice499:
            from programme_requests68 import identity,scope
            value.update(url_verified69=True,scope69=identity(event),profile69=scope(),policy69=negative_scope({}))
        if isinstance(verified77,dict) and verified77.get('decoded77'):
            value.update(decoded77=True,image_width77=verified77['width'],image_height77=verified77['height'])
        from programme_pipeline77 import note
        note(event,'HTTP_RESPONSE','IMAGE_DECODED' if value.get('decoded77') else 'REFERENCE_VERIFIED')
        trace77(event,'IMAGE_LEASE','BOUND')
        source_trace(event,'IMAGE_URL_VERIFIED')
        if typed_choice499:
            # Verified roles share the existing bytes server and keep separate,
            # exact-event receipts. They never overwrite the other role's art.
            value=__import__('sticky_art88').publish89(event,value,verified77.get('_body81'))
            roles499.remember(event,view499,value)
            return value
        if isinstance(verified77,dict):
            value=__import__('artwork_temp85').promote(event,value,verified77.get('_body81'))
            value=__import__('event_art81').commit(event,value,verified77.get('_body81'))
            value=__import__('sticky_art88').remember(event,value,verified77.get('_body81'))
        break
    if not candidates and not agent100 and not allow_lookup and value['code']=='NO_IMAGE':value['code']='AWAITING_BACKGROUND_REFRESH'
    if cancel():return None
    if best86 and (value.get('source')=='placeholder' or not usable86(value) or __import__('hero_art86').classify(best86)[1]<__import__('hero_art86').classify(value)[1]):
        return dict(best86,code='READY_STALE' if value.get('source')=='placeholder' else best86.get('code','READY'))
    if value.get('source')=='placeholder':
        if durable81:return durable81
        value['negative_scope68']=negative68
        if typed499:
            return dict(value,policy69=negative_scope({}))
    if url_mode69:
        if pressure84 and value.get('url_version55') and value.get('source')!='placeholder':
            value=__import__('programme_display84').remember(event,value)
        from programme_session69 import remember as session_save69,persist as persist69
        value=session_save69(event,value)
        value=persist69(event,value)
        session_save69(event,value,persisted=value.get('persisted69',False),update=True)
        remember(event['key'],value,verified47=True)
        return value
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


def promote_focus75(tag,requested='hero'):
    """Worker-only promotion of an exact queued intent; never another lookup."""
    global _focus75
    from programme_requests68 import identity,_aliases
    from agent_programme100 import view
    from epg_handoff63 import profile_scope
    current=profile_scope()
    with _lock:
        for key,job in _queue.items():
            if len(job)<4 or job[3]!=current or view(job[0])!=requested:continue
            bound=identity(job[0])
            if tag==bound or tag in _aliases.get((bound,requested),()):
                _focus75=key;_urgent68.add(key);_queue.move_to_end(key,last=False)
                return True
    return False

def enqueue(event,allow_lookup=False,local_image63=False,priority68=False,reference_only84=False):
    """Worker producer: True prioritizes visible items; 2 is current focus."""
    global _thread,_focus75
    if _stop.is_set() or not event.get('title'):return False
    import agent_programme100 as roles499
    from epg_handoff63 import profile_scope
    view499=roles499.view(event)
    profile499=profile_scope()
    with _lock:
        key=(profile499,event['key'],'reference84' if reference_only84 else view499)
        if not reference_only84 and __import__('home_schedule75').applicable():local_image63=False
        if priority68==2:_focus75=key
        from utils import setting_bool
        if not reference_only84 and view499 not in roles499.PERSON_VIEWS and not local_image63 and not setting_bool('programme_art_local69',False):
            from programme_session69 import get as session69
            available69=session69(event)
            if available69 and (not roles499.fits(available69,view499) or roles499.typed(event)
                                and not roles499.manual(available69) and not roles499.selected(available69,view499)):
                available69=None
            if available69 and __import__('home_schedule75').applicable() and view499=='hero' and not __import__('hero_art86').classify(available69):available69=None
            if available69 and not (allow_lookup and __import__('programme_status70').retry(event,available69)):
                from programme_requests68 import completed
                completed(event,available69);return False
        if key in _pending:
            if priority68 and key in _queue:
                old=_queue[key]
                _queue[key]=(old[0],old[1] or allow_lookup,old[2] or local_image63,old[3],old[4])
                _urgent68.add(key)
                if priority68==2:_queue.move_to_end(key,last=False)
            return False
        if len(_pending)>=24:
            victim=next((k for k in reversed(_queue) if k not in _urgent68),None) if priority68 else None
            if victim is None and priority68==2:victim=next(reversed(_queue),None)
            if victim is None:return False
            deferred75=_queue.pop(victim);_pending.discard(victim);_urgent68.discard(victim)
            try:
                from programme_requests68 import status
                status(deferred75[0],'REQUESTED')
            except (ImportError,AttributeError,RuntimeError):pass
        _pending.add(key);_queue[key]=(dict(event),allow_lookup,bool(local_image63),profile499,bool(reference_only84))
        if priority68:_urgent68.add(key)
        if priority68==2:_queue.move_to_end(key,last=False)
        try:
            from programme_requests68 import status
            if not reference_only84:status(event,'QUEUED')
        except (ImportError,AttributeError,RuntimeError):pass
        if _thread is None or not _thread.is_alive():
            _thread=threading.Thread(target=_run,name='XCMate-programme-URL55',daemon=True);_thread.start()
    _wake.set();return True


def _run():
    global _burst68
    import xbmc
    aborted=getattr(xbmc.Monitor(),'abortRequested',lambda:False)
    while not _stop.is_set() and not aborted():
        with _lock:
            urgent=next((k for k in _queue if k in _urgent68),None)
            if _focus75 in _queue:
                pair=(_focus75,_queue.pop(_focus75));_burst68+=1
            elif urgent is not None and (_burst68<3 or all(k in _urgent68 for k in _queue)):
                pair=(urgent,_queue.pop(urgent));_burst68+=1
            else:
                background=next((k for k in _queue if k not in _urgent68),None)
                pair=(background,_queue.pop(background)) if background is not None else _queue.popitem(last=False) if _queue else None
                _burst68=0
            if pair:_urgent68.discard(pair[0])
        if pair is None:
            try:
                from programme_session69 import flush
                flush(_stop.is_set)
            except Exception:pass
            _wake.wait(.5);_wake.clear();continue
        key,job=pair;event,allow=job[:2];local63=len(job)>2 and job[2]
        person=key[2] in __import__('agent_programme100').PERSON_VIEWS
        try:
            try:
                from epg_handoff63 import profile_scope
                from programme_requests68 import status,completed
                deadline69=time.monotonic()+45
                stopped69=lambda:_stop.is_set() or aborted() or len(job)>3 and job[3]!=profile_scope()
                cancelled=lambda:stopped69() or time.monotonic()>deadline69
                if cancelled():continue
                from storage_policy92 import images_enabled
                if not images_enabled():
                    from artwork_sources96 import health
                    code=health()
                    completed(event,dict(code=code if code not in ('READY','NOT_CREATED')
                                         else 'IMAGE_EPG_DISABLED',source='placeholder'))
                    continue
                if len(job)>4 and job[4]:
                    __import__('programme_reference84').resolve(event,cancelled)
                    continue
                status(event,'RUNNING')
                if local63:value=resolve(event,cancel=cancelled,allow_lookup=allow,local_image63=True)
                else:value=resolve(event,cancel=cancelled,allow_lookup=allow,url_mode69=True)
                if not stopped69():
                    if time.monotonic()>deadline69:
                        value=dict(key=event['key'],code='IMAGE_LOOKUP_TIMEOUT',source='placeholder',image=event['placeholder'],until=time.time()+60)
                        if not person:value=__import__('programme_session69').remember(event,value)
                    completed(event,value)
            except Exception as error482:
                try:
                    value=dict(key=event['key'],code=__import__('programme_state482').error(error482),source='placeholder',image=event['placeholder'],until=time.time()+60)
                    if not person:value=__import__('programme_session69').remember(event,value)
                    completed(event,value)
                except (NameError,AttributeError,RuntimeError):pass
        finally:
            with _lock:_pending.discard(key)


def shutdown():_stop.set();_wake.set()
