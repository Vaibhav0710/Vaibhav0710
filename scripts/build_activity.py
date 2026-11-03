#!/usr/bin/env python3
"""Draw sheet 4, the activity log, from live GitHub data.

    GITHUB_TOKEN=... python3 scripts/build_activity.py --user Vaibhav0710 --out dist

The profile workflow runs this every 12 hours and publishes the SVGs to the
`output` branch. `--sample` draws made-up data for a local layout check only.
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_sheets import THEMES, Sheet  # noqa: E402

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-sheets"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GitHub API error: {body['errors']}")
    u = body["data"]["user"]
    cc = u["contributionsCollection"]
    langs = Counter()
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    return {
        "weeks": [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]]
                  for w in cc["contributionCalendar"]["weeks"]],
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "repos": cc["totalRepositoriesWithContributedCommits"],
        "langs": langs,
    }


def sample():
    rnd = random.Random(7)
    end = dt.date.today()
    start = end - dt.timedelta(days=end.weekday() + 1 + 52 * 7)
    weeks, week = [], []
    for i in range((end - start).days + 1):
        d = start + dt.timedelta(days=i)
        week.append((d.isoformat(), rnd.choice([0, 0, 0, 1, 2, 3, 5])))
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)
    total = sum(c for w in weeks for _, c in w)
    return {"weeks": weeks, "total": total, "commits": int(total * 0.8), "prs": 12, "issues": 3, "reviews": 4,
            "repos": 9, "langs": Counter({"Java": 900, "Python": 400, "JavaScript": 250, "C#": 150, "HTML": 60})}


def streaks(days):
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:  # today not counted yet
        seq = seq[:-1]
    for _, c in reversed(seq):
        if not c:
            break
        cur += 1
    return longest, cur


def nice_max(v):
    if v <= 5:
        return 5
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= v:
            return m * mag
    return 10 * mag


def sheet_activity(data, theme):
    W, H = 1200, 800
    s = Sheet(W, H, theme)
    s.frame(6, 4)
    s.text(62, 96, "ACTIVITY LOG", "d", 40, "ink", ls=1)
    s.text(64, 124, "Public contributions on GitHub over the last year, by week. Redrawn every 12 hours.", "b", 16, "ink2")

    weeks = data["weeks"]
    totals = [sum(c for _, c in w) for w in weeks]
    top = nice_max(max(totals) if totals else 1)
    x0, x1, y0, y1 = 110, 1136, 190, 400  # plot box
    bw = (x1 - x0) / len(totals)
    Y = lambda v: y1 - v / top * (y1 - y0)

    s.text(64, 168, "CONTRIBUTIONS PER WEEK", "mm", 12.5, "ink", ls=1.5)
    for k in range(5):
        v = top * k / 4
        y = Y(v)
        s.line(x0, y, x1, y, "faint" if k else "ink", 1 if k else 1.2)
        s.text(x0 - 10, y + 4, f"{v:g}", "m", 11.5, "ink2", "end")
    for i, t in enumerate(totals):
        if t:
            s.add(f'<rect class="grow" style="animation-delay:{0.8 + i * 0.025:.3f}s" x="{x0 + i * bw + 1.5:.1f}" y="{Y(t):.1f}" '
                  f'width="{bw - 3:.1f}" height="{y1 - Y(t):.1f}" fill="{s.c["hi"]}"/>')
    # month ticks at the first week that starts in a new month
    last = None
    for i, w in enumerate(weeks):
        m = w[0][0][:7]
        if m != last:
            if last is not None:
                x = x0 + i * bw
                s.line(x, y1, x, y1 + 6, "ink", 1)
                s.text(x + 4, y1 + 21, dt.date.fromisoformat(w[0][0]).strftime("%b").upper(), "m", 11, "ink2")
            last = m
    # average line and the busiest week
    avg = sum(totals) / len(totals) if totals else 0
    s.line(x0, Y(avg), x1, Y(avg), "red", 1, "6 4")
    s.text(x0 - 10, Y(avg) + 4, f"AVG {avg:.1f}", "mm", 10.5, "red", "end", 0.5)
    if totals and max(totals):
        i = totals.index(max(totals))
        bx = x0 + (i + 0.5) * bw
        lx = bx - 70 if i > len(totals) / 2 else bx + 70
        s.line(bx, Y(totals[i]) - 3, lx, y0 - 8, "ink", 0.8)
        s.add(f'<circle cx="{bx:.1f}" cy="{Y(totals[i]) - 3:.1f}" r="2.2" fill="{s.c["ink"]}"/>')
        s.text(lx + (6 if lx > bx else -6), y0 - 4, f"BUSIEST WEEK: {max(totals)}", "dm", 14, "ink",
               "start" if lx > bx else "end", 0.6)

    # totals table
    days = [d for w in weeks for d in w]
    longest, current = streaks(days)
    cells = [("CONTRIBUTIONS", data["total"]), ("COMMITS", data["commits"]), ("PULL REQUESTS", data["prs"]),
             ("ISSUES", data["issues"]), ("REVIEWS", data["reviews"]), ("REPOS", data["repos"]),
             ("LONGEST STREAK", f"{longest} d"), ("CURRENT STREAK", f"{current} d")]
    ty, cw = 460, (1136 - 64) / len(cells)
    s.rect(64, ty, 1136 - 64, 74, "ink", 1.4)
    for i, (k, v) in enumerate(cells):
        x = 64 + cw * i
        if i:
            s.line(x, ty, x, ty + 74, "ink", 1)
        s.text(x + 12, ty + 22, k, "m", 9.5, "ink2", ls=0.8)
        s.text(x + 12, ty + 58, str(v), "d", 30, "hi", ls=0.3)

    # languages, drawn to scale
    ly = 586
    s.text(64, ly, "LANGUAGES BY CODE SIZE, OWN PUBLIC REPOSITORIES", "mm", 12.5, "ink", ls=1.5)
    langs = data["langs"].most_common(5)
    whole = sum(data["langs"].values()) or 1
    bx0, bscale = 220, 640  # 100 % = 640 px
    for i, (name, size) in enumerate(langs):
        y = ly + 34 + i * 28
        pct = size / whole * 100
        s.text(64, y, name, "b", 15, "ink")
        s.line(bx0, y - 5, bx0 + bscale, y - 5, "faint", 8)
        s.line(bx0, y - 5, bx0 + bscale * pct / 100, y - 5, "hi", 8)
        s.text(bx0 + bscale + 14, y, f"{pct:.0f} %", "m", 13, "ink2")
    s.strip("ACTIVITY LOG", "4 OF 4")
    return s.svg(f"Activity log: {data['total']} contributions in the last year")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "Vaibhav0710"))
    ap.add_argument("--out", default="assets")
    ap.add_argument("--sample", action="store_true", help="made-up data, for checking the layout locally")
    a = ap.parse_args()
    if a.sample:
        data = sample()
    else:
        token = os.environ.get("GITHUB_TOKEN") or sys.exit("Set GITHUB_TOKEN, or pass --sample for a layout check.")
        data = fetch(a.user, token)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        p = out / f"sheet-activity-{theme}.svg"
        p.write_text(sheet_activity(data, theme), encoding="utf-8")
        print("wrote", p)


if __name__ == "__main__":
    main()
