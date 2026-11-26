#!/usr/bin/env python3
"""
Build del sito Symphony Factory APS.

Assembla le pagine in ../sito/ con CSS e JS inline (nessun file .css/.js esterno).
Uso:  python3 _sorgente/build.py
      python3 _sorgente/build.py --preview /NomeRepo   (anteprima per GitHub Pages in _anteprima/)
Modifica i file in _sorgente/ (pagine, partials, css, js) e rilancia lo script:
i file HTML in sito/ vengono rigenerati.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "sito"
# Anteprima (GitHub Pages): il sito vive in una sottocartella, es. /SymphonyFactoryAPS
BASE = ""
PREVIEW = False
if "--preview" in sys.argv:
    PREVIEW = True
    i = sys.argv.index("--preview")
    BASE = sys.argv[i + 1].rstrip("/") if len(sys.argv) > i + 1 else ""
    OUT = ROOT.parent / "_anteprima"


def rebase(text):
    """Antepone BASE ai percorsi assoluti del sito (/assets/..., /contatti/...)."""
    if not BASE:
        return text
    text = re.sub(r'((?:href|src|data-src)=")/(?!/)', rf"\1{BASE}/", text)
    text = re.sub(r'srcset="([^"]+)"', lambda m: 'srcset="' + re.sub(r"(^|,\s*)/(?!/)", r"\g<1>" + BASE + "/", m.group(1)) + '"', text)
    text = text.replace("url(/assets", f"url({BASE}/assets")
    text = text.replace('"href_matches":"/*"', f'"href_matches":"{BASE}/*"')
    text = text.replace('"href_matches":"/404.html"', f'"href_matches":"{BASE}/404.html"')
    return text

SITE = "https://www.symphonyfactory.it"
LASTMOD = "2026-11-24"

ORG_DESC = (
    "Symphony Factory APS è un'associazione di promozione sociale di Bologna: una realtà culturale "
    "e sociale che mette in relazione creatività, benessere e territorio, con laboratori, "
    "progetti artistici, musica, eventi e collaborazioni per attivare spazi della città."
)

# ---------------------------------------------------------------- pagine
# path: URL pubblico · file: sorgente in pages/ · crumb: nome nel breadcrumb
PAGES = [
    {
        "path": "/",
        "file": "index.html",
        "title": "Symphony Factory APS | Creatività, benessere e territorio",
        "description": "Realtà culturale e sociale di Bologna: laboratori, musica, eventi e collaborazioni con enti per dare nuova vita agli spazi della città. Partecipa anche tu.",
        "css": ["home.css"],
        "js": ["home.js"],
        "type": "WebPage",
        "faq": True,
    },
    {
        "path": "/associazione/",
        "file": "associazione.html",
        "crumb": "Chi siamo",
        "title": "Chi siamo: mission, vision e manifesto | Symphony Factory",
        "description": "Symphony Factory APS, Bologna: da dove arriviamo, dove stiamo andando, mission, vision, valori e manifesto di una realtà culturale e sociale.",
        "type": "AboutPage",
    },
    {
        "path": "/attivita/",
        "file": "attivita.html",
        "crumb": "Cosa facciamo",
        "title": "Cosa facciamo: laboratori, musica e spazi | Symphony Factory",
        "description": "Laboratori, workshop e corsi, Home Studio e artisti emergenti, eventi e spazi urbani da riattivare: le attività di Symphony Factory APS a Bologna.",
        "type": "WebPage",
        "css": ["attivita.css"],
        "services": True,
    },
    {
        "path": "/collabora/",
        "file": "collabora.html",
        "crumb": "Collabora",
        "title": "Collabora: per enti, Comuni e partner | Symphony Factory APS",
        "description": "Per amministrazioni, enti e fondazioni: progetti culturali e sociali per attivare spazi sottoutilizzati e restituirli alla comunità, a Bologna e dintorni.",
        "type": "WebPage",
    },
    {
        "path": "/diventa-socio/",
        "file": "diventa-socio.html",
        "crumb": "Partecipa",
        "title": "Partecipa: diventa socio con 10 € | Symphony Factory",
        "description": "Artisti, creativi e persone curiose: entra in Symphony Factory APS con 10 € l'anno. Laboratori, Home Studio, eventi e open call. Aperto dai 14 anni.",
        "type": "WebPage",
        "faq": True,
        "membership": True,
    },
    {
        "path": "/sostienici/",
        "file": "sostienici.html",
        "crumb": "Sostienici",
        "title": "Sostienici con una donazione | Symphony Factory APS",
        "description": "Sostieni Symphony Factory APS con una donazione: i fondi finanziano nuovi progetti culturali e i materiali per artisti e partecipanti a Bologna.",
        "type": "WebPage",
    },
    {
        "path": "/contatti/",
        "file": "contatti.html",
        "crumb": "Contatti",
        "title": "Contatti | Symphony Factory APS Bologna",
        "description": "Contatta Symphony Factory APS: informazioni, partecipazione e collaborazioni a info@symphonyfactory.it, eventi e serate con Maurizia al 366 182 4404.",
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
        "Progettazione culturale",
        "Laboratori e workshop creativi",
        "Rigenerazione di spazi urbani",
        "Direzione artistica",
        "Eventi musicali dal vivo",
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
    ("Che cos'è Symphony Factory?",
     "È un'associazione di promozione sociale di Bologna: una realtà culturale e sociale che mette in relazione creatività, benessere e territorio, con laboratori, progetti artistici, musica, eventi e collaborazioni per dare nuova vita agli spazi della città."),
    ("Chi può partecipare?",
     "Artisti, creativi e chiunque voglia esprimersi e mettersi in gioco. Possono associarsi tutte le persone che hanno compiuto 14 anni e gli enti del Terzo settore o senza scopo di lucro che condividono le nostre finalità."),
    ("Quanto costa iscriversi?",
     "La quota associativa annuale è di 10 € e va versata contestualmente alla compilazione del modulo di iscrizione online."),
    ("Siete un ente o un Comune: come possiamo collaborare?",
     "Scriveteci a info@symphonyfactory.it: vi mandiamo una presentazione dell'associazione e fissiamo un primo incontro per parlare di spazi da valorizzare e progetti culturali e sociali da costruire insieme."),
    ("Organizzate ancora eventi musicali?",
     "Sì. La musica resta una parte fondamentale della nostra identità: Home Studio per i soci, open call, serate ed eventi. Per eventi e serate contatta Maurizia al 366 182 4404."),
    ("Come posso sostenere l'associazione?",
     "Puoi partecipare come socio, dare una mano come volontario oppure fare una donazione con bonifico intestato ad Associazione Symphony Factory APS (IBAN IT37 C084 7236 7600 0000 0121 991, causale “Donazione liberale”)."),
]

FAQ_SOCIO = [
    ("Chi può iscriversi?",
     "Tutte le persone fisiche che hanno compiuto 14 anni, senza alcuna distinzione, e gli enti del Terzo settore o senza scopo di lucro che condividono le finalità dell'associazione."),
    ("Quanto costa e quanto dura la tessera?",
     "La quota associativa è di 10 € all'anno e va versata contestualmente alla compilazione del modulo di iscrizione."),
    ("Devo essere un artista per partecipare?",
     "No. Symphony Factory accoglie artisti, creativi e anche persone curiose che vogliono partecipare alla vita culturale dell'associazione o sostenerne i progetti."),
    ("Quando diventa effettiva l'iscrizione?",
     "La domanda viene valutata dal Consiglio Direttivo, che comunica l'esito entro 60 giorni come previsto dallo statuto."),
    ("Posso votare in assemblea?",
     "Sì: ogni socio ha diritto di voto in assemblea dopo tre mesi dall'iscrizione nel libro degli associati."),
]

SERVICES = [
    ("Laboratori, workshop e corsi", "Esperienze creative legate a linguaggi artistici differenti, aperte a persone di tutte le età."),
    ("Home Studio per i soci", "Hub artistico riservato ai soci: supporto tecnico per trasformare le idee creative in progetti musicali finiti."),
    ("Attivazione di spazi sottoutilizzati", "Collaborazioni con enti e comunità locali per restituire agli spazi una funzione culturale e sociale."),
    ("Eventi e direzione artistica", "Eventi, format e open call, anche in collaborazione con altre associazioni e realtà private."),
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



# ---------------------------------------------------------------- accenti per Wonderfull
# Wonderfull non ha lettere accentate: nei titoli che lo usano la lettera base resta in Wonderfull
# e l'accento viene disegnato in CSS (.acc), come nel manifesto della brand identity.
ACCENTS = {"à": ("a", "g"), "è": ("e", "g"), "é": ("e", "a"), "ì": ("i", "g"), "ò": ("o", "g"), "ù": ("u", "g"),
           "À": ("A", "g"), "È": ("E", "g"), "É": ("E", "a"), "Ì": ("I", "g"), "Ò": ("O", "g"), "Ù": ("U", "g")}
WF_CLASSES = ("wf", "big-text", "manifesto__title", "idea__title", "marquee__group", "menu__list")


def _acc_text(text):
    out = []
    for ch in text:
        if ch in ACCENTS:
            base, kind = ACCENTS[ch]
            up = " acc-up" if base.isupper() else ""
            out.append(f'<span class="acc acc-{kind}{up}" aria-hidden="true">{base}</span><span class="sr-only">{ch}</span>')
        else:
            out.append(ch)
    return "".join(out)


def accentize(doc):
    def fix(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        cls = re.search(r'class="([^"]*)"', attrs)
        classes = cls.group(1).split() if cls else []
        if tag != "h1" and not any(c in WF_CLASSES for c in classes):
            return m.group(0)
        parts = re.split(r"(<[^>]+>)", inner)
        inner = "".join(p if p.startswith("<") else _acc_text(p) for p in parts)
        return f"<{tag}{attrs}>{inner}</{tag}>"
    return re.sub(r"<(h1|h2|h3|p|ul|ol)\b([^>]*)>(.*?)</\1>", fix, doc, flags=re.S)



# ---------------------------------------------------------------- tipografia italiana
# Apostrofi e virgolette tipografiche, spazi non divisibili dove una riga non deve spezzarsi.
# Si applica solo al testo visibile (non ad attributi, script, stili, SVG). Nei titoli in Wonderfull,
# che ha solo i caratteri di base, l'apostrofo resta dritto per non mescolare due font.
NBSP = " "
VOID = {"img", "br", "input", "meta", "link", "hr", "source", "use", "path", "circle", "rect", "ellipse", "line", "polyline", "polygon", "wbr", "area", "col", "embed", "param", "track"}
SKIP = {"script", "style", "svg", "code", "textarea", "pre", "title"}


def _typo_text(t, wf):
    if not wf:
        t = re.sub(r"(?<=\w)'(?=\w)", "’", t)            # l'arte -> l’arte
        t = re.sub(r'"([^"<>\n]{1,80})"', "“\\1”", t)  # "testo" -> “testo”
    t = t.replace("...", "…")
    t = re.sub(r"(\d) €", "\\1" + NBSP + "€", t)              # 10 € non si spezza
    t = re.sub(r"\b(D\.Lgs\.|Art\.|art\.|artt\.|n\.) (?=\d)", "\\1" + NBSP, t)
    t = re.sub(r"(\d+) (anni|giorni|mesi)\b", "\\1" + NBSP + "\\2", t)
    t = re.sub(r"\b(\d{3}) (\d{3}) (\d{4})\b", "\\1" + NBSP + "\\2" + NBSP + "\\3", t)  # numeri di telefono
    return t


def typo(doc):
    head, sep, body = doc.partition("<body")
    if not sep:
        return doc
    parts = re.split(r"(<[^>]+>)", body)
    stack = []  # (tag, wf)
    skip = 0
    out = []
    for part in parts:
        if part.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)([^>]*)>", part)
            if m:
                closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
                if closing:
                    while stack:
                        t, w = stack.pop()
                        if t in SKIP:
                            skip -= 1
                        if t == tag:
                            break
                elif tag not in VOID and not attrs.rstrip().endswith("/"):
                    cls = re.search(r'class="([^"]*)"', attrs)
                    classes = cls.group(1).split() if cls else []
                    parent_wf = stack[-1][1] if stack else False
                    wf = parent_wf or tag == "h1" or any(c in WF_CLASSES for c in classes)
                    stack.append((tag, wf))
                    if tag in SKIP:
                        skip += 1
            out.append(part)
        else:
            wf = stack[-1][1] if stack else False
            out.append(part if skip else _typo_text(part, wf))
    return head + sep + "".join(out)



# ---------------------------------------------------------------- immagini responsive
# Per le foto con una versione leggera (-480.webp) aggiunge srcset e sizes:
# su smartphone il browser scarica la versione piccola.
FOTO = ROOT.parent / "sito" / "assets" / "img" / "foto"


def responsive_imgs(doc):
    def fix(m):
        tag = m.group(0)
        if "srcset=" in tag:
            return tag
        src = re.search(r'src="(/assets/img/foto/([^"]+)\.webp)"', tag)
        w = re.search(r'width="(\d+)"', tag)
        if not src or not w or not (FOTO / f"{src.group(2)}-480.webp").exists():
            return tag
        big, name, width = src.group(1), src.group(2), w.group(1)
        own = re.search(r'\sdata-sizes="([^"]+)"', tag)
        sizes = (own.group(1) if own else None) or m.group("sizes") or "(max-width: 600px) 45vw, (max-width: 1024px) 40vw, 30vw"
        tag = re.sub(r'\sdata-sizes="[^"]+"', "", tag)
        return tag.replace(f'src="{big}"', f'src="{big}" srcset="/assets/img/foto/{name}-480.webp 480w, {big} {width}w" sizes="{sizes}"')
    # le immagini delle card occupano tutta la larghezza su smartphone
    doc = re.sub(r'(?<=<div class="card__img">)<img [^>]*>', lambda m: fix(_with_sizes(m, "(max-width: 680px) 92vw, (max-width: 960px) 46vw, 30vw")), doc)
    doc = re.sub(r"<img [^>]*>", lambda m: fix(_with_sizes(m, None)), doc)
    return doc


class _with_sizes:
    def __init__(self, m, sizes):
        self._m, self._s = m, sizes
    def group(self, k=0):
        return self._s if k == "sizes" else self._m.group(k)


# ---------------------------------------------------------------- assemblaggio
def build():
    if PREVIEW:
        # copia i file statici (font, immagini, icone) e li adatta alla sottocartella
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.copytree(ROOT.parent / "sito", OUT, ignore=shutil.ignore_patterns("*.html", ".htaccess", "vercel.json"))
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        (OUT / ".nojekyll").write_text("", encoding="utf-8")
        mf = OUT / "site.webmanifest"
        mf.write_text(mf.read_text(encoding="utf-8").replace('"/', f'"{BASE}/'), encoding="utf-8")
    base_css = read("css/base.css")
    base_js = read("js/base.js")
    assert "</script" not in base_js.lower(), "base.js non può contenere </script>"
    header = read("partials/header.html")
    footer = read("partials/footer.html")
    sprite = read("partials/sprite.svg")
    sprite = sprite[: sprite.rfind("</svg>")] + read("partials/logo-symbol.svg") + "</svg>\n"
    cookie = read("partials/cookie.html") + read("partials/a11y.html")
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
        content = accentize(content)

        # voce di menu attiva
        def cur(m):
            target = m.group(1)
            return ' aria-current="page"' if path == target else ""
        head_html = re.sub(r"\{\{cur:([^}]+)\}\}", cur, header)
        foot_html = re.sub(r"\{\{cur:([^}]+)\}\}", cur, footer)

        robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
        if PREVIEW:
            robots = "noindex, nofollow"
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
{canonical}<meta name="theme-color" content="#582c36">
<meta name="color-scheme" content="only light">
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
<meta property="og:image:alt" content="Logo di Symphony Factory APS su sfondo vinaccia, con foto di incontri e laboratori">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/wonderfull.ttf" as="font" type="font/ttf" crossorigin>
<link rel="preload" href="/assets/fonts/dmmono-400.woff2" as="font" type="font/woff2" crossorigin>
<script>(function(d){{d.classList.replace('no-js','js');try{{var a=JSON.parse(localStorage.getItem('sf-a11y')||'{{}}');if(a.size)d.classList.add('a11y-text-'+a.size);['contrast','readable','spacing','links','motion'].forEach(function(k){{if(a[k])d.classList.add('a11y-'+k)}})}}catch(e){{}}}})(document.documentElement)</script>
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
        doc = rebase(responsive_imgs(typo(doc)))
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
    print(f"  ✓ {OUT.name}/sitemap.xml")


if __name__ == "__main__":
    build()
