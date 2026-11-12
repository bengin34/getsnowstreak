#!/usr/bin/env python3
"""Render the static site from templates/ + i18n/*.json + site.json.

Usage: python3 scripts/build.py
Writes index.html (en), <lang>/index.html, privacy/, support/, 404.html,
sitemap.xml, robots.txt and CNAME into the repo root (GitHub Pages serves root).
Guides: every content/<topic>.json becomes /guides/<slug>/ (en) and /<lang>/<guides_path>/<slug>/.
Usage: python3 scripts/build.py --check content/<topic>.json   validates one guide, writes nothing.
Fails on any missing translation key, so a language can never ship half-done.
"""
import html
from html.parser import HTMLParser
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "site.json").read_text())
URL = SITE["url"].rstrip("/")
LANGS = SITE["langs"]
NAMES = {"en": "English", "de": "Deutsch", "fr": "Français", "it": "Italiano", "es": "Español"}
RAW = {"hero_h1"}  # keys whose value is trusted inline HTML

RIDGE_FAR = "M0 220V120L120 70L210 105L330 28L430 90L520 60L640 118L760 38L880 100L980 55L1100 110L1220 32L1330 85L1440 60V220Z"
RIDGE_NEAR = "M0 220V160L90 132L200 170L300 108L420 175L560 92L700 165L820 130L960 185L1080 98L1200 160L1320 118L1440 150V220Z"
CAPS = "M304 44L330 28L356 44L342 41L330 50L318 41Z M738 52L760 38L782 52L770 49L760 57L750 49Z M1196 47L1220 32L1244 47L1231 44L1220 52L1209 44Z M534 106L560 92L586 106L573 104L560 112L547 104Z M1054 113L1080 98L1106 113L1093 110L1080 118L1067 110Z"


def ridges(cls):
    return (f'<svg class="ridges {cls}" viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true">'
            f'<path class="r-far" d="{RIDGE_FAR}"/><path class="r-cap" d="{CAPS}"/>'
            f'<path class="r-near" d="{RIDGE_NEAR}"/></svg>')


def home_path(lang):
    return "/" if lang == "en" else f"/{lang}/"


GUIDE_KEYS = ["title", "description", "headline", "lede", "body_html", "faq", "sources"]
BODY_TAGS = {"h2", "h3", "p", "ul", "ol", "li", "strong", "em", "a", "br", "sup",
             "table", "thead", "tbody", "tr", "th", "td", "div"}


def guides_dir(lang, t):
    return f"/guides/" if lang == "en" else f"/{lang}/{t['guides_path']}/"


class BodyCheck(HTMLParser):
    def __init__(self, topics):
        super().__init__()
        self.topics, self.errors, self.text, self.links = topics, [], [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in BODY_TAGS:
            self.errors.append(f"tag <{tag}> not allowed")
        if "style" in a:
            self.errors.append(f"inline style on <{tag}>")
        if "class" in a and not (tag == "div" and a["class"] == "table-scroll"):
            self.errors.append(f"class on <{tag}> not allowed")
        if tag == "div" and a.get("class") != "table-scroll":
            self.errors.append("<div> only as table-scroll wrapper")
        if tag == "a":
            href = a.get("href") or ""
            if href.startswith("guide:"):
                if href[6:] not in self.topics:
                    self.errors.append(f"unknown guide link {href}")
                self.links.add(href[6:])
            elif href not in ("/", "app") and not href.startswith("https://"):
                self.errors.append(f"bad href {href!r} (use guide:<id>, /, app or https://)")

    def handle_data(self, data):
        self.text.append(data)


def check_guide(path, topics):
    errors, warns = [], []
    try:
        g = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return [f"cannot read: {e}"], warns
    slugs = g.get("slugs", {})
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(g.get("updated", ""))):
        errors.append("updated must be YYYY-MM-DD")
    for lang in LANGS:
        where = f"{lang}:"
        if lang not in g.get("langs", {}) and lang != "en":
            continue
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slugs.get(lang, "")):
            errors.append(f"{where} slug missing or not lowercase ascii-hyphen")
        t = g.get("langs", {}).get(lang)
        if t is None and lang != "en":  # en is required; other languages may be added later
            continue
        if not isinstance(t, dict):
            errors.append(f"{where} language block missing")
            continue
        miss = [k for k in GUIDE_KEYS if not t.get(k)]
        if miss:
            errors.append(f"{where} missing {miss}")
            continue
        if not 30 <= len(t["title"]) <= 65:
            warns.append(f"{where} title {len(t['title'])} chars (aim 50-60)")
        if not 110 <= len(t["description"]) <= 165:
            warns.append(f"{where} description {len(t['description'])} chars (aim 120-160)")
        b = BodyCheck(topics)
        b.feed(t["body_html"])
        errors += [f"{where} {e}" for e in b.errors]
        words = len(" ".join(b.text).split())
        if not 1000 <= words <= 1600:
            warns.append(f"{where} body {words} words (aim 1000-1600)")
        if "guide:ski-fitness-plan" not in t["body_html"] and Path(path).stem != "ski-fitness-plan":
            warns.append(f"{where} no link to hub guide:ski-fitness-plan")
        if 'href="app"' not in t["body_html"]:
            warns.append(f"{where} no app link (href=\"app\")")
        if not 4 <= len(t["faq"]) <= 6 or any(not (f.get("q") and f.get("a")) for f in t["faq"]):
            errors.append(f"{where} faq needs 4-6 items with q and a")
        if len(t["sources"]) < 3 or any(not str(s.get("url", "")).startswith("https://") for s in t["sources"]):
            errors.append(f"{where} needs 3+ sources with https urls")
        cites = {int(n) for n in re.findall(r"<sup>\[(\d+)\]</sup>", t["body_html"])}
        if cites and max(cites) > len(t["sources"]):
            errors.append(f"{where} cites [{max(cites)}] but has {len(t['sources'])} sources")
    return errors, warns


