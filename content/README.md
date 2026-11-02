# Guide content files

One JSON file per topic, all five languages inside: `content/<topic-id>.json`. `scripts/build.py` turns every file into
`/guides/<slug>/` (en) and `/<lang>/<guides_path>/<slug>/` (de `ratgeber`, fr `guides`, it `guide`, es `guias`).
Check one file: `python3 scripts/build.py --check content/<topic-id>.json` (no ERROR lines = good). Topic plan: `content/PLAN.md`.

```json
{
  "updated": "2026-11-02",
  "slugs": { "en": "ski-fitness-plan", "de": "skigymnastik-plan", "fr": "preparation-physique-ski", "it": "preparazione-atletica-sci", "es": "preparacion-fisica-esqui" },
  "langs": {
    "en": {
      "title": "50-60 chars, primary local keyword near the front (no brand, build appends nothing)",
      "description": "120-160 chars, honest promise of what the page answers, contains the keyword.",
      "headline": "H1 of the page",
      "lede": "2-3 sentence plain-text direct answer to the search intent.",
      "body_html": "<h2>...</h2><p>...</p>",
      "faq": [ { "q": "Question?", "a": "Plain-text answer, 1-3 sentences." } ],
      "sources": [ { "label": "Author/Org. Title. Journal/Site, year.", "url": "https://..." } ]
    },
    "de": {}, "fr": {}, "it": {}, "es": {}
  }
}
```

Rules (`--check` enforces ERROR, warns WARN):

- Slugs: lowercase ascii, digits, hyphens; local keyword in the slug.
- `body_html` tags: h2, h3, p, ul, ol, li, strong, em, a, br, sup, table/thead/tbody/tr/th/td (wrap tables in `<div class="table-scroll">`). No h1, no inline styles, no classes except `table-scroll`.
- Links to another guide: `href="guide:<topic-id>"` (build resolves to that guide's URL in the same language). Home: `href="/"`. App Store: `href="app"`. No other internal URLs.
- 1000-1600 body words per language, 4-6 FAQ items, at least 3 sources with real URLs you have opened. Cite inline with `<sup>[n]</sup>` in source order.
- Translations are adaptive, not literal: native phrasing, local keyword in title/H1/slug, local examples (resorts, currency), same facts and sources.
- App claims only from `content/PLAN.md` "App facts". No prices. No medical promises; injury content says to see a clinician for pain.
