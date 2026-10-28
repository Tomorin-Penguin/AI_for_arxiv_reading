import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect_listing import parse_listing
from validate_report import validate


class ReportingTests(unittest.TestCase):
    def status(self):
        return {"report_date": "2026-10-29", "announcement_date": "2026-10-29", "source_status": "verified_rss",
                "all_target_keys": ["2610.12345v1"], "body_reviewed_keys": ["2610.12345v1"],
                "abstract_only_keys": [], "pending_keys": [], "blockers": [],
                "updated_at": "2026-10-29T13:50:00+08:00", "report_status": "complete"}

    def test_no_yesterday_digest(self):
        d = self.status()
        d["announcement_date"] = "2026-10-28"
        with self.assertRaisesRegex(ValueError, "Previous"):
            validate(d, "2026-10-29")

    def test_no_stale_mail(self):
        with self.assertRaisesRegex(ValueError, "today"):
            validate(self.status(), "2026-10-30")

    def test_no_unread_claimed_complete(self):
        d = self.status()
        d["pending_keys"], d["body_reviewed_keys"] = d["body_reviewed_keys"], []
        with self.assertRaisesRegex(ValueError, "Cannot claim"):
            validate(d)

    def test_no_silent_dropped_paper(self):
        d = self.status()
        d["all_target_keys"].append("2610.12346v1")
        with self.assertRaisesRegex(ValueError, "Coverage"):
            validate(d)

    def test_failed_source_is_not_no_updates(self):
        d = self.status()
        d.update(all_target_keys=[], body_reviewed_keys=[], source_status="failed", report_status="no_updates")
        with self.assertRaisesRegex(ValueError, "verified"):
            validate(d)

    def test_listing_without_version_is_unresolved(self):
        p = b'''<a href="/list/gr-qc/recent">recent</a><h3>Showing new listings for Wednesday, 28 October 2026</h3>
        Total of 1 entries<h3>New submissions (showing 1 of 1 entries)</h3><dt><a href="/abs/2610.12345">id</a></dt><dd>
        <div class='list-title mathjax'>Title: Example</div><div class='list-authors'>A</div><p class='mathjax'>Text &amp; $x$</p></dd>'''
        _, rows = parse_listing(p, "gr-qc", "2026-10-28")
        self.assertIsNone(rows[0]["version"])
        self.assertTrue(rows[0]["key"].endswith("@unresolved"))
        with self.assertRaisesRegex(ValueError, "Incomplete pagination"):
            parse_listing(p.replace(b"1 of 1", b"1 of 2"), "gr-qc", "2026-10-28")


if __name__ == "__main__":
    unittest.main()
