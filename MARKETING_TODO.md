# Marketing TODO — SnowStreak web

## Launch blockers (owner)
- [x] Domain getsnowstreak.app set in `site.json` (2026-11-02).
- [x] Repo bengin34/getsnowstreak, Pages on main / root, custom domain set (2026-11-02).
- [x] Porkbun DNS → GitHub Pages, cert issued, HTTPS enforced (2026-11-02).
- [ ] Decide support email (currently support@qrodesk.com, the app's address in `APPS/snowstreak/src/content/links.ts`).
- [ ] Impressum: German commercial site needs one (§5 DDG). Not shipped; add `/impressum/` with publisher details.
- [ ] After launch: point App Store Connect privacy/support URLs and the app's `PRIVACY_URL` to the new domain (currently qrodesk.com).
- [ ] Google Play live → `play_live: true`, rebuild.
- [ ] Replace store button with Apple's official "Download on the App Store" badge artwork if desired.

## Next
- [ ] Localized screens (only en-US raw captures exist; DE/FR/IT/ES pages show English UI).
- [ ] Search Console + Bing Webmaster after domain; submit sitemap.
- [x] Content: 8 guides x 5 langs (`content/PLAN.md`), hub + cluster, guides index per language, home guides block (2026-11-02).
- [x] Guides round 2: 30 new en guides (2026-11-04). Translated to de/fr/it/es (MEN-133, 2026-11-12). Open: refresh pass prices each autumn.
- [ ] Add nl, pl, cs, sv, nb, fi (app supports them).

## Run log
| Date | Work | Skills | Notes |
|---|---|---|---|
| 2026-11-02 | Initial site: home x5 langs, privacy, support, 404, sitemap, OG | ecc:seo, ecc:frontend-design-direction, ecc:brand-voice | Lighthouse mobile: SEO 100, BP 100, a11y 96 → contrast + label fixed |
| 2026-11-02 | Guides: build pipeline + 8 topics x 5 langs (40 pages + 5 indexes) via 8 writer subagents | ecc:seo, ecc:market-research, ecc:article-writing, ecc:brand-voice | `--check` clean, 0 broken internal links, mobile 390 no overflow |
| 2026-11-02 | Home: first-visit ski/snowboard picker, 4.4 s stunt run over 3 peaks (backflip, 360, front flip, camera pan), then scroll-driven slalom rider (JS-only, reduced-motion off, choice in localStorage, privacy note updated) | ecc:seo, ecc:frontend-design-direction |
| 2026-11-04 | Guides round 2 (MEN-131): 30 new topics, English only (38 total en). build.py: de/fr/it/es optional per guide | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` clean on all 38. Follow-up: translate the 30 to de/fr/it/es |
| 2026-11-12 | Guides round 2 translated (MEN-133): 30 topics x de/fr/it/es (120 pages). build.py: duplicate-slug guard per lang | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` 0 warnings on all 38, build 202 pages, sitemap +120. 390px render not done |
