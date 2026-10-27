# Vermut: editorial brief

Weekly local-news letter for one reader (Gašper, who works in Marbella prime real estate at Drumelia).
Sent **Fridays 17:00 Spain time** to gasper@drumelia.com from welcome@gasperplahutnik.com.
Issue #01 went out Tuesday 27 Oct 2026 as a one-off launch.

Look: identical system to Morning Doppio (`newsletter/build.py` helpers, Geist, rounded cards).
Hero is flat terracotta `#b48a6c` with white text; "The week in one line" card is Doppio's sky `#a9bdd6`.
Build: `python3 newsletter/vermut/build.py newsletter/vermut/issues/NN-YYYY-MM-DD.json`.

## Every issue

- **Exactly 10 stories**, news from the past week (Fri to Fri) about Marbella, the Costa del Sol,
  or Spain when it affects the area: real estate, planning, new openings, projects, infrastructure,
  events, tax and law. No fixed sections; order by importance to someone in Marbella property.
- Mix to aim for: 3–4 property/planning, 2 projects or openings, 1–2 Spain-level, 1 infrastructure
  or transport, and the last story is always **What's on** (dated bullets for the coming week).
- **Subject:** `Vermut #NN · <hook>`, hook ≤38 chars, curiosity not spoiler.
- **Preheader:** "Plus: …" naming two or three other stories.
- **one_line:** the week in one sentence.
- Each story: `label` (short topic), `kind`, `title`, 2 short paragraphs, one `<mark>` on the key
  sentence, optional `figs` (3 stat tiles), a `why` box headed "What it means here" (the local,
  practical angle: prices, access, buyers, rentals), 2–3 linked sources, 2 standalone Dig-deeper questions.
- Length ~7 minutes. Plain English, light, no sales tone.

## Research standard

Same as Morning Doppio: several searches per story, prefer primary or local sources (Ayuntamiento de
Marbella, Junta, BOE/BOJA, Marbella Directo, La Noción, Sur, Olive Press, Euro Weekly News, idealista,
El Español Málaga). Every figure confirmed by two sources or stated carefully; nothing invented.
Do not run crime stories unless they change something for residents (security, laws).
Never repeat a story from an earlier issue unless there is a real new development; check `issues/`.
