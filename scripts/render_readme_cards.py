#!/usr/bin/env python3
"""Génère les cartes SVG animées du README (hero, tuiles, repos, graphe de contributions)."""
import json, os, re, urllib.request
from html import escape

USER = "Maxxes0"
NAME = "Maxxes"
BIO = "Dev / Prog · Étudiant à Ynov Campus, Lyon"
ACCENT, BG, FG, MUTED, CARD = "#6c8cff", "#0d1117", "#e6edf3", "#8b949e", "#161b22"
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
STATIC = os.environ.get("STATIC") == "1"
OUT = os.path.join(os.path.dirname(__file__), "..", "cards")
os.makedirs(OUT, exist_ok=True)

CSS = f"""
text{{font-family:{FONT}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{0%{{opacity:0;transform:scale(0)}}70%{{transform:scale(1.25)}}100%{{opacity:1;transform:scale(1)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes swing{{0%{{opacity:0;transform:translateY(24px)}}70%{{transform:translateY(-4px)}}100%{{opacity:1;transform:none}}}}
.a{{opacity:0;animation:rise .7s cubic-bezier(.2,.8,.2,1) forwards}}
.p{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out forwards}}
.g{{transform-box:fill-box;transform-origin:bottom;animation:grow .7s ease-out both}}
.s{{opacity:0;animation:swing .8s ease-out forwards}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;transform:none!important}}}}
""" + ("*{animation:none!important;opacity:1!important;transform:none!important}" if STATIC else "")

def svg(w, h, body, name):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{CSS}</style>' \
        f'<rect width="{w}" height="{h}" rx="14" fill="{BG}" stroke="#30363d"/>{body}</svg>'
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)

def get(url):
    import subprocess
    try:
        return subprocess.run(["curl", "-fsSL", "-A", "readme-cards", url], capture_output=True, text=True, timeout=30, check=True).stdout
    except Exception as e:
        print("warn:", url, e); return ""

# ---------- hero
def hero():
    glow = f'<defs><linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="200" y2="0"><stop offset="0" stop-color="{FG}"/><stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{FG}"/><animateTransform attributeName="gradientTransform" type="translate" from="-200 0" to="700 0" dur="3.5s" begin="1s" repeatCount="indefinite"/></linearGradient></defs>'
    body = glow + f'''
<circle cx="760" cy="40" r="120" fill="{ACCENT}" fill-opacity=".08"/>
<text class="a" x="40" y="70" font-size="14" fill="{ACCENT}" letter-spacing="3" style="animation-delay:.1s">BONJOUR, JE SUIS</text>
<text class="a" x="40" y="130" font-size="58" font-weight="700" fill="url(#sh)" style="animation-delay:.3s">{escape(NAME)}</text>
<text class="a" x="40" y="168" font-size="18" fill="{MUTED}" style="animation-delay:.6s">{escape(BIO)}</text>'''
    svg(840, 200, body, "hero.svg")

# ---------- tiles
def tile(name, title, sub, icon, delay):
    body = f'''<g class="s" style="animation-delay:{delay}s">
<text x="24" y="52" font-size="30">{icon}</text>
<text x="24" y="92" font-size="18" font-weight="600" fill="{FG}">{escape(title)}</text>
<text x="24" y="116" font-size="13" fill="{MUTED}">{escape(sub)}</text></g>'''
    svg(270, 140, body, name)

# ---------- contributions
def contributions():
    html = get(f"https://github.com/users/{USER}/contributions")
    days = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', html) or \
           [(d, l) for l, d in re.findall(r'data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', html)]
    days = sorted(days)
    if not days:
        days = [(f"d{i}", "0") for i in range(371)]
    cols = ["#161b22", "#1c2a5a", "#2f4aa8", "#4a6ae0", ACCENT]
    cell, gap = 11, 3
    body = f'<text class="a" x="24" y="34" font-size="16" font-weight="600" fill="{FG}">Contributions</text>'
    # pad to start on sunday
    first = 0
    try:
        import datetime
        first = (datetime.date.fromisoformat(days[0][0]).weekday() + 1) % 7
    except Exception: pass
    for i, (_, lvl) in enumerate(days):
        idx = i + first
        x, y = 24 + (idx // 7) * (cell + gap), 52 + (idx % 7) * (cell + gap)
        delay = (idx // 7) * 0.025 + 0.3
        body += f'<rect class="p" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{cols[int(lvl)]}" style="animation-delay:{delay:.2f}s"/>'
    total = sum(1 for _, l in days if l != "0")
    body += f'<text x="24" y="170" font-size="12" fill="{MUTED}">{total} jours actifs sur la dernière année</text>'
    svg(840, 190, body, "activity.svg")

# ---------- repos
def repos():
    data = json.loads(get(f"https://api.github.com/users/{USER}/repos?sort=updated&per_page=6") or "[]")
    data = [r for r in data if not r["fork"]][:4]
    for i, r in enumerate(data):
        desc = r["description"] or "Pas de description"
        body = f'''<g class="s" style="animation-delay:{.2+i*.15}s">
<text x="24" y="40" font-size="17" font-weight="600" fill="{ACCENT}">{escape(r["name"])}</text>
<text x="24" y="66" font-size="13" fill="{MUTED}">{escape(desc[:60])}</text>
<circle cx="30" cy="96" r="5" fill="{ACCENT}"/>
<text x="42" y="100" font-size="12" fill="{FG}">{escape(r["language"] or "—")}</text>
<text x="140" y="100" font-size="12" fill="{MUTED}">★ {r["stargazers_count"]}</text></g>'''
        svg(410, 120, body, f"repo{i}.svg")
    return len(data)

hero()
tile("tile_build.svg", "Projets", "Ce que je construis", "🛠️", .8)
tile("tile_learn.svg", "Études", "Ynov Campus · Lyon", "🎓", 1.0)
tile("tile_contact.svg", "Contact", "Voir mon profil", "👋", 1.2)
contributions()
n = repos()

readme = f'''<div align="center">

<img src="./cards/hero.svg" width="100%" alt="{NAME}" />

<a href="https://github.com/{USER}?tab=repositories"><img src="./cards/tile_build.svg" width="32.5%" alt="Projets" /></a>
<a href="https://www.ynov.com/campus/lyon"><img src="./cards/tile_learn.svg" width="32.5%" alt="Études" /></a>
<a href="https://github.com/{USER}"><img src="./cards/tile_contact.svg" width="32.5%" alt="Contact" /></a>

<img src="./cards/activity.svg" width="100%" alt="Contributions" />

''' + "\n".join(f'<a href="https://github.com/{USER}"><img src="./cards/repo{i}.svg" width="49%" /></a>' for i in range(n)) + "\n\n</div>\n"
open(os.path.join(OUT, "..", "README.md"), "w", encoding="utf-8").write(readme)
print("ok")
