"""Bounded upstream spinner, real owned row, unchanged native/foreign geometry."""
import base64
import copy
import json
import lzma
import time
import unittest
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50

ROOT = Path(__file__).resolve().parents[1]

class MediaSpinner(Fixture50, unittest.TestCase):
    def graph(self):
        import widget_skin78
        extra = json.loads(lzma.decompress(base64.b64decode((ROOT/'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes())))
        for name, text in extra.items():
            (self.skin/name).write_text(text)
        return widget_skin78.build({name:(self.skin/name).read_bytes() for name in widget_skin78.FILES})

    def test_two_owned_bounded_spinners_use_the_original_native_animation(self):
        import widget_skin78, widget_skin90
        files = self.graph()
        root = widget_skin78.parse(files['xml/IncludesHomeWidgets.xml'])
        header = root.find("include[@name='widget_header_multi']")
        native = header.find(".//control[@type='multiimage']")
        row = root.find("include[@name='XCMate80.MediaRow']")
        spinners = row.findall("control/control[@type='grouplist']/control[@type='multiimage']")
        self.assertEqual(len(spinners), 2)
        for kind, spinner in zip(('vod','series'), spinners):
            for tag in ('imagepath','timeperimage','fadetime','colordiffuse','aspectratio'):
                self.assertEqual(spinner.findtext(tag), native.findtext(tag))
            self.assertIn('XCMate.Home85.'+kind+'.Busy),true)', spinner.findtext('visible'))
            self.assertIn('Container($PARAM[widgetid]).IsUpdating', spinner.findtext('visible'))
            self.assertFalse(spinner.findall('onclick'))
        self.assertEqual(widget_skin90.upgrade(files), files)
        self.assertTrue(widget_skin90.verify(files))

    def test_every_preexisting_owned_field_and_other_skin_file_is_unchanged(self):
        import widget_skin78, widget_skin90, widget_skin80
        import types, sys
        import xml.etree.ElementTree as E
        previous = types.ModuleType('widget_skin90')
        previous.__file__ = widget_skin90.__file__
        delta = json.loads((ROOT/'tests/fixtures/media_spinner_reviewed_delta.json').read_text())
        exec(compile(delta['old'],previous.__file__,'exec'), previous.__dict__)
        with mock.patch.dict(sys.modules, {'widget_skin90':previous}):
            baseline = self.graph()
        files = self.graph()
        root = widget_skin78.parse(files['xml/IncludesHomeWidgets.xml'])
        original = widget_skin90.original_media_row(root.find("include[@name='XCMate80.MediaRow']"), root.find("include[@name='widget_header_multi']"))
        self.assertEqual(widget_skin80.digest(original), widget_skin90.MEDIA_ROW_SHA)
        # Headings remain the stored user label, not a hard-coded replacement.
        self.assertEqual(original.findtext("control/control[@type='label']/label"), '$PARAM[widgetName]')
        self.assertEqual(original.findtext('control/height'), '244')
        self.assertEqual(original.findtext("control/control[@type='group']/top"), '30')
        # Replacing only the verified own row restores the complete old graph;
        # every native/foreign definition, path and remaining file is exact.
        actual_row = root.find("include[@name='XCMate80.MediaRow']")
        root.insert(list(root).index(actual_row), original)
        root.remove(actual_row)
        self.assertEqual(E.tostring(root), E.tostring(widget_skin78.parse(baseline['xml/IncludesHomeWidgets.xml'])))
        for name in files:
            if name!='xml/IncludesHomeWidgets.xml':
                self.assertEqual(files[name], baseline[name], name)
        self.assertEqual(self.prop.read_text(), repr(self.saved).replace('],','],\n'))

    def test_animation_fits_between_title_and_status_above_the_cover(self):
        import widget_skin78
        root = widget_skin78.parse(self.graph()['xml/IncludesHomeWidgets.xml'])
        group = root.find("include[@name='XCMate80.MediaRow']/control")
        heading = group.find("control[@type='grouplist']")
        title = heading.find("control[@type='label']")
        self.assertEqual(title.findtext('width'), 'auto')
        self.assertEqual(heading.findtext('itemgap'), '12')
        self.assertEqual(int(heading.findtext('left'))+int(heading.findtext('width')), 886)
        self.assertLess(886,900)
        for spinner in heading.findall("control[@type='multiimage']"):
            self.assertEqual(int(spinner.findtext('width')),24)
            self.assertLessEqual(int(spinner.findtext('top'))+int(spinner.findtext('height')), 30)

    def test_unreviewed_row_or_spinner_modification_blocks_guarded_upgrade(self):
        import widget_skin78, widget_skin90
        files = self.graph()
        for before,after in ((b'<itemgap>12</itemgap>',b'<itemgap>600</itemgap>'),
                             (b'<height>244</height>',b'<height>800</height>'),
                             (b'<timeperimage>85</timeperimage>',b'<timeperimage>1</timeperimage>')):
            bad = dict(files)
            bad['xml/IncludesHomeWidgets.xml'] = bad['xml/IncludesHomeWidgets.xml'].replace(before,after)
            with self.subTest(change=after), self.assertRaises(ValueError):
                widget_skin90.upgrade(bad)

    def test_real_pending_status_expires_without_inventing_completion(self):
        import home_loading85 as loading
        loading._records.clear()
        with mock.patch.object(loading,'visible',return_value=[]), mock.patch.object(loading.time,'monotonic',return_value=100):
            status = loading.update(self.portal,'vod',[],'WAITING',pending=True)
        self.assertTrue(status['busy'])
        self.assertEqual(status['state'],'LOADING_CATALOG')
        with mock.patch.object(loading,'visible',return_value=[]), mock.patch.object(loading.time,'monotonic',return_value=161):
            expired = loading.update(self.portal,'vod',[],'WAITING',pending=True)
        self.assertFalse(expired['busy'])
        self.assertEqual(expired['state'],'ERROR_RETRYABLE')
        self.assertEqual(self.properties.get('XCMate.Home85.vod.Busy'), '')

    def test_empty_success_and_network_error_cannot_leave_spinner_running(self):
        import home_loading85 as loading
        for code,state in (('READY','EMPTY'),('FAILED','ERROR_RETRYABLE')):
            with self.subTest(code=code):
                status = loading.update(self.portal,'series',[],code,pending=False)
                self.assertEqual(status['state'],state)
                self.assertFalse(status['busy'])

    def test_separate_skin_candidate_matches_all_source_bytes_and_crc(self):
        import hashlib, zipfile
        source = ROOT/'src/plugin.video.xtreammate'
        path = ROOT/'docs/XCMate/test-builds/media-spinner/plugin.video.xtreammate-0.1.29.90.zip'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), Path(str(path)+'.sha256').read_text().split()[0])
        files = [p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and p.name!='.DS_Store']
        with zipfile.ZipFile(path) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()), {'plugin.video.xtreammate/'+p.relative_to(source).as_posix() for p in files})
            for p in files:
                self.assertEqual(z.read('plugin.video.xtreammate/'+p.relative_to(source).as_posix()), p.read_bytes())

    def test_artwork_pending_cannot_leak_between_rows_accounts_or_profiles(self):
        import widget_assets69 as assets
        with mock.patch.object(assets,'_pending',{'queued'}), mock.patch.object(assets,'_pending_scopes',{'queued':('profile-a','p','series')}), mock.patch.object(assets,'profile',return_value='profile-a'), mock.patch.object(assets,'_fatal82',False):
            assets._stop.clear()
            self.assertTrue(assets.pending({'id':'p'},'series'))
            self.assertFalse(assets.pending({'id':'p'},'vod'))
            self.assertFalse(assets.pending({'id':'other'},'series'))
            with mock.patch.object(assets,'profile',return_value='profile-b'):
                self.assertFalse(assets.pending({'id':'p'},'series'))
            with mock.patch.object(assets,'_fatal82',True):
                self.assertFalse(assets.pending({'id':'p'},'series'))
            assets.shutdown()
            self.assertFalse(assets.pending({'id':'p'},'series'))

    def test_catalogue_loading_uses_only_current_profile_and_active_unit_without_io(self):
        import widget_fast69 as fast, catalog_jobs73 as jobs
        job = dict(pid='p',kinds=['vod','series'],state='RUNNING',units=[['vod',{}],['series',{}]],cursor=1)
        with mock.patch('widget_assets69.pending',return_value=False), mock.patch('epg_handoff63.profile_scope',return_value='profile-a'), mock.patch.object(jobs,'_cache',{'jobs':[job]}), mock.patch.object(jobs,'_cache_profile','profile-a'), mock.patch.object(jobs,'jobs',side_effect=AssertionError('NO_JOURNAL_OR_DB_FOR_SPINNER')):
            self.assertFalse(fast.row_pending({'id':'p'},'vod'))
            self.assertTrue(fast.row_pending({'id':'p'},'series'))
            self.assertFalse(fast.row_pending({'id':'other'},'series'))
            with mock.patch('epg_handoff63.profile_scope',return_value='profile-b'):
                self.assertFalse(fast.row_pending({'id':'p'},'series'))
            job['state']='FAILED'
            self.assertFalse(fast.row_pending({'id':'p'},'series'))

    def test_new_scoped_worker_deltas_do_not_normalize_unreviewed_changes(self):
        from clock50_contract437 import without_clock437
        delta = json.loads((ROOT/'tests/fixtures/media_spinner_reviewed_delta.json').read_text())
        for path, change in delta['modules'].items():
            self.assertEqual(without_clock437(change['new'],path),change['old'])
            extra=change['new']+'\nUNREVIEWED = True\n'
            self.assertEqual(without_clock437(extra,path),extra)
