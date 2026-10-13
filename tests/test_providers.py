import os, sys, json, unittest, urllib.parse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugin.video.noodleprivate')))
from resources.lib.providers import (ORDER, BridgeError, cumination_uri, enabled_sources,
    source_for_url, validated_cumination_url, kodi_directory)

class ProviderTests(unittest.TestCase):
    def test_all_six_have_distinct_search_routes(self):
        for key in ORDER:
            url = cumination_uri(key, 'Search', 'long test & more')
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            self.assertEqual(query['keyword'], ['long test & more'])
            self.assertEqual(query['mode'], ['{}.Search'.format(key)])
            self.assertEqual(source_for_url(url), key)

    def test_external_plugin_validation(self):
        for bad in ['https://test.invalid','plugin://plugin.video.bad/?mode=eporner.Search',
                    'plugin://plugin.video.cumination/?mode=beeg.Playvid',
                    'plugin://plugin.video.cumination/?mode=eporner']:
            with self.assertRaises(BridgeError): validated_cumination_url(bad)

    def test_provider_settings_are_opt_in_defaults(self):
        self.assertEqual(len(enabled_sources({})), 7)
        self.assertNotIn('eporner', enabled_sources({'provider_enabled':{'eporner':False}}))
        self.assertIn('xnxx', enabled_sources({'provider_enabled':{'eporner':False}}))

    def test_jsonrpc_maps_playable_and_folders(self):
        url = cumination_uri('xhamster')
        payload = [{'file':'plugin://plugin.video.cumination/?mode=xhamster.Playvid&url=ab',
                    'filetype':'file','label':'Sample','thumbnail':'https://img.example/t.jpg','duration':92},
                   {'file':'plugin://plugin.video.cumination/?mode=xhamster.List&url=abc',
                    'filetype':'directory','label':'More results'},
                   {'file':'plugin://plugin.video.cumination/?mode=beeg.Playvid',
                    'filetype':'file','label':'Wrong source'}]
        received=[]
        def execute(request):
            received.append(json.loads(request))
            return json.dumps({'jsonrpc':'2.0','id':72,'result':{'files':payload}})
        result = kodi_directory(execute, url, 'xhamster')
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]['provider'],'xhamster')
        self.assertEqual(result[0]['duration'],92)
        self.assertTrue(result[1]['is_folder'])
        self.assertEqual(received[0]['method'],'Files.GetDirectory')

    def test_api_failure_is_scoped(self):
        with self.assertRaises(BridgeError):
            kodi_directory(lambda _: json.dumps({'error':{'message':'no access'}}), cumination_uri('xnxx'), 'xnxx')

if __name__ == '__main__': unittest.main()
