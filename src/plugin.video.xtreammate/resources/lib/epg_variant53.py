"""Reject explicit region, SD/HD and +1 conflicts in automatic name proofs."""
import re


def compatible(provider_name,provider_id,source_name,source_id):
    def variants(name,cid):
        value=(str(name or '')+' '+str(cid or '')).casefold()
        shift=bool(re.search(r'(?:\+\s*1|@plus1|\bplus\s*1\b)',value))
        quality=next((q for q in ('uhd','fhd','hd','sd') if re.search(r'(?:^|[\s@|:._()\[\]-])'+q+r'(?:$|[\s@|:._()\[\]-])',value)),None)
        country=next((c for c in ('de','at','ch') if re.search(r'\.'+c+r'(?:@|$|\s)',value)),None)
        return shift,quality,country
    a,b=variants(provider_name,provider_id),variants(source_name,source_id)
    return a[0]==b[0] and all(x is None or y is None or x==y for x,y in zip(a[1:],b[1:]))
