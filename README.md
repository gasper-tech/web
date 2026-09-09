# Casa Orquídea — landing page

A single-property landing page for Casa Orquídea (El Herrojo Alto, Benahavís),
built as a Claude Design canvas document.

| File | What it is |
| --- | --- |
| `casa-orquidea.html` | The deliverable. Self-contained — open it in any browser, no server. Fonts, the hero image and the runtime are bundled in. |
| `src/casa-orquidea.dc.html` | The editable source. This is what you change; it also opens in the Claude Design canvas. |
| `tools/build.py` | Re-bundles the source into `casa-orquidea.html`. Run it after every edit. |

```sh
python3 tools/build.py
```

## Live preview

`preview/casa-orquidea-preview.html` is a hosted-friendly rendering of the same
page: identical markup, stylesheet and animations, but with the design runtime
removed and its four interactions (FAQ, gallery, form steps, tour poster)
rewritten in ~40 lines of vanilla JS. The runtime evaluates its logic with
`new Function`, which a host's Content-Security-Policy may forbid; the preview
has no such dependency, so it renders anywhere.

It is a preview, not the deliverable — `casa-orquidea.html` remains canonical.
Regenerate it after changing the page:

```sh
node tools/snapshot-preview.js   # drives Chromium, captures the hydrated DOM
python3 tools/make-preview.py    # assembles the standalone page
```

## Wiring up the tour video

The tour poster is the one thing still to connect. In the logic block at the
bottom of `src/casa-orquidea.dc.html`:

```js
static TOUR_URL = "";
```

Set that to the tour's URL and the poster opens it in a new tab. Left empty, the
poster sends the visitor to the enquiry form instead — so there is no play
button that does nothing either way. A new tab (rather than an embedded iframe)
keeps third-party video trackers off a page that collects personal data.

## Editing notes

The page is authored as inline styles so the canvas editor can round-trip it.
Behaviour — transitions, animations, hover/press states, media queries — lives
in the single `<style>` block in the `<helmet>`, because inline styles cannot
express any of those. Four runtime constraints are worth knowing before editing:

- **No `;` inside an inline style *value*.** The runtime splits the `style`
  attribute on `;`, so a `data:` URI with a parameter (`;base64,`, `;utf8,`)
  silently truncates. Select chevrons use a parameter-free, percent-encoded URI.
- **Don't follow `background-image` with the `background` shorthand** in the
  same inline style — the shorthand resets the image.
- **`class` does not work on `<image-slot>`** (or any custom element); the
  runtime renders it as a stray `classname` attribute. Target those by `id`.
- **Boolean attributes need a truthy string** — `required="required"`, not
  `required=""`, which React drops.

Hover styling is deliberately gated behind
`@media (hover: hover) and (pointer: fine)` so tapping a button on a phone does
not leave it stuck in its hover state.
