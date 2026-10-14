"""A manual XMLTV mapping overrides the native provider guide when both exist."""
import importlib.util
import time
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'


class EPGMappingPrecedence(unittest.TestCase):
    def test_manual_stream_id_wins_over_original_tvg_id(self):
        spec = importlib.util.spec_from_file_location('xm_epg_views_mapping_test',
                                                       LIB / 'epg_views.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        now = int(time.time())
        def programme(name):
            return [{'name': name, 'start_timestamp': now-100,
                     'stop_timestamp': now+200}]
        guide = {'welt.original': programme('Falsches altes EPG'),
                 '1001': programme('WELT – aktuelles externes EPG')}
        info = module.guide_for_channel(guide, 'welt.original', '1001', now)
        self.assertEqual(info['now'], 'WELT – aktuelles externes EPG')

if __name__ == '__main__':
    unittest.main()
