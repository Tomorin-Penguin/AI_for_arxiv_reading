"""Validate full Git trees before publishing an incremental reading update."""
import argparse
import json
import re


def _entries(snapshot):
    if snapshot.get("truncated") is not False:
        raise ValueError("complete recursive tree required")
    entries = {}
    seen = set()
    for entry in snapshot["tree"]:
        path = entry["path"]
        if path in seen or not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError("invalid or duplicate path")
        seen.add(path)
        if entry["type"] != "tree":
            entries[path] = (entry["mode"], entry["type"], entry["sha"])
    if not entries:
        raise ValueError("empty repository snapshot")
    return entries


def validate_publication(before, after, expected_blobs):
    """Require zero removals and exact intended regular-file blob hashes.

    expected_blobs maps every intended new/updated path to its locally computed
    Git blob SHA. No permission/type changes or other changes are allowed.
    """
    old, new = _entries(before), _entries(after)
    missing = sorted(old.keys() - new.keys())
    if missing:
        raise ValueError("deleted paths: " + ", ".join(missing))
    changed = {path for path in new if new[path] != old.get(path)}
    unexpected = sorted(changed - expected_blobs.keys())
    if unexpected:
        raise ValueError("unexpected changes: " + ", ".join(unexpected))
    for path, sha in expected_blobs.items():
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("invalid expected blob SHA")
        if new.get(path) != ("100644", "blob", sha):
            raise ValueError("intended content or mode mismatch: " + path)
        if path in old and old[path][:2] != new[path][:2]:
            raise ValueError("mode/type change: " + path)
    return sorted(changed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("expected_blobs")
    args = parser.parse_args()
    with open(args.before) as f, open(args.after) as g, open(args.expected_blobs) as h:
        changed = validate_publication(json.load(f), json.load(g), json.load(h))
    print(json.dumps({"verified": True, "changed": changed}, ensure_ascii=False))
