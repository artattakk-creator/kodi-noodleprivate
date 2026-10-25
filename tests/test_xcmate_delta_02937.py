"""Real streaming category publication: unrelated old heads must stay intact."""
import importlib
import json
import sys
import types
import unittest
from unittest import mock
import test_xcmate_028_streaming as model


class Delta37(unittest.TestCase):
    def setUp(self):
        self.m=model.IndexTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.delta=importlib.import_module('catalog_delta')
        self.portal=dict(self.m.portal,xc_host='https://fixture.invalid',xc_user='fixture',xc_pass='fixture')
        self.calls=[]
        owner=self
        class Client:
            def get_cached_catalog(self,action):return [dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
            def iter_catalog(self,action,cid,**kw):
                owner.calls.append(cid)
                # An unhelpful provider returns unrelated category A too.
                return iter([dict(stream_id='1',category_id='a',name='A value changed upstream'),dict(stream_id='2',category_id='b',name='B')])
        self.client=Client()
        patch=mock.patch.dict(sys.modules,portals=types.SimpleNamespace(get_by_id=lambda pid:self.portal),xtream=types.SimpleNamespace(XtreamClient=lambda *args:self.client));patch.start();self.addCleanup(patch.stop)
        self.index=self.m.index;self.groups=self.m.groups

    def test_new_category_only_does_not_refresh_expired_existing_group_even_if_provider_ignores_filter(self):
        self.groups.save('p',['a'],'live',known=['a','b'],auto_new=False)
        self.index.import_group('p','live','a',[dict(stream_id='1',category_id='a',name='A original')])
        db=self.index.connect(write=True)
        with db:db.execute("UPDATE heads SET updated=0 WHERE cid='a'")
        before=[tuple(row) for row in db.execute("SELECT * FROM items_v2 WHERE cid='a'")];db.close()
        self.groups.save('p',['a','b'],'live',known=['a','b'],auto_new=False)
        self.delta.request(self.portal,'live','b');self.assertTrue(self.delta.pending('p','live'))
        self.assertTrue(self.delta.run_next())
        self.assertEqual(self.calls,['b'])
        db=self.index.connect();self.assertEqual([tuple(row) for row in db.execute("SELECT * FROM items_v2 WHERE cid='a'")],before);db.close()
        self.assertEqual(self.index.Reader('p').page('live',category='b')[1],1)
        self.assertEqual(self.delta.states('p','live')[0]['code'],'READY')
        self.assertFalse(self.delta.pending('p','live'))

    def test_restart_keeps_pending_group_and_failed_worker_cannot_claim_empty_success(self):
        self.groups.save('p',['b'],'live',known=['a','b'],auto_new=False)
        self.delta.request(self.portal,'live','b')
        module=importlib.reload(self.delta);self.assertTrue(module.pending('p','live'))
        with mock.patch.object(self.index,'sync_kind',return_value=None):module.run_next()
        state=module.states('p','live')[0]
        self.assertEqual(state['code'],'FAILED');self.assertEqual(state['attempts'],1)
