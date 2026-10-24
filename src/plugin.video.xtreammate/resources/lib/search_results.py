"""Typed local search rows; no HTTP, SQL or artwork jobs in presentation."""
import xbmcgui
from localization import tr
from media_art import local_art

KINDS={'live':35100,'vod':35101,'series':35102}


def secondary(row):
    kind=row.get('kind','vod');parts=[tr(KINDS.get(kind,35101))]
    if kind=='live':
        title=str(row.get('_now_title') or '')[:512]
        parts.append(tr(35103)+': '+title if title else tr(35104))
    else:
        year=str(row.get('year') or row.get('releaseDate') or '')[:4]
        if year.isdigit() and 1880<=int(year)<=2100:parts.append(year)
        genre=row.get('genre')
        if isinstance(genre,str) and genre.strip():parts.append(genre.strip()[:100])
    return ' · '.join(parts)


def item(row,theme=None):
    result=xbmcgui.ListItem(str(row.get('name') or ''))
    kind=row.get('kind','vod')
    result.setArt(local_art(dict(row,kind=kind),theme))
    result.setProperty('XCMate.SearchKind',kind if kind in KINDS else 'vod')
    result.setProperty('XCMate.SearchSecondary',secondary(row))
    return result
