#!/usr/bin/env python3
"""Check disjoint coverage and prevent a previous batch being emailed as today."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def validate(data, today=None):
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
    for key in keys:
        if len(data[key]) != len(set(data[key])):
            raise ValueError("Duplicate keys in " + key)
    all_keys, body, abstract, pending = [set(data[k]) for k in keys]
    if (body & abstract) or (body & pending) or (abstract & pending):
        raise ValueError("Reading states overlap")
    if all_keys != body | abstract | pending:
        raise ValueError("Coverage is incomplete or contains unlisted papers")
    if all_keys and data["announcement_date"] != data["report_date"]:
        raise ValueError("Previous announcement batch cannot be today's digest")
    if any("@unresolved" in key for key in body):
        raise ValueError("Completed papers must have verified versions")
    if status == "complete" and (pending or abstract or data["blockers"] or data["source_status"] not in {"verified_rss", "verified_listing"}):
        raise ValueError("Cannot claim complete with unread papers or incomplete sources")
    if status == "no_updates" and (all_keys or data["source_status"] != "verified_no_updates"):
        raise ValueError("No updates requires verified absence of new papers")
    return {"targets": len(all_keys), "body_reviewed": len(body), "abstract_only": len(abstract), "pending": len(pending)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status_file", type=Path)
    parser.add_argument("--for-mail", action="store_true", help="Require today's Beijing report date")
    args = parser.parse_args()
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat() if args.for_mail else None
    print(json.dumps(validate(json.loads(args.status_file.read_text()), today), ensure_ascii=False))


if __name__ == "__main__":
    main()
