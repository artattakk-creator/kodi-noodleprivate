"""XMLTV artwork parsing with bounded, source-compatible SAX callbacks."""
import gzip
import io
from pathlib import Path
import sys
import unittest
from unittest import mock


class Chunked(io.BytesIO):
    def read(self,size=-1):
        return super().read(min(size,1) if size>=0 else size)


class XmltvArtwork499(unittest.TestCase):
    def setUp(self):
        lib=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'
        patch=mock.patch.object(sys,'path',[str(lib)]+sys.path)
        patch.start();self.addCleanup(patch.stop)
        import xmltv_stream
        self.xmltv=xmltv_stream

    @staticmethod
    def event(contents):
        return ('<programme channel="one.de" start="20261119201500 +0100" stop="20261119221500 +0100">'
                '<title>Actual programme</title>'+contents+'</programme>')

    def parse(self,contents,stream=io.BytesIO,pack=False,include_channel_images=True,**kwargs):
        raw=('<tv>'+contents+'</tv>').encode()
        if pack:raw=gzip.compress(raw)
        channels=[];events=[];logos=[]
        if include_channel_images:kwargs['channel_image']=lambda *args:logos.append(args)
        counts=self.xmltv.parse(stream(raw),lambda *args:channels.append(args),events.append,**kwargs)
        return channels,events,logos,counts

    def test_chunked_standard_roles_and_multiple_icons_are_bound_to_each_record(self):
        channel=('<channel id="one.de"><display-name>One</display-name>'
                 '<icon src="https://example.invalid/channel.png"/>'
                 '<icon src="https://example.invalid/channel-alt.png" width="100"/>'
                 '</channel><channel id="two.de"><display-name>Two</display-name></channel>')
        body=('<icon src="https://example.invalid/legacy.png"/>'
              '<icon src="https://example.invalid/legacy-landscape.png"/>'
              '<rating system="FSK"><value>12</value></rating>'
              '<review>Reviewed</review>'
              '<image type="poster" orient="P" size="2" system="tmdb">'
              ' https://example.invalid/poster.jpg?w=500&amp;h=700 </image>'
              '<image type="backdrop" orient="L" system="tmdb">https://example.invalid/wide.jpg</image>'
              '<image type="still" orient="L">https://example.invalid/still.jpg</image>'
              '<image type="person">https://example.invalid/person.jpg</image>'
              '<image type="character">https://example.invalid/character.jpg</image>')
        channels,events,logos,counts=self.parse(channel+self.event(body)+self.event(''),Chunked,
                                               include_images=True,include_icons=True,strict_images=True)
        self.assertEqual(channels,[('one.de','One'),('two.de','Two')])
        self.assertEqual(logos,[('one.de','https://example.invalid/channel.png'),
                                ('one.de','https://example.invalid/channel-alt.png')])
        self.assertEqual(events[0]['images'][0],dict(type='poster',orient='P',size='2',system='tmdb',
                         url='https://example.invalid/poster.jpg?w=500&h=700'))
        self.assertEqual([row['type'] for row in events[0]['images']],['poster','backdrop','still','person','character'])
        self.assertEqual(events[0]['images'][-1],dict(type='character',orient='',size='',system='',
                                                     url='https://example.invalid/character.jpg'))
        self.assertEqual(events[0]['icons'],['https://example.invalid/legacy.png','https://example.invalid/legacy-landscape.png'])
        self.assertEqual(events[0]['screenshot_uri'],'https://example.invalid/legacy.png')
        self.assertEqual((events[0]['rating'],events[0]['rating_system']),('12','FSK'))
        self.assertEqual((events[1]['images'],events[1]['icons'],events[1]['screenshot_uri']),([],[],''))
        self.assertEqual(set(counts),{'channels','programmes','skipped','bytes'})
        self.assertEqual(counts['programmes'],2)

    def test_sniffs_gzip_even_with_single_byte_transport_reads(self):
        body=self.event('<image type="poster">https://example.invalid/example.png</image>')
        _,events,_,_=self.parse(body,Chunked,pack=True,include_images=True)
        self.assertEqual(events[0]['images'][0]['type'],'poster')

    def test_legacy_default_preserves_raw_icon_and_no_new_event_fields(self):
        body='<icon src="http://legacy.invalid/old.png"/><icon src="https://example.invalid/fallback.png"/>'
        _,events,_,_=self.parse(self.event(body),include_channel_images=False)
        self.assertEqual(events[0]['screenshot_uri'],'http://legacy.invalid/old.png')
        self.assertNotIn('images',events[0]);self.assertNotIn('icons',events[0])
        _,events,_,_=self.parse(self.event(body*20),include_channel_images=False,include_icons=True)
        self.assertEqual(len(events[0]['icons']),32)
        self.assertEqual(events[0]['icons'][0],'http://legacy.invalid/old.png')

    def test_nonstandard_or_malformed_images_are_ignored_in_a_general_provider_feed(self):
        contents=('<channel id="one.de"><icon src="http://legacy.invalid/channel.png"/>'
                  '<junk><icon src="https://example.invalid/nested-logo.png"/></junk></channel>')
        body=('<rating><icon src="https://example.invalid/nested-event.png"/><value>PG</value></rating>'
              '<image type="episode_still">https://example.invalid/nonstandard.jpg</image>'
              '<image type="poster" orient="bad">https://example.invalid/bad.jpg</image>'
              '<image type="poster" key="unexpected">https://example.invalid/key.jpg</image>'
              '<image type="poster">https://example.invalid/><evil/>nested.jpg</image>'
              '<image type="poster">data:image/png;base64,AA</image>'
              '<image type="poster">https://user:pass@example.invalid/credential.jpg</image>'
              '<image type="poster">https:///missing-host.jpg</image>'
              '<image type="poster">https://example.invalid/valid.jpg</image>')
        _,events,logos,_=self.parse(contents+self.event(body),include_images=True,include_icons=True)
        self.assertEqual([row['url'] for row in events[0]['images']],['https://example.invalid/valid.jpg'])
        self.assertEqual(events[0]['icons'],[])
        self.assertEqual(logos,[])

    def test_strict_rejects_malformed_roles_attributes_nodes_and_basic_urls(self):
        url='https://example.invalid/image.jpg'
        for field in (f'<image type="clearlogo">{url}</image>',f'<image>{url}</image>',
                      f'<image type="still" size="4">{url}</image>',f'<image type="still" orient="l">{url}</image>',
                      f'<image type="still" extra="x">{url}</image>',f'<image type="still"><inner/>{url}</image>',
                      f'<review><image type="still">{url}</image></review>',
                      '<image type="poster"> http://legacy.invalid/bad.png </image>',
                      '<icon src="https://user:pass@example.invalid/icon.png"/>'):
            with self.subTest(field=field),self.assertRaises(self.xmltv.XMLTVSyntaxError):
                self.parse(self.event(field),include_images=True,include_icons=True,strict_images=True)

    def test_strict_rejects_artwork_outside_a_direct_programme_child(self):
        data='<image type="still">https://example.invalid/orphan.jpg</image>'
        with self.assertRaises(self.xmltv.XMLTVSyntaxError):
            self.parse(data,include_images=True,strict_images=True)

    def test_strict_checks_image_order_after_other_programme_fields(self):
        body=('<image type="poster">https://example.invalid/poster.jpg</image>'
              '<review>Late review</review>')
        with self.assertRaises(self.xmltv.XMLTVSyntaxError):
            self.parse(self.event(body),include_images=True,strict_images=True)

    def test_programme_and_channel_artwork_limits_fail_with_typed_limit_error(self):
        from epg_io import XMLTVLimitError
        url='https://example.invalid/image.jpg'
        for contents,kind in ((self.event((f'<image type="still">{url}</image>')*33),'image_nodes'),
                              (self.event((f'<icon src="{url}"/>')*33),'image_nodes'),
                              ('<channel id="one.de">'+(f'<icon src="{url}"/>')*33+'</channel>','image_nodes'),
                              (self.event(f'<image type="still">{url}'+('x'*2048)+'</image>'),'image_url'),
                              (self.event(f'<icon src="{url}'+('x'*2048)+'"/>'),'image_url'),
                              (self.event('<image type="still" system="'+('s'*65)+f'">{url}</image>'),'image_attributes')):
            with self.subTest(kind=kind),self.assertRaises(XMLTVLimitError) as error:
                self.parse(contents,include_images=True,include_icons=True,strict_images=True)
            self.assertEqual(error.exception.kind,kind)

    def test_malformed_xml_dtd_and_corrupt_gzip_are_rejected(self):
        def parse(data):
            return self.xmltv.parse(io.BytesIO(data),lambda *a:None,lambda *a:None,include_images=True)
        with self.assertRaises(self.xmltv.UnsafeXMLTV):
            parse(b'<!DOCTYPE tv [<!ENTITY inject "http://example.invalid">]><tv>&inject;</tv>')
        with self.assertRaises(self.xmltv.XMLTVSyntaxError):
            parse(b'<tv><programme>')
        with self.assertRaises((EOFError,gzip.BadGzipFile)):
            parse(gzip.compress(b'<tv/>')[:-5])


if __name__=='__main__':
    unittest.main()
