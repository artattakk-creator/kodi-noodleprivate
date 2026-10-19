"""SAX XMLTV reader: bounded text/depth, no document tree or strptime import.

Only the inert XMLTV doctype marker is accepted; no entity/DTD is loaded. A source is staged
until the entire XML and gzip trailer validate. Large feeds have no aggregate
byte/programme cap; memory is bounded per element, disk by actual free space.
"""
import datetime
import gzip
import io
import re
import time
from xml.parsers import expat
from epg_io import XMLTVLimitError


class UnsafeXMLTV(ValueError):
    pass


class XMLTVSyntaxError(ValueError):
    pass


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
        self.stream=stream;self.prefix=stream.read(2)
    def read(self,size=65536):
        data=self.prefix[:size];self.prefix=self.prefix[len(data):]
        return data+self.stream.read(min(65536,size-len(data)))


def parse(stream,on_channel,on_programme,cancel=lambda:False,max_seconds=300):
    stream=PrefixReader(stream)
    data=gzip.GzipFile(fileobj=stream) if stream.prefix==b'\x1f\x8b' else stream
    parser=expat.ParserCreate()
    parser.buffer_text=True
    stack=[];record=None;text=[];text_length=0;attrs={};counts=dict(channels=0,programmes=0,skipped=0,bytes=0)
    deadline=time.monotonic()+max_seconds
    def unsafe(*args): raise UnsafeXMLTV('XMLTV DTD/entity declaration rejected')
    def doctype(name,system_id,public_id,internal):
        if name!='tv' or system_id!='xmltv.dtd' or public_id or internal: unsafe()
        # An inert XMLTV marker is common in real feeds. Expat does not load
        # it, and unknown entity references are explicitly rejected below.
    parser.StartDoctypeDeclHandler=doctype;parser.EntityDeclHandler=unsafe
    parser.ExternalEntityRefHandler=unsafe;parser.SkippedEntityHandler=unsafe
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    def start(tag,attributes):
        nonlocal record,text,text_length,attrs
        if len(stack)>=32: raise XMLTVLimitError('XMLTV nesting budget','nesting')
        if not stack and tag!='tv': raise XMLTVSyntaxError('Expected XMLTV tv root')
        stack.append(tag)
        if len(stack)==2 and tag in ('channel','programme'):
            record=dict(attributes);record['type']=tag
        if record is not None:
            text=[];text_length=0;attrs=attributes
            if tag=='icon': record['icon']=str(attributes.get('src',''))[:2048]
            if tag=='episode-num': record['_episode_system']=attributes.get('system','')
    def characters(value):
        nonlocal text_length
        if record is None: return
        # Expat delivers bounded read chunks; discarded text is never retained.
        text_length+=len(value)
        if text_length>256*1024: raise XMLTVLimitError('XMLTV field exceeds memory budget','field_bytes')
        if sum(map(len,text))<4096: text.append(value[:4096])
    def end(tag):
        nonlocal record,text,text_length
        if record is not None:
            value=''.join(text).strip()[:4096]
            if tag in ('display-name','title','desc','category','value') and tag not in record: record[tag]=value
            if tag=='episode-num':
                if record.get('_episode_system')=='onscreen': record['episode']=value[:128]
                elif record.get('_episode_system')=='xmltv_ns':
                    parts=value.split('.')
                    if len(parts)>1 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                        record['episode']='S{:02d}E{:02d}'.format(int(parts[0])+1,int(parts[1])+1)
            if len(stack)==2:
                if tag=='channel':
                    counts['channels']+=1
                    on_channel(str(record.get('id','')),str(record.get('display-name') or record.get('id','')))
                elif tag=='programme':
                    try:
                        begin=timestamp(record.get('start'));stop=timestamp(record.get('stop'))
                        if stop<=begin or not record.get('channel'): raise ValueError('Invalid interval')
                    except (ValueError,OverflowError,TypeError): counts['skipped']+=1
                    else:
                        counts['programmes']+=1
                        on_programme(dict(channel=str(record['channel']),start_timestamp=begin,stop_timestamp=stop,
                            name=str(record.get('title',''))[:512],descr=record.get('desc',''),category=record.get('category',''),
                            screenshot_uri=record.get('icon',''),episode=record.get('episode',''),rating=record.get('value','')))
                record=None
        stack.pop();text=[];text_length=0
    parser.StartElementHandler=start;parser.CharacterDataHandler=characters;parser.EndElementHandler=end
    try:
        while True:
            if cancel(): raise InterruptedError('XMLTV import cancelled')
            if time.monotonic()>deadline: raise TimeoutError('XMLTV streaming deadline')
            chunk=data.read(32768);counts['bytes']+=len(chunk)
            parser.Parse(chunk,not chunk)
            if not chunk: break
    except expat.ExpatError as exc:
        raise XMLTVSyntaxError('Malformed XMLTV') from exc
    finally:
        if isinstance(data,gzip.GzipFile): data.close()
    return counts
