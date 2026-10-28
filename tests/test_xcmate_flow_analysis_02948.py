"""The report consumes private files locally and emits only numeric classes."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
class Flow48(unittest.TestCase):
    def setUp(self):
        patch=mock.patch.object(sys,'path',[str(ROOT/'tools')]+sys.path);patch.start();self.addCleanup(patch.stop)
        import analyse_xcmate_flow48
        self.module=analyse_xcmate_flow48
    def test_wizard_discovery_elapsed_and_startup_p50_p95_are_actual_samples(self):
        lines=['[SETUP37] stage=DISCOVER_BEGIN session=aaaaaaaaaaaa mono_ms=1000','[SETUP37] stage=DISCOVER_DONE session=aaaaaaaaaaaa mono_ms=1250','[START48] phase=LOCAL code=READY duration_ms=10','[START48] phase=LOCAL code=READY duration_ms=30']
        result=self.module.analyse(lines);values={r['phase']:r for r in result['phases']}
        self.assertEqual(values['DISCOVERY']['p50_ms'],250);self.assertEqual(values['LOCAL']['p95_ms'],30)
    def test_private_urls_tokens_unknown_codes_and_ids_are_never_output(self):
        secret='SECRET_PROVIDER_USER_PASSWORD';lines=[secret+' https://private.invalid/'+secret,'[START48] phase=LOCAL code='+secret+' duration_ms=9','[PROGRAMME48] stage=IMAGE event=aaaaaaaaaaaa source=XMLTV code='+secret,'[RETURN48] session=aaaaaaaaaaaa phase=home job=complete posted=1 ack=1 '+secret]
        text=json.dumps(self.module.analyse(lines));self.assertNotIn(secret,text);self.assertNotIn('private.invalid',text);self.assertNotIn('aaaaaaaaaaaa',text);self.assertIn('OTHER',text)
    def test_no_log_samples_are_not_fabricated_pass_or_timings(self):
        value=self.module.analyse([]);self.assertEqual(value['phases'],[]);self.assertEqual(value['counts'],[])
