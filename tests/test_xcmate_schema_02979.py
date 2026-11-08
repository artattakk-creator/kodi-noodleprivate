"""Missing/broken Kodi views: exact read-only diagnosis, preserved user bytes."""
import importlib,sqlite3,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Schema79(Fixture,unittest.TestCase):
 def test_missing_views_and_stored_version_report_without_mutation(self):
  dbfile=self.folder/'MyVideos131.db'
  with sqlite3.connect(dbfile) as db:db.executescript('CREATE TABLE version(idVersion INTEGER); INSERT INTO version VALUES(131); CREATE TABLE movie(idMovie INTEGER);')
  before=dbfile.read_bytes()
  with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder)):result=importlib.import_module('kodi_schema75').inspect()
  self.assertEqual(result['code'],'KODI_LIBRARY_MISSING_VIEWS');self.assertEqual(result['stored_schema_version'],131);self.assertEqual(result['queries']['movie_view'],'MISSING_VIEW');self.assertEqual(dbfile.read_bytes(),before)
 def test_existing_view_with_missing_backing_table_is_query_failure_not_success(self):
  dbfile=self.folder/'MyVideos131.db'
  with sqlite3.connect(dbfile) as db:db.execute('CREATE VIEW movie_view AS SELECT * FROM absent_table')
  before=dbfile.read_bytes()
  with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder)):result=importlib.import_module('kodi_schema75').inspect()
  self.assertEqual(result['queries']['movie_view'],'QUERY_FAILED');self.assertEqual(dbfile.read_bytes(),before)
 def test_all_views_present_but_broken_are_not_ready(self):
  dbfile=self.folder/'MyVideos131.db'
  with sqlite3.connect(dbfile) as db:
   for view in ('movie_view','tvshow_view','musicvideo_view'):db.execute('CREATE VIEW '+view+' AS SELECT * FROM absent_table')
  before=dbfile.read_bytes()
  with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder)):result=importlib.import_module('kodi_schema75').inspect()
  self.assertEqual(result['code'],'KODI_LIBRARY_QUERY_ERROR');self.assertEqual(dbfile.read_bytes(),before)
 def test_saved_cinema_source_classification_does_not_expose_path_or_rebind(self):
  rows=[['mainmenu','1','widgetPath','videodb://movies/titles/'],['mainmenu','1','widgetPath.1','plugin://foreign.addon/?secret=private-canary'],['mainmenu','1','widgetPath.2','plugin://plugin.video.xtreammate/?action=widget_recent_vod']]
  result=importlib.import_module('widget_consumer58').source_types79(rows)
  self.assertEqual((result['videodb'],result['external_plugin'],result['own']),(1,1,1));self.assertNotIn('private-canary',str(result));self.assertEqual(rows[0][3],'videodb://movies/titles/')
