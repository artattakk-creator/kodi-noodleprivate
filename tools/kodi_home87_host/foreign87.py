"""Independent native plugin, synthetic local content, never production code."""
import json,sys,time
from pathlib import Path
from urllib.parse import parse_qs,urlencode
import xbmc,xbmcgui,xbmcplugin
sys.path.insert(0,'/')
from spec87 import FOREIGN,uri
params=parse_qs(sys.argv[2].lstrip('?'));handle=int(sys.argv[1]);index=int(params.get('row87',['0'])[0]);name,addon,content,target,color=FOREIGN[index]
if params.get('play87'):
 with Path('/root/foreign87-clicks.jsonl').open('a') as stream:stream.write(json.dumps(dict(row=index,addon=addon,at=time.time()))+'\n')
 item=xbmcgui.ListItem(path='/root/foreign87.wav');xbmcplugin.setResolvedUrl(handle,True,item)
else:
 for i in range(8):
  item=xbmcgui.ListItem(name+' '+str(i));item.setProperty('IsPlayable','true');item.setProperty('Foreign87',str(index));item.setProperty('SourceStatus87','OFFLINE_CACHED' if Path('/root/foreign87-off').exists() else 'LOCAL_FIXTURE')
  item.setArt(dict(poster='/root/foreign87-'+str(index)+'.png',thumb='/root/foreign87-'+str(index)+'.png',fanart='/root/foreign87-'+str(index)+'.png'))
  if target=='music':item.setInfo('music',dict(title=name+' '+str(i),album=name,artist=['Synthetic artist']))
  else:item.setInfo('video',dict(title=name+' '+str(i),mediatype='tvshow' if content=='tvshows' else 'movie',plot='Synthetic independent source, not Android or real provider verification.'))
  xbmcplugin.addDirectoryItem(handle,uri(index)+'&play87='+str(i+1),item,False)
 xbmcplugin.setContent(handle,content);xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
