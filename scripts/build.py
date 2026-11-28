#!/usr/bin/env python3
"""
WowTech Solution - build script (SEO tags, Arabic pages, sitemap).

Run from anywhere:   python3 scripts/build.py

The English pages (index.html, benefits.html, clients.html) are the source of
truth. Edit them, then run this script. It:

  1. writes the SEO <head> block (canonical, hreflang, Open Graph, Twitter Card,
     JSON-LD) into each English page, between the seo:start / seo:end markers;
  2. generates the static Arabic pages in /ar/ from the English pages and the
     dictionary in scripts/translations-ar.js (Arabic is real HTML now, so
     Google and Bing can index it - it is no longer swapped in by JavaScript);
  3. writes sitemap.xml (with hreflang alternates);
  4. runs sanity checks (broken local links, titles, JSON-LD, hreflang).

Titles and descriptions come from each English page:
  <title>                          English title
  <meta name="description">        English description
  data-title-ar on <html>          Arabic title
  data-ar-content on the meta tag  Arabic description
"""
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- settings --
SITE = "https://wowtech-solutions.com"          # no trailing slash. Change if the live domain differs.
BRAND = "WowTech Solution"
BRAND_ALT = ["WowTech", "واو تيك سوليشن"]
PHONE = "+971521961007"
INSTAGRAM = "https://www.instagram.com/wowtech.solutions/"
OG_IMAGE = f"{SITE}/og-image.png"                # 1200x630
LOGO = f"{SITE}/icon-512.png"                    # square logo for search engines

PAGES = [  # (source file, English path, Arabic path, breadcrumb dictionary key)
    ("index.html", "/", "/ar/", None),
    ("benefits.html", "/benefits.html", "/ar/benefits.html", "Benefits"),
    ("clients.html", "/clients.html", "/ar/clients.html", "Clients"),
]

AR_WHATSAPP = "مرحباً WowTech Solution، أود الحصول على استشارة مجانية حول احتياجات شركتي التقنية."
AR_MENU_OPEN = "فتح القائمة"
AR_LABELS = {
    "WowTech Solution, back to top": "WowTech Solution، العودة للأعلى",
    "WowTech Solution, back to home": "WowTech Solution، العودة للرئيسية",
    "Chat with WowTech Solution on WhatsApp": "تواصل مع WowTech Solution عبر واتساب",
    "WowTech Solution on Instagram": "حساب WowTech Solution على إنستغرام",
    "Main navigation": "التنقل الرئيسي",
    "Mobile navigation": "التنقل على الهاتف",
    "Footer navigation": "التنقل أسفل الصفحة",
    "Connected technology systems visualization": "تصوّر للأنظمة التقنية المترابطة",
}
AR_HOME = "الرئيسية"
AR_OG_ALT = "WowTech Solution - حلول تقنية للشركات في دبي"
EN_OG_ALT = "WowTech Solution - IT solutions for businesses in Dubai"

# Text that is intentionally left untranslated (brand names, numbers, domains).
KEEP_LATIN = {
    "TECH SOLUTION", "WOW", "WowTech Solution.", "Alsanad ZA", "ISAAL GROUP", "Claquet Finance",
    "alsanadza.com", "isaalgroup.com", "claquetfinance.com", "@wowtech.solutions", "EN",
}

# ----------------------------------------------------------------- helpers --
def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def write(p, text):
    path = ROOT / p
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def load_dictionary():
    js = read("scripts/translations-ar.js")
    body = js[js.index("{"): js.rindex("}") + 1]
    return json.loads(re.sub(r",\s*}", "}", body))


AR = load_dictionary()
WARNINGS, ERRORS = [], []


def esc(v):
    return html.escape(v, quote=True)


def attrs_of(tag):
    inner = re.sub(r"^<[\w:-]+|/?>$", "", tag)
    out = {}
    for m in re.finditer(r'([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'))?', inner):
        v = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        out[m.group(1)] = html.unescape(v)
    return out


def set_attr(tag, name, value):
    v = esc(value)
    pat = re.compile(r'(\s%s=)"[^"]*"' % re.escape(name))
    if pat.search(tag):
        return pat.sub(lambda m: f'{m.group(1)}"{v}"', tag, count=1)
    return re.sub(r"(\s*/?>)$", lambda m: f' {name}="{v}"' + m.group(1), tag, count=1)


def del_attr(tag, name):
    return re.sub(r'\s%s(?=[\s/>=])(?:="[^"]*")?' % re.escape(name), "", tag, count=1)