def load_guides():
    topics = {p.stem for p in (ROOT / "content").glob("*.json")}
    guides = []
    for p in sorted((ROOT / "content").glob("*.json")):
        errors, warns = check_guide(p, topics)
        if errors:
            sys.exit(f"ERROR {p.name}: " + "; ".join(errors))
        g = json.loads(p.read_text())
        g["id"] = p.stem
        guides.append(g)
    seen = {}
    for g in guides:
        for lang, slug in g["slugs"].items():
            if (lang, slug) in seen:
                sys.exit(f"ERROR duplicate {lang} slug {slug}: {seen[(lang, slug)]}, {g['id']}")
            seen[(lang, slug)] = g["id"]
    guides.sort(key=lambda g: g["id"] != "ski-fitness-plan")  # hub first
    return guides


def guide_url(g, lang, t):
    return guides_dir(lang, t) + g["slugs"][lang] + "/"


def fill(tpl, values, where):
    def sub(m):
        key = m.group(1)
        if key not in values:
            sys.exit(f"ERROR {where}: missing key '{key}'")
        return str(values[key])
    return re.sub(r"{{\s*([\w.]+)\s*}}", sub, tpl)


def store_buttons(t):
    apple = ('<svg viewBox="0 0 384 512" aria-hidden="true"><path fill="currentColor" d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>')
    out = f'<a class="store" href="{SITE["ios_url"]}" rel="noopener">{apple}<span>{html.escape(t["cta_ios"])}</span></a>'
    if SITE["play_live"]:
        out += f'<a class="store" href="{SITE["play_url"]}" rel="noopener"><span>{html.escape(t["cta_play"])}</span></a>'
    else:
        out += f'<span class="soon">{html.escape(t["android_soon"])}</span>'
    return out


def guides_block(lang, t, guides, ts):
    if not guides:
        return ""
    cards = "".join(f'<li><a href="{guide_url(g, lang, t)}"><b>{html.escape(g["langs"][lang]["headline"])}</b>'
                    f'<span>{html.escape(g["langs"][lang]["description"])}</span></a></li>' for g in guides)
    return (f'<section class="guides-home day-alt" id="guides"><div class="wrap">'
            f'<p class="kicker">{html.escape(t["home_guides_kicker"])}</p><h2>{html.escape(t["home_guides_h2"])}</h2>'
            f'<ul class="cards">{cards}</ul></div></section>')


def guide_chrome(lang, t, ts, canonical, alternates, title, description, main, schema, og_type, tpl):
    """alternates: {lang: path}."""
    v = {k: html.escape(str(t[k])) for k in ("lang", "og_locale", "skip", "lang_label", "cta_ios_short", "foot_tag",
                                             "foot_privacy", "foot_support", "foot_eula", "foot_health", "guides_nav")}
    v.update(
        url=URL, canonical=canonical, home=home_path(lang), ios_url=SITE["ios_url"], lang_code=lang.upper(),
        guides_url=guides_dir(lang, t), page_title=html.escape(title), page_description=html.escape(description),
        og_type=og_type, main=main, schema=json.dumps(schema, ensure_ascii=False).replace("</", "<\\/"),
        hreflang="\n".join([f'<link rel="alternate" hreflang="{l}" href="{URL}{p}" />' for l, p in alternates.items()]
                           + [f'<link rel="alternate" hreflang="x-default" href="{URL}{alternates["en"]}" />']),
        lang_menu="".join(f'<li><a href="{p}" hreflang="{l}" lang="{l}"' + (' aria-current="page"' if l == lang else "")
                          + f'>{NAMES[l]}</a></li>' for l, p in alternates.items()),
    )
    return fill(tpl, v, f"guide/{lang}")


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + p} for i, (n, p) in enumerate(items)]}


