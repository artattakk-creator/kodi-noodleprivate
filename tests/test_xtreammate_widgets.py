"""EPG, VOD metadata and Kodi widget integrations, independent of IPTV provider."""
import importlib.util
import sys
import unittest
from pathlib import Path

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'

def load(name):
    spec=importlib.util.spec_from_file_location('xm_widget_test_'+name, LIB/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

epg=load('epg_views')
media=load('metadata_views')

class WidgetsTest(unittest.TestCase):
    def test_live_now_and_next(self):
        guide={'epg-rtl':[
            {'name':'Nachrichten','start_timestamp':1700000000,'stop_timestamp':1700003600,'descr':'Heute'},
            {'name':'Film','start_timestamp':1700003600,'stop_timestamp':1700007200}]}
        info=epg.guide_for_channel(guide,'epg-rtl','54',1700001800)
        self.assertEqual(info['now'],'Nachrichten')
        self.assertEqual(info['next'],'Film')
        self.assertIn('Heute',epg.programme_plot(info))
        self.assertIn('Danach',epg.row_title('RTL',info))
    def test_no_epg_never_guesses(self):
        d=epg.guide_for_channel({},'wrong','3')
        self.assertEqual(d['now'],'')
        self.assertEqual(d['next'],'')
        self.assertIn('keine EPG',epg.programme_plot(d))
    def test_next_only(self):
        guide={'5':[{'title':'Sport','start_timestamp':1700003600,'stop_timestamp':1700007200}]}
        d=epg.guide_for_channel(guide,'5',now=1700001800)
        self.assertFalse(d['now'])
        self.assertEqual(d['next'],'Sport')
    def test_provider_synopsis_fallback(self):
        self.assertEqual(media.provider_plot({'description':'Kurze Beschreibung'}),'Kurze Beschreibung')
        self.assertEqual(media.provider_plot({'info':{'plot':'Info-Text'}}),'Info-Text')
        self.assertEqual(media.provider_plot({}),'')
    def test_youtube_whitelist(self):
        ident='aBcD123_XyZ'
        for data in ({'youtube_trailer':ident},{'trailer':'https://youtu.be/'+ident},
                     {'youtube_trailer':'https://www.youtube.com/watch?v='+ident},
                     {'info':{'trailer':'https://youtube.com/shorts/'+ident}}):
            self.assertEqual(media.trailer_id(data),ident)
        for input in ('https://evil-youtube.com/watch?v='+ident,
                      'https://youtube.com.evil.invalid/watch?v='+ident,
                      'not an id','../some/file'):
            self.assertIsNone(media.trailer_id({'trailer':input}))
    def test_widget_route_and_no_cached_credentials_in_link(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn("'widget_groups'",source)
        self.assertIn("'widget_channels'",source)
        body=source.split('    def _widget_channels(self):')[1].split('    def _media_details(self):')[0]
        self.assertIn("self.url(action='play_live', pid=p['id'],sid=sid",body)
        self.assertIn('get_cached_catalog',body)
        self.assertIn("li.setInfo('video'",body)
        self.assertNotIn('http_get(',body)
    def test_film_trailer_and_details_routes(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn("'media_details'",source)
        self.assertIn("'trailer'",source)
        self.assertIn('self._add_media_context(li, s,',source)
        self.assertIn('self._add_media_context(li, v,',source)

if __name__=='__main__':unittest.main()
