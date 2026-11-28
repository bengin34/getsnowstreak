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
- [x] Localized screens: de/fr/it/es home use `assets/img/screens/<lang>/` sim captures (MEN-1170, retry of MEN-1164, 2026-11-26). FR home captured at text size small (app bug MEN-1168).
- [ ] Search Console + Bing Webmaster after domain; submit sitemap.
- [x] Content: 8 guides x 5 langs (`content/PLAN.md`), hub + cluster, guides index per language, home guides block (2026-11-02).
- [x] Guides round 2: 30 new en guides (2026-11-04). Translated to de/fr/it/es (MEN-133, 2026-11-12). Open: refresh pass prices each autumn.
- [x] Guides round 3 (MEN-1040): 8 en trip-planning guides (when/where/where to stay), 2026-11-20. Translated to de/fr/it/es (MEN-1081 + MEN-1047, 2026-11-26).
- [x] nl, pl, sv home pages with localized screens (MEN-1487, 2026-11-28). No guides in these three yet.
- [ ] Add cs, nb, fi (app supports them).

## Run log
| Date | Work | Skills | Notes |
|---|---|---|---|
| 2026-11-02 | Initial site: home x5 langs, privacy, support, 404, sitemap, OG | ecc:seo, ecc:frontend-design-direction, ecc:brand-voice | Lighthouse mobile: SEO 100, BP 100, a11y 96 → contrast + label fixed |
| 2026-11-02 | Guides: build pipeline + 8 topics x 5 langs (40 pages + 5 indexes) via 8 writer subagents | ecc:seo, ecc:market-research, ecc:article-writing, ecc:brand-voice | `--check` clean, 0 broken internal links, mobile 390 no overflow |
| 2026-11-02 | Home: first-visit ski/snowboard picker, 4.4 s stunt run over 3 peaks (backflip, 360, front flip, camera pan), then scroll-driven slalom rider (JS-only, reduced-motion off, choice in localStorage, privacy note updated) | ecc:seo, ecc:frontend-design-direction |
| 2026-11-04 | Guides round 2 (MEN-131): 30 new topics, English only (38 total en). build.py: de/fr/it/es optional per guide | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` clean on all 38. Follow-up: translate the 30 to de/fr/it/es |
| 2026-11-12 | Guides round 2 translated (MEN-133): 30 topics x de/fr/it/es (120 pages). build.py: duplicate-slug guard per lang | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` 0 warnings on all 38, build 202 pages, sitemap +120. 390px render not done |
| 2026-11-20 | Guides round 3 (MEN-1040): 8 en trip-planning guides | ecc:seo, ecc:article-writing, ecc:brand-voice, ecc:market-research | `--check` 0 warnings on all 8; translations MEN-1047 |
| 2026-11-22 | Guides round 3 translated (MEN-1081): 5 of 8 trip-planning topics x de/fr/it/es (20 pages). Remaining 3: MEN-1047 | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` 0 warnings on all 5, build 230 pages |
| 2026-11-25 | SEO health (MEN-1147): sitemap lastmod from guide `updated`, OG tags on privacy/support/404. `seo/health-log.md` added | ecc:seo | crawl 230 URLs, 0 issues; GSC no access |
| 2026-11-26 | Localized app screenshots (MEN-1170, retry of MEN-1164): 5 screens x de/fr/it/es, alt text aligned to app strings | ecc:seo, ecc:frontend-design-direction, ecc:brand-voice, impeccable | real sim captures, premium unlocked in throwaway build only |
| 2026-11-26 | Guides round 3 finished (MEN-1047): best-family, cheap-europe, ski-in-ski-out x de/fr/it/es (12 pages); beginners guide now links the family guide | ecc:seo, ecc:article-writing, ecc:brand-voice | `--check` 0 warnings, build 242 pages, selftest pass |
| 2026-11-28 | nl, pl, sv home pages + 5 localized screens each (MEN-1487); guides index hreflang limited to languages with guides | ecc:seo, ecc:article-writing, ecc:brand-voice | build 245 pages, selftest pass, 0 broken links from new pages, 390px no overflow |
