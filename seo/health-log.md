# SEO health log

## 2026-11-25 (MEN-1147, first run)
- Crawl, 230 URLs: FATAL 0, REVENUE 0, FLUFF 0. Raw run had 12 `STATUS 0` timeouts (local network; all 200 via curl, rechecked with the crawler's own checks).
- Local build: internal asset/link targets resolve, 228 JSON-LD blocks parse.
- GSC: no data. Token OK, but the site list for the service account is empty (property not added / no access).
- Fixed: sitemap `lastmod` was the build date on every URL (now the guide's `updated`; home/index = newest guide; privacy/support omitted). Added OG + Twitter tags to privacy, support, 404.
- Left: (1) add the Search Console service account, submit sitemap (owner); (2) Bing Webmaster (owner); (3) 3 round-3 guides still en only (MEN-1047); (4) localized screenshots; (5) Impressum (owner). 2 to 5 are tracked in `MARKETING_TODO.md` or Linear.
