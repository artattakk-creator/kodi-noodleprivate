"""Full provider-index search coverage; widgets are intentionally smaller pages."""
import importlib,unittest
from xcmate027_fixture import Fixture
class Search66(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.select=importlib.import_module('group_selection')
  for pid in ('p','q'):
   for kind in ('vod','series'):self.select.save(pid,['adult-id'],kind=kind,known=['adult-id','disabled'])
 def populate(self,pid='p',kind='vod',count=1205):
  key='series_id' if kind=='series' else 'stream_id'
  rows=[dict({key:str(i)},name='Complete fixture '+str(i),category_id='adult-id',genre='Drama' if i%2==0 else 'Action') for i in range(count)]
  self.index.import_group(pid,kind,'adult-id',rows)
 def test_provider_title_beyond_1000_is_found_independently_of_widget_limits(self):
  for kind in ('vod','series'):
   self.populate(kind=kind);rows,total=self.index.Reader('p').page(kind,query='fixture 1204',category='adult-id')
   self.assertEqual(total,1);self.assertEqual(rows[0]['sid'],'1204')
 def test_genre_search_covers_all_1205_rows_after_bounded_background_derivation(self):
  genre=importlib.import_module('genre_search')
  for kind in ('vod','series'):
   self.populate(kind=kind)
   for _ in range(30):
    if not genre.advance('p',kind):break
   found=[];reader=self.index.Reader('p')
   for offset in range(0,603,100):
    rows,total=reader.page(kind,query='Drama',offset=offset,limit=100)
    self.assertEqual(total,603);found.extend(r['sid'] for r in rows)
   self.assertEqual(set(found),{str(i) for i in range(0,1205,2)});self.assertEqual(len(found),603)
 def test_portal_scope_and_disabled_category_do_not_leak_into_global_title_search(self):
  self.populate('p');self.populate('q',count=1)
  self.index.import_group('p','vod','disabled',[dict(stream_id='hidden',name='Complete fixture 1204',category_id='disabled')])
  self.assertEqual(self.index.Reader('p').page('vod',query='fixture 1204')[1],1)
  self.assertEqual(self.index.Reader('q').page('vod',query='fixture 1204')[1],0)
