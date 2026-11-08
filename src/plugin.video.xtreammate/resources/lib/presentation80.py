"""Bounded display-only text and exact selected-channel EPG entry context."""
import re,unicodedata

def text(value):
 value=str(value or '')
 return value.replace('\\r\\n','\n').replace('\\n','\n').replace('\r\n','\n').replace('\r','\n')[:8192]

def clipped(value,width):
 # Never let an inherited large skin font paint across a narrow EPG cell.
 value=' '.join(text(value).split());budget=max(0,int(width-12)//16)
 if not budget:return ''
 used=0;out=[]
 for c in value:
  used+=2 if unicodedata.east_asian_width(c) in ('W','F') else 1
  if used>budget:return ''.join(out[:-1])+'…' if out else ''
  out.append(c)
 return value

def guide_entry(router,portal):
 params=getattr(router,'_params',{})
 sid=str(params.get('guide_sid80') or '')
 category=str(params.get('guide_group80') or '')
 if not sid:
  from playback_exit import identity
  import xbmc
  try:
   owned=identity(xbmc.Player())
   if owned and owned[0]=='live' and owned[1].get('pid')==str(portal['id']):sid=str(owned[1].get('sid') or '')
  except (RuntimeError,AttributeError,ValueError):pass
 if not sid:sid=__import__('hero_epg63').focused64(portal['id'])
 return sid,category
