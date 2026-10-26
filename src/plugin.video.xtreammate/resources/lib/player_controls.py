"""Shared local player artwork and actual Kodi info labels; no metadata fetch."""
from nav_rail import icon
NAMES=dict(pause='player-pause',play='player-play',stop='player-stop',back='rewind-backward-10',forward='rewind-forward-30',
           back30='player-skip-back',forward10='player-skip-forward',rewind='player-track-prev',fastforward='player-track-next',
           audio='volume',audio_settings='adjustments',subtitles='badge-cc',subtitle_toggle='badge-cc',subtitle='badge-cc',
           video='device-tv',info='info-circle',more='info-circle',autoplay='playlist',epg='calendar',settings='settings',tv='list',live='player-skip-forward')

def texture(name,state='normal'):return icon(NAMES.get(name,'info-circle'),state)

def status():
    import xbmc
    values=[]
    for label in ('VideoPlayer.VideoResolution','VideoPlayer.VideoCodec','VideoPlayer.AudioCodec','VideoPlayer.AudioChannels','VideoPlayer.SubtitleLanguage'):
        try:value=xbmc.getInfoLabel(label)
        except (AttributeError,RuntimeError):continue
        if isinstance(value,str) and value.strip():values.append(value.strip()[:40])
    return ' · '.join(dict.fromkeys(values))
