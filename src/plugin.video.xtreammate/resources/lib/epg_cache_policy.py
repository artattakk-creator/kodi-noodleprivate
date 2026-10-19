"""Background-only coverage check; never initiates HTTP or changes source data."""
import math
import time


def enough_coverage(cache, now=None, runway=86400):
    """Reuse a saved guide while every represented channel covers the next day.

    Latest end time alone is insufficient: one isolated programme next week
    does not cover tonight. Require continuous valid intervals from now,
    allowing at most 60 seconds rounding between adjacent programmes.
    Aliases of a channel are harmless; empty/malformed channels fail closed.
    """
    now=time.time() if now is None else now
    if not isinstance(cache,dict) or not cache: return False
    found=False
    for events in cache.values():
        if not isinstance(events,list) or not events: return False
        intervals=[]
        for event in events:
            if not isinstance(event,dict): continue
            try:
                start=float(event['start_timestamp']);stop=float(event['stop_timestamp'])
                if not math.isfinite(start) or not math.isfinite(stop): continue
                if stop>max(start,now) and (event.get('name') or event.get('title')):
                    intervals.append((start,stop))
            except (KeyError,ValueError,TypeError,OverflowError): continue
        if not intervals: return False
        end=now
        for start,stop in sorted(intervals):
            if start>end+60: break
            end=max(end,stop)
            if end>=now+runway: break
        if end<now+runway: return False
        found=True
    return found
