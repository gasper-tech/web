"""Build the Morning Doppio email from an issue JSON file.

Usage: python3 newsletter/build.py newsletter/issues/<file>.json [out.html]

The JSON shape is documented in newsletter/STYLE.md. Paragraph strings may
contain <b>, <i> and <mark>; <mark> becomes the sand highlight.

The look mirrors Gašper's website (Geist + Geist Mono, soft neutral ground,
large rounded cards, a sky-gradient hero, a sand-gradient feature card, mono
labels and a near-black closing pane). Values are literals because email
clients ignore CSS variables; gradients carry a solid bgcolor fallback.
"""
import json
import re
import sys
from html import escape
from urllib.parse import quote

# ── Site tokens ───────────────────────────────────────────────────────────────
SANS = "Geist,'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'Geist Mono',ui-monospace,Menlo,monospace"
GROUND, RIM, SURFACE, SURFACE2 = "#ebebe9", "#f7f7f6", "#e3e3e1", "#f4f4f3"
INK, INK_SOFT, INK_FAINT, LINE = "#141414", "#5d5d5b", "#9b9b98", "#d5d5d2"
NIGHT, NIGHT_INK, NIGHT_SOFT = "#121212", "#f2f2f0", "#a3a3a0"
SKY = "linear-gradient(160deg,#8fadcf 0%,#a9bdd6 38%,#d2d4da 70%,#d9d3cf 100%)"
SAND = "linear-gradient(180deg,#efe7d8 0%,#ddcdb0 55%,#c4b393 100%)"
SAND_INK, SAND_LABEL = "#1a160f", "#6a5d48"
HLBG = "#efe4cc"  # the site's sand, light, for highlights
NAME = "Morning Doppio"


def ask(topic, q):
    return "https://claude.ai/new?q=" + quote(f"From my newsletter {NAME} ({topic}): {q}")


def rich(html):
    html = re.sub(r"<mark>(.*?)</mark>",
                  rf'<span style="background-color:{HLBG};color:{INK};border-radius:6px;padding:1px 5px;">\1</span>',
                  html, flags=re.S)
    return html.replace("<b>", f'<b style="color:{INK};font-weight:500;">')


def mono(text, color=INK_SOFT, margin="0 0 12px"):
    return f'<div style="font:500 12px/1.4 {MONO};letter-spacing:-.005em;color:{color};margin:{margin};">{text}</div>'


def card(inner, bg, radius=24, pad="22px 22px", margin="6px 0 16px", border=""):
    b = f"border:1px solid {border};" if border else ""
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:{margin};"><tr>'
            f'<td bgcolor="{bg}" style="background-color:{bg};{b}border-radius:{radius}px;padding:{pad};">{inner}</td></tr></table>')


def h2(html):
    return f'<h2 style="font:500 27px/1.1 {SANS};letter-spacing:-.025em;color:{INK};margin:0 0 16px;">{html}</h2>'


def p(html, color=INK_SOFT, size=16):
    return f'<p style="font:400 {size}px/1.6 {SANS};color:{color};margin:0 0 14px;">{rich(html)}</p>'


def why(head, html):
    return card(mono(escape(head), INK_SOFT, "0 0 8px")
                + f'<div style="font:400 15px/1.6 {SANS};color:{INK};">{rich(html)}</div>', SURFACE)


def sources(prefix, links):
    if not links:
        return ""
    parts = [f'<a href="{escape(l["url"])}" style="color:{INK_SOFT};text-decoration:underline;">{escape(l["text"])}</a>' for l in links]
    return f'<p style="font:400 13px/1.55 {SANS};color:{INK_FAINT};margin:0 0 16px;">{escape(prefix)}: ' + " · ".join(parts) + "</p>"


def dig(topic, qs):
    if not qs:
        return ""
    items = "".join(
        f'<table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 0 8px;"><tr>'
        f'<td bgcolor="{GROUND}" style="background-color:{GROUND};border-radius:999px;padding:9px 16px;">'
        f'<a href="{ask(topic, q)}" style="font:400 14px/1.35 {SANS};color:{INK};text-decoration:none;"><span style="color:{INK};">{escape(q)}</span></a>'
        f'</td></tr></table>'
        for q in qs)
    return mono("Dig deeper", INK_FAINT, "6px 0 10px") + items


def tiles(rows, bg=SURFACE):
    """Stat tiles like the site's 'At a glance' row: big number, faint unit, small caption."""
    if not rows:
        return ""
    cells = "".join(
        f'<td bgcolor="{bg}" style="background-color:{bg};border-radius:24px;padding:16px 16px 14px;vertical-align:top;width:33%;">'
        f'{mono(escape(r.get("label", "")), INK_SOFT, "0 0 16px") if r.get("label") else ""}'
        f'<div style="font:500 24px/1.05 {SANS};letter-spacing:-.03em;color:{INK};">{r["n"]}</div>'
        f'<div style="font:400 12px/1.4 {SANS};color:{INK_FAINT};margin-top:6px;">{escape(r["t"])}</div></td>'
        for r in rows)
    return f'<table role="presentation" cellspacing="6" cellpadding="0" style="width:100%;margin:0 -6px 12px;border-collapse:separate;"><tr>{cells}</tr></table>'


