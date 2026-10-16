# Morning Doppio: editorial brief

A personal newsletter for one reader, sent Tuesday and Friday at 07:00 Ljubljana time.
Goal: make the reader sharper, more curious and better company. General knowledge first;
luxury is an occasional topic, never the majority.

Reference issue (approved look, tone and depth): `issues/00-sample.json`.
Build the email with `python3 newsletter/build.py newsletter/issues/NN-YYYY-MM-DD.json`.

## Every issue

- **Subject:** `Doppio #NN · <hook>`. The hook names the strongest topic as a curiosity hook,
  max ~38 characters, no spoilers. Never use the quote as the subject.
- **Preview text (`preheader`):** "Plus: …" teasing two or three other sections. Do not reveal the quote.
- **First sip:** one short opener. Rotate: witty line, motivation, clean joke, fact with attitude.
  Confident, a little manly, never cheesy. Never repeat one from an earlier issue.
- **Length:** about 7–8 minutes, 9–11 sections.
- **Highlights:** one `<mark>` per section on the single most important sentence.
- **Dig deeper:** 2–3 questions per section, written so they make sense on their own
  (they open a fresh Claude chat), e.g. "How do experts spot a fake painting?"

## Sections

Every issue:
- Markets & Macro (this week's news, explained plainly, with the "why")
- One world or business news story worth understanding
- AI Build: one practical idea, not AI news. Rotate: Simplify (automate something in your life),
  Build (small app or script), Learn (a tool or skill worth trying), Sell (product idea with an honest
  take on competition). Include the three tiles (difficulty, time, running cost), how to build it at
  2–3 levels, and a "Could you sell it?" box.
- Medicine & health
- Philosophy: one quote from an old philosopher, with context, exact source citation
- Mind Challenge: rotating logic / lateral / math / wordplay, medium difficulty. The answer to the
  previous puzzle goes in the next issue, in the section's `previous_answer` field.
- One-liner for dinner: a surprising, verifiable fact

Rotating explainers ("what X means", timeless, plain English), 2–3 per issue:
history (empires, events, how fortunes were made), science & space, geopolitics, psychology &
mental models, language & word origins, how things work, and occasionally art, wine, watches, cars
(at most one luxury/collecting item per issue).

Fridays only: **Book of the week**, any field, with a "Read it if" line.

## Tone

Light, warm, plain English, like a well-read friend. Short sentences. A little wit. "Why it matters"
lines explain the general insight; no sales tactics, no client angles.

## Research standard (non-negotiable)

1. For each section, consider 5–10 candidate stories or ideas and pick the most surprising and useful.
2. Research deeply: several searches per topic, prefer primary sources (the study, the company
   report, the central bank statement) over news summaries.
3. Every number and factual claim must be confirmed by at least two independent sources. If they
   disagree, use the careful version or leave it out. No invented figures, quotes or citations.
4. Quotes must be checked against a real source; give work and chapter/letter number.
5. Read enough background that "Why it matters" is a real insight.
6. A final editor pass over the whole issue: accuracy, clarity, tone, no overlap between sections,
   no repeats from earlier issues in `issues/`.
7. If a news topic cannot meet the standard, replace it with a timeless explainer.
