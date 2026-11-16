"""Contract tests for the read-only XCMate agent preflight (synthetic data only)."""
import contextlib
import copy
import io
import json
from pathlib import Path
import unittest

from tools.agent_framework.preflight import evaluate, main


def sample():
    return {
        "schema_version": 1,
        "issue": 470,
        "branch": "agent/xcmate-review-example",
        "commit_sha": "1" * 40,
        "zip_sha256": "2" * 64,
        "tests": {"host": "PASS", "kodi_sim": "PASS"},
        "android": {"status": "NOT_RUN"},
        "approval": {"merge": False, "release": False},
    }


class AgentPreflightContractTests(unittest.TestCase):
    def test_valid_synthetic_candidate_is_review_only_never_release(self):
        self.assertEqual(evaluate(sample())["status"], "REVIEW_ONLY")

    def test_rejects_bad_sha_and_absent_package(self):
        for key, value in (("commit_sha", "abcd"), ("zip_sha256", ""),
                           ("zip_sha256", "g" * 64), ("commit_sha", "A" * 40)):
            with self.subTest(key=key, value=value):
                item = sample()
                item[key] = value
                self.assertEqual(evaluate(item)["status"], "BLOCKED")

    def test_rejects_direct_release_or_merge_claims(self):
        for key in ("merge", "release"):
            item = sample()
            item["approval"][key] = True
            self.assertEqual(evaluate(item)["status"], "BLOCKED")
            item["approval"][key] = "false"
            self.assertEqual(evaluate(item)["status"], "BLOCKED")

    def test_rejects_android_claim_even_with_supplied_evidence(self):
        for status in ("PASS", "FAIL", "pass", "UNKNOWN"):
            item = sample()
            item["android"] = {
                "status": status, "commit_sha": item["commit_sha"],
                "zip_sha256": item["zip_sha256"], "evidence": "claimed",
            }
            self.assertEqual(evaluate(item)["status"], "BLOCKED")

    def test_rejects_missing_or_failed_host_and_kodi_sim_tests(self):
        for key in ("host", "kodi_sim"):
            for value in ("FAIL", "NOT_RUN", None):
                item = sample()
                item["tests"][key] = value
                self.assertEqual(evaluate(item)["status"], "BLOCKED")

    def test_rejects_unsafe_branch_and_invalid_schema(self):
        for branch in ("main", "pilot", "online-test", "release/xcmate-02996",
                       "../secret", "feature", "agent/../main"):
            item = sample()
            item["branch"] = branch
            self.assertEqual(evaluate(item)["status"], "BLOCKED")
        for bad in (None, [], {"schema_version": 1}, {"schema_version": True}):
            self.assertEqual(evaluate(bad)["status"], "BLOCKED")
        item = sample()
        item["issue"] = True  # bool is not an int in this schema
        self.assertEqual(evaluate(item)["status"], "BLOCKED")

    def test_example_cli_is_read_only(self):
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs/agents/examples/review-only.json"
        expected = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(evaluate(expected)["status"], "REVIEW_ONLY")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--manifest", "docs/agents/examples/review-only.json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "REVIEW_ONLY")

    def test_cli_rejects_traversal_and_missing_manifest(self):
        for name in ("../outside.json", "/etc/passwd", "docs/agents/examples/missing.json"):
            with self.subTest(name=name):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(["--manifest", name]), 2)


if __name__ == "__main__":
    unittest.main()
