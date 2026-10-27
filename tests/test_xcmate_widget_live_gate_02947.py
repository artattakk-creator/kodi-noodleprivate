"""Background-only incremental publication, including in-flight art completion."""
import importlib,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class LiveGate47(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.gate=importlib.import_module('widget_live47');self.gate._published.clear()
        self.rows=[dict(sid='1',name='Station',kind='live',category_id='a')]
        self.frame=dict(items=[dict(props={'XtreamMate.Stop':'610'})])

    def test_unchanged_live_rows_do_not_rebuild_before_next_real_boundary(self):
        with mock.patch('widget_refresh45.publish',return_value=True) as publish,mock.patch('widget_refresh45.read',return_value=self.frame),mock.patch.object(self.gate.time,'time',return_value=600):
            self.assertTrue(self.gate.publish(self.portal,'live',self.rows))
            self.assertFalse(self.gate.publish(self.portal,'live',self.rows))
        self.assertEqual(publish.call_count,1)

    def test_next_event_boundary_invalidates_inside_the_same_progress_minute(self):
        with mock.patch('widget_refresh45.publish',return_value=True) as publish,mock.patch('widget_refresh45.read',return_value=self.frame):
            with mock.patch.object(self.gate.time,'time',return_value=600):self.gate.publish(self.portal,'live',self.rows)
            with mock.patch.object(self.gate.time,'time',return_value=609):self.assertFalse(self.gate.publish(self.portal,'live',self.rows))
            with mock.patch.object(self.gate.time,'time',return_value=611):self.assertTrue(self.gate.publish(self.portal,'live',self.rows))
        self.assertEqual(publish.call_count,2)

    def test_art_completion_during_publication_is_not_swallowed_by_post_stamp(self):
        art=importlib.import_module('programme_art46')
        def publish(*a,**kw):art._visual_revision47+=1;return True
        with mock.patch('widget_refresh45.publish',side_effect=publish) as called,mock.patch('widget_refresh45.read',return_value=self.frame),mock.patch.object(self.gate.time,'time',return_value=600):
            self.gate.publish(self.portal,'live',self.rows)
            self.assertTrue(self.gate.publish(self.portal,'live',self.rows))
        self.assertEqual(called.call_count,2)

    def test_series_successful_publication_is_never_gated(self):
        with mock.patch('widget_refresh45.publish',return_value=True) as publish:
            self.gate.publish(self.portal,'series',self.rows)
            self.gate.publish(self.portal,'series',self.rows)
        self.assertEqual(publish.call_count,2)

    def test_real_start_group_or_logo_change_invalidates_existing_live_frame(self):
        with mock.patch('widget_refresh45.publish',return_value=True) as publish,mock.patch('widget_refresh45.read',return_value=self.frame),mock.patch.object(self.gate.time,'time',return_value=600):
            self.gate.publish(self.portal,'live',self.rows)
            self.assertTrue(self.gate.publish(self.portal,'live',[dict(self.rows[0],stream_icon='https://example.test/new.png')]))
        self.assertEqual(publish.call_count,2)
