/* Symphony Factory APS: script condiviso (nessuna dipendenza) */
(() => {
  const doc = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header: sfondo allo scroll, si nasconde scendendo ---------- */
  const header = document.querySelector('[data-header]');
  let lastY = window.scrollY;
  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 24);
    const goingDown = y > lastY && y > 320;
    if (!doc.classList.contains('menu-open')) header.classList.toggle('is-hidden', goingDown);
    lastY = y;
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();
  header.addEventListener('focusin', () => header.classList.remove('is-hidden'));

  /* ---------- Menu mobile ---------- */
  const toggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const label = document.querySelector('[data-menu-label]');
  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    label.textContent = open ? 'Chiudi il menu' : 'Apri il menu';
    doc.classList.toggle('menu-open', open);
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(() => menu.classList.add('is-open'));
      const first = menu.querySelector('a');
      if (first) setTimeout(() => first.focus({ preventScroll: true }), 60);
    } else {
      menu.classList.remove('is-open');
      setTimeout(() => { if (!menu.classList.contains('is-open')) menu.hidden = true; }, 400);
    }
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && doc.classList.contains('menu-open')) { setMenu(false); toggle.focus(); }
  });
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  window.matchMedia('(min-width: 1021px)').addEventListener('change', (e) => { if (e.matches) setMenu(false); });
  // Mantiene il focus dentro menu + pulsante quando il menu è aperto
  document.addEventListener('focusin', (e) => {
    if (!doc.classList.contains('menu-open')) return;
    if (!menu.contains(e.target) && e.target !== toggle) toggle.focus();
  });

  /* ---------- Comparsa elementi allo scroll ---------- */
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-in'));
  }

  /* ---------- Testo che si "accende" parola per parola ---------- */
  document.querySelectorAll('[data-fill]').forEach((block) => {
    const walk = (node) => {
      [...node.childNodes].forEach((child) => {
        if (child.nodeType === 3) {
          const frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            const s = document.createElement('span');
            s.className = 'w';
            s.textContent = part;
            frag.appendChild(s);
          });
          child.replaceWith(frag);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    };
    walk(block);
    block.classList.add('fill');
    const words = block.querySelectorAll('.w');
    if (reduceMotion) { words.forEach((w) => w.classList.add('on')); return; }
    let raf = 0;
    const update = () => {
      raf = 0;
      const r = block.getBoundingClientRect();
      const vh = window.innerHeight;
      const start = vh * 0.85;
      const end = vh * 0.35;
      const p = Math.min(1, Math.max(0, (start - r.top) / (start - end + r.height * 0.6)));
      const n = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('on', i < n));
    };
    window.addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---------- Bagliore che segue il puntatore sulle card ---------- */
  if (window.matchMedia('(hover: hover)').matches) {
    document.querySelectorAll('.card').forEach((card) => {
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${e.clientX - r.left}px`);
        card.style.setProperty('--my', `${e.clientY - r.top}px`);
      });
    });
  }

  /* ---------- Copia negli appunti (IBAN, causale…) ---------- */
  const live = document.createElement('div');
  live.className = 'sr-only';
  live.setAttribute('aria-live', 'polite');
  document.body.appendChild(live);
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    const original = btn.innerHTML;
    btn.addEventListener('click', async () => {
      const text = btn.getAttribute('data-copy');
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
      }
      btn.classList.add('is-done');
      btn.innerHTML = '<svg class="i" aria-hidden="true"><use href="#i-check"/></svg>Copiato';
      live.textContent = 'Copiato negli appunti';
      setTimeout(() => { btn.classList.remove('is-done'); btn.innerHTML = original; live.textContent = ''; }, 2200);
    });
  });

  /* ---------- Form contatti: compone un'email (nessun dato passa dal sito) ---------- */
  const form = document.querySelector('[data-mail-form]');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const topic = data.get('argomento');
      const to = topic === 'Eventi e collaborazioni' ? 'maurizia@symphonyfactory.it' : 'info@symphonyfactory.it';
      const subject = `${topic}: richiesta dal sito`;
      const body = `${data.get('messaggio')}\n\n${data.get('nome')}${data.get('email') ? `\n${data.get('email')}` : ''}`;
      window.location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  }

  /* ---------- Indice dello statuto: evidenzia la sezione in lettura ---------- */
  const toc = document.querySelector('[data-toc]');
  if (toc && 'IntersectionObserver' in window) {
    const links = new Map([...toc.querySelectorAll('a')].map((a) => [a.getAttribute('href').slice(1), a]));
    const tio = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        toc.querySelectorAll('.is-active').forEach((a) => a.classList.remove('is-active'));
        const a = links.get(en.target.id);
        if (a) a.classList.add('is-active');
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    links.forEach((_, id) => { const el = document.getElementById(id); if (el) tio.observe(el); });
  }


  /* ---------- Consenso cookie ----------
     La scelta resta salvata nel browser per 6 mesi (chiave "sf-consent").
     Per attivare uno script solo dopo il consenso:
     usa un tag script con type="text/plain", data-consent="statistiche" e data-src="https://..."
     oppure ascolta l'evento: document.addEventListener('sf:consent', (e) => e.detail.statistiche) */
  const KEY = 'sf-consent';
  const MAX_AGE = 1000 * 60 * 60 * 24 * 180;
  const banner = document.querySelector('[data-cookie]');
  const readConsent = () => {
    try {
      const c = JSON.parse(localStorage.getItem(KEY));
      if (c && c.v === 1 && Date.now() - c.date < MAX_AGE) return c;
    } catch (_) { /* storage non disponibile */ }
    return null;
  };
  const applyConsent = (c) => {
    document.querySelectorAll('script[type="text/plain"][data-consent]').forEach((old) => {
      if (!c[old.dataset.consent]) return;
      const s = document.createElement('script');
      if (old.dataset.src) s.src = old.dataset.src; else s.textContent = old.textContent;
      old.replaceWith(s);
    });
    document.dispatchEvent(new CustomEvent('sf:consent', { detail: c }));
  };
  const switches = banner ? banner.querySelectorAll('[data-cookie-cat]') : [];
  const prefs = banner && banner.querySelector('[data-cookie-prefs]');
  const custom = banner && banner.querySelector('[data-cookie-custom]');
  const saveBtn = banner && banner.querySelector('[data-cookie-save]');
  const showPrefs = (show) => {
    prefs.hidden = !show;
    saveBtn.hidden = !show;
    custom.setAttribute('aria-expanded', String(show));
    custom.textContent = show ? 'Nascondi preferenze' : 'Personalizza';
  };
  const openBanner = (withPrefs) => {
    if (!banner) return;
    const c = readConsent();
    switches.forEach((sw) => sw.setAttribute('aria-checked', String(!!(c && c[sw.dataset.cookieCat]))));
    showPrefs(!!withPrefs);
    banner.hidden = false;
    requestAnimationFrame(() => banner.classList.add('is-open'));
  };
  const closeBanner = () => {
    banner.classList.remove('is-open');
    setTimeout(() => { banner.hidden = true; }, 450);
  };
  const saveConsent = (statistiche) => {
    const c = { v: 1, date: Date.now(), necessari: true, statistiche };
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (_) { /* storage non disponibile */ }
    applyConsent(c);
    closeBanner();
  };
  if (banner) {
    banner.querySelector('[data-cookie-accept]').addEventListener('click', () => saveConsent(true));
    banner.querySelector('[data-cookie-reject]').addEventListener('click', () => saveConsent(false));
    saveBtn.addEventListener('click', () => {
      const stat = banner.querySelector('[data-cookie-cat="statistiche"]');
      saveConsent(stat.getAttribute('aria-checked') === 'true');
    });
    custom.addEventListener('click', () => showPrefs(prefs.hidden));
    switches.forEach((sw) => sw.addEventListener('click', () => {
      sw.setAttribute('aria-checked', String(sw.getAttribute('aria-checked') !== 'true'));
    }));
    banner.addEventListener('keydown', (e) => { if (e.key === 'Escape') saveConsent(false); });
    document.querySelectorAll('[data-cookie-open]').forEach((b) => b.addEventListener('click', () => openBanner(true)));
    const existing = readConsent();
    if (existing) applyConsent(existing); else setTimeout(() => openBanner(false), 600);
  }
  window.SFConsent = { get: readConsent, open: () => openBanner(true) };

  /* ---------- Anno nel footer ---------- */
  document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
