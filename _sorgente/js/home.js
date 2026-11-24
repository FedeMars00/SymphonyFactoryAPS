/* Home: la "tavola bianca". Le foto si possono spostare con mouse e dito (da tablet in su). */
(() => {
  const board = document.querySelector('[data-board]');
  if (!board) return;
  const hero = board.closest('[data-hero]');
  const photos = [...board.querySelectorAll('[data-drag]')];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canDrag = window.matchMedia('(min-width: 601px)');
  let z = 10;

  photos.forEach((ph) => {
    let startX = 0, startY = 0, baseX = 0, baseY = 0, active = false;
    const pos = () => ({
      x: parseFloat(ph.style.getPropertyValue('--dx')) || 0,
      y: parseFloat(ph.style.getPropertyValue('--dy')) || 0,
    });
    ph.addEventListener('pointerdown', (e) => {
      if (!canDrag.matches || e.button > 0) return;
      e.preventDefault();
      active = true;
      try { ph.setPointerCapture(e.pointerId); } catch (_) { /* puntatore non catturabile */ }
      ({ x: baseX, y: baseY } = pos());
      startX = e.clientX; startY = e.clientY;
      ph.style.zIndex = String(++z);
      ph.classList.add('is-dragging');
      hero.classList.add('is-touched');
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
      ph.style.setProperty('--dx', `${dx.toFixed(1)}px`);
      ph.style.setProperty('--dy', `${dy.toFixed(1)}px`);
    });
    const end = () => {
      if (!active) return;
      active = false;
      ph.classList.remove('is-dragging');
      // posa leggermente storta, come una foto appoggiata a mano
      if (!reduce) ph.style.setProperty('--r', `${(Math.random() * 10 - 5).toFixed(1)}deg`);
    };
    ph.addEventListener('pointerup', end);
    ph.addEventListener('pointercancel', end);
    ph.addEventListener('lostpointercapture', end);
  });
})();
