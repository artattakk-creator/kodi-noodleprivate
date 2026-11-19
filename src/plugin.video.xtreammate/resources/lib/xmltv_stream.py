"""SAX XMLTV reader: bounded text/depth, no document tree or strptime import.

Only the inert XMLTV doctype marker is accepted; no entity/DTD is loaded. A source is staged
until the entire XML and gzip trailer validate. Large feeds have no aggregate
byte/programme cap; memory is bounded per element, disk by actual free space.
"""
import datetime
import gzip
import re
import time
from urllib.parse import urlsplit
from xml.parsers import expat
from epg_io import XMLTVLimitError

IMAGE_TYPES=frozenset(('poster','backdrop','still','person','character'))
MAX_IMAGE_NODES=32
MAX_IMAGE_URL=2048
MAX_IMAGE_SYSTEM=64
_IMAGE_ATTRIBUTES=frozenset(('type','orient','size','system'))
_ICON_ATTRIBUTES=frozenset(('src','width','height'))
_SYSTEM=re.compile(r'[A-Za-z0-9][A-Za-z0-9_. -]*\Z')
_HTTPS_REFERENCE=re.compile(r'https://[!-~]+\Z',re.IGNORECASE)


class UnsafeXMLTV(ValueError):
    pass


class XMLTVSyntaxError(ValueError):
    pass


def _invalid_image(strict):
    if strict:raise XMLTVSyntaxError('Invalid XMLTV artwork reference')
    return None


def _image_attributes(attributes,strict):
    system=attributes.get('system','')
    if len(system)>MAX_IMAGE_SYSTEM:
        raise XMLTVLimitError('XMLTV artwork system exceeds limit','image_attributes')
    if (attributes.keys()-_IMAGE_ATTRIBUTES or attributes.get('type') not in IMAGE_TYPES
            or attributes.get('orient') not in (None,'P','L')
            or attributes.get('size') not in (None,'1','2','3')
            or system and not _SYSTEM.fullmatch(system)):
        return _invalid_image(strict)
    return {key:attributes.get(key,'') for key in ('type','orient','size','system')}


def _image_url(value,strict):
    """Check syntax only. Source trust, destinations and URL policy stay downstream."""
    if len(value)>MAX_IMAGE_URL:raise XMLTVLimitError('XMLTV artwork URL exceeds limit','image_url')
    if not _HTTPS_REFERENCE.fullmatch(value) or '\\' in value or '#' in value:
        return _invalid_image(strict)
    try:
        parsed=urlsplit(value)
        if parsed.hostname and parsed.username is None and parsed.password is None and parsed.port in (None,443):
            return value
    except ValueError:pass
    return _invalid_image(strict)


def timestamp(value):
    match=re.fullmatch(r'(\d{14})\s*([+-]\d{4})?',str(value or '').strip())
    if not match: raise ValueError('Invalid XMLTV timestamp')
    digits,zone=match.groups();zone=zone or '+0000'
    hours,minutes=int(zone[1:3]),int(zone[3:5])
    if hours>23 or minutes>59: raise ValueError('Invalid XMLTV timezone')
    # Kodi's embedded interpreters need not import _strptime in worker threads.
    date=datetime.datetime(int(digits[:4]),int(digits[4:6]),int(digits[6:8]),
        int(digits[8:10]),int(digits[10:12]),int(digits[12:14]),tzinfo=datetime.timezone.utc)
    return int(date.timestamp())-(1 if zone[0]=='+' else -1)*(hours*3600+minutes*60)


class PrefixReader:
    def __init__(self,stream):
        self.stream=stream;self.prefix=self._two_bytes(b'')

    def _two_bytes(self,data):
        # A blocking VFS/HTTP read may return a short chunk before EOF.
        while len(data)<2:
            piece=self.stream.read(2-len(data))
            if not piece:break
            data+=piece
        return data

    def read(self,size=65536):
        data=self.prefix[:size];self.prefix=self.prefix[len(data):]
        if size==2:return self._two_bytes(data)
        remaining=min(65536,size-len(data))
        # Kodi VFS can interpret zero bytes as a request for the whole file.
        return data+(self.stream.read(remaining) if remaining>0 else b'')


