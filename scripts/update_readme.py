"""Fills the "Recently updated" block in README.md with the latest pushed public repos."""
import json, os, re, urllib.request
from datetime import datetime, timezone

USER = "AlparslanSemiz"
# Helper repos that aren't projects of their own.
SKIP = {USER, f"{USER}.github.io", "homebrew-tap"}
# Nicer display names where the repo name can't carry the real one.
NAMES = {"Serit": "Şerit", "Gamemetrix": "GameMetrix", "rate-my-professor": "RateMyProf",
         "lost-soul": "Lost Soul", "price-sniper": "Price Sniper",
         "prayer-times-widget": "Prayer Times Widget", "mail-triage-bot": "Mail Triage Bot",
         "godot-mobile-template": "Godot Mobile Template"}

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=40&type=owner",
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"},
)
repos = json.load(urllib.request.urlopen(req))

def ago(iso: str) -> str:
    then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - then).days
    if days <= 0: return "today"
    if days == 1: return "yesterday"
    if days < 30: return f"{days} days ago"
    return then.strftime("%b %Y")

rows = []
for r in repos:
    if r["fork"] or r["private"] or r["archived"] or r["name"] in SKIP:
        continue
    name = NAMES.get(r["name"], r["name"])
    desc = (r["description"] or "").strip()
    rows.append(f"| **[{name}]({r['html_url']})** | {desc} | {ago(r['pushed_at'])} |")
    if len(rows) == 5:
        break

table = "| Project | What it is | Updated |\n|---|---|---|\n" + "\n".join(rows)
path = "README.md"
text = open(path, encoding="utf-8").read()
new = re.sub(r"<!-- RECENT:START -->.*?<!-- RECENT:END -->",
             "<!-- RECENT:START -->\n" + table + "\n<!-- RECENT:END -->", text, flags=re.S)
if new != text:
    open(path, "w", encoding="utf-8").write(new)
    print("README updated")
else:
    print("no change")