def section(s):
    kind = f' · {escape(s["kind"])}' if s.get("kind") else ""
    out = [mono(escape(s["label"]) + kind)]
    if s.get("quote"):
        out.append(f'<div style="font:500 26px/1.2 {SANS};letter-spacing:-.025em;color:{INK};margin:0 0 12px;">“{escape(s["quote"])}”</div>')
        out.append(mono(escape(s.get("cite", "")), INK_FAINT, "0 0 16px"))
    if s.get("oneliner"):
        out.append(f'<div style="font:500 23px/1.25 {SANS};letter-spacing:-.02em;color:{INK};margin:0 0 12px;">{rich(s["oneliner"])}</div>')
        if s.get("cite"):
            out.append(mono(escape(s["cite"]), INK_FAINT, "0 0 16px"))
    if s.get("title"):
        out.append(h2(s["title"]))
    out.append(tiles([{"n": escape(r["n"]), "t": r["t"]} for r in s.get("figs", [])]))
    if s.get("previous_answer"):
        out.append(p("<b>Last puzzle's answer:</b> " + s["previous_answer"]))
    if s.get("puzzle"):
        hint = f'<p style="font:400 14px/1.55 {SANS};color:{INK_SOFT};margin:0;">{rich(s.get("hint", ""))}</p>' if s.get("hint") else ""
        out.append(card(p(s["puzzle"], INK) + hint, SURFACE2, 34, "24px 24px", border=LINE))
    for para in s.get("paragraphs", []):
        out.append(p(para))
    if s.get("bullets"):
        out.append(p("<br>".join("• " + b for b in s["bullets"])))
    if s.get("why"):
        out.append(why(s["why"].get("head", "Why it matters"), s["why"]["text"]))
    out.append(sources(s.get("sources_label", "Sources"), s.get("sources", [])))
    out.append(dig(s.get("topic", s["label"]), s.get("questions", [])))
    inner = "".join(out)
    return (f'<tr><td style="padding:0 0 12px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>'
            f'<td bgcolor="{RIM}" style="background-color:{RIM};border-radius:34px;padding:28px 22px 22px;">{inner}</td></tr></table></td></tr>')


def build(issue):
    zw = lambda t: re.sub(r"(\d)(\d)", "\\1&#8204;\\2", escape(t))  # stops mail apps turning dates into links
    pad = "&#8199;&#847;" * 12
    secs = issue["sections"]
    has_book = any(s.get("label", "").lower().startswith("book") for s in secs)
    glance = tiles([
        {"label": "Read", "n": f'{issue["read_min"]}<span style="color:{INK_FAINT};font-weight:400;"> min</span>', "t": "Over one coffee"},
        {"label": "Topics", "n": f'{len(secs)}', "t": "Money, science, ideas"},
        {"label": "Book" if has_book else "Puzzle", "n": f'1', "t": "Book of the week" if has_book else "Mind challenge"},
    ])
    hero = f'''<tr><td style="padding:0 0 12px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="#a9bdd6" style="background-color:#a9bdd6;background-image:{SKY};border-radius:44px 44px 34px 34px;padding:30px 26px 32px;">
{mono(f'Issue {issue["number"]:02d} · {zw(issue["date_label"])}', "rgba(255,255,255,.85)", "0 0 90px")}
<div style="font:500 46px/1.02 {SANS};letter-spacing:-.025em;color:#ffffff;margin:0;"><span style="font-weight:300;opacity:.78;">Morning</span> Doppio.</div>
<p style="font:400 17px/1.55 {SANS};color:rgba(255,255,255,.92);margin:16px 0 0;">The first double shot of your day. A few minutes that make you sharper, more curious and better company.</p>
</td></tr></table></td></tr>
<tr><td style="padding:0 0 6px;">{glance}</td></tr>
<tr><td style="padding:0 0 12px;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="#ddcdb0" style="background-color:#ddcdb0;background-image:{SAND};border-radius:34px;padding:24px 24px 26px;">
{mono("First sip", SAND_LABEL, "0 0 26px")}
<div style="font:500 23px/1.3 {SANS};letter-spacing:-.02em;color:{SAND_INK};">{escape(issue["first_sip"])}</div>
</td></tr></table></td></tr>'''
    footer = f'''<tr><td style="padding:0;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
<td bgcolor="{NIGHT}" style="background-color:{NIGHT};border-radius:34px;padding:28px 24px 30px;">
{mono(NAME, NIGHT_SOFT, "0 0 10px")}
<div style="font:500 24px/1.15 {SANS};letter-spacing:-.025em;color:{NIGHT_INK};margin:0 0 12px;"><span style="color:{NIGHT_SOFT};">See you</span><br>next Doppio.</div>
<p style="font:400 14px/1.6 {SANS};color:{NIGHT_SOFT};margin:0;">{escape(issue.get("footer", ""))} Tap any question under an item to go deeper with Claude.</p>
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
    print(f"{out} ({len(html)} bytes)\nSubject: Doppio #{issue['number']:02d} · {issue['subject_hook']}")
