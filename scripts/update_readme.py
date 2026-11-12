"""Fills the "Recently updated" block in README.md with the latest pushed public repos."""
import json, os, re, urllib.request

USER = "AlparslanSemiz"
SKIP = {USER, f"{USER}.github.io"}
req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner",
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"},
)
repos = json.load(urllib.request.urlopen(req))
rows = []
for r in repos:
    if r["fork"] or r["private"] or r["archived"] or r["name"] in SKIP:
        continue
    desc = (r["description"] or "").strip()
    rows.append(f"- [{r['name']}]({r['html_url']}){': ' + desc if desc else ''}")
    if len(rows) == 5:
        break

path = "README.md"
text = open(path, encoding="utf-8").read()
block = "<!-- RECENT:START -->\n" + "\n".join(rows) + "\n<!-- RECENT:END -->"
new = re.sub(r"<!-- RECENT:START -->.*?<!-- RECENT:END -->", block, text, flags=re.S)
if new != text:
    open(path, "w", encoding="utf-8").write(new)
    print("README updated")
else:
    print("no change")
