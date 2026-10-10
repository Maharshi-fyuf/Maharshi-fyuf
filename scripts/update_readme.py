#!/usr/bin/env python3
"""Refresh the 'Recently pushed' section of README.md.

Lists the owner's most recently pushed public, non-fork repos between the
<!--START_SECTION:recent--> and <!--END_SECTION:recent--> markers.
Standard library only, so the workflow needs no pip install.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime

USER = os.environ.get("GH_USER", "Maharshi-fyuf")
TOKEN = os.environ.get("GITHUB_TOKEN")
LIMIT = 5
README = "README.md"
START = "<!--START_SECTION:recent-->"
END = "<!--END_SECTION:recent-->"


def api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "readme-updater",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def build_section():
    repos = api(
        f"https://api.github.com/users/{USER}/repos"
        "?sort=pushed&direction=desc&per_page=30&type=owner"
    )
    lines = []
    for repo in repos:
        if repo["fork"] or repo["archived"] or repo["name"].lower() == USER.lower():
            continue
        desc = (repo.get("description") or "").strip()
        lang = repo.get("language")
        pushed = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
        parts = [f"**[{repo['name']}]({repo['html_url']})**"]
        if desc:
            parts.append(f"— {desc}")
        meta = [f"`{lang}`"] if lang else []
        meta.append(pushed.strftime("%b %d, %Y"))
        lines.append("- " + " ".join(parts) + " · " + " · ".join(meta))
        if len(lines) == LIMIT:
            break
    return "\n".join(lines) if lines else "_No public repos pushed yet._"


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"Markers {START} / {END} not found in {README}")
    body = build_section()
    new_text = pattern.sub(lambda m: f"{START}\n{body}\n{END}", text)
    if new_text != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("README updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
