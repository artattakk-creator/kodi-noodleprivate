"""Dynamic Cumination catalogue tests – offline and deterministic."""
import os
import sys
import unittest
import urllib.parse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugin.video.noodleprivate')))
from resources.lib.catalogue import parse_sites, search_link, search_with_keyword


class CatalogueTests(unittest.TestCase):
    def test_filters_invalid_paths_and_deduplicates(self):
        rows = [
            {'file': 'plugin://plugin.video.cumination/?mode=eporner.Main&url=https%3A%2F%2Fexample.net',
             'filetype': 'directory', 'label': '[COLOR hotpink]Eporner[/COLOR]'},
            {'file': 'plugin://plugin.video.cumination/?mode=eporner.Main', 'filetype':'directory', 'label':'Duplicate'},
            {'file': 'plugin://plugin.video.cumination/?mode=beeg.BGMain',
             'filetype': 'directory', 'label':'Beeg'},
            {'file': 'plugin://plugin.video.bad/?mode=bad.Main', 'filetype': 'directory', 'label':'Bad'},
            {'file': 'plugin://plugin.video.cumination/?mode=main.site_list',
             'filetype': 'directory', 'label':'Site list'},
        ]
        sites = parse_sites(rows)
        self.assertEqual(set(sites), {'eporner', 'beeg'})
        self.assertEqual(sites['eporner']['name'], 'Eporner')
    def test_real_search_link_and_keyword_encoding(self):
        directory = [
            {'file': 'plugin://plugin.video.cumination/?mode=xhamster.Main'},
            {'file': 'plugin://plugin.video.cumination/?mode=xhamster.Search&url=https%3A%2F%2Fxhamster.com%2Fsearch%2F'},
        ]
        native = search_link(directory, 'xhamster')
        self.assertIn('xhamster.Search', native)
        result = search_with_keyword(native, 'two & three')
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(result).query)
        self.assertEqual(params['keyword'], ['two & three'])
        self.assertIn('url', params)
    def test_nonsearch_module_returns_empty_route(self):
        self.assertEqual(search_link([{'file':'plugin://plugin.video.cumination/?mode=beeg.BGMain'}], 'beeg'), '')


if __name__ == '__main__': unittest.main()
