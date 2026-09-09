#!/usr/bin/env python3
"""Build a dependency-free preview of the landing page.

The shipped file (casa-orquidea.html) runs a React-based design runtime that
evaluates its logic with `new Function`. A hosted page may run under a CSP that
forbids eval, so this rebuilds the same page as plain HTML + CSS + ~40 lines of
vanilla JS. Markup, stylesheet and animations are the real ones, snapshotted
from the running page; only the four interactions are re-implemented.
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / '.preview-cache'
DEST = ROOT / 'preview' / 'casa-orquidea-preview.html'

snap = json.load(open(CACHE / 'snapshot.json'))
hero = (CACHE / 'hero_uri.txt').read_text().strip()

styles = snap['shell']['styles']
shell  = snap['shell']['html']

def strip_tpl(h):
    return re.sub(r'\s*data-dc-tpl="\d+"', '', h)

def pick(html, pattern):
    m = re.search(pattern, html, re.S)
    assert m, pattern
    return m.group(0)

def element(html, opening):
    """Slice out one element by walking div depth from its opening tag."""
    start = html.index(opening)
    depth, i = 0, start
    while True:
        m = re.compile(r'</?div\b').search(html, i)
        depth += 1 if m.group(0) == '<div' else -1
        i = m.end()
        if depth == 0:
            return html[start:html.index('>', i) + 1]

step1 = pick(strip_tpl(snap['step1']['form']), r'<form class="step".*?</form>')
step2 = pick(strip_tpl(snap['step2']['form']), r'<form class="step".*?</form>')
thanks = element(strip_tpl(snap['thanks']['form']), '<div class="thanks"')

shell = strip_tpl(shell)

# ── image-slot is a custom element backed by shadow DOM; swap in real markup ──
def slot(m):
    tag = m.group(0)
    sid = re.search(r'id="([^"]+)"', tag).group(1)
    ph  = re.search(r'placeholder="([^"]*)"', tag)
    style = re.search(r'style="([^"]*)"', tag)
    style = style.group(1) if style else 'width:100%;height:100%;'
    if sid == 'orq-hero':
        return (f'<img alt="Casa Orquídea seen from the terrace at dusk" src="{hero}" '
                f'style="{style}object-fit:cover;">')
    label = ph.group(1) if ph else ''
    return (f'<div class="slot" style="{style}" role="img" aria-label="Photo placeholder: {label}">'
            f'<span class="slot-ico" aria-hidden="true"></span><span>{label}</span></div>')

shell = re.sub(r'<image-slot[^>]*></image-slot>', slot, shell)
assert '<image-slot' not in shell and 'blob:' not in shell

# ── rebuild the booking card so all three states are present in one document ──
card_open = re.search(r'<div class="pad-card reveal"[^>]*>', shell).group(0)
start = shell.index(card_open)
depth, i = 0, start
while True:                                   # walk to the card's matching </div>
    m = re.compile(r'</?div\b').search(shell, i)
    depth += 1 if m.group(0) == '<div' else -1
    i = m.end()
    if depth == 0:
        break
card_end = shell.index('</div>', i - 6) + 6

header = '''
        <div class="form-head" style="display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin-bottom:14px;">
          <div id="form-title" style="font-weight:600;font-size:24px;letter-spacing:-.018em;color:#1d1d1f;">Book a Viewing</div>
          <div id="step-label" class="step-label" style="font-weight:400;font-size:13px;letter-spacing:.01em;color:#6e6e73;white-space:nowrap;">Step 1 of 2 — your search · takes 30 seconds</div>
        </div>
        <div aria-hidden="true" style="display:flex;gap:6px;margin-bottom:26px;">
          <span style="height:3px;flex:1;border-radius:980px;background:#1d1d1f;"></span>
          <span id="track2" style="height:3px;flex:1;border-radius:980px;background:#e8e8ed;transition:background-color 300ms ease;"></span>
        </div>'''

note = ('<div id="privacy-note" style="margin-top:22px;font-weight:400;font-size:13px;line-height:1.5;'
        'letter-spacing:.005em;color:#6e6e73;">Strictly confidential. Your details are used only to arrange '
        'this conversation — no newsletters, no sharing of your data.</div>')

card = (card_open + '<div id="form-live">' + header
        + step1.replace('<form class="step"', '<form id="step1" class="step"', 1)
        + step2.replace('<form class="step"', '<form id="step2" class="step" hidden', 1)
        + note + '</div>' + thanks.replace('<div class="thanks"', '<div id="thanks" class="thanks" hidden', 1)
        + '</div>')
shell = shell[:start] + card + shell[card_end:]

extra = '''
  /* preview only: stands in for the photos you drop into the real file */
  .slot{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px;
         background:#f0f0f2; color:#86868b; font-size:13px; text-align:center; padding:16px; }
  .slot-ico{ width:26px; height:22px; border:1.5px solid currentColor; border-radius:4px; opacity:.7; }
  #step1[hidden],#step2[hidden],#thanks[hidden]{ display:none; }
  .tour-fig .slot{ justify-content:flex-end; padding-bottom:20px; }
'''

js = '''
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  // FAQ — one open at a time, matching the shipped behaviour
  $$('[aria-controls^="faq-a-"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      $$('[aria-controls^="faq-a-"]').forEach(function (b) {
        b.setAttribute('aria-expanded', 'false');
        $('#' + b.getAttribute('aria-controls')).dataset.open = 'false';
        $('.mark', b).dataset.open = 'false';
      });
      if (!open) {
        btn.setAttribute('aria-expanded', 'true');
        $('#' + btn.getAttribute('aria-controls')).dataset.open = 'true';
        $('.mark', btn).dataset.open = 'true';
      }
    });
  });

  var gal = $('[aria-controls="orq-gallery-more"]');
  gal.addEventListener('click', function () {
    var open = gal.getAttribute('aria-expanded') !== 'true';
    gal.setAttribute('aria-expanded', String(open));
    $('#orq-gallery-more').dataset.open = String(open);
    gal.textContent = open ? 'Hide photos' : 'View all photos';
  });

  // Both forms are real, so `submit` only fires once the browser is satisfied
  var s1 = $('#step1'), s2 = $('#step2'), thanks = $('#thanks');
  function show(step) {
    s1.hidden = step !== 1; s2.hidden = step !== 2;
    $('#form-title').textContent = step === 1 ? 'Book a Viewing' : 'Where can I reach you?';
    $('#step-label').textContent = step === 1
      ? 'Step 1 of 2 — your search · takes 30 seconds'
      : "Step 2 of 2 — I'll be in touch within 24 hours";
    $('#track2').style.background = step === 2 ? '#1d1d1f' : '#e8e8ed';
    (step === 1 ? s1 : s2).classList.remove('step');
    void (step === 1 ? s1 : s2).offsetWidth;      // restart the entrance
    (step === 1 ? s1 : s2).classList.add('step');
  }
  s1.addEventListener('submit', function (e) { e.preventDefault(); show(2); });
  s2.addEventListener('submit', function (e) {
    e.preventDefault();
    $('#form-live').hidden = true; thanks.hidden = false;
  });
  $$('button', s2).forEach(function (b) {
    if (b.type === 'button') b.addEventListener('click', function () { show(1); });
  });

  // No tour URL yet, so the poster takes an interested visitor to the enquiry
  var tour = $('.tour-fig');
  if (tour) tour.addEventListener('click', function () {
    $('#viewing').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
'''

out = ('<title>Casa Orquídea · El Herrojo Alto, Benahavís — €19.880.000</title>\n'
       '<meta name="description" content="Casa Orquídea — the highest plot in El Herrojo Alto, '
       'Benahavís. 280° of sea and mountains, 8 bedrooms, 2.309 m² built, delivered fully furnished.">\n'
       f'<style>\n{styles}\n{extra}</style>\n{shell}\n<script>{js}</script>\n')

DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text(out, encoding='utf-8')
print(f'{DEST.relative_to(ROOT)}: {len(out):,} bytes')
markup = re.sub(r'(?is)<(script|style)\b.*?</\1>', '', out)
for bad in ('<!DOCTYPE', '<html', '<head>', '<body>', 'blob:', 'image-slot', '{{', 'sc-if', 'sc-for'):
    assert bad not in markup, bad
print('clean')