def build_guide(g, lang, ts, guides, tpl):
    t, c = ts[lang], g["langs"][lang]
    path = guide_url(g, lang, t)
    resolve = {"app": SITE["ios_url"], "/": home_path(lang)}
    body = re.sub(r'href="(guide:[\w-]+|app|/)"', lambda m: 'href="%s"' % (
        guide_url(next(x for x in guides if x["id"] == m.group(1)[6:]), lang, t)
        if m.group(1).startswith("guide:") else resolve[m.group(1)]), c["body_html"])
    body = body.replace('href="https://', 'rel="noopener" href="https://')
    faq = "".join(f'<details><summary>{html.escape(f["q"])}</summary><p>{html.escape(f["a"])}</p></details>' for f in c["faq"])
    sources = "".join(f'<li>{html.escape(s["label"])} <a href="{html.escape(s["url"])}" rel="noopener">{html.escape(s["url"].split("/")[2])}</a></li>'
                      for s in c["sources"])
    more = "".join(f'<li><a href="{guide_url(x, lang, t)}">{html.escape(x["langs"][lang]["headline"])}</a></li>'
                   for x in guides if x is not g)
    main = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{home_path(lang)}">{html.escape(t["crumb_home"])}</a> / '
            f'<a href="{guides_dir(lang, t)}">{html.escape(t["guides_nav"])}</a></nav>'
            f'<article><h1>{html.escape(c["headline"])}</h1><p class="lede">{html.escape(c["lede"])}</p>'
            f'<p class="updated">{html.escape(t["guide_updated"])}: <time datetime="{g["updated"]}">{g["updated"]}</time></p>'
            f'{body}'
            f'<aside class="guide-cta"><h2>{html.escape(t["guide_cta_h"])}</h2><p>{html.escape(t["guide_cta_p"])}</p>'
            f'<div class="stores">{store_buttons(t)}</div></aside>'
            f'<section class="faq"><h2>{html.escape(t["faq_h2"])}</h2>{faq}</section>'
            f'<section class="sources"><h2>{html.escape(t["guide_sources"])}</h2><ol>{sources}</ol></section></article>'
            + (f'<nav class="more" aria-label="{html.escape(t["guide_more"])}"><h2>{html.escape(t["guide_more"])}</h2><ul>{more}</ul></nav>' if more else ""))
    schema = [
        {"@context": "https://schema.org", "@type": "Article", "headline": c["headline"], "description": c["description"],
         "inLanguage": lang, "datePublished": g.get("published", g["updated"]), "dateModified": g["updated"],
         "mainEntityOfPage": URL + path, "image": f"{URL}/assets/img/og.png",
         "author": {"@type": "Organization", "name": "SnowStreak", "url": URL + "/"},
         "publisher": {"@type": "Organization", "name": "Mendi Tekstilwaren"}},
        crumbs([(t["crumb_home"], home_path(lang)), (t["guides_nav"], guides_dir(lang, t)), (c["headline"], path)]),
        {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in c["faq"]]},
    ]
    alternates = {l: guide_url(g, l, ts[l]) for l in LANGS if l in g["langs"]}
    return path, guide_chrome(lang, t, ts, URL + path, alternates, c["title"], c["description"], main, schema, "article", tpl)


def build_guides_index(lang, ts, guides, tpl):
    t = ts[lang]
    path = guides_dir(lang, t)
    items = "".join(f'<li><a href="{guide_url(g, lang, t)}"><b>{html.escape(g["langs"][lang]["headline"])}</b>'
                    f'<span>{html.escape(g["langs"][lang]["description"])}</span></a></li>' for g in guides)
    main = f'<h1>{html.escape(t["guides_h1"])}</h1><p class="lede">{html.escape(t["guides_lede"])}</p><ul class="cards">{items}</ul>'
    schema = [crumbs([(t["crumb_home"], home_path(lang)), (t["guides_nav"], path)])]
    alternates = {l: guides_dir(l, ts[l]) for l in LANGS}
    return path, guide_chrome(lang, t, ts, URL + path, alternates, t["guides_title"], t["guides_description"], main, schema, "website", tpl)


