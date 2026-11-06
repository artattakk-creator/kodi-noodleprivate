"""Verified hidden preparation never fabricates native receiver evidence."""
import importlib,json,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON

class Prepared76(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.s=importlib.import_module('home_schedule75');self.s.configure(self.portals)
        self.w=importlib.import_module('widget_refresh45');self.proof=importlib.import_module('home_prepared76').proof
        self.rows=[dict(sid=str(i),name='Synthetic '+str(i),cover='') for i in range(3)]
        self.worker=importlib.import_module('widget_fast69');self.worker._next=0;self.worker._published.clear()
    def phase(self):return self.s._read(self.s.KEY)
    def live(self):
        state=self.phase();state.update(phase=1,visible=['live']);self.properties[self.s.KEY]=json.dumps(state)
    def publish(self,kind='vod',rows=None,portal=None):
        with mock.patch('programme_assets47.read_many',return_value={}):
            self.assertTrue(self.w.publish(portal or self.portal,kind,self.rows if rows is None else rows))
    def alter(self,change,kind='vod'):
        path=Path(self.w.path('p',kind));frame=json.loads(path.read_text());change(frame);path.write_text(json.dumps(frame))
    def test_hidden_movie_and_series_pages_release_background_without_visible_claim_or_focus_change(self):
        self.live();self.properties[self.s.FOCUS]='unchanged'
        with mock.patch.object(self.s,'applicable',return_value=True),mock.patch('widget_data41.snapshot',return_value=(self.rows,'READY')),mock.patch('widget_assets69.prepare'),mock.patch('programme_assets47.read_many',return_value={}):
            self.assertTrue(self.worker.prepare())
        state=self.phase();self.assertEqual(state['phase'],3);self.assertEqual(state['visible'],['live']);self.assertEqual(state['prepared'],['vod','series'])
        self.assertEqual(self.properties[self.s.FOCUS],'unchanged')
        self.assertEqual(state['ready76']['vod']['p']['fallbacks'],3);self.assertFalse(self.builtins)
    def test_count_or_queued_reference_without_published_page_cannot_release(self):
        self.live();self.assertFalse(self.s.prepared('vod',3));self.assertFalse(self.s.prepared('vod',3,self.portal,self.rows));self.assertEqual(self.phase()['phase'],1)
    def test_complete_preparation_before_live_observation_never_skips_live_priority(self):
        self.publish();self.assertTrue(self.s.prepared('vod',3,self.portal,self.rows));self.assertEqual(self.phase()['phase'],0);self.assertFalse(self.phase()['visible'])
    def test_expired_or_changed_policy_source_identity_and_signature_reject_receipt(self):
        changes=[lambda f:f.update(at=time.time()-601),lambda f:f.update(policy='wrong'),lambda f:f.update(source_refs74={}),lambda f:f.update(signature='wrong'),lambda f:f['items'][0]['props'].update({'XCMate.MediaId':'wrong'})]
        for change in changes:
            with self.subTest(change=change):
                Path(self.w.path('p','vod')).unlink(missing_ok=True);self.publish();self.alter(change);self.assertIsNone(self.proof(self.portal,'vod',self.rows))
    def test_queue_only_or_unapproved_remote_art_is_not_a_prepared_image(self):
        self.publish()
        from home_publication74 import signature
        def change(frame):
            frame['items'][0]['art']['poster']='https://unapproved.invalid/poster.jpg';frame['signature']=signature(frame['items'],'vod')
        self.alter(change)
        with mock.patch('widget_assets69.read',return_value={}):self.assertIsNone(self.proof(self.portal,'vod',self.rows))
    def test_approved_image_is_counted_separately_from_neutral_fallback(self):
        self.publish();url='https://approved.invalid/poster.jpg'
        from home_publication74 import signature
        def change(frame):
            frame['items'][0]['art']['poster']=url;frame['signature']=signature(frame['items'],'vod')
        self.alter(change)
        with mock.patch('widget_assets69.read',return_value={'0':{'poster':url}}):receipt=self.proof(self.portal,'vod',self.rows)
        self.assertEqual((receipt['images'],receipt['fallbacks']),(1,2));self.assertFalse(self.phase()['visible'])
    def test_corrupt_art_value_does_not_crash_preparation_worker(self):
        self.publish()
        from home_publication74 import signature
        def change(frame):
            frame['items'][0]['art']['poster']={'invalid':'value'};frame['signature']=signature(frame['items'],'vod')
        self.alter(change);self.assertIsNone(self.proof(self.portal,'vod',self.rows))
    def test_missing_local_image_does_not_count_as_verified(self):
        self.publish()
        from home_publication74 import signature
        def change(frame):
            frame['items'][0]['art']['poster']=str(self.folder/'missing.png');frame['signature']=signature(frame['items'],'vod')
        self.alter(change);self.assertIsNone(self.proof(self.portal,'vod',self.rows))
    def test_all_enabled_portals_must_be_prepared_before_series(self):
        second=dict(self.portal,id='second');self.portals.append(second);self.s.configure(self.portals);self.live()
        self.publish();self.assertTrue(self.s.prepared('vod',3,self.portal,self.rows));self.assertEqual(self.phase()['phase'],1)
        self.publish(portal=second);self.assertTrue(self.s.prepared('vod',3,second,self.rows));self.assertEqual(self.phase()['phase'],2)
    def test_profile_or_context_change_during_validation_discards_stale_receipt(self):
        self.live();original=self.proof
        def changed(*args):
            value=original(*args);self.portal['start_group_id']='changed';self.s.configure(self.portals);return value
        self.publish()
        with mock.patch('home_prepared76.proof',side_effect=changed):self.assertFalse(self.s.prepared('vod',3,self.portal,self.rows))
        self.assertEqual(self.phase()['phase'],0);self.assertFalse(self.phase()['ready76'])
    def test_same_stamp_missing_frame_is_republished_instead_of_waiting_forever(self):
        self.live()
        with mock.patch.object(self.s,'applicable',return_value=True),mock.patch('widget_data41.snapshot',return_value=(self.rows,'READY')),mock.patch('widget_assets69.prepare'),mock.patch('programme_assets47.read_many',return_value={}):
            self.worker.prepare();Path(self.w.path('p','vod')).unlink();self.worker._next=0;self.worker.prepare()
        self.assertIsNotNone(self.proof(self.portal,'vod',self.rows))
    def observe(self,kind):
        values={'ListItem.Property(XCMate.WidgetKind41)':kind,'ListItem.Property(XCMate.PortalId)':'p','ListItem.Property(XCMate.MediaId)':'0','Control.GetLabel(296752)':'Title','Control.GetLabel(296754)':'Title'}
        image=types.SimpleNamespace(getPosition=lambda:(270,20),getWidth=lambda:1080,getHeight=lambda:580)
        window=types.SimpleNamespace(getFocusId=lambda:2510,getControl=lambda cid:image,setProperty=self.properties.__setitem__,getProperty=lambda k:self.properties.get(k,''))
        with mock.patch.object(self.s,'applicable',return_value=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmcgui.Window',return_value=window),mock.patch('xbmc.getInfoLabel',side_effect=lambda key:values.get(key,'')),mock.patch('xbmc.getCondVisibility',return_value=True):self.s.observe()
    def test_visible_receipt_requires_real_observation_even_after_automatic_phase_three(self):
        self.live()
        for kind in ('vod','series'):self.publish(kind);self.assertTrue(self.s.prepared(kind,3,self.portal,self.rows))
        self.assertEqual(self.phase()['visible'],['live']);self.observe('vod');self.assertEqual(self.phase()['visible'],['live','vod']);self.observe('series');self.assertEqual(self.phase()['visible'],['live','vod','series'])
    def test_disabled_media_phases_skip_only_after_actual_live_observation(self):
        self.portal.update(include_vod=False,include_series=False);self.s.configure(self.portals)
        self.assertEqual(self.phase()['phase'],0);self.observe('live');self.assertEqual(self.phase()['phase'],3);self.assertEqual(self.phase()['visible'],['live'])
    def test_failed_snapshot_does_not_publish_fake_empty_success(self):
        self.live()
        with mock.patch.object(self.s,'applicable',return_value=True),mock.patch('widget_data41.snapshot',return_value=([],'INDEX_MISSING')),mock.patch('widget_live47.publish') as publish:self.worker.prepare()
        publish.assert_not_called();self.assertEqual(self.phase()['phase'],1)
    def test_unconfirmed_empty_catalogue_does_not_release_series(self):
        self.live()
        with mock.patch.object(self.s,'applicable',return_value=True),mock.patch('widget_data41.snapshot',return_value=([],'READY')):self.worker.prepare()
        self.assertEqual(self.phase()['phase'],1)
    def test_confirmed_empty_catalogue_releases_without_fabricated_images(self):
        self.live()
        with mock.patch('home_publication74.source',return_value='verified-empty'):self.publish(rows=[])
        self.assertTrue(self.s.prepared('vod',0,self.portal,[]));self.assertEqual(self.phase()['phase'],2);self.assertEqual(self.phase()['ready76']['vod']['p']['images'],0)
