"""Visible content identity and cached native writes, independent of progress."""
def signature(values):
    def events(rows):
        return tuple((e.get('start',e.get('start_timestamp')),e.get('stop',e.get('stop_timestamp')),e.get('title',e.get('name')),e.get('description',e.get('descr'))) for e in rows if isinstance(e,dict))
    return tuple((sid,tuple(value.get(k) for k in ('now','next','description','start','stop','next_start','next_stop','source_index','image')),events(value.get('events',[])),events(value.get('programme_events',[]))) for sid,value in sorted(values.items()))


def write(owner,control,method,*values):
    cache=getattr(owner,'_row_paint44',None)
    if cache is None:owner._row_paint44=cache={}
    key=(id(control),method)
    if cache.get(key)!=values:
        getattr(control,method)(*values);cache[key]=values
