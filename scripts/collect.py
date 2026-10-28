#!/usr/bin/env python3
"""Validate official RSS snapshots and build a resumable, deduplicated queue.

Fetch the two feeds externally, then run with --feed-dir and --date. Network
failures, stale feeds, and genuine empty feeds must not be conflated.
"""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

NS = {"a": "http://arxiv.org/schemas/atom", "dc": "http://purl.org/dc/elements/1.1/"}
CATEGORIES = ("gr-qc", "hep-th")
KINDS = {"new", "cross", "replace", "replace-cross"}
IDENTIFIER = re.compile(r"(?:arXiv:|arXiv.org:)([a-z-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})v(\d+)")


def parse_feed(raw, category, expected_date):
    root = ET.fromstring(raw)
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise ValueError("Expected an RSS channel, not an error or login page")
    title = channel.findtext("title", "")
    if not title.startswith(category + " updates on arXiv.org"):
        raise ValueError("Unexpected category: " + title)
    published = channel.findtext("pubDate", "")
    feed_date = parsedate_to_datetime(published).date().isoformat()
    if feed_date != expected_date:
        raise ValueError("Stale/mismatched feed: expected %s, got %s" % (expected_date, feed_date))
    entries = []
    for item in channel.findall("item"):
        description = item.findtext("description", "")
        match = IDENTIFIER.search(description) or IDENTIFIER.search(item.findtext("guid", ""))
        if not match or "Abstract:" not in description:
            raise ValueError("Missing versioned identifier or abstract")
        identifier, version = match.group(1), int(match.group(2))
        kind = item.findtext("a:announce_type", "", NS).strip()
        if kind not in KINDS:
            raise ValueError("Unknown announcement type: " + kind)
        abstract = description.split("Abstract:", 1)[1].strip()
        if not abstract:
            raise ValueError("Empty abstract: " + identifier)
        entries.append({
            "id": identifier, "version": version, "key": identifier + "v" + str(version),
            "title": item.findtext("title", "").strip(),
            "authors": item.findtext("dc:creator", "", NS).strip(),
            "abstract_en": abstract,
            "categories": [x.text for x in item.findall("category") if x.text],
            "license": item.findtext("dc:rights", "", NS),
            "abs_url": "https://arxiv.org/abs/" + identifier + "v" + str(version),
            "html_url": "https://arxiv.org/html/" + identifier + "v" + str(version),
            "pdf_url": "https://arxiv.org/pdf/" + identifier + "v" + str(version),
            "announcement_date": feed_date,
            "announcements": {category: kind},
        })
    return {
        "category": category, "url": "https://rss.arxiv.org/rss/" + category,
        "pub_date": published, "last_build_date": channel.findtext("lastBuildDate"),
        "sha256": hashlib.sha256(raw).hexdigest(), "count": len(entries),
    }, entries


def build_manifest(snapshots, expected_date, completed=None):
    completed = completed or {}
    sources, unique = [], {}
    if set(snapshots) != set(CATEGORIES):
        raise ValueError("Both gr-qc and hep-th feeds are required")
    for category in CATEGORIES:
        source, entries = parse_feed(snapshots[category], category, expected_date)
        sources.append(source)
        for entry in entries:
            key = entry["key"]
            if key in unique:
                old = unique[key]
                if old["abstract_en"] != entry["abstract_en"] or old["title"] != entry["title"]:
                    raise ValueError("Conflicting metadata for " + key)
                old["announcements"].update(entry["announcements"])
                old["categories"] = sorted(set(old["categories"] + entry["categories"]))
            else:
                unique[key] = entry
    entries = sorted(unique.values(), key=lambda x: x["key"])
    for e in entries:
        e["queue"] = "new_or_cross" if any(t in ("new", "cross") for t in e["announcements"].values()) else "revision"
        e["previous_review"] = completed.get(e["key"])
        e["needs_review"] = e["queue"] == "new_or_cross" and not e["previous_review"]
    return {
        "schema_version": 1, "announcement_date": expected_date,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_status": "verified_rss", "sources": sources,
        "counts": {"raw_items": sum(s["count"] for s in sources), "unique_versions": len(entries),
                   "new_or_cross": sum(e["queue"] == "new_or_cross" for e in entries),
                   "revisions": sum(e["queue"] == "revision" for e in entries),
                   "pending_new_or_cross": sum(e["needs_review"] for e in entries)},
        "papers": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed-dir", type=Path, required=True)
    parser.add_argument("--date", required=True, help="RSS announcement date YYYY-MM-DD")
    parser.add_argument("--state", type=Path, default=Path("state/processed.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    datetime.strptime(args.date, "%Y-%m-%d")
    completed = json.loads(args.state.read_text())["completed"] if args.state.exists() else {}
    data = build_manifest({c: (args.feed_dir / (c + ".xml")).read_bytes() for c in CATEGORIES}, args.date, completed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(args.output)
    print(json.dumps(data["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
