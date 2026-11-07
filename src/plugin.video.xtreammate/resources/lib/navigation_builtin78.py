"""Strict own-plugin URI/builtin boundary; never execute a directory as code."""
import re
from urllib.parse import urlsplit,quote

def uri(value):
    if not isinstance(value,str) or not value or len(value)>4096 or any(ord(c)<32 for c in value):raise ValueError('INVALID_NAVIGATION')
    value=value.strip()
    if value.lower().startswith('activatewindow('):
        match=re.fullmatch(r'ActivateWindow\((?:Videos|10025),\s*("[^"]*"|[^,()]*),\s*return\)',value,re.I)
        if not match:raise ValueError('INVALID_NAVIGATION')
        value=match[1].strip('"')
    parsed=urlsplit(value)
    if parsed.scheme!='plugin' or parsed.netloc!='plugin.video.xtreammate' or parsed.fragment or any(c in value for c in ('"','\\','(',')')):raise ValueError('INVALID_NAVIGATION')
    return value

def activate(value):
    return 'ActivateWindow(Videos,"'+uri(value)+'",return)'

def update(value):
    return 'Container.Update("'+uri(value)+'",replace)'
