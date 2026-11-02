# Marketing TODO — SnowStreak web

## Launch blockers (owner)
- [x] Domain getsnowstreak.app set in `site.json` (2026-11-02).
- [x] Repo bengin34/getsnowstreak, Pages on main / root, custom domain set (2026-11-02).
- [ ] Porkbun DNS: replace parking records with GitHub Pages A/AAAA + www CNAME; then enforce HTTPS in Pages settings.
- [ ] Decide support email (currently support@qrodesk.com, the app's address in `APPS/snowstreak/src/content/links.ts`).
- [ ] Impressum: German commercial site needs one (§5 DDG). Not shipped; add `/impressum/` with publisher details.
- [ ] After launch: point App Store Connect privacy/support URLs and the app's `PRIVACY_URL` to the new domain (currently qrodesk.com).
- [ ] Google Play live → `play_live: true`, rebuild.
- [ ] Replace store button with Apple's official "Download on the App Store" badge artwork if desired.

## Next
- [ ] Localized screens (only en-US raw captures exist; DE/FR/IT/ES pages show English UI).
- [ ] Search Console + Bing Webmaster after domain; submit sitemap.
- [ ] Content: pre-season ski workout guides (one per language) → app CTA. Use `ecc:market-research` first.
- [ ] Add nl, pl, cs, sv, nb, fi (app supports them).

## Run log
| Date | Work | Skills | Notes |
|---|---|---|---|
| 2026-11-02 | Initial site: home x5 langs, privacy, support, 404, sitemap, OG | ecc:seo, ecc:frontend-design-direction, ecc:brand-voice | Lighthouse mobile: SEO 100, BP 100, a11y 96 → contrast + label fixed |