def parse(stream,on_channel,on_programme,cancel=lambda:False,max_seconds=None,progress=None,include_icons=False,
          *,include_images=False,channel_image=None,strict_images=False):
    stream=PrefixReader(stream)
    data=gzip.GzipFile(fileobj=stream) if stream.prefix==b'\x1f\x8b' else stream
    parser=expat.ParserCreate()
    parser.buffer_text=True
    stack=[];record=None;text=[];text_length=0;picture=None;counts=dict(channels=0,programmes=0,skipped=0,bytes=0)
    deadline=None if max_seconds is None else time.monotonic()+max_seconds
    def unsafe(*args): raise UnsafeXMLTV('XMLTV DTD/entity declaration rejected')
    def doctype(name,system_id,public_id,internal):
        if name!='tv' or system_id!='xmltv.dtd' or public_id or internal: unsafe()
        # An inert XMLTV marker is common in real feeds. Expat does not load
        # it, and unknown entity references are explicitly rejected below.
    parser.StartDoctypeDeclHandler=doctype;parser.EntityDeclHandler=unsafe
    parser.ExternalEntityRefHandler=unsafe;parser.SkippedEntityHandler=unsafe
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    def picture_start(tag,attributes):
        key='_image_nodes' if tag=='image' else '_icon_nodes'
        record[key]=record.get(key,0)+1
        if record[key]>MAX_IMAGE_NODES:
            raise XMLTVLimitError('XMLTV artwork nodes exceed per-record limit','image_nodes')
        if tag=='image':
            fields=_image_attributes(attributes,strict_images)
        else:
            url=_image_url(attributes.get('src',''),strict_images)
            fields={'url':url} if url and not attributes.keys()-_ICON_ATTRIBUTES else _invalid_image(strict_images)
        return {'tag':tag,'fields':fields}

    def start(tag,attributes):
        nonlocal record,text,text_length,picture
        if len(stack)>=32: raise XMLTVLimitError('XMLTV nesting budget','nesting')
        if not stack and tag!='tv': raise XMLTVSyntaxError('Expected XMLTV tv root')
        stack.append(tag)
        direct=len(stack)==3
        if strict_images and tag=='image' and not (direct and stack[1]=='programme'):
            _invalid_image(True)
        if len(stack)==2 and tag in ('channel','programme'):
            record={key:attributes[key] for key in ('id','channel','start','stop') if key in attributes}
            record['cast']=[];record['director']=[]
        if record is not None:
            text=[];text_length=0
            if picture is not None:picture['fields']=_invalid_image(strict_images)  # These nodes must have no children.
            if strict_images and direct and stack[1]=='programme' and record.get('_image_nodes') and tag!='image':
                _invalid_image(True)  # XMLTV places programme images last.
            if tag=='icon' and direct:
                if strict_images or stack[1]=='channel' and channel_image is not None:
                    picture=picture_start(tag,attributes)
                elif stack[1]=='programme':
                    icon=attributes.get('src','')[:MAX_IMAGE_URL]
                    if not record.get('icon'):record['icon']=icon
                    if include_icons and len(record.get('icons',()))<MAX_IMAGE_NODES:
                        record.setdefault('icons',[]).append(icon)
            elif tag=='image' and direct and stack[1]=='programme' and (include_images or strict_images):
                picture=picture_start(tag,attributes)
            if tag=='episode-num': record['_episode_system']=attributes.get('system','')
            if tag=='rating' and stack[-2:]==['programme','rating']:
                record['_rating_system']=str(attributes.get('system',''))[:32]
    def characters(value):
        nonlocal text_length
        if record is None: return
        # Expat delivers bounded read chunks; discarded text is never retained.
        text_length+=len(value)
        if picture is not None and len(stack)==3 and text_length>MAX_IMAGE_URL+128:
            raise XMLTVLimitError('XMLTV artwork text exceeds limit','image_url')
        if text_length>256*1024: raise XMLTVLimitError('XMLTV field exceeds memory budget','field_bytes')
        if sum(map(len,text))<4096: text.append(value[:4096])
    def end(tag):
        nonlocal record,text,text_length,picture
        if record is not None:
            value=''.join(text).strip()[:4096]
            if picture is not None and len(stack)==3 and tag==picture['tag']:
                fields=picture['fields']
                picture=None
                if fields is not None:
                    if tag=='image':
                        url=_image_url(value,strict_images)
                        if url and include_images:record.setdefault('images',[]).append(dict(fields,url=url))
                    elif value:_invalid_image(strict_images)  # XMLTV icons are empty elements.
                    elif stack[1]=='channel':
                        if channel_image is not None:record.setdefault('logos',[]).append(fields['url'])
                    else:
                        if not record.get('icon'):record['icon']=fields['url']
                        if include_icons:record.setdefault('icons',[]).append(fields['url'])
            if tag in ('display-name','title','sub-title','date','desc','category','country') and tag not in record: record[tag]=value
            if tag=='value' and stack[-3:]==['programme','rating','value'] and value and 'rating' not in record:
                record['rating']=value[:32]
                record['rating_system']=record.get('_rating_system','')
            if tag=='director' and value and len(record.setdefault('director',[]))<8:record['director'].append(value[:120])
            if tag=='actor' and value and len(record.setdefault('cast',[]))<24:record['cast'].append(value[:120])
            if tag=='episode-num':
                if record.get('_episode_system')=='onscreen': record['episode']=value[:128]
                elif record.get('_episode_system')=='xmltv_ns':
                    parts=value.split('.')
                    if len(parts)>1 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                        record['episode']='S{:02d}E{:02d}'.format(int(parts[0])+1,int(parts[1])+1)
                        record['season']=int(parts[0])+1;record['episode_number']=int(parts[1])+1
            if len(stack)==2:
                if tag=='channel':
                    counts['channels']+=1
                    cid=record.get('id','')
                    on_channel(cid,record.get('display-name') or cid)
                    if channel_image is not None and cid:
                        for logo in record.get('logos',()):channel_image(cid,logo)
                elif tag=='programme':
                    try:
                        begin=timestamp(record.get('start'));stop=timestamp(record.get('stop'))
                        if stop<=begin or not record.get('channel'): raise ValueError('Invalid interval')
                    except (ValueError,OverflowError,TypeError): counts['skipped']+=1
                    else:
                        counts['programmes']+=1
                        event=dict(channel=record['channel'],start_timestamp=begin,stop_timestamp=stop,
                            name=str(record.get('title',''))[:512],descr=record.get('desc',''),category=record.get('category',''),
                            screenshot_uri=record.get('icon',''),episode=record.get('episode',''),rating=record.get('rating',''),
                            rating_system=record.get('rating_system',''),
                            sub_title=record.get('sub-title',''),date=record.get('date',''),cast=record.get('cast',[]),director=record.get('director',[]),
                            season=record.get('season'),episode_number=record.get('episode_number'))
                        if include_icons:event['icons']=record.get('icons',[])
                        if include_images:event['images']=record.get('images',[])
                        if record.get('country'):event['country']=record['country']
                        on_programme(event)
                record=None
        stack.pop();text=[];text_length=0
    parser.StartElementHandler=start;parser.CharacterDataHandler=characters;parser.EndElementHandler=end
    try:
        while True:
            if cancel(): raise InterruptedError('XMLTV import cancelled')
            if deadline is not None and time.monotonic()>deadline: raise TimeoutError('XMLTV streaming deadline')
            chunk=data.read(32768);counts['bytes']+=len(chunk)
            parser.Parse(chunk,not chunk)
            if progress:progress(counts)
            if not chunk: break
    except expat.ExpatError as exc:
        raise XMLTVSyntaxError('Malformed XMLTV') from exc
    finally:
        if isinstance(data,gzip.GzipFile): data.close()
    return counts
