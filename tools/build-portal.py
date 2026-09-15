#!/usr/bin/env python3
"""Inline src/brand.css into src/portal-home.html -> preview/portal-home.html.

A hosted artifact has no external stylesheet of its own to link to, and the
wrapper supplies <head>/<body>, so this inlines the token sheet and strips the
document scaffolding.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'portal-home.html'
DEST = ROOT / 'preview' / 'portal-home.html'

html = SRC.read_text(encoding='utf-8')
tokens = (ROOT / 'src' / 'brand.css').read_text(encoding='utf-8')

html = html.replace('<link rel="stylesheet" href="brand.css">',
                    '<style>\n' + tokens + '\n</style>')
assert 'href="brand.css"' not in html, 'brand.css link not inlined'

head = html[html.index('<head>') + 6:html.index('</head>')]
body = html[html.index('<body>') + 6:html.rindex('</body>')]
head = re.sub(r'<meta charset[^>]*>|<meta name="viewport"[^>]*>', '', head)

out = head.strip() + '\n' + body.strip() + '\n'
for bad in ('<!doctype', '<html', '<body>', '</head>'):
    assert bad not in re.sub(r'(?is)<(script|style)\b.*?</\1>', '', out).lower(), bad

DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text(out, encoding='utf-8')
print(f'{DEST.relative_to(ROOT)}: {len(out):,} bytes')
