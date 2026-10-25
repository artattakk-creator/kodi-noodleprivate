"""Preview foundation only: existing profiles can never trigger automatic setup."""
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib/setup_entry_policy.py'
spec=importlib.util.spec_from_file_location('wizard_preview_policy',SOURCE)
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)


class WizardEntryPreview(unittest.TestCase):
    def test_empty_explicit_root_is_eligible_but_policy_does_not_open_or_write(self):
        self.assertEqual(policy.eligibility('root',7,[]),(True,'ELIGIBLE'))
    def test_existing_active_account_is_preserved(self):
        self.assertEqual(policy.eligibility('root',7,[dict(id='existing',enabled=True)]),(False,'EXISTING_PROFILE'))
    def test_all_disabled_accounts_are_still_existing_profiles(self):
        self.assertEqual(policy.eligibility('root',7,[dict(id='existing',enabled=False)]),(False,'EXISTING_PROFILE'))
    def test_widgets_search_and_service_actions_never_auto_open(self):
        for action in ('widget_live_start_group','global_search','search_continue','play_start','settings'):
            self.assertEqual(policy.eligibility(action,7,[]),(False,'ACTION_CONTEXT'))
    def test_runplugin_cannot_own_first_run_directory(self):
        self.assertEqual(policy.eligibility('root',-1,[]),(False,'NO_DIRECTORY_OWNER'))
    def test_foreign_or_busy_modal_is_not_ignored(self):
        self.assertEqual(policy.eligibility('root',7,[],modal=True),(False,'MODAL_BUSY'))
    def test_stale_portal_hint_requires_explicit_entry(self):
        self.assertEqual(policy.eligibility('root',7,[],portal_hint='stale'),(False,'PORTAL_HINT'))
    def test_missing_profile_snapshot_fails_closed(self):
        self.assertEqual(policy.eligibility('root',7,None),(False,'INVALID_CONTEXT'))
        self.assertEqual(policy.eligibility('root',True,[]),(False,'INVALID_CONTEXT'))
