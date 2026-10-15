#!/usr/bin/env python3
"""
Build del sito Symphony Factory APS.

Assembla le pagine in ../sito/ con CSS e JS inline (nessun file .css/.js esterno).
Uso:  python3 _sorgente/build.py
Modifica i file in _sorgente/ (pagine, partials, css, js) e rilancia lo script:
i file HTML in sito/ vengono rigenerati.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "sito"
SITE = "https://www.symphonyfactory.it"
LASTMOD = "2026-10-15"

ORG_DESC = (
    "Symphony Factory APS è un'associazione di promozione sociale di Bologna che promuove "
    "la cultura musicale e artistica attraverso la contaminazione e sostiene lo sviluppo "
    "dei progetti degli artisti associati."
)

# ---------------------------------------------------------------- pagine
# path: URL pubblico · file: sorgente in pages/ · crumb: nome nel breadcrumb
PAGES = [
    {
        "path": "/",
        "file": "index.html",
        "title": "Symphony Factory APS | Associazione musicale a Bologna",
        "description": "Associazione di promozione sociale a Bologna: home studio per i soci, eventi e direzione artistica per artisti emergenti. Diventa socio con 10 € l'anno.",
        "css": ["home.css"],
        "js": ["home.js"],
        "type": "WebPage",
        "faq": True,
    },
    {
        "path": "/associazione/",
        "file": "associazione.html",
        "crumb": "L'associazione",
        "title": "L'associazione | Symphony Factory APS Bologna",
        "description": "Chi siamo: un'associazione di promozione sociale nata a Bologna dalla passione per la musica e l'arte. Missione, valori, statuto e come partecipare.",
        "type": "AboutPage",
    },
    {
        "path": "/attivita/",
        "file": "attivita.html",
        "crumb": "Attività",
        "title": "Home studio, eventi e formazione | Symphony Factory",
        "description": "Home studio per i soci, direzione artistica di eventi e format, workshop e progetti educativi: le attività di Symphony Factory APS a Bologna.",
        "type": "WebPage",
        "css": ["attivita.css"],
        "services": True,
    },
    {
        "path": "/diventa-socio/",
        "file": "diventa-socio.html",
        "crumb": "Diventa socio",
        "title": "Diventa socio a 10 € l'anno | Symphony Factory APS",
        "description": "Iscriviti a Symphony Factory APS: quota annuale di 10 €, accesso all'home studio, eventi e iniziative. Aperto ad artisti e sostenitori dai 14 anni.",
        "type": "WebPage",
        "faq": True,
        "membership": True,
    },
    {
        "path": "/sostienici/",
        "file": "sostienici.html",
        "crumb": "Sostienici",
        "title": "Sostienici con una donazione | Symphony Factory APS",
        "description": "Sostieni la musica emergente a Bologna con una donazione a Symphony Factory APS: i fondi finanziano nuovi progetti e i materiali dell'home studio.",
        "type": "WebPage",
    },
    {
        "path": "/contatti/",
        "file": "contatti.html",
        "crumb": "Contatti",
        "title": "Contatti | Symphony Factory APS Bologna",
        "description": "Contatta Symphony Factory APS: informazioni su associazione e tesseramento a info@symphonyfactory.it, eventi e serate musicali con Maurizia al 366 182 4404.",
        "type": "ContactPage",
    },
    {
        "path": "/statuto/",
        "file": "statuto.html",
        "crumb": "Statuto",
        "css": ["statuto.css"],
        "title": "Statuto dell'associazione | Symphony Factory APS",
        "description": "Lo statuto di Symphony Factory, associazione di promozione sociale con sede a Bologna, costituita ai sensi del Codice del Terzo Settore (D.Lgs. 117/2017).",
        "type": "WebPage",
    },
    {
        "path": "/privacy/",
        "file": "privacy.html",
        "crumb": "Privacy e cookie",
        "title": "Privacy e cookie policy | Symphony Factory APS",
        "description": "Informativa privacy e cookie del sito di Symphony Factory APS: nessun cookie di profilazione, statistiche solo con il tuo consenso.",
        "type": "WebPage",
    },
    {
        "path": "/404.html",
        "file": "404.html",
        "title": "Pagina non trovata | Symphony Factory APS",
        "description": "La pagina che cerchi non esiste o è stata spostata.",
        "type": "WebPage",
        "noindex": True,
        "nositemap": True,
    },
]

# ---------------------------------------------------------------- dati strutturati
ORG = {
    "@type": "NGO",
    "@id": f"{SITE}/#organization",
    "name": "Symphony Factory APS",
    "legalName": "Symphony Factory Associazione di Promozione Sociale",
    "alternateName": ["Symphony Factory", "Symphony Factory - APS"],
    "url": f"{SITE}/",
    "logo": {
        "@type": "ImageObject",
        "url": f"{SITE}/assets/img/logo-512.png",
        "width": 512,
        "height": 512,
    },
    "image": f"{SITE}/assets/img/og-image.jpg",
    "description": ORG_DESC,
    "email": "info@symphonyfactory.it",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Via Paride Pasquali 9",
        "postalCode": "40134",
        "addressLocality": "Bologna",
        "addressRegion": "BO",
        "addressCountry": "IT",
    },
    "areaServed": {"@type": "City", "name": "Bologna"},
    "contactPoint": [
        {
            "@type": "ContactPoint",
            "contactType": "Informazioni generali e tesseramento",
            "email": "info@symphonyfactory.it",
            "availableLanguage": "it",
        },
        {
            "@type": "ContactPoint",
            "contactType": "Eventi e serate musicali",
            "name": "Maurizia",
            "telephone": "+39 366 182 4404",
            "email": "maurizia@symphonyfactory.it",
            "availableLanguage": "it",
        },
    ],
    "sameAs": [
        "https://www.instagram.com/symphony_factory_aps/",
        "https://www.facebook.com/SymphonyFactory",
    ],
    "knowsAbout": [
        "Cultura musicale",
        "Produzione musicale",
        "Direzione artistica",
        "Eventi musicali dal vivo",
        "Formazione musicale",
        "Artisti emergenti",
    ],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": f"{SITE}/#website",
    "url": f"{SITE}/",
    "name": "Symphony Factory APS",
    "inLanguage": "it-IT",
    "publisher": {"@id": f"{SITE}/#organization"},
}

FAQ_HOME = [
    ("Chi può diventare socio di Symphony Factory?",
     "Possono associarsi tutte le persone che hanno compiuto 14 anni e condividono le finalità dell'associazione, oltre ad altri enti del Terzo settore o senza scopo di lucro. Aspettiamo sia artisti sia persone che vogliono sostenere il progetto."),
    ("Quanto costa iscriversi?",
     "La quota associativa annuale è di 10 € e va versata contestualmente alla compilazione del modulo di iscrizione online."),
    ("Che cos'è l'home studio di Symphony Factory?",
     "È un hub artistico riservato ai soci: offriamo supporto tecnico per trasformare le idee creative in progetti musicali finiti, pronti per essere diffusi e valorizzati."),
    ("Organizzate eventi e serate musicali?",
     "Sì. La nostra direzione artistica crea eventi e format, anche in collaborazione con altre associazioni e realtà private. Per proporre una collaborazione contatta Maurizia al 366 182 4404 o scrivi a maurizia@symphonyfactory.it."),
    ("Come posso sostenere l'associazione?",
     "Puoi diventare socio oppure fare una donazione con bonifico intestato ad Associazione Symphony Factory APS (IBAN IT37 C084 7236 7600 0000 0121 991, causale “Donazione liberale”). Le donazioni finanziano nuovi progetti e i materiali dell'home studio."),
]

FAQ_SOCIO = [
    ("Chi può iscriversi?",
     "Tutte le persone fisiche che hanno compiuto 14 anni, senza alcuna distinzione, e gli enti del Terzo settore o senza scopo di lucro che condividono le finalità dell'associazione."),
    ("Quanto costa e quanto dura la tessera?",
     "La quota associativa è di 10 € all'anno e va versata contestualmente alla compilazione del modulo di iscrizione."),
    ("Devo essere un musicista per associarmi?",
     "No. Symphony Factory accoglie artisti e anche persone interessate a supportare il progetto e a partecipare alla vita dell'associazione."),
    ("Quando diventa effettiva l'iscrizione?",
     "La domanda viene valutata dal Consiglio Direttivo, che comunica l'esito entro 60 giorni come previsto dallo statuto."),
    ("Posso votare in assemblea?",
     "Sì: ogni socio ha diritto di voto in assemblea dopo tre mesi dall'iscrizione nel libro degli associati."),
]

SERVICES = [
    ("Home Studio per i soci", "Hub artistico riservato ai soci: supporto tecnico per trasformare le idee creative in progetti musicali finiti."),
    ("Direzione artistica di eventi e format", "Creazione di eventi e format musicali, anche in collaborazione con altre associazioni e realtà private, per valorizzare giovani artisti emergenti."),
    ("Workshop, seminari e masterclass", "Percorsi di formazione musicale per diffondere la cultura musicale e far crescere le competenze degli artisti."),
]


def jsonld(page):
    url = SITE + ("/" if page["path"] == "/" else page["path"])
    graph = [ORG, WEBSITE]
    webpage = {
        "@type": page.get("type", "WebPage"),
        "@id": f"{url}#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "inLanguage": "it-IT",
        "isPartOf": {"@id": f"{SITE}/#website"},
        "about": {"@id": f"{SITE}/#organization"},
        "primaryImageOfPage": {"@type": "ImageObject", "url": f"{SITE}/assets/img/og-image.jpg"},
        "dateModified": LASTMOD,
    }
    if "crumb" in page:
        webpage["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
        graph.append({
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url},
            ],
        })
    graph.append(webpage)
    if page.get("faq"):
        faqs = FAQ_HOME if page["path"] == "/" else FAQ_SOCIO
        graph.append({
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs
            ],
        })
    if page.get("services"):
        for name, desc in SERVICES:
            graph.append({
                "@type": "Service",
                "name": name,
                "description": desc,
                "provider": {"@id": f"{SITE}/#organization"},
                "areaServed": {"@type": "City", "name": "Bologna"},
            })
    if page.get("membership"):
        graph.append({
            "@type": "Service",
            "name": "Tesseramento annuale Symphony Factory APS",
            "description": "Quota associativa annuale per diventare socio di Symphony Factory APS.",
            "provider": {"@id": f"{SITE}/#organization"},
            "areaServed": {"@type": "City", "name": "Bologna"},
            "offers": {
                "@type": "Offer",
                "price": "10.00",
                "priceCurrency": "EUR",
                "url": f"{SITE}/diventa-socio/",
            },
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- helpers
def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def compact_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\n\s*\n+", "\n", css)
    css = re.sub(r"^[ \t]+", "", css, flags=re.M)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r"([a-z-]):\s+", r"\1:", css)
    css = css.replace(";}", "}")
    return css.strip()


def faq_html(items, heading_id="faq-title"):
    out = []
    for q, a in items:
        out.append(
            '<details class="faq__item">'
            f'<summary><span>{html.escape(q)}</span><span class="faq__icon" aria-hidden="true"></span></summary>'
            f'<div class="faq__answer"><p>{html.escape(a)}</p></div>'
            "</details>"
        )
    return "\n".join(out)


VINYL_COUNT = [0]


def vinyl(cls=""):
    VINYL_COUNT[0] += 1
    i = VINYL_COUNT[0]
    return f"""<div class="vinyl {cls}" aria-hidden="true">
  <div class="vinyl__glow"></div>
  <div class="vinyl__disc">
    <div class="vinyl__label">
      <svg viewBox="0 0 200 200" focusable="false">
        <defs>
          <path id="vo{i}" d="M100 100m-74 0a74 74 0 1 1 148 0a74 74 0 1 1-148 0"/>
          <path id="vi{i}" d="M100 100m-52 0a52 52 0 1 1 104 0a52 52 0 1 1-104 0"/>
        </defs>
        <text class="vinyl__t1"><textPath href="#vo{i}" textLength="460" lengthAdjust="spacing">SYMPHONY FACTORY ✦ APS ✦ BOLOGNA ✦</textPath></text>
        <text class="vinyl__t2"><textPath href="#vi{i}" textLength="322" lengthAdjust="spacing">LATO A ✦ 33⅓ GIRI ✦ STEREO ✦</textPath></text>
      </svg>
    </div>
  </div>
  <div class="vinyl__sheen"></div>