def build_home(lang, t, tpl, block=""):
    v = {k: (val if k in RAW else html.escape(str(val))) for k, val in t.items() if not isinstance(val, (list, dict))}
    canonical = URL + home_path(lang)
    v.update(
        url=URL, canonical=canonical, home=home_path(lang), ios_url=SITE["ios_url"],
        lang_code=lang.upper(), guides_block=block, ridges=ridges("night-ridges"), ridges_day=ridges("day-ridges"),
        ridges_top=ridges("top-ridges"), store_buttons=store_buttons(t),
        hreflang="\n".join([f'<link rel="alternate" hreflang="{l}" href="{URL}{home_path(l)}" />' for l in LANGS]
                           + [f'<link rel="alternate" hreflang="x-default" href="{URL}/" />']),
        lang_menu="".join(f'<li><a href="{home_path(l)}" hreflang="{l}" lang="{l}"'
                          + (' aria-current="page"' if l == lang else "") + f'>{NAMES[l]}</a></li>' for l in LANGS),
        free_list="".join(f"<li>{html.escape(i)}</li>" for i in t["free_items"]),
        premium_list="".join(f"<li>{html.escape(i)}</li>" for i in t["premium_items"]),
        faq_html="".join(f'<details><summary>{html.escape(f["q"])}</summary><p>{html.escape(f["a"])}</p></details>'
                         for f in t["faq"]),
        js_json=json.dumps({**t["js"], "lang": lang, "currency": t["currency"]}, ensure_ascii=False).replace("</", "<\\/"),
    )
    schema = [
        {"@context": "https://schema.org", "@type": "MobileApplication", "name": "SnowStreak",
         "operatingSystem": "iOS", "applicationCategory": "HealthApplication", "url": canonical,
         "description": t["description"], "image": f"{URL}/assets/img/icon-192.png",
         "installUrl": SITE["ios_url"], "inLanguage": lang,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "publisher": {"@type": "Organization", "name": "Mendi Tekstilwaren"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in t["faq"]]},
    ]
    v["schema"] = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return fill(tpl, v, f"home/{lang}")


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def main():
    if sys.argv[1:2] == ["--check"]:
        topics = {p.stem for p in (ROOT / "content").glob("*.json")}
        bad = False
        for f in sys.argv[2:]:
            errors, warns = check_guide(f, topics | {Path(f).stem})
            for e in errors:
                print(f"ERROR {f}: {e}")
            for w in warns:
                print(f"WARN  {f}: {w}")
            bad |= bool(errors)
            if not errors:
                print(f"ok    {f} ({len(warns)} warnings)")
        sys.exit(1 if bad else 0)
    guides = load_guides()
    guide_tpl = (ROOT / "templates/guide.html").read_text()
    home_tpl = (ROOT / "templates/home.html").read_text()
    page_tpl = (ROOT / "templates/page.html").read_text()
    en = json.loads((ROOT / "i18n/en.json").read_text())
    urls = []
    ts = {}
    for lang in LANGS:
        t = ts[lang] = json.loads((ROOT / f"i18n/{lang}.json").read_text())
        missing = set(en) - set(t)
        if missing:
            sys.exit(f"ERROR i18n/{lang}.json missing: {sorted(missing)}")
    for lang in LANGS:  # guide dirs are fully generated; wipe so renamed slugs leave no stale pages
        shutil.rmtree(ROOT / guides_dir(lang, ts[lang]).strip("/"), ignore_errors=True)
    for lang in LANGS:
        write(f"{home_path(lang).strip('/')}/index.html".lstrip("/"),
              build_home(lang, ts[lang], home_tpl, guides_block(lang, ts[lang], [g for g in guides if lang in g["langs"]], ts)))
        urls.append(URL + home_path(lang))
        gl = [g for g in guides if lang in g["langs"]]
        if gl:
            pages = [build_guides_index(lang, ts, gl, guide_tpl)] + [build_guide(g, lang, ts, gl, guide_tpl) for g in gl]
            for path, text in pages:
                write(path.strip("/") + "/index.html", text)
                urls.append(URL + path)

    pages = {
        "privacy": ("Privacy policy", "How SnowStreak handles your data: no account, no analytics, no location tracking. Everything stays on your device."),
        "support": ("Support", "Get help with SnowStreak: contact, restoring purchases, cancelling the yearly plan, refunds and moving to a new phone."),
    }
    for slug, (title, desc) in pages.items():
        body = fill((ROOT / f"templates/pages/{slug}.html").read_text(), SITE, slug)
        write(f"{slug}/index.html", fill(page_tpl, {"title": title, "description": desc, "canonical": f"{URL}/{slug}/",
                                                     "ios_url": SITE["ios_url"], "body": body}, slug))
        urls.append(f"{URL}/{slug}/")

    write("404.html", fill(page_tpl, {"title": "Page not found", "description": "This page does not exist.",
                                      "canonical": URL + "/", "ios_url": SITE["ios_url"],
                                      "body": '<h1>Off piste.</h1><p>This page does not exist. <a href="/">Back to the start</a>.</p>'}, "404"))
    today = date.today().isoformat()
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n")
    write("CNAME", URL.split("://", 1)[1] + "\n")
    print(f"built {len(urls)} pages for {URL}")


if __name__ == "__main__":
    main()
