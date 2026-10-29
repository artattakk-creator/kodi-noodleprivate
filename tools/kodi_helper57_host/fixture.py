"""Synthetic provider in REAL Kodi. This is explicitly NOT TMDb Helper."""
import json,sys,time,threading
from urllib.parse import parse_qs
import xbmc,xbmcgui,xbmcplugin
p=parse_qs(sys.argv[2].lstrip('?'));handle=int(sys.argv[1])
internal=None
if p.get('internal')==['true']:
    captured=[]
    def execute():
        captured.append(json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=57,method='Files.GetDirectory',params=dict(directory='plugin://plugin.video.xcmate.contract57/?info=details',media='video',properties=['title','year','art','uniqueid']))))))
    worker=threading.Thread(target=execute);worker.start()
    until=time.monotonic()+8
    while worker.is_alive() and time.monotonic()<until:xbmc.sleep(25)
    internal=bool(captured and len(captured[0].get('result',{}).get('files',[]))==1)
if p.get('slow')==['true']:time.sleep(3)
episode=p.get('episode')==['3']
title='Test Episode' if episode else 'Harry Potter und die Kammer des Schreckens'
li=xbmcgui.ListItem(title,offscreen=True)
tag=li.getVideoInfoTag();tag.setTitle(title);tag.setYear(2002);tag.setMediaType('episode' if episode else 'movie');tag.setUniqueIDs({'tmdb':'999001' if episode else '672'},'tmdb')
if episode:tag.setSeason(2);tag.setEpisode(3);tag.setTvShowTitle('Test Series')
li.setArt({'fanart':'https://image.tmdb.org/t/p/w500/SYNTHETIC_CONTRACT_ONLY.jpg','poster':'https://image.tmdb.org/t/p/w500/SYNTHETIC_POSTER_ONLY.jpg'})
li.setProperty('TMDb_ID','672')
li.setProperty('H57.DialogId',str(xbmcgui.getCurrentWindowDialogId()))
if internal is not None:li.setProperty('H57.InternalWorkerPassed',str(internal))
path='plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=tv&tmdb_id=1399&season=2&episode=3' if episode else 'plugin://plugin.video.themoviedb.helper/?info=details&tmdb_type=movie&tmdb_id=672'
xbmcplugin.addDirectoryItem(handle,path,li,False)
xbmcplugin.endOfDirectory(handle,cacheToDisc=False)
