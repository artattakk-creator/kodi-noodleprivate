"""Credentialless image redirects, local previews and a real native hero list."""
import importlib
import io
from pathlib import Path
import sys
import threading
import time
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as E
from PIL import Image
from xcmate027_fixture import Fixture,ADDON,LIB

class ImagesHero48(Fixture,unittest.TestCase):
    def image(self):
        out=io.BytesIO();Image.new('RGB',(320,180),(20,70,90)).save(out,'PNG');return out.getvalue()
    def response(self,status=200,location=''):
        return types.SimpleNamespace(status=status,headers={'Location':location},close=mock.Mock())
    def test_public_cdn_redirect_revalidates_dns_and_never_forwards_credentials(self):
        module=importlib.import_module('image_redirect48');a=self.response(302,'https://cdn.example.test/a.png');b=self.response()
        connect=mock.Mock(side_effect=[a,b]);dns=mock.Mock(return_value=['8.8.8.8'])
        value=module.open_image('https://origin.example.test/a',{'Authorization':'SECRET','Cookie':'SECRET','Referer':'SECRET','Accept':'image/png'},connect,dns)
        self.assertIs(value,b);self.assertEqual(dns.call_count,2);a.close.assert_called_once()
        self.assertEqual(connect.call_args_list[-1].args[2],{'Accept':'image/png'})
    def test_https_downgrade_and_url_credentials_are_blocked_before_destination_request(self):
        module=importlib.import_module('image_redirect48');error=importlib.import_module('media_sources43').SourceError
        for location in ('http://cdn.example.test/a','https://user:SECRET@cdn.example.test/a','https://127.0.0.1/a','https://router.local/a','file:///etc/passwd'):
            connect=mock.Mock(return_value=self.response(302,location))
            with self.assertRaises(error):module.open_image('https://origin.example.test/a',{},connect,lambda u:['8.8.8.8'])
            self.assertEqual(connect.call_count,1)
    def test_redirect_chain_has_strict_three_hop_limit_and_no_retry_loop(self):
        module=importlib.import_module('image_redirect48');error=importlib.import_module('media_sources43').SourceError
        responses=[self.response(302,'https://cdn.example.test/'+str(i)) for i in range(5)]
        connect=mock.Mock(side_effect=responses)
        with self.assertRaises(error):module.open_image('https://origin.example.test/a',{},connect,lambda u:['8.8.8.8'])
        self.assertEqual(connect.call_count,4)
    def test_redirect_loop_and_cancel_never_start_unbounded_worker_or_request(self):
        module=importlib.import_module('image_redirect48');error=importlib.import_module('media_sources43').SourceError
        connect=mock.Mock(return_value=self.response(302,'https://origin.example.test/a'))
        with self.assertRaises(error):module.open_image('https://origin.example.test/a',{},connect,lambda u:['8.8.8.8'])
        self.assertEqual(connect.call_count,1)
        with self.assertRaises(error):module.open_image('https://origin.example.test/a',{},connect,lambda u:[],cancel=lambda:True)
        self.assertEqual(connect.call_count,1)
    def test_private_dns_answer_is_rejected_by_existing_pinned_address_resolver(self):
        from download_redirect import addresses
        with mock.patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(Exception):addresses('https://public.example.test/image')
    def test_decoder_verified_offline_manual_choice_is_a_real_preview(self):
        overrides=importlib.import_module('media_overrides43');storage=importlib.import_module('art_storage')
        with mock.patch.object(storage,'check'):overrides.save('p','vod','1',image=self.image())
        item=overrides.apply_many('p',[dict(kind='vod',sid='1',name='Movie')])[0]
        preview=importlib.import_module('media_preview48');rows=preview.candidates('p',item)
        self.assertTrue(rows[0]['local_path48']);self.assertEqual(preview.local_bytes('p',rows[0]['local_path48']),self.image())
        sys.modules['utils'].http_get.assert_not_called()
    def test_offline_preview_cannot_read_an_arbitrary_file_or_symlink(self):
        preview=importlib.import_module('media_preview48');error=importlib.import_module('media_sources43').SourceError
        filename=self.folder/'private.png';filename.write_bytes(self.image())
        with self.assertRaises(error):preview.local_bytes('p',str(filename))
    def test_xmltv_rating_icon_cannot_replace_the_actual_programme_image(self):
        parser=importlib.import_module('xmltv_stream');events=[]
        data=b'<tv><programme channel="a" start="20261028090000 +0000" stop="20261028100000 +0000"><title>Actual episode</title><icon src="https://image.example.test/episode.png"/><credits><actor>Actual actor</actor><director>Actual director</director></credits><rating><icon src="https://image.example.test/age-logo.png"/></rating></programme></tv>'
        parser.parse(io.BytesIO(data),lambda *a:None,events.append)
        self.assertEqual(events[0]['screenshot_uri'],'https://image.example.test/episode.png');self.assertEqual(events[0]['director'],['Actual director'])
        meta=importlib.import_module('programme_store46').metadata(events[0]);self.assertEqual(meta['director'],'Actual director')
    def test_hero_includes_small_station_buttons_with_focus_only_local_bindings(self):
        tree=E.parse(ADDON/'resources/skins/Default/720p/XCMateLiveHero48.xml');panel=tree.find(".//control[@id='200']")
        self.assertEqual(panel.findtext('orientation'),'horizontal');self.assertLess(int(panel.find('itemlayout').get('width')),160)
        self.assertTrue(any('ProgrammeImage46' in (e.text or '') for e in tree.iter('texture')))
        self.assertFalse(list(tree.iter('onfocus')));self.assertFalse(list(tree.iter('onclick')))
        self.assertNotIn('http',E.tostring(tree.getroot(),encoding='unicode'))
    def test_hero_lists_all_88_and_focus_does_not_start_a_stream(self):
        module=importlib.import_module('live_hero48');rows=[dict(sid=str(i),name='Station '+str(i)) for i in range(88)]
        items=[dict(label=r['name'],url='plugin://plugin.video.xtreammate/?action=play_live&pid=p&sid='+r['sid'],info={},art={},props={}) for r in rows]
        window=module.LiveHeroWindow48('XCMateLiveHero48.xml',str(ADDON),'Default','720p');window.configure(self.router,self.portal);window.show();self.addCleanup(window.close)
        from concurrent.futures import Future
        f=Future();f.set_result((rows,items,'READY'));window.future=f;window.next=time.monotonic()+100;window.pump()
        self.assertEqual(window.getControl(200).size(),88)
        with mock.patch('socket.getaddrinfo',side_effect=AssertionError('network on focus')),mock.patch('sqlite3.connect',side_effect=AssertionError('DB on focus')):
            window.getControl(200).selectItem(87);window.onAction(types.SimpleNamespace(getId=lambda:2))
        self.assertFalse(window.intent);self.assertFalse(self.builtins)
        window.onClick(200);self.assertEqual(window.intent['sid'],'87');self.assertTrue(window._closed)
    def test_programme_prefetch_rotates_beyond_first_sixteen_without_widget_repaint(self):
        p=importlib.import_module('programme_prefetch48');p._next.clear();p._positions.clear();rows=[dict(sid=str(i),name=str(i)) for i in range(88)]
        seen=[]
        with mock.patch('local_epg.now_next',return_value={}),mock.patch('programme_events46.from_info',side_effect=lambda portal,row,info:dict(title='Real',key=row['sid'])),mock.patch('programme_urls55.enqueue',side_effect=lambda e,**kw:seen.append(e['key'])),mock.patch('programme_index46.publish'):
            for _ in range(11):
                p._next.clear();p.prepare(self.portal,rows)
        self.assertEqual(set(seen),{str(i) for i in range(88)});self.assertEqual(len(seen),88)
    def test_cancelled_prefetch_does_not_touch_source_or_create_picture_jobs(self):
        p=importlib.import_module('programme_prefetch48');p._next.clear()
        with mock.patch('programme_urls55.enqueue') as enqueue:
            self.assertFalse(p.prepare(self.portal,[dict(sid='1')],cancel=lambda:True));enqueue.assert_not_called()
    def test_bingie_review_include_has_no_movies_series_rebinding_or_auto_apply(self):
        folder=ADDON.parents[1]/'integrations/titan-bingie-mod/0.1.29.48'
        text=(folder/'Includes_XCMate48_REVIEW.xml').read_text()
        self.assertNotIn('widget_recent_vod',text);self.assertNotIn('widget_recent_series',text)
        self.assertNotIn('limit="12"',text);self.assertNotIn('RunPlugin(',text);self.assertIn('$PARAM[existing_live_url]',text)