def lastmod(rel):
    """Date of the last commit touching the file; today's date if it has uncommitted changes."""
    today = datetime.date.today().isoformat()
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.strip()
        if dirty:
            return today
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or today
    except Exception:
        return today


# -------------------------------------------------------------- page data --
def page_meta(src):
    return {
        "title": {"en": html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1)).strip(),
                  "ar": html.unescape(re.search(r'<html[^>]*data-title-ar="([^"]*)"', src).group(1))},
        "desc": {"en": html.unescape(re.search(r'<meta name="description" content="([^"]*)"', src).group(1)),
                 "ar": html.unescape(re.search(r'data-ar-content="([^"]*)"', src).group(1))},
    }


def services_from_home(src, lang):
    out = []
    for card in re.findall(r'<article class="service-card.*?</article>', src, re.S):
        name = html.unescape(re.search(r"<h3>(.*?)</h3>", card, re.S).group(1)).strip()
        items = [html.unescape(i).strip() for i in re.findall(r"<li>(.*?)</li>", card, re.S)]
        if lang == "ar":
            name = tr(name)
            items = [tr(i) for i in items]
        out.append((name, items))
    return out


def tr(text):
    if text not in AR:
        WARNINGS.append(f"no Arabic translation for: {text!r}")
    return AR.get(text, text)


def url_for(page, lang):
    return SITE + (page[1] if lang == "en" else page[2])


# ------------------------------------------------------------- SEO block ---
def jsonld(page, lang, meta, services):
    url = url_for(page, lang)
    home_url = SITE + ("/" if lang == "en" else "/ar/")
    org_id, site_id = f"{SITE}/#organization", f"{SITE}/#website"
    title, desc = meta["title"][lang], meta["desc"][lang]
    org = {
        "@type": "ProfessionalService",
        "@id": org_id,
        "name": BRAND,
        "alternateName": BRAND_ALT,
        "url": f"{SITE}/",
        "logo": {"@type": "ImageObject", "url": LOGO, "width": 512, "height": 512},
        "image": OG_IMAGE,
        "description": meta["desc"][lang],
        "telephone": PHONE,
        "address": {"@type": "PostalAddress", "addressLocality": "Dubai", "addressCountry": "AE"},
        "areaServed": {"@type": "City", "name": "Dubai"},
        "sameAs": [INSTAGRAM],
    }
    graph = [org]
    is_home = page[3] is None
    if is_home:
        org["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Services" if lang == "en" else "الخدمات",
            "itemListElement": [
                {"@type": "OfferCatalog", "name": name,
                 "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": i}} for i in items]}
                for name, items in services
            ],
        }
        graph.insert(0, {"@type": "WebSite", "@id": site_id, "url": f"{SITE}/", "name": BRAND,
                         "inLanguage": ["en", "ar"], "publisher": {"@id": org_id}})
        graph.append({"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": title, "description": desc,
                      "inLanguage": lang, "isPartOf": {"@id": site_id}, "about": {"@id": org_id}})
    else:
        crumb = tr(page[3]) if lang == "ar" else page[3]
        graph.append({"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": title, "description": desc,
                      "inLanguage": lang, "isPartOf": {"@id": site_id}, "about": {"@id": org_id},
                      "breadcrumb": {"@id": f"{url}#breadcrumb"}})
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home" if lang == "en" else AR_HOME, "item": home_url},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]})
    return {"@context": "https://schema.org", "@graph": graph}


def seo_block(page, lang, meta, services):
    title, desc = meta["title"][lang], meta["desc"][lang]
    url = url_for(page, lang)
    loc, alt = ("en_US", "ar_AE") if lang == "en" else ("ar_AE", "en_US")
    og_alt = EN_OG_ALT if lang == "en" else AR_OG_ALT
    ld = json.dumps(jsonld(page, lang, meta, services), ensure_ascii=False, indent=2)
    ld = "\n".join("      " + line for line in ld.splitlines()).lstrip()
    lines = [
        '<!-- seo:start (generated by scripts/build.py - edit titles/descriptions in the English page, then re-run it) -->',
        f'<link rel="canonical" href="{esc(url)}" />',
        f'<link rel="alternate" hreflang="en" href="{esc(url_for(page, "en"))}" />',
        f'<link rel="alternate" hreflang="ar" href="{esc(url_for(page, "ar"))}" />',
        f'<link rel="alternate" hreflang="x-default" href="{esc(url_for(page, "en"))}" />',
        '<meta name="robots" content="index, follow, max-image-preview:large" />',
        '<meta property="og:type" content="website" />',
        f'<meta property="og:site_name" content="{esc(BRAND)}" />',
        f'<meta property="og:title" content="{esc(title)}" />',
        f'<meta property="og:description" content="{esc(desc)}" />',
        f'<meta property="og:url" content="{esc(url)}" />',
        f'<meta property="og:locale" content="{loc}" />',
        f'<meta property="og:locale:alternate" content="{alt}" />',
        f'<meta property="og:image" content="{OG_IMAGE}" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{esc(og_alt)}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{esc(title)}" />',
        f'<meta name="twitter:description" content="{esc(desc)}" />',
        f'<meta name="twitter:image" content="{OG_IMAGE}" />',
        f'<script type="application/ld+json">\n      {ld}\n    </script>',
        '<!-- seo:end -->',
    ]
    return ("\n    ").join(lines)


