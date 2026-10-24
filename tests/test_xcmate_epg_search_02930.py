"""Current cached short guide and bounded long-guide search, no provider IO."""
import importlib,json,sqlite3,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class EpgSearch30Tests(Fixture,unittest.TestCase):
    def search(self,query='Upload'):
        return importlib.import_module('search_data').search(self.portal,query,kind='live',now=self.now)['live']

    def test_cached_short_current_programme_found_without_network_or_long_database(self):
        self.details['get_short_epg']={'epg_listings':[dict(title='Upload',start_timestamp=self.now-60,stop_timestamp=self.now+60)]}
        result=self.search();self.assertEqual(result['total'],3);self.assertEqual(result['code'],'READY')
        self.assertTrue(all(row['_now_title']=='Upload' for row in result['rows']))
        self.assertTrue(all(call.kwargs['cached_only'] for call in self.client._get_json.call_args_list))
        self.assertEqual([k for k in self.client._get_json.call_args_list[0].kwargs['extra']],['stream_id','limit'])
        self.assertFalse((self.folder/'guide_v1.sqlite').exists())

    def test_future_long_guide_does_not_mask_current_short_and_expired_short_never_matches(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml':[dict(channel='xml',name='Tomorrow',start_timestamp=self.now+3600,stop_timestamp=self.now+7200)]})
        self.details['get_short_epg']={'epg_listings':[dict(title='Upload',start_timestamp=self.now-60,stop_timestamp=self.now+60)]}
        self.assertEqual(self.search()['total'],3)
        self.details['get_short_epg']['epg_listings'][0]['stop_timestamp']=self.now
        result=self.search();self.assertEqual(result['total'],0);self.assertEqual(result['code'],'NO_CURRENT_EPG')

    def test_manual_mapping_and_xml_current_win_over_short_wrong_programme(self):
        guide=importlib.import_module('guide_store');cfg=importlib.import_module('epg_sources')
        guide.import_cache('p',{'canonical':[dict(channel='canonical',name='Current exact',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        self.details['get_short_epg']={'epg_listings':[dict(title='Upload',start_timestamp=self.now-60,stop_timestamp=self.now+60)]}
        with mock.patch.object(cfg,'configuration',return_value={'mappings':{'1':'canonical','2':'missing','3':'missing'}}):
            result=self.search();self.assertEqual(result['total'],0)
            result=self.search('Current exact');self.assertEqual(result['total'],1);self.assertEqual(result['rows'][0]['sid'],'1')
        self.client._get_json.assert_not_called()

    def test_unrelated_current_programmes_cannot_exhaust_global_result_limit(self):
        guide=importlib.import_module('guide_store');db=guide.connect()
        with db:
            db.executemany('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',
                [('p','unrelated'+str(i),self.now-60,self.now+60,'Other','description'*40,0) for i in range(50002)])
            db.execute('INSERT INTO guide_alias VALUES(?,?,?)',('p','xml','last'))
            db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',('p','last',self.now-60,self.now+60,'Upload','private description',1))
        db.close();result=self.search();self.assertEqual(result['total'],3);self.assertEqual(result['code'],'READY')

    def test_missing_and_broken_database_emit_only_anonymous_diagnostics(self):
        diag=importlib.import_module('live_diagnostics')
        with mock.patch.object(diag,'record') as record:
            result=self.search('PRIVATE QUERY')
        self.assertEqual(result['code'],'NO_EPG')
        text=json.dumps(record.call_args.args)+json.dumps(record.call_args.kwargs)
        for secret in ('PRIVATE','provider.invalid','SECRET','canonical','Channel '):self.assertNotIn(secret,text)
        (self.folder/'guide_v1.sqlite').write_bytes(b'not a database')
        self.assertEqual(self.search()['code'],'EPG_UNAVAILABLE')


if __name__=='__main__':unittest.main()
