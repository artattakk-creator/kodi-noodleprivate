"""Anonymized measurements are aggregates, never public private-log excerpts."""
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('flow_analyser47',ROOT/'tools/analyse_xcmate_flow47.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class FlowAnalysis47(unittest.TestCase):
    def test_correlated_live_prepare_and_player_intervals_have_correct_real_counts(self):
        ident='a'*32
        result=module.analyse([
            '[XCMate][FLOW46] id='+ident+' kind=live phase=PLAYBACK_REQUEST ms=100',
            '[XCMate][FLOW46] id='+ident+' kind=live phase=FIRST_VIDEO ms=250',
            '[XCMate][FLOW46] id='+ident+' kind=live phase=GROUPS_READY ms=400',
            '[XCMate][PREPARE47] id='+ident+' code=START_GROUP_MODEL_READY rows=88 ms=150'])
        values={v['phase']:v for v in result['timings']}
        self.assertEqual(values['PLAYBACK_REQUEST_TO_FIRST_VIDEO']['p50_ms'],150)
        self.assertEqual(values['PREPARE_START_GROUP_MODEL_READY']['n'],1)

    def test_private_lines_and_identifiers_are_never_exported(self):
        text='[XCMate][WIDGET47] flow='+'b'*12+' portal='+'c'*12+' kind=vod stage=SELECT code=READY selected=24 https://private.invalid/user/SECRET'
        result=module.analyse([text,'smb://user:SECRET@private/path'])
        exported=json.dumps(result)
        for secret in ('SECRET','private.invalid','smb://','c'*12,'b'*12):self.assertNotIn(secret,exported)
        self.assertEqual(result['widgets'][0]['counts']['selected']['max'],24)

    def test_unknown_log_codes_cannot_export_a_private_token(self):
        text='[XCMate][WIDGET47] flow='+'a'*12+' portal='+'b'*12+' kind=live stage=ASSETS code=PRIVATESECRET selected=0'
        result=module.analyse([text])
        self.assertNotIn('PRIVATESECRET',json.dumps(result))
        self.assertEqual(result['widgets'][0]['code'],'OTHER_CODE')
