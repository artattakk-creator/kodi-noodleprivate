"""Exact Kodi21 dimensions, stable own-live samples, existing infobar only."""
import importlib,sys,unittest
from unittest import mock
import test_xcmate_stream_osd_02939 as stream_model
import test_xcmate_infobar_reference_02945 as ui_model


class Pixels52(unittest.TestCase):
    def setUp(self):
        self.m=stream_model.StreamOSD39(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.reader=self.m.reader;self.details=self.m.details;self.clock=0;self.width='1920';self.height='1080'
        self.token=('live',dict(nonce='synthetic-one',pid='p',sid='1',at=1))
        for p in (mock.patch.object(self.details,'own',return_value=True),mock.patch.object(self.details.time,'monotonic',side_effect=lambda:self.clock),mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=lambda key:{'Player.Process(VideoWidth)':self.width,'Player.Process(VideoHeight)':self.height,'VideoPlayer.VideoCodec':'h264'}.get(key,''))):
            p.start();self.addCleanup(p.stop)
    def sample(self):
        value=self.reader.read(self.m.player,self.token);self.clock+=2;return value

    def test_720_1080_1440_and_uhd_use_exact_pixel_pairs(self):
        for width,height in [('1280','720'),('1920','1080'),('2560','1440'),('3840','2160')]:
            self.reader=self.details.Details();self.width,self.height=width,height
            self.assertNotIn('width',self.sample());value=self.sample()
            self.assertEqual((value['width'],value['height']),(width,height))

    def test_new_nonce_and_station_change_clear_previous_dimensions_immediately(self):
        self.sample();self.assertEqual(self.sample()['width'],'1920')
        self.token=('live',dict(nonce='synthetic-two',pid='p',sid='2',at=2))
        self.assertNotIn('width',self.sample())
        self.width,self.height='1280','720';self.assertNotIn('width',self.sample())
        self.assertEqual(self.sample()['width'],'1280')

    def test_missing_or_fractional_dimension_never_becomes_a_pixel_badge(self):
        for width,height in [('1920',''),('0','1080'),('nan','1080'),('1920.5','1080'),('40000','2160')]:
            self.reader=self.details.Details();self.width,self.height=width,height
            self.sample();value=self.sample();self.assertNotIn('width',value);self.assertNotIn('height',value)

    def test_missing_label_does_not_keep_last_decoded_pair(self):
        self.sample();self.sample();self.height=''
        self.assertNotIn('width',self.sample());self.assertNotIn('height',self.reader.values)

    def test_media_snapshot_keeps_existing_immediate_behavior(self):
        self.token=self.m.token
        self.assertEqual(self.sample()['width'],'1920')

    def test_no_token_clears_values_without_native_label_queries(self):
        self.sample();self.sample()
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel') as labels:self.assertEqual(self.reader.read(self.m.player,None),{})
        labels.assert_not_called();self.assertIsNone(self.reader.pixel_candidate52)

    def test_existing_two_second_throttle_does_not_gain_extra_reads(self):
        self.sample()
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel') as labels:
            self.clock=1
            for _ in range(50):self.reader.read(self.m.player,self.token)
        labels.assert_not_called()


class PixelFrame52(unittest.TestCase):
    def test_exact_resolution_is_framed_and_unknown_hides_without_touching_audio(self):
        fixture=ui_model.ReferenceInfo45(methodName='runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
        tech=fixture.o._micro44
        tech.render(dict(width='3840',height='2160',audio='aac',channels='2.0'))
        self.assertTrue(tech.resolution_frame52.visible);self.assertEqual(tech.text['video'].label,'3840 × 2160')
        tech.render(dict(audio='aac',channels='2.0'))
        self.assertFalse(tech.resolution_frame52.visible);self.assertEqual(tech.text['audio'].label,'AAC 2.0')
