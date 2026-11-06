"""Public image resize modifiers only; signed/authentication queries stay out."""
import re
from urllib.parse import parse_qsl
def public_query(query):
    if not query:return True
    if len(query)>256:return False
    try:rows=parse_qsl(query,keep_blank_values=True,strict_parsing=True)
    except ValueError:return False
    if not 0<len(rows)<=8 or len({k for k,v in rows})!=len(rows):return False
    choices={'fit':{'crop','clip','fill','max','scale','contain','cover'},'format':{'jpg','jpeg','png'},'fm':{'jpg','jpeg','png'},'crop':{'center','faces','edges'},'auto':{'format','compress','compress,format','format,compress'}}
    for key,value in rows:
        if key in ('w','h','width','height'):
            if not value.isascii() or not value.isdigit() or not 1<=int(value)<=4096:return False
        elif key in ('q','quality'):
            if not value.isascii() or not value.isdigit() or not 1<=int(value)<=100:return False
        elif key not in choices or value not in choices[key]:return False
    return True
