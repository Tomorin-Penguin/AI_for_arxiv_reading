import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect import build_manifest, parse_feed


def feed(category, kind="new", version=1, date="28 Oct 2026", empty=False):
    item = "" if empty else f'''<item><title>A test paper</title><link>https://arxiv.org/abs/2610.12345</link>
    <description>arXiv:2610.12345v{version} Announce Type: {kind}\nAbstract: Test &amp; formula $x &lt; 1$.</description>
    <arxiv:announce_type>{kind}</arxiv:announce_type><category>hep-th</category></item>'''
    return f'''<rss xmlns:arxiv="http://arxiv.org/schemas/atom"><channel><title>{category} updates on arXiv.org</title>
    <pubDate>Wed, {date} 00:00:00 -0400</pubDate>{item}</channel></rss>'''.encode()


class CollectorTests(unittest.TestCase):
    def test_cross_list_is_one_paper(self):
        m = build_manifest({"gr-qc": feed("gr-qc", "cross"), "hep-th": feed("hep-th")}, "2026-10-28")
        self.assertEqual(m["counts"]["new_or_cross"], 1)
        self.assertEqual(m["counts"]["raw_items"], 2)
        self.assertEqual(m["papers"][0]["announcements"], {"gr-qc": "cross", "hep-th": "new"})
        self.assertIn("x < 1", m["papers"][0]["abstract_en"])

    def test_old_feed_fails(self):
        with self.assertRaisesRegex(ValueError, "Stale"):
            parse_feed(feed("gr-qc", date="27 Oct 2026"), "gr-qc", "2026-10-28")

    def test_empty_is_valid_but_missing_feed_is_not(self):
        m = build_manifest({c: feed(c, empty=True) for c in ["gr-qc", "hep-th"]}, "2026-10-28")
        self.assertEqual(m["counts"]["unique_versions"], 0)
        with self.assertRaisesRegex(ValueError, "Both"):
            build_manifest({"gr-qc": feed("gr-qc")}, "2026-10-28")

    def test_revision_is_not_new(self):
        m = build_manifest({"gr-qc": feed("gr-qc", "replace", 2), "hep-th": feed("hep-th", "replace-cross", 2)}, "2026-10-28")
        self.assertEqual(m["counts"]["revisions"], 1)
        self.assertEqual(m["counts"]["pending_new_or_cross"], 0)

    def test_only_completed_version_is_deduplicated(self):
        done = {"2610.12345v1": "reports/old/papers/2610.12345v1.md"}
        m = build_manifest({"gr-qc": feed("gr-qc"), "hep-th": feed("hep-th")}, "2026-10-28", done)
        self.assertEqual(m["counts"]["pending_new_or_cross"], 0)
        m = build_manifest({"gr-qc": feed("gr-qc", version=2), "hep-th": feed("hep-th", version=2)}, "2026-10-28", done)
        self.assertEqual(m["counts"]["pending_new_or_cross"], 1)

    def test_html_error_is_not_empty_day(self):
        with self.assertRaises(ValueError):
            parse_feed(b"<html>unavailable</html>", "gr-qc", "2026-10-28")


if __name__ == "__main__":
    unittest.main()
