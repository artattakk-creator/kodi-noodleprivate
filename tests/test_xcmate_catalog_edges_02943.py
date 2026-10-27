"""Real catalogue edge pages and changes between worker portions."""
import importlib,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Catalogue43(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.pages=importlib.import_module('media_page43')
    def records(self,n):return [dict(stream_id=str(i),series_id=str(i),category_id='edge',name='Title '+str(i),added=self.now-i) for i in range(n)]
    def test_empty_single_partial_and_large_pages_preserve_exact_unique_totals(self):
        for kind in ('vod','series'):
            for n in (0,1,23,24,25,48,49,500,1703):

                if n:self.index.import_group('p',kind,'edge',self.records(n))
                reader=self.index.Reader('p');seen=[]
                for start in range(0,max(1,n),24):
                    page=self.pages.read(reader,kind,'edge',start,24)
                    self.assertEqual(page[1],n);self.assertLessEqual(len(page[0]),24);seen.extend(row['sid'] for row in page[0])
                self.assertEqual(seen,[str(i) for i in range(n)])
    def test_catalogue_generation_changed_before_append_is_rejected(self):
        self.index.import_group('p','vod','edge',self.records(50));r=self.index.Reader('p');token=self.pages.revision(r,'vod')
        self.index.import_group('p','vod','edge',self.records(51))
        with self.assertRaises(self.pages.CatalogueChanged):self.pages.read(r,'vod','edge',24,24,expected=token)
    def test_change_during_page_read_is_rejected_instead_of_mixed_rows(self):
        self.index.import_group('p','vod','edge',self.records(50));r=self.index.Reader('p');page=r.page
        def changed(*a,**kw):
            value=page(*a,**kw);self.index.import_group('p','vod','edge',self.records(51));return value
        with mock.patch.object(r,'page',side_effect=changed):
            with self.assertRaises(self.pages.CatalogueChanged):self.pages.read(r,'vod','edge',0,24)
    def test_shrunken_catalogue_restores_last_real_page_instead_of_empty_group(self):
        self.index.import_group('p','vod','edge',self.records(25));r=self.index.Reader('p')
        page=self.pages.read(r,'vod','edge',240,24);self.assertEqual(page.offset,24);self.assertEqual(page[0][0]['sid'],'24')
    def test_restore_selected_identity_uses_actual_new_position_not_old_offset(self):
        self.index.import_group('p','vod','edge',self.records(60));r=self.index.Reader('p')
        page=self.pages.read(r,'vod','edge',0,24,restore='41');self.assertEqual(page.offset,24)
        self.assertIn('41',[x['sid'] for x in page[0]]);self.assertEqual(page.selected,'41')
    def test_optional_search_metadata_never_invents_quality_language_seasons_or_portal(self):
        from search_results import secondary
        base=secondary(dict(kind='series',name='Show 4K German Season 12'))
        for text in ('4K','German','12'):self.assertNotIn(text,base)
        full=secondary(dict(kind='series',year=2024,genre='Drama',languages=['de','en'],quality='1080P',season_count=3,_portal_name43='Own portal'))
        for text in ('2024','Drama','de, en','1080P','3','Own portal'):self.assertIn(text,full)
        invalid=secondary(dict(kind='series',quality='secret-url',season_count=True,language={'bad':1}))
        self.assertNotIn('secret',invalid);self.assertNotIn('True',invalid)
