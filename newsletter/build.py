"""Build the Morning Doppio email from an issue JSON file.

Usage: python3 newsletter/build.py newsletter/issues/<file>.json [out.html]

The JSON shape is documented in newsletter/STYLE.md. Paragraph strings may
contain <b>, <i> and <mark>; <mark> becomes the yellow highlight.
"""
import json
import re
import sys
from html import escape
from urllib.parse import quote

F = "Inter,Helvetica,Arial,sans-serif"
INK, MUTED, LINE, HL = "#1a1a1a", "#6b6b6b", "#dadada", "#7d6c2c"
HLBG = "#ebdfb3"  # the dark yellow at low opacity, flattened for email clients
CHIP = "#eeede9"
NAME = "Morning Doppio"


def ask(topic, q):
    return "https://claude.ai/new?q=" + quote(f"From my newsletter {NAME} ({topic}): {q}")


def rich(html):
    return re.sub(r"<mark>(.*?)</mark>",
                  rf'<span style="background-color:{HLBG};border-radius:3px;padding:1px 3px;">\1</span>',
                  html, flags=re.S)


def label(text, kind=""):
    k = f' <span style="color:{MUTED};letter-spacing:.06em;">· {escape(kind)}</span>' if kind else ""
    return f'<div style="font:600 11px/1.4 {F};letter-spacing:.12em;text-transform:uppercase;color:{HL};margin:0 0 8px;">{escape(text)}{k}</div>'


def h2(html):
    return f'<h2 style="font:700 22px/1.2 {F};letter-spacing:-.02em;color:{INK};margin:0 0 10px;">{html}</h2>'


def p(html):
    return f'<p style="font:400 16px/1.6 {F};color:{INK};margin:0 0 12px;">{rich(html)}</p>'


def why(head, html):
    return (f'<div style="border-left:2px solid {HL};padding:2px 0 2px 14px;margin:4px 0 12px;font:400 15px/1.55 {F};color:{INK};">'
            f'<div style="font:600 10px/1.4 {F};letter-spacing:.1em;text-transform:uppercase;color:{HL};">{escape(head)}</div>{rich(html)}</div>')


def small(html):
    return f'<p style="font:400 13px/1.5 {F};color:{MUTED};margin:0 0 10px;">{html}</p>'


def sources(prefix, links):
    if not links:
        return ""
    parts = [f'<a href="{escape(l["url"])}" style="color:{INK};text-decoration:underline;">{escape(l["text"])}</a>' for l in links]
    return small(f"{escape(prefix)}: " + " · ".join(parts))


def dig(topic, qs):
    if not qs:
        return ""
    items = "".join(
        f'<table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 0 8px;"><tr>'
        f'<td bgcolor="{CHIP}" style="background-color:{CHIP};border-radius:999px;padding:10px 16px;">'
        f'<a href="{ask(topic, q)}" style="font:500 15px/1.3 {F};color:{INK};text-decoration:none;"><span style="color:{INK};">{escape(q)}</span></a>'
        f'</td></tr></table>'
        for q in qs)
    return f'<div style="font:600 10px/1.4 {F};letter-spacing:.1em;text-transform:uppercase;color:{MUTED};margin:6px 0 8px;">Dig deeper</div>{items}'


def figs(rows):
    if not rows:
        return ""
    cells = "".join(
        f'<td style="background:#ffffff;border:1px solid {LINE};border-radius:4px;padding:9px 11px;vertical-align:top;width:33%;">'
        f'<div style="font:700 16px/1.3 {F};color:{INK};">{escape(r["n"])}</div><div style="font:400 12px/1.35 {F};color:{MUTED};">{escape(r["t"])}</div></td>'
        for r in rows)
    return f'<table role="presentation" cellspacing="6" cellpadding="0" style="width:100%;margin:0 -6px 8px;border-collapse:separate;"><tr>{cells}</tr></table>'