</div>"""


def breadcrumb(page):
    if page["path"] in ("/", "/404.html"):
        return ""
    return (
        '<nav class="crumbs" aria-label="Percorso di navigazione"><ol>'
        '<li><a href="/">Home</a></li>'
        f'<li><span aria-current="page">{html.escape(page["crumb"])}</span></li>'
        "</ol></nav>"
    )


# ---------------------------------------------------------------- statuto
def nodash(t):
    """Toglie i trattini lunghi/medi: 'Vice – Presidente' -> 'Vice-Presidente', il resto diventa virgola."""
    t = re.sub(r"(\w)\s*[–—]\s*(\w)", r"\1-\2", t)
    return re.sub(r"\s*[–—]\s*", ", ", t)


def build_statuto():
    lines = read("data/statuto.txt").splitlines()
    body, toc = [], []
    titolo_n = 0
    open_titolo = False
    list_open = False

    def close_list():
        nonlocal list_open
        if list_open:
            body.append("</ul>")
            list_open = False

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("====") or line in ("STATUTO", "ASSOCIAZIONE DI PROMOZIONE SOCIALE", "“SYMPHONY FACTORY”"):
            continue
        m_t = re.match(r"^Titolo\s+([IVX]+)\s*[–-]\s*(.+)$", line)
        m_a = re.match(r"^Art\.\s*(\d+)\s*[–-]?\s*(.+)$", line)
        m_sub = re.match(r"^(\d+\.\d+)\s*[–-]?\s*(.+)$", line)
        line = nodash(line) if not (m_a or m_sub) else line
        esc = html.escape(line, quote=False)
        if m_t:
            close_list()
            if open_titolo:
                body.append("</section>")
            titolo_n += 1
            tid = f"titolo-{titolo_n}"
            body.append(f'<section class="statuto__titolo" aria-labelledby="{tid}">')
            body.append(f'<h2 id="{tid}"><span class="statuto__kicker">Titolo {m_t.group(1)}</span>{html.escape(nodash(m_t.group(2)))}</h2>')
            toc.append({"id": tid, "label": f"Titolo {m_t.group(1)} · {nodash(m_t.group(2))}", "arts": []})
            open_titolo = True
        elif m_a:
            close_list()
            aid = f"t{titolo_n}-art-{m_a.group(1)}"
            title = nodash(m_a.group(2).strip())
            title = title[0].upper() + title[1:]
            body.append(f'<h3 id="{aid}"><span>Art. {m_a.group(1)}</span> {html.escape(title)}</h3>')
            toc[-1]["arts"].append({"id": aid, "label": f"Art. {m_a.group(1)} · {title}"})
        elif m_sub:
            close_list()
            t = nodash(m_sub.group(2).strip())
            body.append(f"<h4>{m_sub.group(1)} {html.escape(t[0].upper() + t[1:])}</h4>")
        elif line.startswith("●"):
            if not list_open:
                body.append("<ul>")
                list_open = True
            body.append(f"<li>{html.escape(line.lstrip('● ').strip(), quote=False)}</li>")
        elif re.match(r"^[a-z][\)\.]\s", line):
            close_list()
            body.append(f'<p class="statuto__item">{esc}</p>')
        else:
            close_list()
            body.append(f"<p>{esc}</p>")
    close_list()
    if open_titolo:
        body.append("</section>")

    toc_html = ['<ol class="toc__list">']
    for t in toc:
        toc_html.append(f'<li><a href="#{t["id"]}">{html.escape(t["label"])}</a><ol>')
        for a in t["arts"]:
            toc_html.append(f'<li><a href="#{a["id"]}">{html.escape(a["label"])}</a></li>')
        toc_html.append("</ol></li>")
    toc_html.append("</ol>")
    return "\n".join(body), "\n".join(toc_html)


# ---------------------------------------------------------------- assemblaggio
def build():
    base_css = read("css/base.css")
    base_js = read("js/base.js")
    assert "</script" not in base_js.lower(), "base.js non può contenere </script>"
    header = read("partials/header.html")
    footer = read("partials/footer.html")
    sprite = read("partials/sprite.svg")
    cookie = read("partials/cookie.html")
    statuto_body, statuto_toc = build_statuto()

    sitemap = []
    for page in PAGES:
        VINYL_COUNT[0] = 0
        path = page["path"]
        url = SITE + path
        content = read("pages/" + page["file"])

        css = base_css + "\n" + "\n".join(read("css/" + c) for c in page.get("css", []))
        js_page = "\n".join(read("js/" + j) for j in page.get("js", []))

        # macro nei contenuti
        content = content.replace("{{breadcrumb}}", breadcrumb(page))
        content = content.replace("{{faq_home}}", faq_html(FAQ_HOME))
        content = content.replace("{{faq_socio}}", faq_html(FAQ_SOCIO))
        content = content.replace("{{statuto_body}}", statuto_body)
        content = content.replace("{{statuto_toc}}", statuto_toc)
        content = re.sub(r"\{\{vinyl(?::([^}]*))?\}\}", lambda m: vinyl(m.group(1) or ""), content)

        # voce di menu attiva
        def cur(m):
            target = m.group(1)
            return ' aria-current="page"' if path == target else ""
        head_html = re.sub(r"\{\{cur:([^}]+)\}\}", cur, header)
        foot_html = re.sub(r"\{\{cur:([^}]+)\}\}", cur, footer)

        robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
        canonical = "" if page.get("noindex") else f'<link rel="canonical" href="{url}">\n'
        og_url = "" if page.get("noindex") else f'<meta property="og:url" content="{url}">\n'
        title = html.escape(page["title"])
        desc = html.escape(page["description"])

        doc = f"""<!doctype html>
