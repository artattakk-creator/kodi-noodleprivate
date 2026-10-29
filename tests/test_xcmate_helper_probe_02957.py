"""Probe privacy/explicit Box B selection; never makes a device connection."""
import contextlib,importlib.util,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]


class Probe57(unittest.TestCase):
    def setUp(self):
        p=mock.patch.object(sys,'path',list(sys.path));p.start();self.addCleanup(p.stop)
        spec=importlib.util.spec_from_file_location('probe_helper57_test',ROOT/'tools/probe_xcmate_helper57.py');self.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.mod)

    def test_explicit_box_b_confirmation_is_required_before_any_request(self):
        with mock.patch.object(self.mod,'Endpoint',side_effect=AssertionError('No authorized endpoint')),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):self.mod.main(['--endpoint','http://test/jsonrpc','--report','unused.json'])

    def test_endpoint_credentials_and_redirect_prone_urls_are_rejected_without_network(self):
        for uri in ('http://user:PRIVATE@test/jsonrpc','file:///private','http://test/jsonrpc?password=PRIVATE','https://test/other'):
            with self.assertRaises(self.mod.Error) as exc:self.mod.Endpoint(uri)
            self.assertNotIn('PRIVATE',str(exc.exception))

    def test_offline_probe_is_blocked_not_a_synthetic_android_pass_and_contains_no_endpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            report=Path(folder)/'report.json'
            with mock.patch.object(self.mod,'Endpoint',side_effect=self.mod.Error('BLOCKED_DEVICE_ACCESS')),contextlib.redirect_stdout(io.StringIO()):
                result=self.mod.main(['--box-b','--endpoint','http://PRIVATE_BOX_B:8080/jsonrpc','--report',str(report)])
            value=json.loads(report.read_text());self.assertEqual(result,2)
            self.assertEqual(value['device_access'],'BLOCKED_DEVICE_ACCESS');self.assertEqual(value['android'],'NOT_TESTED')
            self.assertNotIn('PRIVATE',report.read_text());self.assertEqual(report.stat().st_mode&0o777,0o600)
