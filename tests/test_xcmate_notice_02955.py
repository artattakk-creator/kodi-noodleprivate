"""User-requested installation confirmation includes the installed changes."""
import unittest
import test_xcmate_update_notice_02941 as old


class Notice55(unittest.TestCase):
    def setUp(self):
        self.case=old.UpdateNotice41(methodName='runTest');self.case.setUp();self.addCleanup(self.case.doCleanups)
        self.case.current='0.1.29.55';self.case.options['xcmate_ui_language']='de_de'

    def test_installation_success_version_and_current_changes_are_visible(self):
        self.assertTrue(self.case.notice.detect());self.assertTrue(self.case.notice.show())
        title,text=self.case.dialog.ok.call_args.args
        self.assertEqual(title,'Installation erfolgreich')
        for phrase in ('0.1.29.55','Änderungen:','Widgets','EPG','Live-Navigation','Passwörter','Wizard .54'):self.assertIn(phrase,text)

    def test_upgrade_from_54_acknowledges_once_without_reopening_on_restart(self):
        self.case.baseline('0.1.29.54');self.assertTrue(self.case.notice.detect());self.assertTrue(self.case.notice.show())
        self.case.properties.clear();self.assertFalse(self.case.notice.detect());self.assertFalse(self.case.notice.show())
        self.case.dialog.ok.assert_called_once()
