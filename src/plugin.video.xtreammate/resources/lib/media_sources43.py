"""Explicit provider/TMDb/Commons research. No scraping, logging or bulk jobs.

Uses the existing verified-IP/TLS transport without changing downloads. API redirects
are refused; public image redirects are bounded/pinned; bearer credentials are never sent with image requests.
"""
import io,json,time,threading
from urllib.parse import urlencode,urlsplit

MAX_IMAGE=3*1024*1024
MAX_JSON=1024*1024
TMDB='https://api.themoviedb.org/3'
_network_slots=threading.BoundedSemaphore(2)


class SourceError(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def get(url,*,api=False,token='',cancel=lambda:False,transport=None):
    from artwork_visible import syntactic
    from download_redirect import addresses,_connect
    if not syntactic(url):raise SourceError('UNSAFE_SOURCE')
    p=urlsplit(url)
    if api and (p.scheme!='https' or p.port not in (None,443) or p.hostname not in ('api.themoviedb.org','commons.wikimedia.org')):
        raise SourceError('UNSAFE_SOURCE')
    if cancel():raise SourceError('CANCELLED')
    deadline=time.monotonic()+12
    headers={'User-Agent':'XCMate/0.1.29.47 (manual artwork research)','Accept-Encoding':'identity',
             'Accept':'application/json' if api else 'image/jpeg,image/png'}
    if token:
        if p.hostname!='api.themoviedb.org' or any(ord(c)<33 or ord(c)>126 for c in token):raise SourceError('INVALID_TOKEN')
        headers['Authorization']='Bearer '+token
    if not _network_slots.acquire(blocking=False):raise SourceError('RESEARCH_BUSY')
    response=None
    try:
        # Every DNS answer must be public, then the selected IP is connected
        # directly with original hostname TLS/SNI. Never resolve a second time.
        if api:response=(transport or _connect)(url,addresses(url),headers)
        else:
            from image_redirect48 import open_image
            response=open_image(url,headers,transport or _connect,addresses,cancel,deadline)
        status=response.status
        if 300<=status<400:raise SourceError('REDIRECT_BLOCKED')
        if status in (401,403):raise SourceError('HTTP_AUTH')
        if status in (404,410):raise SourceError('HTTP_NOT_FOUND')
        if status==429:
            from art_errors import retry_after
            error=SourceError('HTTP_RATE_LIMIT')
            error.retry_after60=retry_after(response)
            raise error
        if status>=500:raise SourceError('HTTP_SERVER')
        if status!=200:raise SourceError('HTTP_CLIENT')
        mime=response.headers.get('Content-Type','').partition(';')[0].strip().lower()
        if mime not in (('application/json',) if api else ('image/png','image/jpeg')):raise SourceError('CONTENT_TYPE')
        if response.headers.get('Content-Encoding','identity').lower() not in ('','identity'):raise SourceError('CONTENT_ENCODING')
        limit=MAX_JSON if api else MAX_IMAGE;chunks=[];size=0
        while True:
            if cancel():raise SourceError('CANCELLED')
            if time.monotonic()>deadline:raise SourceError('TIMEOUT')
            chunk=response.read(min(65536,limit-size+1))
            if not chunk:break
            size+=len(chunk)
            if size>limit:raise SourceError('RESPONSE_LIMIT')
            chunks.append(chunk)
        data=b''.join(chunks)
        if api:
            try:value=json.loads(data)
            except (ValueError,RecursionError):raise SourceError('INVALID_JSON') from None
            if not isinstance(value,dict):raise SourceError('INVALID_JSON')
            return value
        validate_image(data);return data
    except SourceError:raise
    except Exception as error:
        from art_errors import classify
        code=getattr(error,'code','')
        raise SourceError('UNSAFE_SOURCE' if str(code).startswith('REDIRECT_') else classify(error)) from None
    finally:
        try:
            if response:response.close()
        finally:_network_slots.release()


def validate_image(data):
    from media_art import dimensions,MAX_PIXELS
    if not isinstance(data,bytes) or not 0<len(data)<=MAX_IMAGE:raise SourceError('IMAGE_LIMIT')
    try:
        width,height=dimensions(data)
        if not 0<width<=4096 or not 0<height<=4096 or width*height>MAX_PIXELS:raise ValueError()
        try:from PIL import Image
        except ImportError:raise SourceError('IMAGE_DECODER_MISSING') from None
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ('JPEG','PNG') or image.size!=(width,height):raise ValueError()
            image.verify()
        with Image.open(io.BytesIO(data)) as image:image.load()
        return width,height
    except SourceError:raise
    except Exception:raise SourceError('INVALID_IMAGE') from None


def provider(item):
    from media_art import poster_candidates,valid_source
    from media_data import video_info
    info=video_info(item);metadata={k:v for k,v in info.items() if k in ('plot','genre','year','rating','director','cast') and v not in (None,'')}
    if info.get('duration'):metadata['duration_secs']=info['duration']
    if 'rating' in metadata:
        try:metadata['rating']=float(metadata['rating'])
        except (TypeError,ValueError):metadata.pop('rating',None)
    values=[]
    for url in poster_candidates(item):
        values.append(dict(source='provider',url=url,name='Anbieter · Poster',role='poster',attribution='Anbieter – Nutzungsrechte beachten',metadata=metadata))
    for field in ('backdrop_path','backdrop','fanart','fanart_image'):
        raw=item.get(field);raw=raw if isinstance(raw,list) else [raw]
        for url in raw[:8]:
            if valid_source(url) and not any(v['url']==url for v in values):
                values.append(dict(source='provider',url=url,name='Anbieter · Hintergrund',role='fanart',attribution='Anbieter – Nutzungsrechte beachten',metadata=metadata))
    if not values and metadata:values.append(dict(source='provider',url='',name='Anbieter · Informationen',role='poster',attribution='Anbieter',metadata=metadata))
    return values[:12]


def tmdb_token():
    from utils import setting_bool,setting
    if not setting_bool('tmdb_research43',False):raise SourceError('TMDB_DISABLED')
    token=setting('tmdb_read_token43','').strip()
    if not token:raise SourceError('TMDB_TOKEN_MISSING')
    return token


def _tmdb_image(path):
    import re
    return 'https://image.tmdb.org/t/p/w500'+path if isinstance(path,str) and re.fullmatch(r'/[A-Za-z0-9_-]+\.(jpg|png)',path) else ''


def tmdb(query,kind,person=False,cancel=lambda:False):
    endpoint='person' if person else 'movie' if kind=='vod' else 'tv'
    token=tmdb_token()
    data=get(TMDB+'/search/'+endpoint+'?'+urlencode(dict(query=str(query)[:200],language='de-DE',include_adult='false')),api=True,token=token,cancel=cancel)
    result=[]
    rows=data.get('results',[])
    if not isinstance(rows,list):raise SourceError('INVALID_JSON')
    for row in rows[:12]:
        if not isinstance(row,dict) or not isinstance(row.get('id'),int):continue
        date=str(row.get('release_date') or row.get('first_air_date') or '')[:4]
        title=str(row.get('title') or row.get('name') or '')[:200]
        meta={}
        if not person:
            if isinstance(row.get('overview'),str) and row['overview']:meta['plot']=row['overview'][:6000]
            if date.isdigit() and 1880<=int(date)<=2100:meta['year']=int(date)
        before=len(result)
        for field,role in (('profile_path','replacement'),) if person else (('poster_path','poster'),('backdrop_path','fanart')):
            url=_tmdb_image(row.get(field))
            if url:result.append(dict(source='tmdb',url=url,name=title+(' · '+date if date else '')+' · '+endpoint,
                title=title,year=date,remote_id=row['id'],media_type=endpoint,role=role,
                attribution='TMDb · https://www.themoviedb.org/'+endpoint+'/'+str(row['id'])+' · API-/Bildnutzungsbedingungen beachten; nicht von TMDb zertifiziert.',metadata=meta))
        if not person and len(result)==before:
            result.append(dict(source='tmdb',url='',name=title+(' · '+date if date else '')+' · '+endpoint,title=title,year=date,remote_id=row['id'],media_type=endpoint,role='poster',attribution='TMDb · https://www.themoviedb.org/'+endpoint+'/'+str(row['id']),metadata=meta))
    return result[:24]


def tmdb_details(candidate,cancel=lambda:False):
    kind=candidate.get('media_type');remote=candidate.get('remote_id')
    if kind not in ('movie','tv') or not isinstance(remote,int):return {}
    data=get(TMDB+'/'+kind+'/'+str(remote)+'?'+urlencode(dict(language='de-DE',append_to_response='credits')),api=True,token=tmdb_token(),cancel=cancel)
    result={}
    if data.get('id')!=remote:raise SourceError('IDENTITY_MISMATCH')
    for key,field in (('overview','plot'),):
        if isinstance(data.get(key),str):result[field]=data[key][:6000]
    date=str(data.get('release_date') or data.get('first_air_date') or '')[:4]
    if date.isdigit() and 1880<=int(date)<=2100:result['year']=int(date)
    genres=[v['name'] for v in data.get('genres',[])[:16] if isinstance(v,dict) and isinstance(v.get('name'),str)]
    if genres:result['genre']=' / '.join(genres)
    runtime=data.get('runtime')
    if isinstance(runtime,int) and 0<runtime<=2880:result['duration_secs']=runtime*60
    credits=data.get('credits',{})
    if isinstance(credits,dict):
        cast=[v['name'] for v in credits.get('cast',[])[:16] if isinstance(v,dict) and isinstance(v.get('name'),str)]
        if cast:result['cast']=cast
        directors=[v['name'] for v in credits.get('crew',[])[:100] if isinstance(v,dict) and v.get('job')=='Director' and isinstance(v.get('name'),str)]
        if directors:result['director']=' / '.join(directors[:4])
    return result


def commons(query,cancel=lambda:False):
    # Official image-search API. No Google HTML or obsolete custom-search API.
    params=dict(action='query',format='json',generator='search',gsrsearch=str(query)[:200],gsrnamespace=6,
                gsrlimit=12,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=1000)
    data=get('https://commons.wikimedia.org/w/api.php?'+urlencode(params),api=True,cancel=cancel)
    result=[]
    from html import unescape
    import re
    def plain(value):return unescape(re.sub('<[^>]*>','',str(value or '')))[:1000]
    pages=data.get('query',{}).get('pages',{})
    if not isinstance(pages,dict):return []
    for row in list(pages.values())[:12]:
        info=(row.get('imageinfo') or [{}])[0];meta=info.get('extmetadata',{})
        license=plain(meta.get('LicenseShortName',{}).get('value',''))
        if not re.fullmatch(r'(CC0|Public domain|CC BY(?:-SA)? [1-4]\.0)',license,re.I):continue
        url=info.get('thumburl') or info.get('url')
        if not isinstance(url,str) or urlsplit(url).scheme!='https' or urlsplit(url).hostname!='upload.wikimedia.org':continue
        from urllib.parse import quote
        page='https://commons.wikimedia.org/wiki/'+quote(str(row.get('title','')),safe=':')
        result.append(dict(source='commons',url=url,name=plain(row.get('title','')).removeprefix('File:'),role='replacement',metadata={},
            remote_id=row.get('pageid'),media_type='image',
            attribution=license+' · '+plain(meta.get('Artist',{}).get('value',''))+' · '+page))
    return result
