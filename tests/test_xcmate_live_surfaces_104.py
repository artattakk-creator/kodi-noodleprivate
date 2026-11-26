"""Exact programme receipts and bounded preparation across live surfaces."""
import unittest
from types import SimpleNamespace
from unittest import mock

from xcmate027_fixture import Fixture


class LiveSurfaces104(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.options['epg_agent_enabled'] = True
        self.row = dict(sid='1', name='Station', epg_channel_id='s1.station.de')
        self.event = dict(start=self.now - 60, stop=self.now + 600, title='Current episode',
                          description='Exact text', source=1, source_key46='agent',
                          epg_source46='agent', fact_revision46='facts-a',
                          _agent_generation103='generation-a', _agent_event104='slot-a',
                          agent_art={'backdrop': dict(source='agent_tmdb', provider='tmdb',
                                                      match='EXACT_EVENT',
                                                      url='https://image.tmdb.org/t/p/w1280/current.jpg')})

    def test_ram_handoff_preserves_imported_art_and_exact_generation(self):
        from epg_handoff63 import get, remember
        from epg_views import guide_for_channel

        info = guide_for_channel({'xml': [self.event]}, 'xml', now=self.now)
        info.update(canonical46='s1.station.de', snapshot_revision=('a', 1))
        remember('p', self.row, info)
        with mock.patch('sqlite3.connect', side_effect=AssertionError('GUI SQL')):
            published = get('p', '1', now=self.now)['events'][0]
        self.assertEqual(published.get('_agent_generation103'), 'generation-a')
        self.assertEqual(published.get('_agent_event104'), 'slot-a')
        self.assertEqual(published.get('agent_art'), self.event['agent_art'])

    def test_home_texture_does_not_outlive_agent_generation(self):
        from event_art81 import key
        from hero_render86 import PREFIX, choose, window

        event = dict(self.event, pid='p', sid='1', canonical='s1.station.de', key='schedule')
        updated = dict(event, _agent_generation103='generation-b')
        win = window()
        win.setProperty(PREFIX + 'Event', key(event))
        win.setProperty('XCMate.Hero63.Active', 'A')
        win.setProperty('XCMate.Hero63.A.Image', '/verified/old-generation.jpg')
        win.setProperty('XCMate.Hero63.A.ArtSource', 'agent_tmdb')
        win.setProperty('XCMate.Hero63.A.Rank86', '0')
        with mock.patch('xbmc.getInfoLabel', return_value=''):
            replacement = choose(updated, {}, {}, win)
        self.assertNotEqual(replacement['Image'], '/verified/old-generation.jpg')

    def test_focused_home_bank_uses_the_shared_backdrop_receipt(self):
        import json
        import time
        from epg_handoff63 import get, remember
        from epg_views import guide_for_channel
        from hero_epg63 import poll
        from hero_render86 import PREFIX, tag
        from programme_events46 import visible
        from programme_requests68 import completed, identity

        info = guide_for_channel({'xml': [self.event]}, 'xml', now=self.now)
        info.update(canonical46='s1.station.de', snapshot_revision=('guide', 1))
        remember('p', self.row, info)
        event = visible(self.portal, self.row, get('p', '1'))
        art = dict(key=event['key'], code='READY', source='agent_tmdb', match='EXACT_EVENT',
                   role81='backdrop', image='/verified/backdrop.jpg', scope69=identity(event),
                   image_width77=1280, image_height77=720, until=time.time() + 60)
        completed(event, art)
        self.properties['XCMate.Home86.IdentityReady'] = 'true'
        self.properties[PREFIX + 'Ready'] = json.dumps(dict(key=tag(event, art), at=time.monotonic()))
        labels = {'XCMate.Home50': 'true', 'XCMate.WidgetKind41': 'live', 'XCMate.PortalId': 'p',
                  'XCMate.MediaId': '1', 'XCMate.WidgetToken41': 'e' * 32,
                  'XCMate.NoEpg63': 'Unavailable', 'XCMate.RemainingFormat63': '{0} min'}
        label = lambda value: labels.get(value.removeprefix('ListItem.Property(').removesuffix(')'), '')
        with (mock.patch('xbmc.getSkinDir', return_value='skin.titan.bingie.mod', create=True),
              mock.patch('xbmcgui.getCurrentWindowId', return_value=10000),
              mock.patch('xbmc.getInfoLabel', side_effect=label),
              mock.patch('hero_epg63._next', 0),
              mock.patch('sqlite3.connect', side_effect=AssertionError('GUI SQL'))):
            poll()
        bank = 'XCMate.Hero63.' + self.properties['XCMate.Hero63.Active'] + '.'
        self.assertEqual(self.properties[bank + 'Title'], 'Current episode')
        self.assertEqual(self.properties[bank + 'Image'], '/verified/backdrop.jpg')
        self.assertEqual(self.properties[bank + 'ArtSource'], 'agent_tmdb')

    def test_decoded_lock_is_bound_to_the_agent_generation(self):
        from programme_lock89 import key

        event = dict(self.event, pid='p', sid='1', canonical='s1.station.de', key='schedule')
        self.assertNotEqual(key(event, 'agent_tmdb'),
                            key(dict(event, _agent_generation103='generation-b'), 'agent_tmdb'))

    def test_worker_cannot_publish_a_ready_texture_after_focus_moves(self):
        import json
        from hero_render86 import PREFIX, prepare, window

        event = dict(self.event, pid='p', sid='1', canonical='s1.station.de', key='schedule')
        url = self.event['agent_art']['backdrop']['url']
        artwork = dict(code='READY', source='agent_tmdb', match='EXACT_EVENT', role81='backdrop',
                       image=url, image_width77=1280, image_height77=720)
        focused = True

        def decoded(*args):
            nonlocal focused
            focused = False
            return dict(width=320, height=180)

        reply = json.dumps(dict(result=dict(textures=[dict(url=url)])))
        with (mock.patch('xbmc.executeJSONRPC', create=True, return_value=reply),
              mock.patch('widget_cache82.decoded', side_effect=decoded)):
            prepare(event, artwork, still_current=lambda: focused)
        self.assertFalse(window().getProperty(PREFIX + 'Ready'))

    def test_background_prefetch_only_enqueues_five_current_events(self):
        from programme_prefetch48 import prepare

        rows = [dict(sid=str(i), name='Station ' + str(i)) for i in range(1, 13)]
        replay = dict(self.event, source_key46='provider', epg_source46='provider', source=0)
        future = dict(replay, start=self.now + 600, stop=self.now + 2400, title='Next episode')
        infos = {row['sid']: dict(events=[replay, future], start=replay['start'],
                                 stop=replay['stop'], now=replay['title']) for row in rows}
        with (mock.patch('epg_coverage66.warm'), mock.patch('local_epg.now_next', return_value=infos),
              mock.patch('programme_index46.publish'), mock.patch('epg_snapshot75.checkpoint'),
              mock.patch('home_schedule75.applicable', return_value=False),
              mock.patch('home_schedule75.rest_allowed', return_value=True),
              mock.patch('programme_prefetch48._next', {}),
              mock.patch('programme_urls55.enqueue') as queue):
            self.assertTrue(prepare(self.portal, rows))
        self.assertEqual([(c.args[0]['sid'], c.args[0]['title']) for c in queue.call_args_list],
                         [(str(i), 'Current episode') for i in range(1, 6)])

    def test_overlay_rollover_retains_current_programme_source_and_roles(self):
        from epg_views import guide_for_channel
        from tv_data import GuideSnapshot

        following = dict(self.event, start=self.now + 600, stop=self.now + 1200,
                         title='Following episode', _agent_event104='slot-b')
        info = guide_for_channel({'s1.station.de': [self.event, following]},
                                 's1.station.de', now=self.now)
        info.update(canonical46='s1.station.de', snapshot_revision=('guide', 1))
        state = GuideSnapshot(self.portal, self.client)
        state._values['1'] = info
        with mock.patch('sqlite3.connect', side_effect=AssertionError('GUI SQL')):
            updated = state.get('1', now=self.now + 601)
        self.assertEqual(updated['now'], 'Following episode')
        self.assertEqual(updated['events'][0].get('_canonical'), 's1.station.de')
        self.assertEqual(updated['events'][0].get('_agent_event104'), 'slot-b')
        self.assertEqual(updated['events'][0].get('agent_art'), self.event['agent_art'])

    def test_infobar_draws_the_exact_details_role_and_hides_it_after_rollover(self):
        import time
        from epg_views import guide_for_channel
        from infobar45 import InfoBar
        from programme_events46 import visible
        from programme_requests68 import completed, identity

        def schedule(event):
            value = guide_for_channel({'s1.station.de': [event]}, 's1.station.de', now=self.now)
            value.update(canonical46='s1.station.de', snapshot_revision=('guide', 1))
            return value

        status = {}
        bar = SimpleNamespace(programme_image=object(),
                              write=lambda control, name, value: status.update({name: value}))
        info = schedule(self.event)
        event = dict(visible(self.portal, self.row, info), _detail93=True)
        art = dict(key=event['key'], code='READY', source='agent_tmdb', match='EXACT_EVENT',
                   role81='episode_still', image='/verified/still.jpg', scope69=identity(event),
                   until=time.time() + 60)
        completed(event, art)
        with mock.patch('sqlite3.connect', side_effect=AssertionError('GUI SQL')):
            InfoBar.render_programme(bar, self.portal, self.row, info)
            self.assertEqual(status, {'setImage': '/verified/still.jpg', 'setVisible': True})
            replacement = schedule(dict(self.event, _agent_generation103='generation-b'))
            InfoBar.render_programme(bar, self.portal, self.row, replacement)
            self.assertEqual(status, {'setImage': '', 'setVisible': False})

    def test_native_live_items_share_the_same_schedule_for_text_and_art(self):
        from epg_views import guide_for_channel
        from live_items62 import values

        info = guide_for_channel({'xml': [self.event]}, 'xml', now=self.now)
        info.update(canonical46='s1.station.de', snapshot_revision=('a', 1))
        with mock.patch('widget_group46.infos', return_value={'1': info}) as read:
            item = values(self.portal, [self.row])[0]
        self.assertEqual(item['props']['XCMate.ProgrammeTitle46'], 'Current episode')
        self.assertEqual(read.call_count, 1)
