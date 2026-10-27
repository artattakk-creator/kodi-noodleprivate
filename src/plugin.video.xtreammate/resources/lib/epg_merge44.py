"""Legacy M3U/STB feeds use the same conservative interval-gap policy."""
from bisect import bisect_left


def extend(existing,incoming,source_index):
    from epg_views import _as_int
    rows=list(existing or []);ranges=[]
    def bounds(e):return _as_int(e.get('start_timestamp',e.get('start'))),_as_int(e.get('stop_timestamp',e.get('stop')))
    for row in sorted(rows,key=lambda e:bounds(e)[0]):
        start,stop=bounds(row)
        if stop<=start:continue
        if ranges and start<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],max(stop,ranges[-1][1]))
        else:ranges.append((start,stop))
    starts=[r[0] for r in ranges];added=0
    for row in sorted(incoming or [],key=lambda e:bounds(e)[0]):
        start,stop=bounds(row)
        if start<=0 or stop<=start or not (row.get('name') or row.get('title')):continue
        pos=bisect_left(starts,start)
        if pos and ranges[pos-1][1]>start or pos<len(ranges) and ranges[pos][0]<stop:continue
        ranges.insert(pos,(start,stop));starts.insert(pos,start);rows.append(dict(row,_source_index=source_index));added+=1
    rows.sort(key=lambda e:bounds(e));return rows,added
