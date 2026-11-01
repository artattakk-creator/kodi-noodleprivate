"""Distinguish evidence-backed incomplete index from disabled, zero and cache."""
import importlib,unittest
from xcmate027_fixture import Fixture
class Status66(Fixture,unittest.TestCase):
 def code(self,**values):
  row=dict(enabled=True,local_count=0,evidence={},job={});row.update(values)
  return importlib.import_module('catalog_status65').acceptance66(row)
 def test_positive_remote_evidence_with_missing_rows_is_index_incomplete(self):
  proof=dict(transport='REMOTE',code='READY',stored=1205)
  self.assertEqual(self.code(local_count=100,evidence=proof),'INDEX_INCOMPLETE')
  self.assertEqual(self.code(local_count=1205,evidence=proof),'READY')
 def test_disabled_zero_filtered_and_local_cache_have_distinct_meanings(self):
  self.assertEqual(self.code(enabled=False),'DISABLED')
  self.assertEqual(self.code(evidence=dict(code='SOURCE_EMPTY',transport='REMOTE')),'SOURCE_EMPTY')
  self.assertEqual(self.code(evidence=dict(code='SOURCE_FILTERED',transport='REMOTE')),'SOURCE_FILTERED')
  self.assertEqual(self.code(evidence=dict(code='CACHED',transport='LOCAL_CACHE',stored=1205)),'CACHED')
 def test_unknown_provider_count_is_not_falsely_zero_or_incomplete(self):
  self.assertEqual(self.code(),'NOT_VERIFIED')
  self.assertEqual(self.code(job=dict(code='PENDING')),'PENDING')
  self.assertEqual(self.code(job=dict(code='FAILED')),'FAILED')
