"""Programme details show source-attributed local facts without artwork."""
import unittest
from unittest import mock

from xcmate027_fixture import ADDON, Fixture


class ProgrammeFeedFacts102(Fixture, unittest.TestCase):
    def window(self, **fields):
        from programme_events46 import describe
        from programme_window46 import ProgrammeWindow46

        channel = {'sid': '1', 'name': 'One'}
        event = describe(self.portal, channel, dict(title='Programme', start=self.now - 30,
                                                    stop=self.now + 1800, **fields))
        event.update(fields)
        window = ProgrammeWindow46('XCMateProgramme46.xml', str(ADDON), 'Default', '720p')
        window.configure(self.portal, channel)
        window._ready = True
        window.event = event
        self.addCleanup(window.close)
        return window, event

    def test_tmdb_feed_rating_and_series_id_show_without_artwork(self):
        self.options['programme_tmdb_optout77'] = True
        window, event = self.window(xmltv_tmdb_id='tv/126027', xmltv_tmdb_score=8.1, xmltv_title_lang='de')
        window._paint_facts(event)
        with mock.patch('programme_requests68.result', return_value={'code': 'NO_IMAGE', 'source': 'placeholder'}):
            window.pump()
        self.assertFalse(window.getControl(110).visible)
        self.assertTrue(window.getControl(130).visible)
        self.assertEqual(window.getControl(108).label, '8,1/10 · Serie')
        self.assertIn('Metadaten-Sprache   DE', window.getControl(127).text)
        self.assertIn('TMDB-ID   tv/126027', window.getControl(127).text)
        self.assertIn('TMDB 8,1/10 · Serie', window.getControl(127).text)

    def test_feed_id_can_be_visible_without_an_invented_score(self):
        window, event = self.window(xmltv_tmdb_id='movie/721')
        window._paint_facts(event)
        self.assertIn('TMDB-ID   movie/721', window.getControl(127).text)
        self.assertFalse(window.getControl(108).visible)

    def test_unrecognized_feed_id_cannot_supply_scoped_tmdb_rating(self):
        window, event = self.window(xmltv_tmdb_id='episode/rejected', xmltv_tmdb_score=8.1)
        window._paint_facts(event)
        self.assertNotIn('TMDB-ID', window.getControl(127).text)
        self.assertFalse(window.getControl(108).visible)

    def test_reported_programme_language_takes_precedence_over_title_language(self):
        window, event = self.window(language='Englisch', xmltv_title_lang='de')
        window._paint_facts(event)
        self.assertIn('Englisch', window.getControl(106).label)
        self.assertNotIn('Metadaten-Sprache', window.getControl(127).text)

    def test_technical_channel_uses_the_exact_agent_source_channel(self):
        window, event = self.window(canonical='1', source_key46='agent', field_sources52={
            'xmltv_tmdb_id': {'source': 'external:other', 'channel': 'other.channel'},
            'xmltv_title_lang': {'source': 'agent', 'channel': 's1.Comedy.Central.de'},
        })
        window._paint_facts(event)
        self.assertIn('EPG-Kanal-ID   s1.Comedy.Central.de', window.getControl(127).text)
