/* Home: la "tavola bianca". Le foto si possono spostare con mouse e dito, anche da smartphone.
   Toccare una foto la sposta; lo scroll della pagina resta libero sul resto del hero. */
(() => {
  const board = document.querySelector('[data-board]');
  if (!board) return;
  const hero = board.closest('[data-hero]');
  const photos = [...board.querySelectorAll('[data-drag]')];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let z = 10;

  photos.forEach((ph) => {
    let startX = 0, startY = 0, baseX = 0, baseY = 0, t0 = 0, moved = 0, active = false;
    // a fine animazione d'ingresso la foto resta visibile senza dipendere dal fill dell'animazione
    ph.addEventListener('animationend', (e) => {
      if (e.animationName === 'drop') ph.classList.add('is-in');
      if (e.animationName === 'ph-pop') ph.classList.remove('is-tapped');
    });
    const pos = () => ({
      x: parseFloat(ph.style.getPropertyValue('--dx')) || 0,
      y: parseFloat(ph.style.getPropertyValue('--dy')) || 0,
    });
    ph.addEventListener('pointerdown', (e) => {
      if (e.button > 0) return;
      e.preventDefault();
      active = true;
      try { ph.setPointerCapture(e.pointerId); } catch (_) { /* puntatore non catturabile */ }
      ({ x: baseX, y: baseY } = pos());
      startX = e.clientX; startY = e.clientY; t0 = Date.now(); moved = 0;
      ph.classList.add('is-in');
      ph.style.zIndex = String(++z);
      ph.classList.add('is-dragging');
      hero.classList.add('is-touched');
      if (e.pointerType === 'touch' && 'vibrate' in navigator) { try { navigator.vibrate(8); } catch (_) { /* non supportato */ } }
    });
    ph.addEventListener('pointermove', (e) => {
      if (!active) return;
      const hb = hero.getBoundingClientRect();
      const r = ph.getBoundingClientRect();
      const cur = pos();
      // rettangolo della foto senza spostamento, per tenerla dentro il hero (almeno 40px visibili)
      const nl = r.left - cur.x, nt = r.top - cur.y;
      const w = r.width, h = r.height, keep = 40;
      const dx = Math.max(hb.left - nl - w + keep, Math.min(hb.right - nl - keep, baseX + e.clientX - startX));
      const dy = Math.max(hb.top - nt - h + keep, Math.min(hb.bottom - nt - keep, baseY + e.clientY - startY));
      moved = Math.max(moved, Math.abs(e.clientX - startX), Math.abs(e.clientY - startY));
      ph.style.setProperty('--dx', `${dx.toFixed(1)}px`);
      ph.style.setProperty('--dy', `${dy.toFixed(1)}px`);
    });
    const end = () => {
      if (!active) return;
      active = false;
      ph.classList.remove('is-dragging');
      // posa leggermente storta, come una foto appoggiata a mano
      if (!reduce) ph.style.setProperty('--r', `${(Math.random() * 10 - 5).toFixed(1)}deg`);
      // tocco senza spostamento: la foto sobbalza e il nastro si stacca un attimo
      if (!reduce && moved < 6 && Date.now() - t0 < 450) {
        ph.classList.remove('is-tapped');
        void ph.offsetWidth;
        ph.classList.add('is-tapped');
      }
    };
    // un ascoltatore di click rende la foto "toccabile" per Safari e Chrome mobile:
    // senza, il tocco vicino a un pulsante verrebbe dirottato sul pulsante
    ph.addEventListener('click', (e) => e.preventDefault());
    ph.addEventListener('pointerup', end);
    ph.addEventListener('pointercancel', end);
    ph.addEventListener('lostpointercapture', end);
  });
})();
