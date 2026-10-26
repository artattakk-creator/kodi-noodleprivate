"""Clock-driven expiry: admission stays strict, existing textures stay stable."""
import importlib,socket,threading,types,unittest
from unittest import mock
import test_xcmate_dynamic_02937 as dynamic_model

class Flicker38(unittest.TestCase):
    def setUp(self):
        self.fixture=dynamic_model.Dynamic37(methodName='runTest');self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.v=self.fixture.visible;self.row=dict(kind='vod',cover='https://artwork.example.com/38')
        self.now=[0.0];self.release=threading.Event();self.block=False;self.fail=False
        self.addCleanup(self.release.set)
        def resolve(*args,**kw):
            if self.block:self.release.wait(2)
            return [] if self.fail else [(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',443))]
        patch=mock.patch.object(self.v,'time',types.SimpleNamespace(monotonic=lambda:self.now[0]));patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.object(self.v.socket,'getaddrinfo',side_effect=resolve);patch.start();self.addCleanup(patch.stop)
        self.v.dynamic(self.row['cover']);self.fixture.drain()

    def refresh(self):
        self.v.dynamic(self.row['cover']);self.fixture.drain()

    def test_two_expiry_rounds_do_not_change_url_or_revision_on_success(self):
        original=self.v.dynamic(self.row['cover']);revision=self.v.revision()
        for value in (21,42,63,84):
            self.now[0]=value;self.refresh();self.assertEqual(self.v.dynamic(self.row['cover']),original)
        self.assertEqual(self.v.revision(),revision)

    def test_expired_url_not_admitted_to_new_item_but_existing_texture_retained_while_pending(self):
        original=self.fixture.m.art.local_art(self.row)
        self.now[0]=31;self.block=True
        self.assertEqual(self.v.dynamic(self.row['cover']),'')
        proposed=self.fixture.m.art.local_art(self.row)
        self.assertEqual(self.v.retain_displayed(self.row,original,proposed),original)
        self.assertNotEqual(self.v.retain_displayed(self.row,{},proposed)['poster'],original['poster'])
        self.release.set();self.fixture.drain()

    def test_definitive_dns_failure_removes_previous_texture_without_security_bypass(self):
        original=self.fixture.m.art.local_art(self.row);self.now[0]=31;self.fail=True;self.refresh()
        proposed=self.fixture.m.art.local_art(self.row)
        self.assertNotEqual(proposed['poster'],original['poster'])
        self.assertEqual(self.v.retain_displayed(self.row,original,proposed),proposed)

    def test_new_source_cannot_inherit_other_sources_existing_approval(self):
        original=self.fixture.m.art.local_art(self.row);other=dict(self.row,cover='https://artwork.example.com/other38')
        self.now[0]=31;self.block=True;proposed=self.fixture.m.art.local_art(other)
        self.assertNotEqual(self.v.retain_displayed(other,original,proposed)['poster'],original['poster'])
        self.release.set();self.fixture.drain()
