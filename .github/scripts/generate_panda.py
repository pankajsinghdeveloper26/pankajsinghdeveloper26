#!/usr/bin/env python3
"""
Builds assets/panda-contrib.svg: a cute panda hopping across YOUR real GitHub
contribution boxes. Run by the GitHub Action in .github/workflows/panda.yml.

Local test with fake data:  python .github/scripts/generate_panda.py --sample
Real data:                  GITHUB_TOKEN=... GH_USER=name python .github/scripts/generate_panda.py
Only the Python standard library is used.
"""
import json, os, sys, urllib.request, random

USER = os.environ.get("GH_USER", "pankajsinghdeveloper26")
OUT = os.environ.get("PANDA_OUT", "assets/panda-contrib.svg")
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionCount contributionLevel weekday}}}}}}"""
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
COLORS = ["#ffffff", "#c8f3d4", "#8fe3a8", "#4fc477", "#2a9d58"]  # level 0 is drawn faint white
PITCH, CELL, X0, Y0, W, H = 18, 15, 23, 96, 1000, 250

def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]

def sample():
    """Fake data (quiet year, busy last ~10 weeks) only for testing the look."""
    random.seed(3); weeks = []
    for w in range(53):
        days = []
        for d in range(7):
            lvl = random.choice([0, 0, 1, 2, 3, 4]) if w >= 43 and random.random() < .75 else 0
            days.append({"contributionCount": lvl * 2, "contributionLevel": list(LEVELS)[lvl], "weekday": d})
        weeks.append({"contributionDays": days})
    return 155, weeks

PANDA = """<g transform="translate(0 -25)">
<ellipse cx="-10" cy="19" rx="7" ry="6" fill="#2b2540"><animate attributeName="cy" values="19;15;19" dur="{t}s" repeatCount="indefinite"/></ellipse>
<ellipse cx="10" cy="19" rx="7" ry="6" fill="#2b2540"><animate attributeName="cy" values="15;19;15" dur="{t}s" repeatCount="indefinite"/></ellipse>
<ellipse cx="0" cy="7" rx="17" ry="15" fill="#fff"/>
<g transform="translate(-16 0)"><g><animateTransform attributeName="transform" type="rotate" values="30;-40;30" dur="{t}s" repeatCount="indefinite"/><ellipse cx="0" cy="7" rx="5.5" ry="9" fill="#2b2540"/></g></g>
<g transform="translate(16 0)"><g><animateTransform attributeName="transform" type="rotate" values="-30;40;-30" dur="{t}s" repeatCount="indefinite"/><ellipse cx="0" cy="7" rx="5.5" ry="9" fill="#2b2540"/></g></g>
<circle cx="-13" cy="-27" r="7" fill="#2b2540"/><circle cx="13" cy="-27" r="7" fill="#2b2540"/>
<circle cx="0" cy="-13" r="18" fill="#fff"/>
<ellipse cx="-7.5" cy="-13" rx="5" ry="6.6" transform="rotate(22 -7.5 -13)" fill="#2b2540"/><ellipse cx="7.5" cy="-13" rx="5" ry="6.6" transform="rotate(-22 7.5 -13)" fill="#2b2540"/>
<circle cx="-7.5" cy="-13.5" r="2.6" fill="#fff"/><circle cx="7.5" cy="-13.5" r="2.6" fill="#fff"/>
<circle cx="-7.2" cy="-13.2" r="1.4" fill="#2b2540"/><circle cx="7.8" cy="-13.2" r="1.4" fill="#2b2540"/>
<ellipse cx="0" cy="-6.5" rx="3" ry="2.1" fill="#2b2540"/><path d="M-3 -3Q0 0 3 -3" fill="none" stroke="#2b2540" stroke-width="1.4" stroke-linecap="round"/>
<circle cx="-13" cy="-5" r="3.2" fill="#ff9fc2" opacity=".7"/><circle cx="13" cy="-5" r="3.2" fill="#ff9fc2" opacity=".7"/></g>"""

def build(total, weeks):
    grid = [[0] * 7 for _ in weeks]
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            grid[c][d["weekday"]] = LEVELS.get(d["contributionLevel"], 0)
    cells = ""
    for c, col in enumerate(grid):
        for r, lvl in enumerate(col):
            op = ' opacity=".5"' if lvl == 0 else ""
            cells += f'<rect x="{X0+c*PITCH}" y="{Y0+r*PITCH}" width="{CELL}" height="{CELL}" rx="4" fill="{COLORS[lvl]}"{op}/>'
    # the panda stands on the highest contributed box of each week, else on top of the grid
    pts = []
    for c, col in enumerate(grid):
        top = next((r for r, l in enumerate(col) if l > 0), None)
        pts.append((X0 + c * PITCH + CELL / 2, Y0 + (top if top is not None else 0) * PITCH - 1))
    d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f}"
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        up = min(y1, y2) - 26; dx = x2 - x1
        d += f"C{x1+dx*.25:.0f} {up:.0f} {x2-dx*.25:.0f} {up:.0f} {x2:.0f} {y2:.0f}"
    hop = 0.24; dur = hop * len(pts)
    stalk = lambda x: "".join(f'<rect x="{x}" y="{y}" width="10" height="30" rx="4" fill="#7bd88f" stroke="#2a9d58" stroke-width="2"/>' for y in (20, 54, 88, 122, 156, 190))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A cute panda hopping across {total} GitHub contributions from the last year">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe4f1"/><stop offset=".55" stop-color="#e6dcff"/><stop offset="1" stop-color="#d6ecff"/></linearGradient><clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#g)"/>
<g opacity=".7">{stalk(4)}{stalk(986)}</g>
{cells}
<text x="{X0}" y="{H-18}" font-family="Georgia,serif" font-size="17" fill="#5a4a78">{total} contributions in the last year</text>
<g><animateMotion path="{d}" dur="{dur:.1f}s" repeatCount="indefinite"/>
<g transform="scale(.62)"><g><animateTransform attributeName="transform" type="scale" values="1.1 .9;.94 1.1;1.1 .9" dur="{hop}s" repeatCount="indefinite"/>{PANDA.format(t=hop*2)}</g></g></g></g></svg>'''

if __name__ == "__main__":
    total, weeks = sample() if "--sample" in sys.argv else fetch()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(build(total, weeks))
    print("wrote", OUT, "-", total, "contributions,", len(weeks), "weeks")
