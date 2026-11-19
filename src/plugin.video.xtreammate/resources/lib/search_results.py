"""Typed local search rows; no HTTP, SQL or artwork jobs in presentation."""
import time
import xbmcgui
from localization import tr
from media_art import local_art

KINDS={'live':35100,'vod':35101,'series':35102}


def clock(timestamp):
    return time.strftime('%H:%M',time.localtime(timestamp)) if timestamp else ''


def secondary(row):
    kind=row.get('kind','vod');parts=[tr(KINDS.get(kind,35101))]
    if kind=='live':
        title=str(row.get('_now_title') or '')[:512]
        if title:
            interval='–'.join(v for v in (clock(row.get('_now_start')),clock(row.get('_now_stop'))) if v)
            prefix=tr(36031) if row.get('_now_match') else tr(35103)
            parts.append(' '.join(v for v in (prefix,interval,title) if v))
        else:parts.append(tr(35104))
    else:
        year=str(row.get('year') or row.get('releaseDate') or '')[:4]
        if year.isdigit() and 1880<=int(year)<=2100:parts.append(year)
        genre=row.get('genre')
        if isinstance(genre,str) and genre.strip():parts.append(genre.strip()[:100])
        language=row.get('languages') or row.get('language')
        if isinstance(language,list):language=', '.join(v[:20] for v in language[:4] if isinstance(v,str))
        if isinstance(language,str) and language.strip():parts.append(language.strip()[:60])
        quality=str(row.get('quality') or row.get('video_quality') or '').strip().upper()
        if quality in ('SD','HD','FHD','UHD','4K','720P','1080P','2160P'):parts.append(quality)
        if kind=='series':
            seasons=row.get('num_seasons',row.get('season_count',row.get('seasons_count')))
            if isinstance(seasons,int) and not isinstance(seasons,bool) and 0<seasons<=1000:parts.append(tr(35951,seasons))
        source=row.get('_portal_name43')
        if isinstance(source,str) and source.strip():parts.append(source.strip()[:80])
    return ' · '.join(parts)


def tertiary(row):
    if row.get('kind')!='live':return ''
    next_title=str(row.get('_next_title') or '')[:90]
    following=' '.join(v for v in (tr(36032),clock(row.get('_next_start')),next_title) if v) if next_title else ''
    source=row.get('_epg_source_name') or {'provider':tr(32555),'xmltv':'XMLTV'}.get(row.get('_epg_source'),'')
    return ' · '.join(v for v in (following,source) if v)


def item(row,theme=None,art=None):
    result=xbmcgui.ListItem(str(row.get('name') or ''))
    kind=row.get('kind','vod')
    result.setArt(local_art(dict(row,kind=kind),theme) if art is None else art)
    result.setProperty('XCMate.SearchKind',kind if kind in KINDS else 'vod')
    result.setProperty('XCMate.SearchSecondary',secondary(row))
    result.setProperty('XCMate.SearchTertiary',tertiary(row))
    return result