<html lang="it" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
{canonical}<meta name="theme-color" content="#0f0e0d">
<meta name="author" content="Symphony Factory APS">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Symphony Factory APS">
<meta property="og:locale" content="it_IT">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
{og_url}<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Logo di Symphony Factory APS con un disco in vinile che sorge sull'orizzonte">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/montserrat-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/fraunces-italic-500.woff2" as="font" type="font/woff2" crossorigin>
<script>document.documentElement.classList.replace('no-js','js')</script>
<style>
{compact_css(css)}
</style>
<script type="application/ld+json">
{jsonld(page)}
</script>
<script type="speculationrules">
{{"prerender":[{{"where":{{"and":[{{"href_matches":"/*"}},{{"not":{{"href_matches":"/404.html"}}}}]}},"eagerness":"moderate"}}]}}
</script>
</head>
<body class="page-{page['file'].replace('.html', '')}">
{sprite}
<a class="skip-link" href="#main">Vai al contenuto</a>
{head_html}
<main id="main" tabindex="-1">
{content}
</main>
{foot_html}
{cookie}
<script>
{base_js}
</script>
{"<script>" + chr(10) + js_page + chr(10) + "</script>" if js_page else ""}
</body>
</html>
"""
        if path == "/":
            target = OUT / "index.html"
        elif path.endswith(".html"):
            target = OUT / path.lstrip("/")
        else:
            target = OUT / path.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding="utf-8")
        print(f"  ✓ {target.relative_to(OUT.parent)}  ({len(doc.encode()) // 1024} KB)")

        if not page.get("nositemap"):
            sitemap.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>")

    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap)
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    print("  ✓ sito/sitemap.xml")


if __name__ == "__main__":
    build()
