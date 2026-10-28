import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from triage import decision_for, interests_digest, load_policy
from validate_report import validate


class TriageTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(key="2610.12345v1", interest_score=1, research_score=1,
                   abstract_available=True, confidence="high", core_match=False,
                   method_transfer=False, user_requested_read=False, decision="skip",
                   source_url="https://arxiv.org/abs/2610.12345v1",
                   reason="Specialized stellar-population fit with no identified method transfer.")
        row.update(changes)
        return row

    def fixtures(self):
        row = self.row()
        status = dict(schema_version=2, report_date="2026-10-29", announcement_date="2026-10-29",
                      source_status="verified_rss", all_target_keys=[row["key"]], body_reviewed_keys=[],
                      abstract_only_keys=[], pending_keys=[], skipped_low_relevance_keys=[row["key"]],
                      blockers=[], updated_at="2026-10-29T13:50:00+08:00", report_status="complete")
        triage = dict(report_date=status["report_date"], announcement_date=status["announcement_date"],
                      policy_version=load_policy()["policy_version"], interests_sha256=interests_digest(), items=[row])
        return status, triage

    def test_both_scores_must_be_low(self):
        self.assertEqual(decision_for(self.row(interest_score=2, research_score=2)), "skip")
        self.assertEqual(decision_for(self.row(interest_score=3)), "read")
        self.assertEqual(decision_for(self.row(research_score=3)), "read")

    def test_interest_or_research_alone_protects(self):
        self.assertEqual(decision_for(self.row(interest_score=4)), "priority")
        self.assertEqual(decision_for(self.row(research_score=4)), "priority")

    def test_uncertainty_missing_metadata_and_method_transfer_protect(self):
        for changes in [dict(confidence="medium"), dict(confidence="low"), dict(method_transfer=True),
                        dict(key="2610.12345@unresolved"),
                        dict(abstract_available=False, interest_score=None, research_score=None)]:
            with self.subTest(changes=changes):
                self.assertEqual(decision_for(self.row(**changes)), "read")
        with self.assertRaisesRegex(ValueError, "Missing abstracts"):
            decision_for(self.row(abstract_available=False))

    def test_core_and_user_request_protect(self):
        self.assertEqual(decision_for(self.row(core_match=True)), "priority")
        self.assertEqual(decision_for(self.row(user_requested_read=True)), "priority")

    def test_skipped_is_not_body_reviewed_or_no_updates(self):
        status, triage = self.fixtures()
        result = validate(status, "2026-10-29", triage)
        self.assertEqual(result["body_reviewed"], 0)
        self.assertEqual(result["requires_body_reading"], 0)
        self.assertEqual(result["skipped_low_relevance"], 1)
        status["report_status"] = "no_updates"
        with self.assertRaisesRegex(ValueError, "No updates"):
            validate(status, triage=triage)

    def test_unsupported_skip_cannot_hide_unread_paper(self):
        status, triage = self.fixtures()
        with self.assertRaisesRegex(ValueError, "triage evidence"):
            validate(status)
        for changes in [dict(interest_score=4), dict(method_transfer=True), dict(confidence="low")]:
            altered = copy.deepcopy(triage)
            altered["items"][0].update(changes)
            with self.assertRaisesRegex(ValueError, "inconsistent"):
                validate(status, triage=altered)

    def test_complete_requires_all_retained_papers_read(self):
        status, triage = self.fixtures()
        triage["items"][0].update(interest_score=4, decision="priority")
        status["pending_keys"] = status.pop("skipped_low_relevance_keys")
        status["skipped_low_relevance_keys"] = []
        with self.assertRaisesRegex(ValueError, "Cannot claim complete"):
            validate(status, triage=triage)
        status["report_status"] = "partial"
        self.assertEqual(validate(status, triage=triage)["pending"], 1)

    def test_stale_interest_profile_and_date_rejected_for_mail(self):
        status, triage = self.fixtures()
        triage["interests_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Interest profile changed"):
            validate(status, "2026-10-29", triage)
        triage["interests_sha256"] = interests_digest()
        triage["announcement_date"] = "2026-10-28"
        with self.assertRaisesRegex(ValueError, "Triage date"):
            validate(status, triage=triage)

    def test_skipped_set_and_coverage_are_exact(self):
        status, triage = self.fixtures()
        status["body_reviewed_keys"] = status["skipped_low_relevance_keys"][:]
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate(status, triage=triage)
        status["body_reviewed_keys"] = []
        triage["items"] *= 2
        with self.assertRaisesRegex(ValueError, "exactly once"):
            validate(status, triage=triage)


if __name__ == "__main__":
    unittest.main()
