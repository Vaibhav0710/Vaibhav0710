#!/usr/bin/env python3
"""Refresh the "Recent commits" section of README.md from GitHub.

    GITHUB_TOKEN=... python3 scripts/build_readme.py

Finds my latest commits on the default branch of each public repository I own
and rewrites the lines between the recent_commits markers in README.md.
Run daily by .github/workflows/update-readme.yml.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("PROFILE_LOGIN", "Vaibhav0710")
README = Path(__file__).resolve().parent.parent / "README.md"
SKIP = {LOGIN.lower()}  # the profile repo itself
LIMIT = 8

QUERY = """
query($login: String!) {
  user(login: $login) {
    id
    repositories(first: 30, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        url
        defaultBranchRef { target { ... on Commit {
          history(first: 10) { nodes { messageHeadline committedDate url author { user { login } } } }
        } } }
      }
    }
  }
}
"""


def graphql(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        sys.exit(f"GitHub API error: {body['errors']}")
    return body["data"]


def recent_commits(data):
    out = []
    for repo in data["user"]["repositories"]["nodes"]:
        ref = repo["defaultBranchRef"]
        if repo["name"].lower() in SKIP or not ref:
            continue
        for c in ref["target"]["history"]["nodes"]:
            who = (c["author"] or {}).get("user") or {}
            if (who.get("login") or "").lower() != LOGIN.lower():
                continue
            if c["messageHeadline"].startswith("Merge "):
                continue
            out.append((c["committedDate"], repo, c))
    out.sort(key=lambda x: x[0], reverse=True)
    return out[:LIMIT]


def render(commits):
    if not commits:
        return "No public commits yet."
    lines = []
    for when, repo, c in commits:
        day = dt.datetime.fromisoformat(when.replace("Z", "+00:00")).strftime("%d %b %Y")
        msg = c["messageHeadline"].replace("[", "\\[").replace("]", "\\]")
        lines.append(f"- [{repo['name']}]({repo['url']}): [{msg}]({c['url']}) · {day}")
    return "\n".join(lines)


def replace_section(text, name, body):
    pattern = re.compile(rf"(<!-- {name} starts -->).*?(<!-- {name} ends -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"README.md has no {name} markers")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)


def main():
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("Set GITHUB_TOKEN")
    text = README.read_text(encoding="utf-8")
    new = replace_section(text, "recent_commits", render(recent_commits(graphql(token))))
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
