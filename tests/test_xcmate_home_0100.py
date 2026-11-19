"""Home-only group policy against real SQLite and the native settings entry."""
import unittest
from unittest import mock

from xcmate027_fixture import Fixture


class HomeGroupPolicy(Fixture, unittest.TestCase):
    def seed_groups(self):
        from library_index import replace_catalog
        groups = [
            dict(category_id='films', category_name='Filme'),
            dict(category_id='adult', category_name='DE | 18+'),
            dict(category_id='sport', category_name='Boxen'),
        ]
        replace_catalog('p', 'vod', [], groups)
        return groups

    def movie(self, sid, group, age):
        return dict(stream_id=sid, category_id=group, name=sid, added=self.now-age)

    def widget_ids(self):
        from widget_read56 import read
        rows, code = read(self.portal, 'vod')
        self.assertEqual(code, 'READ_ONLY')
        return [row['sid'] for row in rows]

    def manage(self, commands, selections=()):
        import home_filter92
        self.dialog.select.side_effect = commands
        self.dialog.multiselect = mock.Mock(side_effect=selections or [None])

        def local_read(task, *args, **kwargs):
            return task(lambda: False, lambda **status: None)

        with mock.patch('artwork_ui.job', side_effect=local_read):
            home_filter92.manage(self.portal)

    def test_hidden_memberships_are_checked_before_top_24_in_read_only_snapshot(self):
        from home_filter92 import save
        from library_index import Reader, import_group
        self.seed_groups()
        films = [self.movie(f'safe-{i}', 'films', i+50) for i in range(30)]
        mixed = [self.movie(f'mixed-{i}', 'films', i) for i in range(27)]
        import_group('p', 'vod', 'films', mixed + films)
        import_group('p', 'vod', 'adult', [dict(row, category_id='adult') for row in mixed])
        save('p', ['films'])

        self.assertEqual(self.widget_ids(), [f'safe-{i}' for i in range(24)])
        self.assertEqual(Reader('p').get('vod', 'mixed-0')['name'], 'mixed-0')

        import_group('p', 'vod', 'adult', [self.movie('now-adult', 'adult', 0)])
        self.assertEqual(self.widget_ids()[0], 'mixed-0')

    def test_legacy_hidden_membership_blocks_current_candidate_until_replaced(self):
        from home_filter92 import save
        from library_index import import_group, replace_catalog
        groups = self.seed_groups()
        replace_catalog('p', 'vod', [self.movie('same', 'adult', 1)], groups)
        import_group('p', 'vod', 'films', [self.movie('same', 'films', 1), self.movie('safe', 'films', 2)])
        save('p', ['films'])

        self.assertEqual(self.widget_ids(), ['safe'])
        import_group('p', 'vod', 'adult', [self.movie('other', 'adult', 1)])
        self.assertEqual(self.widget_ids(), ['same', 'safe'])

    def test_confirmed_adult_suggestion_hides_explicit_names_and_keeps_sport(self):
        from home_filter92 import selected
        self.seed_groups()

        self.manage([6, 4])

        self.assertEqual(selected('p'), ['films', 'sport'])

    def test_edit_and_restore_keep_prior_ids_during_partial_provider_refresh(self):
        from home_filter92 import save, selected
        self.seed_groups()
        save('p', ['adult', 'currently-missing'])

        self.manage([1, 3, 0, 4], [[0, 1]])

        self.assertEqual(selected('p'), ['adult', 'currently-missing', 'films'])

    def test_cancel_keeps_existing_policy_when_draft_was_changed(self):
        from home_filter92 import save, selected
        self.seed_groups()
        save('p', ['adult'])

        self.manage([1, 2, -1])

        self.assertEqual(selected('p'), ['adult'])

    def test_none_updates_only_existing_isolated_movies_reload_hook(self):
        from home_filter92 import selected
        self.seed_groups()
        bindings = {'bindings': [
            dict(pid='p', kind='vod', hooks=['XCMate.Widget45.Reload.vod', 'widgetreload']),
            dict(pid='p', kind='series', hooks=['XCMate.Widget45.Reload.series']),
            dict(pid='another', kind='vod', hooks=['XCMate.Widget45.Reload.another']),
        ]}
        with mock.patch('widget_hooks45.read', return_value=bindings):
            self.manage([2, 4])

        self.assertEqual(selected('p'), [])
        self.assertTrue(self.properties['XCMate.Widget45.Reload.vod'])
        self.assertNotIn('widgetreload', self.properties)
        self.assertNotIn('XCMate.Widget45.Reload.series', self.properties)
        self.assertNotIn('XCMate.Widget45.Reload.another', self.properties)

    def test_newly_indexed_hidden_group_retires_last_good_movies_under_same_policy(self):
        from home_filter92 import save
        from library_index import import_group
        from widget_data41 import snapshot
        self.seed_groups()
        save('p', ['films'])
        import_group('p', 'vod', 'films', [self.movie('shared', 'films', 1)])
        self.assertEqual([row['sid'] for row in snapshot(self.portal, 'vod')[0]], ['shared'])
        import_group('p', 'vod', 'adult', [self.movie('shared', 'adult', 1)])

        self.assertEqual(snapshot(self.portal, 'vod', background=True), ([], 'READY'))

    def test_budget_failure_does_not_reuse_the_unfiltered_snapshot(self):
        from home_filter92 import save
        from library_index import IndexReadError, import_group
        from widget_data41 import snapshot
        self.seed_groups()
        import_group('p', 'vod', 'adult', [self.movie('blocked', 'adult', 1)])
        self.assertEqual([row['sid'] for row in snapshot(self.portal, 'vod')[0]], ['blocked'])
        save('p', [])
        failure = IndexReadError('BUDGET')
        failure.code = 'BUDGET'

        with mock.patch('widget_movie47.MovieReader.state', side_effect=failure):
            self.assertEqual(snapshot(self.portal, 'vod'), ([], 'BUDGET'))

    def test_save_rejects_native_setting_when_readable_policy_still_has_the_old_value(self):
        from home_filter92 import KEY, save
        self.seed_groups()

        with mock.patch('settings_guard96.value', return_value=''):
            with self.assertRaises(OSError):
                save('p', ['films'])
        self.assertIn(KEY, self.options)

    def test_read_only_empty_movies_release_preparation_for_following_rows(self):
        import fcntl
        import json
        from pathlib import Path
        from home_filter92 import save
        import home_schedule75
        from library_index import import_group
        from widget_data41 import files
        from widget_fast69 import prepare

        self.portal.update(include_live=False, include_series=False)
        self.seed_groups()
        import_group('p', 'vod', 'films', [self.movie('feature', 'films', 1)])
        save('p', [])
        state = home_schedule75.configure([self.portal])
        state['phase'] = 1
        self.properties[home_schedule75.KEY] = json.dumps(state)
        filename, lock = files('p', 'vod')
        with open(lock, 'a') as lease, mock.patch('widget_fast69._next', 0):
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            prepare()

        updated = home_schedule75._read(home_schedule75.KEY)
        self.assertEqual(updated['ready76']['vod']['p']['count'], 0)
        self.assertEqual(updated['phase'], 3)
        self.assertFalse(Path(filename).exists())
