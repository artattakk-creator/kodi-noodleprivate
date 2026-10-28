"""Final publication retains .52 source proof in the shared programme index."""
import importlib,unittest
import test_xcmate_wizard_epg_02948 as old

class WizardAlias53(unittest.TestCase):
    def setUp(self):
        self.m=old.WizardEPG48(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups);self.d=self.m.d
    def test_final_save_promotes_52_source_alias_proofs_for_later_programme_merge(self):
        self.d.scan()
        from programme_index46 import connect
        db=connect(True,self.d.guide)
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS source_aliases52(pid TEXT,sid TEXT,source_id TEXT,cid TEXT,proof TEXT,PRIMARY KEY(pid,sid,source_id))')
            db.execute('INSERT INTO source_aliases52 VALUES(?,?,?,?,?)',(self.d.pid,'live-1','external:verified','other-id','name'))
        db.close();portal=self.d.save()
        db=connect(False)
        try:
            rows=db.execute('SELECT sid,source_id,cid,proof FROM source_aliases52 WHERE pid=?',(portal['id'],)).fetchall()
            self.assertIn(('live-1','external:verified','other-id','name'),rows);self.assertEqual(len(rows),2)
        finally:db.close()
