"""Exact XMLTV person references remain separate from names and programme art."""
from io import BytesIO
import unittest
from unittest import mock

from PIL import Image

from xcmate027_fixture import ADDON, Fixture


BASE = 'https://image.tmdb.org/t/p/w500/'


class PersonReferences102(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.options.update(epg_agent_enabled=True, programme_tmdb46=True, tmdb_research43=True)

    def imported_event(self):
        from epg_agent100_art import event_art, validator
        from programme_events46 import describe
        from xmltv_stream import parse

        xml = '''<tv><channel id="one"><display-name>One</display-name></channel>
          <programme channel="one" start="20261125110000 +0000" stop="20261125120000 +0000">
            <title>Show with pictures</title><credits><actor>Cast member</actor></credits>
            <image type="backdrop" orient="L">https://image.tmdb.org/t/p/w500/programme.png</image>
            <image type="poster" orient="P">https://image.tmdb.org/t/p/w500/poster.png</image>
            <image type="person" orient="P">https://image.tmdb.org/t/p/w500/first.png</image>
            <image type="person" orient="P">https://image.tmdb.org/t/p/w500/first.png</image>
            <image type="person" orient="P">https://unapproved.example.com/private.png</image>
            <image type="person" orient="P">https://image.tmdb.org/t/p/w500/second.png</image>
            <image type="person" orient="P">https://image.tmdb.org/t/p/w500/third.png</image>
          </programme></tv>'''
        rows = []
        parse(BytesIO(xml.encode()), lambda *_: None, rows.append, include_images=True)
        return dict(describe(self.portal, {'sid': '1', 'name': 'One'}, {
            'title': rows[0]['name'], 'start': self.now - 10, 'stop': self.now + 3600,
            'cast': ['Cast member']}), agent_art=event_art(rows[0], validator()), _detail93=True)

    @staticmethod
    def preflight(url, **kwargs):
        size = (320, 480) if url.endswith(('first.png', 'second.png', 'poster.png')) else (640, 360)
        output = BytesIO()
        Image.new('RGB', size, 'red' if url.endswith('first.png') else 'blue').save(output, 'PNG')
        return dict(url=url, width=size[0], height=size[1], decoded77=True, _body81=output.getvalue())

    def test_import_retains_second_distinct_safe_person_reference(self):
        person = self.imported_event()['agent_art']['person']

        self.assertEqual(person['url'], BASE + 'first.png')
        self.assertEqual([row['url'] for row in person.get('alternatives', [])], [BASE + 'second.png'])

    def test_each_reference_uses_its_own_decoded_receipt_and_keeps_the_hero(self):
        from programme_requests68 import result
        from programme_urls55 import resolve

        event = self.imported_event()
        hero = dict(event, _art_view499='hero')
        first = dict(event, _art_view499='person1')
        second = dict(event, _art_view499='person2')
        with mock.patch('programme_urls55.probe', side_effect=self.preflight) as probe, \
             mock.patch('programme_match46.candidate', side_effect=AssertionError('unexpected title search')):
            hero_art = resolve(hero, url_mode69=True)
            first_art = resolve(first, allow_lookup=True, url_mode69=True)
            second_art = resolve(second, allow_lookup=True, url_mode69=True)
        self.assertEqual(first_art.get('source_url'), BASE + 'first.png')
        self.assertEqual(second_art.get('source_url'), BASE + 'second.png')
        self.assertEqual([call.args[0] for call in probe.call_args_list],
                         [BASE + 'programme.png', BASE + 'first.png', BASE + 'second.png'])
        self.assertTrue(first_art['decoded88'] and second_art['decoded88'])
        self.assertNotEqual(first_art['image'], second_art['image'])
        self.assertEqual(result(first).get('image'), first_art['image'])
        self.assertEqual(result(second).get('image'), second_art['image'])
        self.assertEqual(result(hero).get('image'), hero_art['image'])

    def test_decoder_refusal_never_passes_remote_url_back_to_the_details(self):
        from programme_requests68 import completed, result
        from programme_urls55 import resolve

        first = dict(self.imported_event(), _art_view499='person1')
        with mock.patch('programme_urls55.probe', side_effect=self.preflight) as probe, \
             mock.patch('decoded_assets88.put', side_effect=OSError('bounded storage unavailable')):
            value = resolve(first, url_mode69=True)
        completed(first, value)
        probe.assert_called_once()
        self.assertFalse(value.get('image'))
        self.assertFalse(result(first).get('image'))

    def test_mislabeled_known_cdn_is_rejected_with_agent_pictures_enabled(self):
        from programme_urls55 import resolve

        event = self.imported_event()
        event['agent_art']['person'] = dict(url=BASE + 'first.png', match='EXACT_EVENT',
                                            source='agent_xmltv', provider='xmltv', attribution='XMLTV')
        with mock.patch('programme_urls55.probe', side_effect=self.preflight) as probe:
            value = resolve(dict(event, _art_view499='person1'), url_mode69=True)
        self.assertFalse(value.get('image'))
        probe.assert_not_called()

    def test_terminal_failure_removes_empty_photo_card(self):
        from programme_requests68 import completed
        from programme_urls55 import resolve
        from programme_window46 import ProgrammeWindow46

        event = self.imported_event()
        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, {'sid': '1', 'name': 'One'})
        window._ready = True
        window.event = event
        self.addCleanup(window.close)
        window._paint_facts(event)
        first = resolve(dict(event, _art_view499='person1'), check=self.preflight)
        completed(dict(event, _art_view499='person2'), dict(code='HTTP_NOT_FOUND', source='placeholder'))

        window.onClick(504)
        window.pump()
        self.assertEqual(window.getControl(150).image, first['image'])
        self.assertFalse(window.getControl(157).visible)

    def test_native_details_show_two_sources_and_no_name_assignment(self):
        from epg_handoff63 import profile_scope
        from programme_window46 import ProgrammeWindow46
        from programme_urls55 import resolve

        event = self.imported_event()
        channel = {'sid': '1', 'name': 'One'}
        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, channel)
        window._ready = True
        window.event = event
        self.addCleanup(window.close)
        window._paint_facts(event)
        with mock.patch('programme_urls55.probe', side_effect=self.preflight):
            first = resolve(dict(event, _art_view499='person1'), url_mode69=True)
            second = resolve(dict(event, _art_view499='person2'), url_mode69=True)
            hero = resolve(dict(event, _art_view499='hero'), url_mode69=True)
            cover = resolve(dict(event, _art_view499='card'), url_mode69=True)

        with mock.patch('programme_urls55.probe', side_effect=AssertionError('network from dialog')):
            window.pump()
            self.assertFalse(any(control.visible for cid, control in window.controls.items() if cid in (150, 154)))
            window.onClick(504)
            window._next = 0
            window.pump()
            self.assertEqual(window.getControl(110).image, hero['image'])
            self.assertEqual(window.getControl(114).image, cover['image'])
            self.assertEqual(window.getControl(140).image, hero['image'])
            for cid, image in ((150, first['image']), (154, second['image'])):
                self.assertTrue(cid in window.controls and window.getControl(cid).visible)
                self.assertEqual(window.getControl(cid).image, image)
                self.assertIn('TMDB', window.getControl(cid + 1).label)
                assignment = window.getControl(cid + 2)
                self.assertEqual(assignment.kind, 'textbox')
                self.assertIn('Nicht zugeordnet', assignment.text)
                height = getattr(assignment, 'height', int(assignment.node.findtext('height')))
                self.assertGreaterEqual(height, 46, 'reserve both caption lines at native size')
                self.assertLessEqual(assignment.y + height, 610, 'caption fits in the picture panel')
                self.assertGreaterEqual(assignment.width, 105, 'fit the complete second caption word')
            self.options.update(programme_tmdb46=False, tmdb_research43=False, programme_tmdb_optout77=True)
            window._next = 0
            window.pump()
            for cid, artwork in ((150, first), (154, second)):
                self.assertTrue(window.getControl(cid).visible)
                self.assertEqual(window.getControl(cid).image, artwork['image'])
            self.properties['XCMate.Agent103.Variant.' + profile_scope()] = 'standard'
            window._next = 0
            window.pump()
            self.assertFalse(window.getControl(150).visible)
            self.assertFalse(window.getControl(154).visible)
