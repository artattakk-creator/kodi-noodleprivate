"""One bounded, cache-only inventory; never open thousands of absent EPG files."""
import os


def candidates(client, rows, cancel=lambda:False):
    """Return existing cache candidates, or None when absence cannot be proved.

    Only opaque filenames are compared. Unreadable/unsupported roots retain the
    old cache-only path, so an inventory failure cannot suppress valid results.
    A generation's existing ShortGuideRevision invalidation covers new files.
    """
    if not callable(getattr(client, '_cache_key', None)):
        return None
    try:
        from utils import cache_dir, _private_cache_dir
        names=set()
        for root in dict.fromkeys((cache_dir(), _private_cache_dir())):
            if cancel():return None
            if '://' in root:
                import xbmcvfs
                _, files=xbmcvfs.listdir(root)
                if len(files)>100000:return None
                names.update(files)
            else:
                try:
                    with os.scandir(root) as entries:
                        for entry in entries:
                            if cancel() or len(names)>=100000:return None
                            names.add(entry.name)
                except FileNotFoundError:
                    continue
        result=[]
        for row in rows:
            if cancel():return None
            if any(client._cache_key('get_short_epg',dict(stream_id=row['sid'],limit=limit))+'.json' in names
                   for limit in (12,4)):
                result.append(row)
        return result
    except (OSError,RuntimeError,ValueError,TypeError,AttributeError):
        return None
