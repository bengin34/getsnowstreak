# SnowStreak website

Static marketing site for the SnowStreak iOS app (`APPS/snowstreak`). Plain HTML/CSS/JS, no framework, no deps. GitHub Pages serves the repo root.

## Build

- Edit `site.json` (domain, store URLs, `play_live`, support email), `i18n/<lang>.json` (all copy) or `templates/`.
- `python3 scripts/build.py` regenerates `index.html`, `<lang>/index.html`, `privacy/`, `support/`, `404.html`, `sitemap.xml`, `robots.txt`, `CNAME`. Never hand-edit generated HTML.
- Build fails if a language is missing a key that `en.json` has.
- `node scripts/selftest.mjs` checks countdown + pass break-even math in `assets/js/site.js`.
- OG image: serve root (`python3 -m http.server`), screenshot `scripts/og.html` at 1200x630 into `assets/img/og.png`.

## Domain

`site.json.url` is `https://getsnowstreak.app`. To change domain: edit it, rebuild, push. Every canonical, hreflang, sitemap and CNAME follows.

## Rules

- Languages: en (root), de, fr, it, es. Every home string exists in all 5. Legal pages are EN only.
- Palette and fonts mirror the app (`APPS/snowstreak/src/theme/index.ts`, Barlow Condensed + Manrope). Fonts are self-hosted (no Google Fonts: GDPR).
- Screens in `assets/img/screens/` come from `APPS/snowstreak/assets/app-store/source/en-US` (raw simulator captures), converted with `cwebp -resize 390|780`.
- Claims must match the app: free tier = week 1 + 5 ski days (`src/engine/freeTier.ts`), yearly with 7-day trial or lifetime. No prices on the site.
- No cookies, analytics or third-party requests. Adding any means updating `privacy/`.
- Unrelated to qrodesk.com. Do not copy from it.
- Marketing skills per agent-ops AGENTS.md: `ecc:seo` always; copy changes `ecc:article-writing` + `ecc:brand-voice`.
