"""Build the Morning Doppio email from an issue JSON file.

Usage: python3 newsletter/build.py newsletter/issues/<file>.json [out.html]

The JSON shape is documented in newsletter/STYLE.md. Paragraph strings may
contain <b>, <i> and <mark>; <mark> becomes the sand highlight.

The look follows the site's brand sheet (src/brand.css): Hanken Grotesk light
for display type, the reader's system face for everything small, Apple-style
greys, one warm sand accent, pill shapes and soft surface cards. Values are
copied here as literals because email clients ignore CSS variables.
"""
import json
import re
import sys
from html import escape
from urllib.parse import quote

# ── Brand tokens (from src/brand.css) ─────────────────────────────────────────
DISPLAY = "'Hanken Grotesk',Helvetica,Arial,sans-serif"
UI = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
INK, INK2, INK3, INK4 = "#1d1d1f", "#424245", "#6e6e73", "#86868b"
ON_DARK, ON_DARK3 = "#f5f5f7", "#a1a1a6"
SURFACE, DARK = "#f5f5f7", "#1d1d1f"
LINE_SOFT = "#e8e8ed"
SAND, SAND_DEEP = "#a99f89", "#8a8069"
HLBG = "#ebe6dc"  # sand at low opacity, flattened for email clients
NAME = "Morning Doppio"


def ask(topic, q):
    return "https://claude.ai/new?q=" + quote(f"From my newsletter {NAME} ({topic}): {q}")


def rich(html):
    html = re.sub(r"<mark>(.*?)</mark>",
                  rf'<span style="background-color:{HLBG};color:{INK};border-radius:4px;padding:1px 4px;">\1</span>',
                  html, flags=re.S)
    return html.replace("<b>", f'<b style="color:{INK};font-weight:600;">')


def caps(text, color=INK3, margin="0 0 10px"):
    return f'<div style="font:500 11px/1.4 {UI};letter-spacing:.14em;text-transform:uppercase;color:{color};margin:{margin};">{text}</div>'


def label(text, kind=""):
    k = f'<span style="color:{INK4};"> · {escape(kind)}</span>' if kind else ""
    return caps(escape(text) + k, SAND_DEEP, "0 0 12px")


def h2(html):
    return f'<h2 style="font:300 28px/1.12 {DISPLAY};letter-spacing:-.025em;color:{INK};margin:0 0 14px;">{html}</h2>'


def p(html, color=INK2):
    return f'<p style="font:400 16px/1.6 {UI};color:{color};margin:0 0 14px;">{rich(html)}</p>'


def card(inner, bg=SURFACE, radius=12, pad="16px 18px", margin="4px 0 14px"):
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:{margin};"><tr>'
            f'<td bgcolor="{bg}" style="background-color:{bg};border-radius:{radius}px;padding:{pad};">{inner}</td></tr></table>')


def why(head, html):
    return card(caps(escape(head), SAND_DEEP, "0 0 6px")
                + f'<div style="font:400 15px/1.55 {UI};color:{INK};">{rich(html)}</div>')


def small(html):
    return f'<p style="font:400 13px/1.5 {UI};color:{INK3};margin:0 0 14px;">{html}</p>'


def sources(prefix, links):
    if not links:
        return ""
    parts = [f'<a href="{escape(l["url"])}" style="color:{INK2};text-decoration:underline;">{escape(l["text"])}</a>' for l in links]
    return small(f"{escape(prefix)}: " + " · ".join(parts))


def dig(topic, qs):
    if not qs:
        return ""
    items = "".join(
        f'<table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 0 8px;"><tr>'
        f'<td bgcolor="{SURFACE}" style="background-color:{SURFACE};border-radius:980px;padding:11px 18px;">'
        f'<a href="{ask(topic, q)}" style="font:400 15px/1.35 {UI};color:{INK};text-decoration:none;"><span style="color:{INK};">{escape(q)}</span></a>'
        f'</td></tr></table>'
        for q in qs)
    return caps("Dig deeper", INK3, "6px 0 10px") + items


def figs(rows):
    if not rows:
        return ""
    cells = "".join(
        f'<td bgcolor="{SURFACE}" style="background-color:{SURFACE};border-radius:14px;padding:12px 14px;vertical-align:top;width:33%;">'
        f'<div style="font:300 22px/1.2 {DISPLAY};letter-spacing:-.014em;color:{INK};">{escape(r["n"])}</div>'
        f'<div style="font:400 12px/1.4 {UI};color:{INK3};margin-top:2px;">{escape(r["t"])}</div></td>'
        for r in rows)
    return f'<table role="presentation" cellspacing="6" cellpadding="0" style="width:100%;margin:0 -6px 10px;border-collapse:separate;"><tr>{cells}</tr></table>'


