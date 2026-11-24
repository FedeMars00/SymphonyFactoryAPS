# Symphony Factory APS: sito web

## Struttura

```
sito/          ← la cartella da caricare online (è il sito completo)
_sorgente/     ← i sorgenti per modificare il sito (non va caricata)
```

Ogni pagina in `sito/` è un file HTML autonomo, con CSS e JS scritti al suo interno.
Fuori dall'HTML restano solo font, immagini e i file per Google (sitemap, robots, ecc.).

## Vedere il sito in locale

I link usano percorsi assoluti (`/attivita/`), quindi serve un piccolo server:

```bash
python3 -m http.server 8765 --directory sito
```

Poi apri http://localhost:8765

## Modificare il sito

Header, footer e stili sono condivisi tra le pagine: modificali in `_sorgente/` e rigenera.

```bash
python3 _sorgente/build.py
```

- `_sorgente/pages/`: contenuti di ogni pagina
- `_sorgente/partials/`: header, footer, icone
- `_sorgente/css/` e `_sorgente/js/`: stili e script (`home.*` solo per la home)
- `_sorgente/build.py`: titoli, descrizioni SEO, FAQ, dati strutturati

Se modifichi direttamente i file in `sito/`, la prossima build li sovrascrive.

## Anteprima su GitHub Pages

L'anteprima è su https://fedemars00.github.io/SymphonyFactoryAPS/ (non indicizzata da Google).
Dopo ogni modifica, aggiornala con:

```bash
bash _sorgente/pubblica-anteprima.sh
```

Lo script genera `_anteprima/` (percorsi adattati alla sottocartella) e la carica sul branch `gh-pages`.

## Messa online

- **Hosting Apache** (Aruba, SiteGround, ecc.): carica il contenuto di `sito/`. Il file `.htaccess` gestisce HTTPS, www, la pagina 404, la cache e i redirect dai vecchi indirizzi di Google Sites.
- **Vercel**: importa la cartella `sito/`. Il file `vercel.json` contiene gli stessi redirect.

Dopo la pubblicazione: verifica il dominio su Google Search Console e invia `https://www.symphonyfactory.it/sitemap.xml`.

## Brand identity 2026/27

Il sito segue il piano di comunicazione e riposizionamento 2026/27 e la brand identity ufficiale.

- **Logo**: vettoriale in `sito/assets/img/logo-symphony-factory.svg` e nel simbolo `#logo` (`_sorgente/partials/logo-symbol.svg`), ricostruito dal font Wonderfull sui PNG ufficiali.
- **Font**: Wonderfull (logo, headline, H1), National Park (H2, H3), DM Mono (testi). Wonderfull non ha accenti: nei titoli che lo usano il build disegna l'accento sopra la lettera (classe `.acc`), come nel manifesto.
- **Palette**: Wine plum #582C36, Sand dune #EDE1CD, Ink Black #011411, Burnt Tangerine #E14630, Magenta Bloom #D13260, Baby Blue #A8D0FF.

## Da verificare con l'associazione

- **Foto**: le foto vengono dal PDF del piano di comunicazione. Molte sembrano immagini di moodboard o di riferimento: vanno sostituite con foto di eventi e attività dell'associazione (o verificati i diritti) prima della pubblicazione definitiva. Le grafiche di Symphony Park e Contest Musicare 2024 riportano ancora il vecchio logo.

- **CAP della sede legale**: è indicato 40134 (via Paride Pasquali, Bologna). Va confermato.
- **Codice fiscale dell'associazione**: va aggiunto nel footer (`_sorgente/partials/footer.html`) e nei dati strutturati.
- **Privacy policy**: il testo è una base. Va confermato il nome del fornitore di hosting e, se l'associazione è iscritta al RUNTS, si possono aggiungere il numero di iscrizione e le informazioni sul 5×1000.
- **Foto**: il sito usa solo grafica generativa. Foto reali di studio ed eventi (in WebP, con testo alternativo) aumenterebbero coinvolgimento e SEO.
