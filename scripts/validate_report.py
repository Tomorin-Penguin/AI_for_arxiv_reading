#!/usr/bin/env python3
"""Check disjoint coverage and prevent a previous batch being emailed as today."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from triage import validate_triage


def validate(data, today=None, triage=None):
    required = {"report_date", "announcement_date", "source_status", "all_target_keys", "body_reviewed_keys",
                "abstract_only_keys", "pending_keys", "blockers", "updated_at", "report_status"}
    if required - set(data):
        raise ValueError("Missing fields: " + ", ".join(sorted(required - set(data))))
    if today and data["report_date"] != today:
        raise ValueError("Report is not for today's Beijing date")
    status = data["report_status"]
    if status not in {"complete", "partial", "no_updates", "source_failed"}:
        raise ValueError("Unknown report status")
    keys = ["all_target_keys", "body_reviewed_keys", "abstract_only_keys", "pending_keys"]
    skipped_list = data.get("skipped_low_relevance_keys", [])
    if not isinstance(skipped_list, list) or len(skipped_list) != len(set(skipped_list)):
        raise ValueError("Duplicate or invalid skipped keys")
    for key in keys:
        if len(data[key]) != len(set(data[key])):
            raise ValueError("Duplicate keys in " + key)
    all_keys, body, abstract, pending = [set(data[k]) for k in keys]
    skipped = set(skipped_list)
    states = [body, abstract, pending, skipped]
    if any(a & b for i, a in enumerate(states) for b in states[i + 1:]):
        raise ValueError("Reading states overlap")
    if all_keys != body | abstract | pending | skipped:
        raise ValueError("Coverage is incomplete or contains unlisted papers")
    if all_keys and data["announcement_date"] != data["report_date"]:
        raise ValueError("Previous announcement batch cannot be today's digest")
    if any("@unresolved" in key for key in body | skipped):
        raise ValueError("Completed or skipped papers must have verified versions")
    needs_triage = data.get("schema_version", 1) >= 2 or bool(skipped)
    if needs_triage and "skipped_low_relevance_keys" not in data:
        raise ValueError("Screened reports require a skipped-key list, even when empty")
    if needs_triage and triage is None:
        raise ValueError("Skipped papers require verified triage evidence")
    if triage is not None:
        expected_skipped = validate_triage(triage, all_keys, data["report_date"], bool(today))
        if skipped != expected_skipped:
            raise ValueError("Skipped state does not match triage decisions")
        unavailable = {row["key"] for row in triage["items"] if not row["abstract_available"]}
        if unavailable & (body | abstract | skipped):
            raise ValueError("Missing-abstract triage must be resolved before marking reading complete")
    if status == "complete" and (pending or abstract or data["blockers"] or data["source_status"] not in {"verified_rss", "verified_listing"}):
        raise ValueError("Cannot claim complete with unread papers or incomplete sources")
    if status == "no_updates" and (all_keys or data["source_status"] != "verified_no_updates"):
        raise ValueError("No updates requires verified absence of new papers")
    return {"targets": len(all_keys), "requires_body_reading": len(all_keys - skipped),
            "body_reviewed": len(body), "abstract_only": len(abstract), "pending": len(pending),
            "skipped_low_relevance": len(skipped)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status_file", type=Path)
    parser.add_argument("--for-mail", action="store_true", help="Require today's Beijing report date")
    parser.add_argument("--triage-file", type=Path, help="Default: triage.json next to status.json")
    args = parser.parse_args()
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat() if args.for_mail else None
    path = args.triage_file or args.status_file.with_name("triage.json")
    triage = json.loads(path.read_text()) if path.exists() else None
    print(json.dumps(validate(json.loads(args.status_file.read_text()), today, triage), ensure_ascii=False))


if __name__ == "__main__":
    main()