SEO_RE = re.compile(r"<!-- seo:start.*?<!-- seo:end -->", re.S)

# --------------------------------------------------------- Arabic pages ----
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TOKEN = re.compile(r"(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", re.S)
PAGE_LINK = re.compile(r"^\./(?:#.*)?$|^\./(?:benefits|clients)\.html(?:#.*)?$")
SWITCH_RE = re.compile(r'<div class="language-switch".*?</div>', re.S)


def ar_switch(page):
    home = page[3] is None
    en_href = "../" if home else f"../{page[0]}"
    ar_href = "./" if home else f"./{page[0]}"
    return ('<div class="language-switch" role="group" aria-label="Language / اللغة">\n'
            f'          <a href="{en_href}" hreflang="en" lang="en">EN</a>\n'
            '          <span aria-hidden="true">/</span>\n'
            f'          <a href="{ar_href}" hreflang="ar" lang="ar" aria-current="true">عربي</a>\n'
            '        </div>')


def ar_tag(tag, name, a, meta):
    classes = a.get("class", "").split()
    if name == "meta" and a.get("name") == "description":
        tag = set_attr(tag, "content", meta["desc"]["ar"])
    if name == "img" and "data-alt-ar" in a:
        tag = set_attr(tag, "alt", a["data-alt-ar"])
    if "data-placeholder-ar" in a:
        tag = set_attr(tag, "placeholder", a["data-placeholder-ar"])
    for k in ("data-alt-ar", "data-placeholder-ar", "data-ar-content", "data-title-ar", "data-en", "data-ar"):
        if k in a:
            tag = del_attr(tag, k)
    if "aria-label" in a and "language-switch" not in classes:
        label = a["aria-label"]
        if "menu-toggle" in classes:
            tag = set_attr(tag, "aria-label", AR_MENU_OPEN)
        else:
            if label not in AR_LABELS:
                WARNINGS.append(f"no Arabic aria-label for: {label!r}")
            tag = set_attr(tag, "aria-label", AR_LABELS.get(label, label))
    if name == "a" and a.get("href", "").startswith("https://wa.me/"):
        tag = set_attr(tag, "href", "https://wa.me/971521961007?text=" + quote(AR_WHATSAPP, safe=""))
    for k in ("src", "href"):
        v = a.get(k)
        if v and v.startswith("./") and not PAGE_LINK.match(v):
            tag = set_attr(tag, k, "../" + v[2:])
    return tag


def ar_text(text, parent, page_name):
    original = html.unescape(text)
    english = original.strip()
    if not english or english == "@@LANGSWITCH@@":
        return text
    translation = (parent or {}).get("data-ar") or AR.get(english)
    if translation:
        return html.escape(original.replace(english, translation, 1), quote=False)
    if re.search(r"[A-Za-z]{2,}", english) and english not in KEEP_LATIN:
        WARNINGS.append(f"{page_name}: untranslated text {english[:60]!r}")
    return text


def process(chunk, meta, page_name, translate_text):
    out, stack = [], []
    for tok in TOKEN.split(chunk):
        if not tok:
            continue
        if tok.startswith("<!--"):
            out.append(tok)
        elif tok.lower().startswith("<script"):
            open_tag = re.match(r"<script[^>]*>", tok).group(0)
            out.append(ar_tag(open_tag, "script", attrs_of(open_tag), meta) + tok[len(open_tag):])
        elif tok.lower().startswith("<style"):
            out.append(tok)
        elif tok.startswith("</"):
            name = tok[2:-1].strip().lower()
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
            out.append(tok)
        elif tok.startswith("<"):
            m = re.match(r"<([A-Za-z][\w:-]*)", tok)
            if not m:
                out.append(tok)
                continue
            name, a = m.group(1).lower(), attrs_of(tok)
            if not (tok.endswith("/>") or name in VOID):
                stack.append((name, a))
            out.append(ar_tag(tok, name, a, meta))
        else:
            parent = stack[-1][1] if stack else None
            out.append(ar_text(tok, parent, page_name) if translate_text else tok)
    return "".join(out)


