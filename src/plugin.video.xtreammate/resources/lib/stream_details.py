"""Owner-checked Kodi21 InfoLabels, sampled only while own UI is visible.

No RPC/network, guessed quality, v22-only bitrate fields or provider metadata.
Empty values stay unknown. Cached fields are discarded on session change/Stop.
"""
import math
import time
from localization import tr

LABELS={
    'width':'Player.Process(VideoWidth)','height':'Player.Process(VideoHeight)',
    'fps':'Player.Process(VideoFPS)','scan':'Player.Process(VideoScanType)',
    'aspect':'Player.Process(VideoDAR)','decoder':'Player.Process(VideoDecoder)',
    'pixels':'Player.Process(PixFormat)','video':'VideoPlayer.VideoCodec',
    'hdr':'VideoPlayer.HdrType','audio':'VideoPlayer.AudioCodec',
    'channels':'VideoPlayer.AudioChannels','language':'VideoPlayer.AudioLanguage',
    'subtitles':'VideoPlayer.SubtitlesLanguage','samplerate':'Player.Process(AudioSamplerate)'}


def own(player,token):
    from playback_exit import identity,_same
    try:return _same(identity(player),token)
    except (AttributeError,RuntimeError,TypeError,ValueError):return False


def number(value,ceiling):
    try:
        n=float(value)
        return n if math.isfinite(n) and 0<n<=ceiling else None
    except (TypeError,ValueError):return None


class Details:
    def __init__(self):self.token=None;self.values={};self.next_sample=0

    def read(self,player,token):
        from playback_exit import _same
        if not token or not own(player,token):
            self.token=None;self.values={};self.next_sample=0;return {}
        if not _same(token,self.token):self.token=token;self.values={};self.next_sample=0
        if time.monotonic()<self.next_sample:return dict(self.values)
        import xbmc
        values={}
        for key,label in LABELS.items():
            try:value=xbmc.getInfoLabel(label)
            except (AttributeError,RuntimeError):continue
            if isinstance(value,str) and value.strip() and '://' not in value:values[key]=value.strip()[:80]
        for key,limit in (('width',16384),('height',16384),('fps',240)):
            n=number(values.get(key),limit)
            if n is None:values.pop(key,None)
            else:values[key]=format(n,'g')
        # Missing HDR/scan is unknown, never inferred SDR/progressive.
        try:values['subtitle_enabled']=bool(xbmc.getCondVisibility('VideoPlayer.SubtitlesEnabled'))
        except (AttributeError,RuntimeError):pass
        if not own(player,token):self.token=None;self.values={};return {}
        self.values=values;self.next_sample=time.monotonic()+2
        return dict(values)


def compact(values):
    parts=[]
    if values.get('width') and values.get('height'):
        scan={'progressive':'p','interlaced':'i','p':'p','i':'i'}.get(values.get('scan','').lower(),'')
        parts.append(values['width']+'×'+values['height']+scan)
    if values.get('fps'):parts.append(values['fps']+' fps')
    parts.extend(values[k] for k in ('video','audio','channels','language','hdr') if values.get(k))
    if values.get('subtitles'):parts.append(tr(35801)+': '+values['subtitles'])
    return ' · '.join(parts)


def text(values):
    if not values:return tr(35800)
    keys=('width','height','scan','fps','aspect','video','decoder','pixels','hdr','audio','channels','language','samplerate','subtitles')
    lines=[tr(35810+i)+': '+values.get(key,tr(35800)) for i,key in enumerate(keys)]
    if 'subtitle_enabled' in values:lines.append(tr(35801)+': '+tr(35802 if values['subtitle_enabled'] else 35803))
    lines.append(tr(35804))
    return '\n'.join(lines)
