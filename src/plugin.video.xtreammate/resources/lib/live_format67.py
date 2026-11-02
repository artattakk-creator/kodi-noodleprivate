"""Live transport hints only; unknown URLs go to Kodi's native demuxer."""
from urllib.parse import urlsplit
def kind(url):
 try:path=urlsplit(url.partition('|')[0]).path.lower()
 except ValueError:return 'http'
 if path.endswith('.m3u8'):return 'hls'
 if path.endswith('.mpd'):return 'dash'
 if path.endswith('.ts'):return 'direct'
 if path.startswith(('rtmp:','rtsp:')):return 'http'
 return 'http'
def configure(item,url,kind):
 path=urlsplit(url.partition('|')[0]).path.lower()
 mime='video/mp2t' if path.endswith('.ts') else 'application/vnd.apple.mpegurl' if kind=='hls' else 'application/dash+xml' if kind=='dash' else ''
 if mime:
  if callable(getattr(item,'setMimeType',None)):item.setMimeType(mime)
  if callable(getattr(item,'setContentLookup',None)):item.setContentLookup(False)
 item.setProperty('XCMate.LiveTransport67',kind)

def extension():
 from utils import setting
 try:value=int(setting('live_stream_format67','0'))
 except (ValueError,TypeError):value=0
 return 'm3u8' if value==2 else 'ts'