def build_arabic(page, src, meta):
    head, body = src.split("<body", 1)
    body = "<body" + body
    body = SWITCH_RE.sub("@@LANGSWITCH@@", body, count=1)
    head = process(head, meta, page[0], translate_text=False)
    body = process(body, meta, page[0], translate_text=True).replace("@@LANGSWITCH@@", ar_switch(page))
    head = re.sub(r'<html\b[^>]*>', '<html lang="ar" dir="rtl">', head, count=1)
    head = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(meta['title']['ar'], quote=False)}</title>",
                  head, count=1, flags=re.S)
    return head + body


# ------------------------------------------------------------- sitemap -----
def build_sitemap():
    rows = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in PAGES:
        mod = lastmod(page[0])
        for lang in ("en", "ar"):
            rows.append("  <url>")
            rows.append(f"    <loc>{url_for(page, lang)}</loc>")
            rows.append(f"    <lastmod>{mod}</lastmod>")
            for hl, target in (("en", "en"), ("ar", "ar"), ("x-default", "en")):
                rows.append(f'    <xhtml:link rel="alternate" hreflang="{hl}" href="{url_for(page, target)}"/>')
            rows.append("  </url>")
    rows.append("</urlset>")
    return "\n".join(rows)


# ---------------------------------------------------------------- checks ---
def check_site():
    ref = re.compile(r'\b(?:href|src)="([^"]+)"')
    for rel in [p[0] for p in PAGES] + [f"ar/{p[0]}" for p in PAGES]:
        s = read(rel)
        base = (ROOT / rel).parent
        for link in ref.findall(s):
            if re.match(r"(?:https?:|mailto:|tel:|data:|#|//)", link):
                continue
            target = link.split("#")[0].split("?")[0]
            if not target:
                continue
            path = (base / target)
            if target.endswith("/"):
                path = path / "index.html"
            if not path.exists():
                ERRORS.append(f"{rel}: broken local link {link!r}")
        title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
        if len(title) > 65:
            WARNINGS.append(f"{rel}: title is {len(title)} chars (aim for 60 or less)")
        if len(desc) > 165:
            WARNINGS.append(f"{rel}: description is {len(desc)} chars (aim for 160 or less)")
        if len(re.findall(r"<h1\b", s)) != 1:
            ERRORS.append(f"{rel}: expected exactly one <h1>")
        if not re.search(r'<link rel="canonical" href="[^"]+"', s):
            ERRORS.append(f"{rel}: missing canonical")
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(block)
            except ValueError as exc:
                ERRORS.append(f"{rel}: invalid JSON-LD ({exc})")
        if rel.startswith("ar/") and not re.search(r'<html lang="ar" dir="rtl">', s):
            ERRORS.append(f"{rel}: missing lang=ar dir=rtl")
    for page in PAGES:
        for lang in ("en", "ar"):
            rel = page[0] if lang == "en" else f"ar/{page[0]}"
            canon = re.search(r'<link rel="canonical" href="([^"]+)"', read(rel)).group(1)
            if canon != url_for(page, lang):
                ERRORS.append(f"{rel}: canonical {canon} != {url_for(page, lang)}")


# ------------------------------------------------------------------ main ---
def main():
    home_src = read("index.html")
    for page in PAGES:
        src = read(page[0])
        if "<!-- seo:start" not in src:
            sys.exit(f"{page[0]} has no <!-- seo:start --> / <!-- seo:end --> markers")
        meta = page_meta(src)
        # 1) English page: refresh the SEO block
        en_services = services_from_home(home_src, "en")
        en_src = SEO_RE.sub(lambda m: seo_block(page, "en", meta, en_services), src, count=1)
        write(page[0], en_src)
        # 2) Arabic page: static HTML generated from the English page
        ar_src = build_arabic(page, en_src, meta)
        ar_src = SEO_RE.sub(lambda m: seo_block(page, "ar", meta, services_from_home(home_src, "ar")), ar_src, count=1)
        write(f"ar/{page[0]}", ar_src)
        print(f"built {page[0]}  ->  ar/{page[0]}")
    write("sitemap.xml", build_sitemap())
    print("wrote sitemap.xml")
    check_site()
    for w in dict.fromkeys(WARNINGS):
        print("WARNING:", w)
    for e in ERRORS:
        print("ERROR:", e)
    if ERRORS:
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
