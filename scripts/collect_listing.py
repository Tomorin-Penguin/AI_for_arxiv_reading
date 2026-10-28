#!/usr/bin/env python3
"""Strict provisional collector for /list/<category>/new when RSS lags.

Download both complete official pages first. Missing versions are deliberately
null and must be resolved from the abstract page or later RSS, never guessed.
"""
import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from collect import CATEGORIES


def plain(markup):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def parse_listing(raw, category, expected_date):
    page = raw.decode("utf-8")
    date_match = re.search(r"Showing new listings for ([^<]+)", page)
    if not date_match:
        raise ValueError("Missing announcement date; do not interpret as an empty feed")
    actual_date = datetime.strptime(date_match.group(1).strip(), "%A, %d %B %Y").date().isoformat()
    if actual_date != expected_date:
        raise ValueError("Stale listing: " + actual_date)
    if not re.search(r"/list/" + re.escape(category) + r"/(?:new|recent)", page):
        raise ValueError("Cannot verify category")
    total_match = re.search(r"Total of\s+(\d+)\s+entries", page)
    if not total_match:
        raise ValueError("Missing total; inspect page manually")
    total = int(total_match.group(1))
    entries = []
    sections = re.split(r"<h3>\s*(New submissions|Cross submissions|Replacement submissions|Cross-lists|Replacements)\s*\(showing (\d+) of (\d+) entries\)</h3>", page)
    for offset in range(1, len(sections), 4):
        name, shown, count, section = sections[offset:offset + 4]
        if shown != count:
            raise ValueError("Incomplete pagination for " + name)
        pairs = re.findall(r"<dt\b[^>]*>(.*?)</dt>\s*<dd\b[^>]*>(.*?)</dd>", section, re.S)
        if len(pairs) != int(count):
            raise ValueError("Parsed count does not match section count")
        kind = {"New submissions": "new", "Cross submissions": "cross", "Cross-lists": "cross", "Replacement submissions": "replace", "Replacements": "replace"}[name]
        for dt, dd in pairs:
            identifier = re.search(r'href\s*=\s*[\x22\x27]/abs/([^\x22\x27]+)', dt)
            if not identifier:
                raise ValueError("Missing arXiv ID")
            arxiv_id = re.sub(r"v\d+$", "", identifier.group(1))
            version_match = re.search(re.escape(arxiv_id) + r"v(\d+)", dt)
            version = int(version_match.group(1)) if version_match else None
            title = re.search(r"<div class=[\x22\x27]list-title[^\x22\x27]*[\x22\x27]>(.*?)</div>", dd, re.S)
            authors = re.search(r"<div class=[\x22\x27]list-authors[\x22\x27]>(.*?)</div>", dd, re.S)
            abstract = re.search(r"<p class=[\x22\x27]mathjax[\x22\x27]>(.*?)</p>", dd, re.S)
            if not title or not authors or not abstract:
                raise ValueError("Missing metadata for " + arxiv_id)
            key = arxiv_id + ("v" + str(version) if version else "@unresolved")
            entries.append({"id": arxiv_id, "version": version, "key": key,
                            "title": re.sub(r"^Title:\s*", "", plain(title.group(1))),
                            "authors": plain(authors.group(1)), "abstract_en": plain(abstract.group(1)),
                            "announcements": {category: kind}, "announcement_date": actual_date,
                            "abs_url": "https://arxiv.org/abs/" + arxiv_id,
                            "version_verified": version is not None, "queue": "revision" if kind == "replace" else "new_or_cross"})
    if len(entries) != total:
        raise ValueError("Incomplete listing: parsed %d, expected %d" % (len(entries), total))
    return {"category": category, "count": total, "sha256": hashlib.sha256(raw).hexdigest(),
            "url": "https://arxiv.org/list/" + category + "/new?show=2000", "announcement_date": actual_date}, entries


def build_listing(snapshots, expected_date):
    if set(snapshots) != set(CATEGORIES):
        raise ValueError("Both categories are required")
    unique, sources = {}, []
    for category in CATEGORIES:
        source, entries = parse_listing(snapshots[category], category, expected_date)
        sources.append(source)
        for entry in entries:
            key = entry["id"]
            if key in unique:
                old = unique[key]
                if old["version"] and entry["version"] and old["version"] != entry["version"]:
                    raise ValueError("Conflicting versions for " + key)
                if not old["version"] and entry["version"]:
                    old.update({k: entry[k] for k in ("version", "key", "version_verified")})
                old["announcements"].update(entry["announcements"])
                if entry["queue"] == "new_or_cross":
                    old["queue"] = "new_or_cross"
            else:
                unique[key] = entry
    return {"schema_version": 1, "announcement_date": expected_date,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "source_status": "provisional_listing",
            "sources": sources, "papers": sorted(unique.values(), key=lambda x: x["id"]),
            "counts": {"raw_items": sum(s["count"] for s in sources), "unique_versions": len(unique),
                       "new_or_cross": sum(p["queue"] == "new_or_cross" for p in unique.values()),
                       "revisions": sum(p["queue"] == "revision" for p in unique.values())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed-dir", type=Path, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_listing({c: (args.feed_dir / (c + "-new.html")).read_bytes() for c in CATEGORIES}, args.date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(args.output)
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
