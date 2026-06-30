#!/usr/bin/env python3
"""
X post optimizer — the engine of the self-improving content loop.

Reads a CSV of your posts (exported/transcribed from X analytics), scores each
one with an "Algo Score" that mirrors how the active ranking scorer in this
repo weights engagement (replies/reposts/shares/profile-clicks >> likes;
video completion matters), normalizes by reach, then prints:

  1. Your posts ranked best -> worst by Algo Score / 1k impressions
  2. Which format / hook / topic / post-hour cluster at the top vs bottom
  3. One concrete recommendation for next week

The weights are DIRECTIONAL, not the exact runtime coefficients X uses
(those are feature-switch params). Tune them in WEIGHTS as you learn what your
own audience rewards — that's what makes the loop "self-improving".

Usage:
    python3 scripts/x_post_optimizer.py posts.csv
    python3 scripts/x_post_optimizer.py posts.csv --top 5

CSV columns (header row required; missing numeric cells treated as 0):
    date, post_id, format, hook_type, topic, impressions, likes, replies,
    reposts, quotes, bookmarks, shares, profile_clicks, follows, video_views,
    avg_watch_seconds, video_length_seconds

`format`, `hook_type`, `topic` are free-text labels you assign (e.g.
format=video|thread|single|question; hook_type=result-first|question|hot-take;
topic=build-in-public|teach|take|case-study). The script clusters on whatever
labels you use.
"""

import argparse
import csv
import sys
from collections import defaultdict

# Directional weights — mirror ranking_scorer.rs ordering, not its exact params.
# Edit these as your data teaches you what converts. This is the tuning knob.
WEIGHTS = {
    "like": 1.0,
    "reply": 14.0,
    "repost": 20.0,          # applied to reposts + quotes
    "share": 10.0,           # applied to bookmarks + shares (save/DM/copy-link)
    "profile_click": 12.0,
    "follow": 24.0,          # follows attributed to the post
    "video_completion": 8.0,  # weight * completion_ratio (0..1)
}

NUMERIC = [
    "impressions", "likes", "replies", "reposts", "quotes", "bookmarks",
    "shares", "profile_clicks", "follows", "video_views",
    "avg_watch_seconds", "video_length_seconds",
]


def to_float(value):
    try:
        return float(str(value).replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def completion_ratio(row):
    length = row["video_length_seconds"]
    if length <= 0:
        return 0.0
    return min(row["avg_watch_seconds"] / length, 1.0)


def algo_score_per_1k(row):
    impressions = row["impressions"]
    if impressions <= 0:
        return 0.0
    raw = (
        WEIGHTS["like"] * row["likes"]
        + WEIGHTS["reply"] * row["replies"]
        + WEIGHTS["repost"] * (row["reposts"] + row["quotes"])
        + WEIGHTS["share"] * (row["bookmarks"] + row["shares"])
        + WEIGHTS["profile_click"] * row["profile_clicks"]
        + WEIGHTS["follow"] * row["follows"]
        + WEIGHTS["video_completion"] * completion_ratio(row) * 100.0
    )
    return raw / impressions * 1000.0


def load(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit("CSV has no header row.")
        for raw in reader:
            row = dict(raw)
            for col in NUMERIC:
                row[col] = to_float(row.get(col, 0))
            for label in ("format", "hook_type", "topic"):
                row[label] = (row.get(label) or "unlabeled").strip() or "unlabeled"
            row["score"] = algo_score_per_1k(row)
            rows.append(row)
    if not rows:
        sys.exit("No data rows found.")
    return rows


def cluster_report(rows, dimension):
    buckets = defaultdict(list)
    for row in rows:
        buckets[row[dimension]].append(row["score"])
    summary = [
        (label, sum(scores) / len(scores), len(scores))
        for label, scores in buckets.items()
    ]
    summary.sort(key=lambda item: item[1], reverse=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Score & cluster X posts.")
    parser.add_argument("csv", help="Path to posts CSV")
    parser.add_argument("--top", type=int, default=10, help="How many ranked posts to show")
    args = parser.parse_args()

    rows = load(args.csv)
    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)

    print("\n=== POSTS RANKED BY ALGO SCORE / 1k IMPRESSIONS ===")
    print(f"{'score':>8}  {'impr':>8}  {'format':<12} {'hook':<14} {'topic':<16} post_id")
    for row in ranked[: args.top]:
        print(
            f"{row['score']:>8.1f}  {int(row['impressions']):>8d}  "
            f"{row['format']:<12.12} {row['hook_type']:<14.14} "
            f"{row['topic']:<16.16} {row.get('post_id', '')}"
        )

    for dimension in ("format", "hook_type", "topic"):
        print(f"\n=== AVG SCORE BY {dimension.upper()} (best -> worst) ===")
        for label, avg, count in cluster_report(rows, dimension):
            print(f"  {avg:>8.1f}   n={count:<3d}  {label}")

    # One actionable recommendation: best format x best hook, and what to cut.
    best_format = cluster_report(rows, "format")[0]
    worst_format = cluster_report(rows, "format")[-1]
    best_hook = cluster_report(rows, "hook_type")[0]
    flagged = [r for r in rows if r["impressions"] > 0 and r["score"] < 0]

    print("\n=== RECOMMENDATION FOR NEXT WEEK ===")
    print(f"  • Do MORE: '{best_format[0]}' posts with a '{best_hook[0]}' hook "
          f"(top format avg {best_format[1]:.0f}/1k).")
    if len(cluster_report(rows, "format")) > 1:
        print(f"  • Do LESS: '{worst_format[0]}' posts "
              f"(avg {worst_format[1]:.0f}/1k — your weakest format).")
    print("  • Change only ONE variable vs this week so the signal stays clean.")
    if flagged:
        print(f"  • ⚠ {len(flagged)} post(s) scored negative — check for "
              f"'not interested'/mutes and avoid that pattern.")
    print()


if __name__ == "__main__":
    main()
