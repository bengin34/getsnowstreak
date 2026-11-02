#!/usr/bin/env python3
"""Render the static site from templates/ + i18n/*.json + site.json.

Usage: python3 scripts/build.py
Writes index.html (en), <lang>/index.html, privacy/, support/, 404.html,
sitemap.xml, robots.txt and CNAME into the repo root (GitHub Pages serves root).
Fails on any missing translation key, so a language can never ship half-done.
"""
import html
import json
import re
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


def build_home(lang, t, tpl):
    v = {k: (val if k in RAW else html.escape(str(val))) for k, val in t.items() if not isinstance(val, (list, dict))}
    canonical = URL + home_path(lang)
    v.update(
        url=URL, canonical=canonical, home=home_path(lang), ios_url=SITE["ios_url"],
        lang_code=lang.upper(), ridges=ridges("night-ridges"), ridges_day=ridges("day-ridges"),
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
    home_tpl = (ROOT / "templates/home.html").read_text()
    page_tpl = (ROOT / "templates/page.html").read_text()
    en = json.loads((ROOT / "i18n/en.json").read_text())
    urls = []
    for lang in LANGS:
        t = json.loads((ROOT / f"i18n/{lang}.json").read_text())
        missing = set(en) - set(t)
        if missing:
            sys.exit(f"ERROR i18n/{lang}.json missing: {sorted(missing)}")
        write(f"{home_path(lang).strip('/')}/index.html".lstrip("/"), build_home(lang, t, home_tpl))
        urls.append(URL + home_path(lang))

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
