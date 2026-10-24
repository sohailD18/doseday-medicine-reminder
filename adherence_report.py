#!/usr/bin/env python3
"""DoseDay adherence report.

Reads adherence_log.csv exported from the DoseDay web app and prints a
compliance summary. Uses only Python's standard library.

Usage:
    python adherence_report.py [csv_file]                  last 7 days (default)
    python adherence_report.py [csv_file] --days 30        last 30 days
    python adherence_report.py [csv_file] --days 365       last 365 days
    python adherence_report.py [csv_file] --month 2026-10  one calendar month
"""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, timedelta

REQUIRED = {"date", "medicine", "dosage", "scheduled_time", "status"}
LINE = "=" * 60


def read_log(path):
    """Return (valid_rows, number_of_skipped_rows)."""
    rows, skipped = [], 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"Error: missing column(s) in CSV: {', '.join(sorted(missing))}")
        for r in reader:
            try:
                r["_date"] = date.fromisoformat(r["date"].strip())
                status = r["status"].strip().lower()
                if status not in ("taken", "missed"):
                    raise ValueError("unknown status")
                r["_taken"] = status == "taken"
                rows.append(r)
            except (ValueError, AttributeError):
                skipped += 1
    return rows, skipped


def pct(taken, total):
    return 100.0 * taken / total if total else 0.0


def bar(p, width=20):
    filled = round(p / 100 * width)
    return "#" * filled + "." * (width - filled)


def rating(p):
    if p >= 90:
        return "Excellent"
    if p >= 75:
        return "Good"
    if p >= 50:
        return "Needs improvement"
    return "Low - consider reminders or a check-in with your doctor"


def parse_month(text):
    try:
        year, month = text.split("-")
        first = date(int(year), int(month), 1)
    except (ValueError, TypeError):
        sys.exit("Error: --month must look like 2026-10")
    nxt = date(first.year + (first.month == 12), first.month % 12 + 1, 1)
    return first, nxt - timedelta(days=1)


def tally(window, key):
    """Group rows by key(row) -> [taken, total]."""
    out = defaultdict(lambda: [0, 0])
    for r in window:
        out[key(r)][1] += 1
        if r["_taken"]:
            out[key(r)][0] += 1
    return out


def main():
    ap = argparse.ArgumentParser(description="DoseDay adherence report")
    ap.add_argument("csv_file", nargs="?", default="adherence_log.csv")
    ap.add_argument("--days", type=int, default=7, help="look back N days from the latest date in the file")
    ap.add_argument("--month", help="report one calendar month, e.g. 2026-10")
    args = ap.parse_args()
    if args.days < 1:
        sys.exit("Error: --days must be at least 1")

    try:
        rows, skipped = read_log(args.csv_file)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {args.csv_file}")
    if not rows:
        sys.exit("No valid rows found in the CSV.")

    if args.month:
        start, end = parse_month(args.month)
        title = f"MONTHLY ADHERENCE REPORT - {start.strftime('%B %Y')}"
    else:
        end = max(r["_date"] for r in rows)
        start = end - timedelta(days=args.days - 1)
        title = f"ADHERENCE REPORT - LAST {args.days} DAYS"
    window = [r for r in rows if start <= r["_date"] <= end]
    if not window:
        sys.exit(f"No doses found between {start} and {end}.")

    total = len(window)
    taken = sum(r["_taken"] for r in window)
    overall = pct(taken, total)
    by_day = tally(window, lambda r: r["_date"])
    by_med = tally(window, lambda r: r["medicine"])

    print(LINE)
    print(f" DOSEDAY - {title}")
    print(f" Period: {start} to {end}")
    print(LINE)
    print(f" Doses scheduled : {total}")
    print(f" Doses taken     : {taken}")
    print(f" Doses missed    : {total - taken}")
    print(f" Compliance      : {overall:.1f}%  [{bar(overall)}]")
    print(f" Rating          : {rating(overall)}")

    if len(by_day) <= 31:
        print("\n Daily compliance")
        print(" " + "-" * 58)
        for d in sorted(by_day):
            t, n = by_day[d]
            print(f" {d} {d.strftime('%a')}  {t}/{n:<2} {pct(t, n):5.1f}%  [{bar(pct(t, n), 15)}]")
    else:  # long periods: show months instead of one line per day
        by_month = tally(window, lambda r: r["_date"].strftime("%Y-%m"))
        print("\n Monthly compliance")
        print(" " + "-" * 58)
        for m in sorted(by_month):
            t, n = by_month[m]
            print(f" {m}      {t}/{n:<4} {pct(t, n):5.1f}%  [{bar(pct(t, n), 15)}]")

    print("\n By medicine (lowest first)")
    print(" " + "-" * 58)
    for name, (t, n) in sorted(by_med.items(), key=lambda kv: pct(*kv[1])):
        print(f" {name[:20]:<20} {t}/{n:<4} {pct(t, n):5.1f}%  [{bar(pct(t, n), 15)}]")

    worst = min(by_med.items(), key=lambda kv: pct(*kv[1]))
    best_day = max(by_day.items(), key=lambda kv: pct(*kv[1]))
    worst_day = min(by_day.items(), key=lambda kv: pct(*kv[1]))
    print("\n Insights")
    print(" " + "-" * 58)
    print(f" - Most-missed medicine : {worst[0]} ({pct(*worst[1]):.0f}% taken)")
    print(f" - Best day             : {best_day[0]} ({pct(*best_day[1]):.0f}%)")
    print(f" - Hardest day          : {worst_day[0]} ({pct(*worst_day[1]):.0f}%)")
    if skipped:
        print(f"\n Note: {skipped} invalid row(s) in the CSV were skipped.")
    print("\n This report is informational and not medical advice.")
    print(LINE)


if __name__ == "__main__":
    main()
