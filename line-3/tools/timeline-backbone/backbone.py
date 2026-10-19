#!/usr/bin/env python3
"""Summarize the definite and unresolved pairwise order in a verified timeline pack."""
import argparse
from bisect import bisect_left, bisect_right
from datetime import datetime, timezone
import hashlib
import json
import sys

import replay


def instant(text):
    """Convert Replay's canonical aware UTC instant to integer microseconds."""
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError("timeline contains a non-UTC instant")
    delta = value.astimezone(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds


def summarize(timeline, limit=50):
    """Return exact interval-order counts, with bounded event citations.

    Intervals are half-open. A.end <= B.start establishes A before B. Intersecting
    intervals are unresolved as an order claim; that does not mean simultaneous.
    """
    if type(limit) is not int or not 0 <= limit <= 200:
        raise ValueError("limit must be an integer from 0 to 200")
    events = timeline.get("events")
    if not isinstance(events, list):
        raise ValueError("verified timeline has no event list")
    parsed = []
    for event in events:
        start = instant(event["start_utc"])
        end = instant(event["end_utc_exclusive"])
        if end <= start:
            raise ValueError("timeline contains an empty or reversed interval")
        parsed.append((event, start, end))

    starts = sorted(start for _, start, _ in parsed)
    ends = sorted(end for _, _, end in parsed)
    rows = []
    definite_pairs = 0
    for event, start, end in parsed:
        before = bisect_right(ends, start)
        after = len(parsed) - bisect_left(starts, end)
        unresolved = len(parsed) - 1 - before - after
        definite_pairs += before
        rows.append({
            "source": event["source"],
            "line": event["line"],
            "line_sha256": event["line_sha256"],
            "start_utc": event["start_utc"],
            "end_utc_exclusive": event["end_utc_exclusive"],
            "definitely_before": before,
            "definitely_after": after,
            "unresolved_pairs": unresolved,
        })

    # Surface the least ordered events first, with replay chronology as a tie break.
    rows.sort(key=lambda row: (-row["unresolved_pairs"], row["start_utc"],
                              row["source"], row["line"]))
    n = len(parsed)
    pair_total = n * (n - 1) // 2
    return {
        "verified": True,
        "events": n,
        "pairs": pair_total,
        "definitely_ordered_pairs": definite_pairs,
        "unresolved_pairs": pair_total - definite_pairs,
        "citations": rows[:limit],
        "omitted_citations": n - min(n, limit),
        "semantics": "Half-open uncertainty intervals that do not intersect establish order; intersecting intervals leave order unresolved.",
    }


def demo():
    sample = [
        ("client.log", b"2026-10-18T10:00:00Z accepted\n"),
        ("retry.log", b"2026-10-18T10:00:01Z retried\n"),
        ("server.log", b"2026-10-18T10:00:04Z completed\n"),
    ]
    pack = replay.make_pack(sample, clock_uncertainty_ms=250)
    verified = replay.verify_pack(pack)
    result = summarize(pack["timeline"])
    result["example"] = "synthetic; no real incident or clock error measured"
    result["pack_sha256"] = replay.digest(replay.canonical(pack) + b"\n")
    result["replay"] = verified
    return result


def analyze(path, expected, limit):
    raw = replay.read_workspace(path, replay.MAX_PACK_BYTES)
    if expected is not None:
        if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
            raise replay.ReplayError("expected hash must be 64 lowercase hex digits")
        if hashlib.sha256(raw).hexdigest() != expected:
            raise replay.ReplayError("pack SHA-256 does not match expected digest")
    pack = replay.load_pack(raw)
    verified = replay.verify_pack(pack)
    result = summarize(pack["timeline"], limit)
    result["pack_sha256"] = hashlib.sha256(raw).hexdigest()
    result["replay"] = verified
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="run the synthetic verified example")
    inspect = commands.add_parser("analyze", help="summarize a workspace evidence pack")
    inspect.add_argument("pack")
    inspect.add_argument("--expect-sha256", help="optional independently trusted pack digest")
    inspect.add_argument("--limit", type=int, default=50, help="event citations to show (0..200)")
    args = parser.parse_args(argv)
    try:
        result = demo() if args.command == "demo" else analyze(
            args.pack, args.expect_sha256, args.limit)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print("timeline-backbone: " + str(exc).replace("\n", "\\n"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
