"""TVmaze adapter contract: all HTTP is mocked; no box and no private tokens."""
import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / 'src' / 'plugin.video.xtreammate' / 'resources' / 'lib'
sys.path.insert(0, str(LIB))


class FakeSourceError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class TVmaze59(unittest.TestCase):
    def setUp(self):
        sys.modules.pop('tvmaze59', None)
        self.source = importlib.import_module('tvmaze59')
        self.mods = mock.patch.dict(sys.modules, {
            'media_sources43': types.SimpleNamespace(SourceError=FakeSourceError),
            'epg_events': types.SimpleNamespace(title_key=lambda x: str(x or '').casefold().strip()),
            'programme_urls55': types.SimpleNamespace(
                safe=lambda x: isinstance(x, str) and x.startswith('https://static.tvmaze.com/uploads/images/')),
        })
        self.mods.start()
        self.opt = mock.patch.object(self.source, 'enabled', return_value=True)
        self.opt.start()
        self.addCleanup(self.mods.stop)
        self.addCleanup(self.opt.stop)

    @staticmethod
    def show(showid=6446):
        return {'show': {'id': showid, 'name': 'Tatort',
                         'url': 'https://www.tvmaze.com/shows/%d/tatort' % showid,
                         'image': {'original': 'https://static.tvmaze.com/uploads/images/original_untouched/10/100.jpg'}}}

    @staticmethod
    def episode():
        return {'season': 1, 'number': 1, 'name': 'Episode 1',
                'image': {'original': 'https://static.tvmaze.com/uploads/images/original_untouched/10/101.jpg'}}

    def transport(self, path, *, duplicates=False, bad_episode=False):
        def fake(url):
            if '/search/shows?' in url:
                return [self.show()] + ([self.show(6450)] if duplicates else [])
            if '/episodebynumber?' in url:
                return dict(self.episode(), number=2) if bad_episode else self.episode()
            raise AssertionError('Unexpected endpoint ' + url)
        return fake

    def test_exact_episode_and_credit(self):
        found = self.source.candidate(dict(title='Tatort', season=1, episode=1, subtitle='Episode 1'),
                                      transport=self.transport('unused'))
        self.assertEqual(found['match'], 'EXACT_TVMAZE_EPISODE59')
        self.assertEqual(found['source'], 'tvmaze_episode')
        self.assertIn('tvmaze.com/shows/6446', found['attribution'])
        self.assertEqual(found['image_scope57'], 'episode')

    def test_duplicate_series_rejected(self):
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Tatort', season=1, episode=1),
                                  transport=self.transport('unused', duplicates=True))
        self.assertEqual(raised.exception.code, 'TVMAZE_AMBIGUOUS')

    def test_inconsistent_episode_number_rejected(self):
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Tatort', season=1, episode=1),
                                  transport=self.transport('unused', bad_episode=True))
        self.assertEqual(raised.exception.code, 'TVMAZE_EPISODE_UNCERTAIN')

    def test_episode_subtitle_mismatch_rejected(self):
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Tatort', season=1, episode=1, subtitle='Wrong'),
                                  transport=self.transport('unused'))
        self.assertEqual(raised.exception.code, 'TVMAZE_EPISODE_UNCERTAIN')

    def test_general_epg_programme_without_season_is_searched(self):
        found = self.source.candidate(dict(title='Tatort', genre='Fernsehreihe'),
                                      transport=self.transport('unused'))
        self.assertEqual(found['source'], 'tvmaze_programme')
        self.assertEqual(found['match'], 'EXACT_TVMAZE_PROGRAMME59')

    def test_explicit_film_never_matches_a_tv_series(self):
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Tatort', genre='Spielfilm', year='1979'),
                                  transport=self.transport('unused'))
        self.assertEqual(raised.exception.code, 'TVMAZE_MOVIE_UNAVAILABLE')

    def test_tv_movie_if_genuinely_classified_and_year_matches(self):
        def fake(url):
            row = self.show()['show']
            row.update(type='TV Movie', premiered='1979-05-25')
            return [{'show': row}]
        found = self.source.candidate(dict(title='Tatort', genre='Spielfilm', year='1979'), transport=fake)
        self.assertEqual(found['source'], 'tvmaze_programme')

    def test_mismatched_movie_year_is_not_accepted(self):
        def fake(url):
            row = self.show()['show']
            row.update(type='TV Movie', premiered='1980-05-25')
            return [{'show': row}]
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Tatort', genre='Spielfilm', year='1979'), transport=fake)
        self.assertEqual(raised.exception.code, 'TVMAZE_MOVIE_UNAVAILABLE')

    def test_no_matching_movie_never_uses_alien_earth(self):
        def fake(url):
            row = self.show()['show']
            row.update(name='Alien: Earth', type='Scripted')
            return [{'show': row}]
        with self.assertRaises(FakeSourceError) as raised:
            self.source.candidate(dict(title='Alien', genre='Spielfilm', year='1979'), transport=fake)
        self.assertEqual(raised.exception.code, 'TVMAZE_NO_MATCH')

    def test_explicit_opt_in_required(self):
        with mock.patch.object(self.source, 'enabled', return_value=False):
            self.assertIsNone(self.source.candidate(dict(title='Tatort', season=1, episode=1),
                                                     transport=lambda _: self.fail('network while off')))

    def test_no_specific_episode_image_is_only_show_fallback(self):
        def fake(url):
            if '/search/shows?' in url:
                return [self.show()]
            return dict(self.episode(), image=None)
        result = self.source.candidate(dict(title='Tatort', season=1, episode=1), transport=fake)
        self.assertEqual(result['image_scope57'], 'series_fallback')
        self.assertEqual(result['source'], 'tvmaze_series')

    def test_api_transport_rejects_arbitrary_paths(self):
        with self.assertRaises(FakeSourceError) as error:
            self.source._get('http://internal', transport=lambda _: None)
        self.assertEqual(error.exception.code, 'TVMAZE_PATH_BLOCKED')

    def test_existing_experimental_route_and_whitelist(self):
        routes = (LIB / 'app_routes.py').read_text(encoding='utf-8')
        menu = (LIB / 'settings_sections45.py').read_text(encoding='utf-8')
        pin = (LIB / 'experimental45.py').read_text(encoding='utf-8')
        source = (LIB / 'programme_sources57.py').read_text(encoding='utf-8')
        urls = (LIB / 'programme_urls55.py').read_text(encoding='utf-8')
        assert 'tvmaze_experiment59' in routes and 'tvmaze_experiment59' in menu and 'tvmaze_experiment59' in pin
        self.assertIn('EXACT_TVMAZE_EPISODE59', source)
        self.assertIn('EXACT_TVMAZE_PROGRAMME59', source)
        self.assertIn('static.tvmaze.com', urls)
        self.assertIn("source_policy59", urls)


if __name__ == '__main__':
    unittest.main()