def section(s):
    out = [label(s["label"], s.get("kind", ""))]
    if s.get("quote"):
        out.append(f'<div style="font:700 24px/1.25 {F};letter-spacing:-.02em;color:{INK};margin:0 0 6px;">“{escape(s["quote"])}”</div>')
        out.append(small(escape(s.get("cite", ""))))
    if s.get("oneliner"):
        out.append(f'<div style="font:700 19px/1.35 {F};letter-spacing:-.015em;color:{INK};margin:0 0 6px;">{rich(s["oneliner"])}</div>')
        if s.get("cite"):
            out.append(small(escape(s["cite"])))
    if s.get("title"):
        out.append(h2(s["title"]))
    out.append(figs(s.get("figs")))
    if s.get("puzzle"):
        hint = f'<p style="font:400 14px/1.5 {F};color:{MUTED};margin:0;">{rich(s.get("hint", ""))}</p>' if s.get("hint") else ""
        out.append(f'<div style="background:#ffffff;border:1px solid {LINE};border-radius:4px;padding:16px;margin:0 0 12px;">{p(s["puzzle"])}{hint}</div>')
    for para in s.get("paragraphs", []):
        out.append(p(para))
    if s.get("bullets"):
        out.append(p("<br>".join("• " + b for b in s["bullets"])))
    if s.get("why"):
        out.append(why(s["why"].get("head", "Why it matters"), s["why"]["text"]))
    out.append(sources(s.get("sources_label", "Sources"), s.get("sources", [])))
    out.append(dig(s.get("topic", s["label"]), s.get("questions", [])))
    return f'<tr><td style="padding:0 0 34px;">{"".join(out)}</td></tr>'


def build(issue):
    zw = lambda t: re.sub(r"(\d)(\d)", "\\1&#8204;\\2", escape(t))  # stops mail apps turning dates into links
    pad = "&#8199;&#847;" * 12
    body = "".join(section(s) for s in issue["sections"])
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background:#f6f6f6;">
<div style="display:none;max-height:0;overflow:hidden;">{escape(issue["preheader"])}{pad}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f6f6f6;"><tr><td align="center" style="padding:28px 16px 40px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;">
<tr><td style="padding:0 0 22px;border-bottom:1px solid {LINE};">
<div style="font:500 12px/1.5 {F};color:{MUTED};letter-spacing:.04em;">Issue {issue["number"]:02d} · {zw(issue["date_label"])} · About {issue["read_min"]} min</div>
<div style="font:800 40px/1.05 {F};letter-spacing:-.04em;color:#111111;margin:6px 0 12px;">{NAME}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:0 0 14px;"><tr><td bgcolor="{HLBG}" style="background-color:{HLBG};border-radius:4px;padding:12px 15px;">
<div style="font:600 10px/1.4 {F};letter-spacing:.12em;text-transform:uppercase;color:{HL};">First sip</div>
<div style="font:600 18px/1.4 {F};letter-spacing:-.01em;color:{INK};">{escape(issue["first_sip"])}</div>
</td></tr></table>
<p style="font:400 16px/1.55 {F};color:{MUTED};margin:0 0 14px;"><b style="color:{INK};font-weight:600;">The first double shot of your day.</b> A few minutes that make you sharper, more curious and better company. One dose at a time, you build the person you want to be.</p>
<p style="font:400 13px/1.5 {F};color:{MUTED};margin:0;">Tap any question under an item to ask Claude.</p>
</td></tr>
<tr><td style="height:30px;"></td></tr>
{body}
<tr><td style="border-top:1px solid {LINE};padding:18px 0 0;font:400 13px/1.55 {F};color:{MUTED};">
{escape(issue.get("footer", ""))}
</td></tr>
</table></td></tr></table></body></html>'''


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.json$", ".html", src)
    issue = json.load(open(src))
    html = build(issue)
    open(out, "w").write(html)
    print(f"{out} ({len(html)} bytes)\nSubject: Doppio #{issue['number']:02d} · {issue['subject_hook']}")
