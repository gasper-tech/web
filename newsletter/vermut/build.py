"""Build the Vermut email (weekly local news) from an issue JSON file.

Usage: python3 newsletter/vermut/build.py newsletter/vermut/issues/<file>.json [out.html]

Same look and helpers as Morning Doppio (newsletter/build.py); only the hero,
the at-a-glance row, the "In one line" card and the footer differ. The JSON
shape and editorial rules are in newsletter/vermut/STYLE.md.
"""
import json
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import build as doppio  # noqa: E402
from build import (GROUND, INK_FAINT, MONO, NIGHT, NIGHT_INK, NIGHT_SOFT,  # noqa: E402
                   SANS, mono, section, tiles)

NAME = "Vermut"
HERO = "#b48a6c"   # warm terracotta, flat, white text
LINE_CARD = "#a9bdd6"  # Doppio's sky, used here for "In one line"
doppio.NAME = NAME  # dig-deeper links say "From my newsletter Vermut"


def build(issue):
    zw = lambda t: re.sub(r"(\d)(\d)", "\\1&#8204;\\2", escape(t))
    pad = "&#8199;&#847;" * 12
    secs = issue["sections"]
    for i, s in enumerate(secs, 1):
        s["label"] = f'{i:02d} · {s["label"]}'
    glance = tiles([
        {"label": "Read", "n": f'{issue["read_min"]}<span style="color:{INK_FAINT};font-weight:400;"> min</span>', "t": "Before the first drink"},
        {"label": "Stories", "n": f'{len(secs)}', "t": "That move the coast"},
        {"label": "Patch", "n": "Costa", "t": "Marbella to Spain"},
    ])
    hero = f'''<tr><td style="padding:0 0 12px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="{HERO}" style="background-color:{HERO};border-radius:44px 44px 34px 34px;padding:30px 26px 32px;">
{mono(f'Issue {issue["number"]:02d} · {zw(issue["date_label"])}', "rgba(255,255,255,.85)", "0 0 90px")}
<div style="font:500 46px/1.02 {SANS};letter-spacing:-.025em;color:#ffffff;margin:0;"><span style="font-weight:300;">Friday</span> Vermut.</div>
<p style="font:400 17px/1.55 {SANS};color:rgba(255,255,255,.92);margin:16px 0 0;">Ten things that changed on the coast this week. Property, plans, openings and the odd surprise, served at five.</p>
</td></tr></table></td></tr>
<tr><td style="padding:0 0 6px;">{glance}</td></tr>
<tr><td style="padding:0 0 12px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="{LINE_CARD}" style="background-color:{LINE_CARD};border-radius:34px;padding:24px 24px 28px;">
{mono("The week in one line", "rgba(255,255,255,.85)", "0 0 22px")}
<div style="font:500 23px/1.3 {SANS};letter-spacing:-.02em;color:#ffffff;">{escape(issue["one_line"])}</div>
</td></tr></table></td></tr>'''
    footer = f'''<tr><td style="padding:0;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="{NIGHT}" style="background-color:{NIGHT};border-radius:34px;padding:28px 24px 30px;">
{mono(NAME, NIGHT_SOFT, "0 0 10px")}
<div style="font:500 24px/1.15 {SANS};letter-spacing:-.025em;color:{NIGHT_INK};margin:0 0 12px;"><span style="color:{NIGHT_SOFT};">Salud.</span><br>See you next Friday.</div>
<p style="font:400 14px/1.6 {SANS};color:{NIGHT_SOFT};margin:0;">{escape(issue.get("footer", ""))} Tap any question under a story to go deeper with Claude.</p>
</td></tr></table></td></tr>'''
    body = "".join(section(s) for s in secs)
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300..600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background:{GROUND};">
<div style="display:none;max-height:0;overflow:hidden;">{escape(issue["preheader"])}{pad}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:{GROUND};"><tr><td align="center" style="padding:14px 10px 24px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;">
{hero}
{body}
{footer}
</table></td></tr></table></body></html>'''


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.json$", ".html", src)
    issue = json.load(open(src))
    html = build(issue)
    open(out, "w").write(html)
    print(f"{out} ({len(html)} bytes)\nSubject: Vermut #{issue['number']:02d} · {issue['subject_hook']}")