def section(s, first=False):
    out = [label(s["label"], s.get("kind", ""))]
    if s.get("quote"):
        out.append(f'<div style="font:300 30px/1.15 {DISPLAY};letter-spacing:-.025em;color:{INK};margin:0 0 10px;">“{escape(s["quote"])}”</div>')
        out.append(small(escape(s.get("cite", ""))))
    if s.get("oneliner"):
        out.append(f'<div style="font:300 25px/1.2 {DISPLAY};letter-spacing:-.02em;color:{INK};margin:0 0 10px;">{rich(s["oneliner"])}</div>')
        if s.get("cite"):
            out.append(small(escape(s["cite"])))
    if s.get("title"):
        out.append(h2(s["title"]))
    out.append(figs(s.get("figs")))
    if s.get("previous_answer"):
        out.append(p("<b>Last puzzle's answer:</b> " + s["previous_answer"]))
    if s.get("puzzle"):
        hint = f'<p style="font:400 14px/1.5 {UI};color:{INK3};margin:0;">{rich(s.get("hint", ""))}</p>' if s.get("hint") else ""
        out.append(card(p(s["puzzle"], INK) + hint, radius=20, pad="20px 22px"))
    for para in s.get("paragraphs", []):
        out.append(p(para))
    if s.get("bullets"):
        out.append(p("<br>".join("• " + b for b in s["bullets"])))
    if s.get("why"):
        out.append(why(s["why"].get("head", "Why it matters"), s["why"]["text"]))
    out.append(sources(s.get("sources_label", "Sources"), s.get("sources", [])))
    out.append(dig(s.get("topic", s["label"]), s.get("questions", [])))
    border = "" if first else f"border-top:1px solid {LINE_SOFT};"
    return f'<tr><td style="{border}padding:36px 0 30px;">{"".join(out)}</td></tr>'


def build(issue):
    zw = lambda t: re.sub(r"(\d)(\d)", "\\1&#8204;\\2", escape(t))  # stops mail apps turning dates into links
    pad = "&#8199;&#847;" * 12
    body = "".join(section(s, i == 0) for i, s in enumerate(issue["sections"]))
    first_sip = card(
        caps("First sip", SAND, "0 0 8px")
        + f'<div style="font:300 22px/1.3 {DISPLAY};letter-spacing:-.014em;color:{ON_DARK};">{escape(issue["first_sip"])}</div>',
        bg=DARK, radius=20, pad="22px 24px", margin="0 0 20px")
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400;500;600&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background:#ffffff;">
<div style="display:none;max-height:0;overflow:hidden;">{escape(issue["preheader"])}{pad}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff;"><tr><td align="center" style="padding:32px 20px 48px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;">
<tr><td style="padding:0 0 8px;">
{caps(f'Issue {issue["number"]:02d} · {zw(issue["date_label"])} · {issue["read_min"]} min read', INK3, "0 0 14px")}
<div style="font:300 46px/1.04 {DISPLAY};letter-spacing:-.028em;color:{INK};margin:0 0 16px;">{NAME}</div>
<p style="font:400 17px/1.55 {UI};color:{INK2};margin:0 0 22px;"><b style="color:{INK};font-weight:600;">The first double shot of your day.</b> A few minutes that make you sharper, more curious and better company. One dose at a time, you build the person you want to be.</p>
{first_sip}
<p style="font:400 13px/1.5 {UI};color:{INK3};margin:0 0 4px;">Tap any question under an item to ask Claude.</p>
</td></tr>
{body}
<tr><td style="border-top:1px solid {LINE_SOFT};padding:22px 0 0;">
{caps(NAME, INK4, "0 0 8px")}
<p style="font:400 13px/1.55 {UI};color:{INK3};margin:0;">{escape(issue.get("footer", ""))}</p>
</td></tr>
</table></td></tr></table></body></html>'''


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.json$", ".html", src)
    issue = json.load(open(src))
    html = build(issue)
    open(out, "w").write(html)
    print(f"{out} ({len(html)} bytes)\nSubject: Doppio #{issue['number']:02d} · {issue['subject_hook']}")
