#!/usr/bin/env python3
"""Rebuild casa-orquidea.html (the self-contained bundle) from src/casa-orquidea.dc.html.

The bundle is a self-extracting shell: a loader, an asset manifest (fonts, the
hero image, the dc-runtime), and the page itself stored as a JSON string inside
<script type="__bundler/template">. Only that template line changes when the
page is edited, so this script swaps it in place and leaves the shell alone.

    python3 tools/build.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "casa-orquidea.html"
SOURCE = ROOT / "src" / "casa-orquidea.dc.html"


def main() -> int:
    page = SOURCE.read_text(encoding="utf-8")
    lines = BUNDLE.read_text(encoding="utf-8").split("\n")

    open_tag = '<script type="__bundler/template">'
    idx = next((i for i, l in enumerate(lines) if open_tag in l), None)
    if idx is None:
        sys.exit("could not find the bundler template tag in " + str(BUNDLE))
    tpl = idx + 1

    # `</` must be escaped or the literal `</script>` inside the JSON string
    # would close the surrounding <script> element during HTML parsing.
    encoded = json.dumps(page, ensure_ascii=False).replace("</", "<\\u002F")
    assert json.loads(encoded) == page

    lines[tpl] = "  " + encoded
    BUNDLE.write_text("\n".join(lines), encoding="utf-8")
    print(f"rebuilt {BUNDLE.name} ({len(page):,} page bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
