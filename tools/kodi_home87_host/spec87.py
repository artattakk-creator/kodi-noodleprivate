"""Synthetic existing user sources, deliberately not XCMate plugin URLs."""
FOREIGN=[
 ('MP3 Streams Echoed','plugin.audio.m3sr2019','albums','music',(160,70,180)),
 ('SHOUTcast','plugin.audio.shoutcast','songs','music',(60,170,180)),
 ('Neu im Kino','plugin.video.fixture87.cinema','movies','videos',(180,100,30)),
 ('Meine Serien','plugin.video.fixture87.series','tvshows','videos',(100,60,180)),
 ('Mein Wetter','plugin.video.fixture87.weather','movies','videos',(140,170,40)),
 ('Meine Nachrichten','plugin.video.fixture87.news','movies','videos',(40,140,190)),
 ('Frisch im Kino','plugin.video.fixture87.cinema','movies','videos',(180,100,30)),
 ('Diese Woche im Trend','plugin.video.fixture87.trends','tvshows','videos',(160,60,110)),
]
def uri(index):
 from urllib.parse import urlencode
 return 'plugin://'+FOREIGN[index][1]+'/?'+urlencode(dict(row87=index))
