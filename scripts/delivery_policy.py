#!/usr/bin/env python3
"""Choose a delivery action from verified run state; never sends email."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")


def delivery_action(run, now, already_sent=False):
    if now.tzinfo is None:
        raise ValueError("An explicit timezone is required")
    if already_sent:
        return "already_sent"
    local = now.astimezone(SHANGHAI)
    minute = local.hour * 60 + local.minute
    if minute < 14 * 60:
        return "wait_window"
    if minute > 16 * 60 + 30:
        return "missed_window"
    if not run or run.get("report_date") != local.date().isoformat():
        return "send_failure"
    phase = run.get("phase")
    if phase not in {"waiting_source", "reading", "complete", "no_updates", "blocked"}:
        raise ValueError("Unknown run phase")
    for key in ("backlog_authorized", "report_ready"):
        if type(run.get(key, False)) is not bool:
            raise ValueError(key + " must be boolean")
    if phase == "blocked":
        return "send_failure"
    announcement = run.get("announcement_status")
    if announcement not in {"unverified", "confirmed_new", "confirmed_no_updates"}:
        raise ValueError("Unknown announcement status")
    backlog = run.get("backlog_authorized", False)
    if announcement == "confirmed_no_updates" and not backlog:
        return "send_no_updates"
    if announcement == "unverified" and not backlog:
        return "send_failure"
    if not run.get("reading_started_at"):
        return "send_failure"
    if phase == "complete" and run.get("report_ready", False):
        return "send_digest"
    if minute == 16 * 60 + 30:
        return "send_partial"
    return "wait_reading"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_state", type=Path)
    parser.add_argument("--already-sent", action="store_true",
                        help="Set only after checking the receipt and Gmail Sent")
    parser.add_argument("--now", help="ISO time with timezone, for reproducible checks")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(SHANGHAI)
    run = json.loads(args.run_state.read_text()) if args.run_state.exists() else None
    print(json.dumps({"action": delivery_action(run, now, args.already_sent),
                      "checked_at": now.astimezone(SHANGHAI).isoformat()}))


if __name__ == "__main__":
    main()
