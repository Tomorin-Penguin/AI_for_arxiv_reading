#!/usr/bin/env python3
"""Validate abstract-based triage; this is a routing guard, not a keyword classifier."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def load_policy():
    return json.loads((ROOT / "config/triage.json").read_text())


def interests_digest():
    return hashlib.sha256((ROOT / "config/interests.md").read_bytes()).hexdigest()


def decision_for(item, policy=None):
    policy = policy or load_policy()
    for name in ("abstract_available", "core_match", "method_transfer", "user_requested_read"):
        if type(item.get(name)) is not bool:
            raise ValueError("Triage requires a boolean " + name)
    if item.get("confidence") not in {"high", "medium", "low"}:
        raise ValueError("Unknown triage confidence")
    if not item["abstract_available"]:
        if item.get("interest_score") is not None or item.get("research_score") is not None:
            raise ValueError("Missing abstracts require unknown scores, not low scores")
        return "read"
    for name in ("interest_score", "research_score"):
        value = item.get(name)
        if type(value) is not int or not 0 <= value <= 5:
            raise ValueError("Triage scores must be integers from 0 to 5")
    if (item["user_requested_read"] or item["core_match"]
            or item["interest_score"] >= policy["priority_min_interest"]
            or item["research_score"] >= policy["priority_min_research"]):
        return "priority"
    if (policy["enabled"] and item["interest_score"] <= policy["skip_max_interest"]
            and item["research_score"] <= policy["skip_max_research"]
            and item["confidence"] == policy["skip_confidence"]
            and not item["method_transfer"] and "@unresolved" not in item.get("key", "")):
        return "skip"
    return "read"


def validate_triage(data, target_keys, report_date, require_current_interests=False):
    policy = load_policy()
    if data.get("report_date") != report_date or data.get("announcement_date") != report_date:
        raise ValueError("Triage date does not match report date")
    if data.get("policy_version") != policy["policy_version"]:
        raise ValueError("Triage policy version is stale or missing")
    digest = data.get("interests_sha256", "")
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Triage requires an interest-profile hash")
    if require_current_interests and digest != interests_digest():
        raise ValueError("Interest profile changed: review triage before mailing")
    rows = data.get("items", [])
    keys = [row.get("key") for row in rows]
    if len(keys) != len(set(keys)) or set(keys) != set(target_keys):
        raise ValueError("Triage coverage must match every target exactly once")
    skipped = set()
    for row in rows:
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError("Triage requires a concrete reason")
        source = urlparse(row.get("source_url", ""))
        if source.scheme != "https" or source.hostname != "arxiv.org" or not source.path.startswith("/abs/"):
            raise ValueError("Triage requires an official arXiv abstract URL")
        expected = decision_for(row, policy)
        if row.get("decision") != expected:
            raise ValueError("Unsafe or inconsistent triage decision for " + row["key"])
        if expected == "skip":
            skipped.add(row["key"])
    return skipped
