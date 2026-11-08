import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import api_pilot as pilot


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root / "out"
        self.cfg = pilot.read_json(Path(__file__).resolve().parents[1] / "config/api-pilot.json")
        self.cfg["prices_verified_on"] = date.today().isoformat()
        self.cfg["prices_valid_through"] = date.today().isoformat()
        self.body = "\n".join(["[S1] Introduction", "The physical boundary conditions are fixed.",
                               "[S2] Results", "The conserved charge remains finite."])
        self.card = {k: "中文 and English substantive text" for k in pilot.TEXT_FIELDS}
        self.card.update(interest_score=4, research_score=3, evidence=[
            {"quote": "physical boundary conditions are fixed", "location": "S1",
             "claim_zh": "边界条件固定", "claim_en": "Boundary conditions are fixed"},
            {"quote": "conserved charge remains finite", "location": "S2",
             "claim_zh": "荷有限", "claim_en": "The charge is finite"}])

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self):
        papers = []
        for n in range(10):
            key = "2610." + str(40000 + n) + "v1"
            paper = {"key": key, "title": "Test paper " + str(n), "version_verified": True,
                     "announcements": {"gr-qc" if n % 2 else "hep-th": "new"},
                     "abstract_en": "Official abstract with different words.",
                     "abs_url": "https://arxiv.org/abs/" + key,
                     "body_source": "https://arxiv.org/html/" + key,
                     "body_sha256": hashlib.sha256(self.body.encode()).hexdigest()}
            papers.append(paper)
            path = self.out / "sources" / (key + ".txt")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.body)
        pilot.save_json(self.root / "state/processed.json", {"completed": {}})
        (self.root / "config").mkdir()
        (self.root / "config/interests.md").write_text("Physics interests")
        sample = {"pilot_id": self.cfg["pilot_id"], "announcement_date": "2026-10-28", "papers": papers, "failures": []}
        pilot.save_json(self.out / "sample.json", sample)
        return papers

    def response(self):
        return {"id": "resp_test", "model": self.cfg["model"], "service_tier": "default", "status": "completed",
                "usage": {"input_tokens": 1000, "output_tokens": 2000,
                          "input_tokens_details": {"cached_tokens": 400, "cache_write_tokens": 100},
                          "output_tokens_details": {"reasoning_tokens": 1200}},
                "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(self.card)}]}]}

    def env(self):
        return patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "ARXIV_PILOT_CLAIMED": self.cfg["pilot_id"],
                                       "OPENAI_API_KEY": "offline-test-placeholder"})

    def test_selection_excludes_processed_skip_uncertain_version_and_duplicates(self):
        papers = self.fixture()
        triage = {"items": [{"key": p["key"], "decision": "read"} for p in papers]}
        triage["items"][0]["decision"] = "skip"
        papers[1]["version_verified"] = False
        selected = pilot.choose_papers({"papers": papers + [papers[3]]}, triage, {papers[2]["key"]}, 6, 42)
        keys = [p["key"] for p in selected]
        self.assertEqual(len(set(keys)), 6)
        self.assertFalse(set(keys).intersection({p["key"] for p in papers[:3]}))

    def test_insufficient_unread_papers_does_not_reread(self):
        with self.assertRaises(ValueError):
            pilot.choose_papers({"papers": []}, {"items": []}, {}, 10, 42)

    def test_parallel_budget_reservation_prevents_overspend(self):
        budget = pilot.Budget(self.out / "ledger.json", self.cfg)
        def reserve(n):
            try:
                budget.reserve(str(n), Decimal("0.70"))
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=10) as pool:
            accepted = sum(pool.map(reserve, range(20)))
        self.assertEqual(accepted, 7)
        self.assertEqual(len(pilot.read_json(self.out / "ledger.json")["calls"]), 7)

    def test_existing_ledger_and_duplicate_paper_are_rejected(self):
        ledger = self.out / "ledger.json"
        budget = pilot.Budget(ledger, self.cfg)
        budget.reserve("paper", Decimal("0.1"))
        with self.assertRaises(ValueError):
            budget.reserve("paper", Decimal("0.1"))
        with self.assertRaises(ValueError):
            pilot.Budget(ledger, self.cfg)

    def test_reasoning_and_cache_write_cost_are_included(self):
        cost = pilot.usage_cost(self.response()["usage"], self.cfg)
        self.assertEqual(cost, Decimal("0.02129"))
        self.assertEqual(pilot.reservation(80000, self.cfg), Decimal("0.28"))

    def test_uncertain_charge_keeps_reservation_and_stops_new_work(self):
        budget = pilot.Budget(self.out / "ledger.json", self.cfg)
        budget.reserve("p1", Decimal("0.28"))
        budget.block("p1", TimeoutError())
        self.assertNotIn("actual_usd", budget.data["calls"]["p1"])
        self.assertEqual(budget.data["calls"]["p1"]["reserved_usd"], "0.28")
        with self.assertRaises(ValueError):
            budget.reserve("p2", Decimal("0.28"))

    def test_reject_unverified_price_and_model_changes(self):
        self.cfg["prices_valid_through"] = "2000-01-01"
        with self.assertRaises(ValueError):
            pilot.validate_config(self.cfg, paid=True)
        self.cfg["model"] = "other-model"
        with self.assertRaises(ValueError):
            pilot.validate_config(self.cfg)

    def test_body_evidence_validation(self):
        pilot.validate_card(self.card, self.body, "Different abstract")
        bad = copy.deepcopy(self.card)
        bad["evidence"][0]["quote"] = "Words absent from the body"
        with self.assertRaises(ValueError):
            pilot.validate_card(bad, self.body, "Different abstract")
        with self.assertRaises(ValueError):
            pilot.validate_card(self.card, self.body, self.card["evidence"][0]["quote"])

    def test_math_is_preserved_in_html(self):
        html = "<article><h1>Title</h1><h2>Method</h2><section id='S1'><math alttext='R=2'>lost</math>" + "body " * 700 + "</section><h2>Conclusion</h2></article>"
        text, sections = pilot.extract_html(html.encode())
        self.assertIn("$R=2$", text)
        self.assertIn("[S1]", text)
        self.assertEqual(len(sections), 3)

    def test_exact_version_required_in_abstract(self):
        raw = ("<meta name='citation_arxiv_id' content='2610.40000v1'><blockquote class='abstract'><span class='descriptor'>Abstract:</span>" + "abstract " * 20 + "</blockquote>").encode()
        result = pilot.extract_abstract(raw, "2610.40000v1")
        self.assertNotIn("Abstract:", result["abstract_en"])
        with self.assertRaises(ValueError):
            pilot.extract_abstract(raw, "2610.40000v2")
        with self.assertRaises(ValueError):
            pilot.extract_abstract(raw.replace(b"v1", b"v10"), "2610.40000v1")

    def test_full_offline_pipeline_produces_reports_and_usage(self):
        self.fixture()
        counted, generated = [], []
        def fake(endpoint, request, key):
            if endpoint == "responses/input_tokens":
                counted.append(request)
                return {"input_tokens": 1000}
            generated.append(request)
            return self.response()
        with self.env():
            pilot.run_pilot(self.root, self.cfg, self.out, pilot.CONFIRMATION, post=fake)
        self.assertEqual(len(generated), 10)
        self.assertEqual(len(counted), 10)
        self.assertEqual({r["input"] for r in generated}, {r["input"] for r in counted})
        self.assertTrue(all(r["text"] == counted[0]["text"] and r["instructions"] == counted[0]["instructions"] for r in generated))
        self.assertEqual(len(list((self.out / "cards").glob("*.md"))), 10)
        self.assertIn("2026-10-28", (self.out / "daily-zh.md").read_text())
        self.assertIn("0.21290", (self.out / "selected-bilingual.md").read_text())
        self.assertEqual(pilot.read_json(self.root / "state/processed.json"), {"completed": {}})

    def test_no_api_call_without_cloud_claim(self):
        def fail(*args):
            self.fail("API must not be called")
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            pilot.run_pilot(self.root, self.cfg, self.out, pilot.CONFIRMATION, post=fail)

    def test_timeout_is_not_retried_or_refunded(self):
        self.fixture()
        calls = []
        def fake(endpoint, request, key):
            if endpoint == "responses/input_tokens":
                return {"input_tokens": 1000}
            calls.append(request)
            raise TimeoutError()
        with self.env(), self.assertRaises(ValueError):
            pilot.run_pilot(self.root, self.cfg, self.out, pilot.CONFIRMATION, post=fake)
        self.assertLessEqual(len(calls), 2)
        ledger = pilot.read_json(self.out / "ledger.json")
        self.assertTrue(ledger["blocked"])
        self.assertTrue(all("actual_usd" not in c for c in ledger["calls"].values()))

    def test_input_over_limit_is_not_truncated_or_generated(self):
        self.fixture()
        def fake(endpoint, request, key):
            self.assertEqual(endpoint, "responses/input_tokens")
            return {"input_tokens": 80001}
        with self.env(), self.assertRaises(ValueError):
            pilot.run_pilot(self.root, self.cfg, self.out, pilot.CONFIRMATION, post=fake)

    def test_newly_completed_paper_stops_all_paid_calls(self):
        papers = self.fixture()
        pilot.save_json(self.root / "state/processed.json", {"completed": {papers[0]["key"]: {}}})
        with self.env(), self.assertRaises(ValueError):
            pilot.run_pilot(self.root, self.cfg, self.out, pilot.CONFIRMATION, post=lambda *args: self.fail("No paid call"))


if __name__ == "__main__":
    unittest.main()
