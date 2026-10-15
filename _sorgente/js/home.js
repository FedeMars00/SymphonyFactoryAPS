/* Home: giradischi interattivo: rotazione, scratch, riflesso, onda e audio generativo */
(() => {
  const hero = document.querySelector('[data-hero]');
  if (!hero) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const vinyl = hero.querySelector('.vinyl');
  const disc = vinyl.querySelector('.vinyl__disc');
  const canvas = hero.querySelector('[data-wave]');
  const g = canvas.getContext('2d');
  const playBtn = hero.querySelector('[data-play]');
  const playLabel = hero.querySelector('[data-play-label]');

  const IDLE = reduce ? 0 : 22;   // gradi al secondo, a riposo
  const PLAY = 200;               // 33⅓ giri al minuto
  let angle = Math.random() * 360;
  let vel = IDLE;
  let target = IDLE;
  let dragging = false;
  let lastA = 0, lastT = 0, dragVel = 0;
  let sheen = 200, sheenTarget = 200, lastPointer = 0;
  let px = -1;
  let playing = false;
  let visible = true;
  let level = 0;
  let raf = 0;
  let engine = null;

  const center = () => {
    const r = disc.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  };
  const angleTo = (x, y) => {
    const c = center();
    return (Math.atan2(y - c.y, x - c.x) * 180) / Math.PI;
  };

  /* ---------- Riflesso che segue il puntatore ---------- */
  hero.addEventListener('pointermove', (e) => {
    const hr = hero.getBoundingClientRect();
    px = e.clientX - hr.left;
    sheenTarget = angleTo(e.clientX, e.clientY) + 90 - 16;
    lastPointer = performance.now();
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { px = -1; });

  /* ---------- Scratch con mouse o penna ---------- */
  // Col dito: il disco lascia al browser lo scorrimento verticale (touch-action: pan-y)
  // e intercetta i trascinamenti orizzontali, con sensibilità maggiore e una piccola vibrazione.
  const hints = hero.querySelectorAll('[data-hint]');
  const canVibrate = 'vibrate' in navigator;
  let touchGain = 1;
  let travel = 0;
  disc.addEventListener('pointerdown', (e) => {
    if (e.button > 0) return;
    if (e.pointerType !== 'touch') e.preventDefault();
    touchGain = e.pointerType === 'touch' ? 1.6 : 1;
    dragging = true;
    try { disc.setPointerCapture(e.pointerId); } catch (_) { /* puntatore non catturabile */ }
    lastA = angleTo(e.clientX, e.clientY);
    lastT = performance.now();
    dragVel = 0;
    travel = 0;
    hints.forEach((h) => { h.hidden = true; });
  });
  disc.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const a = angleTo(e.clientX, e.clientY);
    let d = a - lastA;
    if (d > 180) d -= 360;
    if (d < -180) d += 360;
    d *= touchGain;
    const now = performance.now();
    const dt = Math.max(8, now - lastT) / 1000;
    angle += d;
    dragVel = dragVel * 0.6 + (d / dt) * 0.4;
    lastA = a;
    lastT = now;
    if (engine && playing) engine.scratch(true, dragVel);
    if (touchGain > 1 && canVibrate) {
      travel += Math.abs(d);
      if (travel > 40) { travel = 0; try { navigator.vibrate(6); } catch (_) { /* non supportato */ } }
    }
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    vel = Math.max(-1200, Math.min(1200, dragVel));
    if (engine) engine.scratch(false);
  };
  disc.addEventListener('pointerup', endDrag);
  disc.addEventListener('pointercancel', endDrag);
  disc.addEventListener('lostpointercapture', endDrag);

  /* ---------- Onda sull'orizzonte ---------- */
  const DPR = Math.min(2, window.devicePixelRatio || 1);
  let W = 0, H = 0, strokeGold = null, strokePeach = null;
  const resize = () => {
    const r = canvas.getBoundingClientRect();
    W = r.width; H = r.height;
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    g.setTransform(DPR, 0, 0, DPR, 0, 0);
    strokeGold = g.createLinearGradient(0, 0, W, 0);
    strokeGold.addColorStop(0, 'rgba(233,194,122,0)');
    strokeGold.addColorStop(0.12, 'rgba(233,194,122,.85)');
    strokeGold.addColorStop(0.88, 'rgba(233,194,122,.85)');
    strokeGold.addColorStop(1, 'rgba(233,194,122,0)');
    strokePeach = g.createLinearGradient(0, 0, W, 0);
    strokePeach.addColorStop(0, 'rgba(242,155,95,0)');
    strokePeach.addColorStop(0.5, 'rgba(242,155,95,.45)');
    strokePeach.addColorStop(1, 'rgba(242,155,95,0)');
  };
  new ResizeObserver(resize).observe(canvas);
  resize();

  const ys = [];
  const draw = (t, data) => {
    g.clearRect(0, 0, W, H);
    const mid = H / 2;
    const N = Math.max(60, Math.ceil(W / 4));
    for (let i = 0; i <= N; i++) {
      const x = (i / N) * W;
      const edge = Math.sin((Math.PI * i) / N);
      let y;
      if (data) {
        const v = (data[Math.floor((i / N) * (data.length - 1))] - 128) / 128;
        y = v * (30 + level * 70) * edge;
      } else {
        let amp = 3.2;
        if (px >= 0) {
          const dx = (x - px) / 150;
          amp += 18 * Math.exp(-dx * dx);
        }
        y = (Math.sin(x * 0.017 + t * 0.0015) * 0.62 + Math.sin(x * 0.043 - t * 0.0024) * 0.38) * amp * edge;
      }
      ys[i] = y;
    }
    g.lineJoin = 'round';
    g.lineWidth = 1.6;
    g.strokeStyle = strokeGold;
    if (W > 720) { g.shadowColor = 'rgba(242,155,95,.75)'; g.shadowBlur = 10; }
    g.beginPath();
    for (let i = 0; i <= N; i++) {
      const x = (i / N) * W;
      if (i) g.lineTo(x, mid + ys[i]); else g.moveTo(x, mid + ys[i]);
    }
    g.stroke();
    g.shadowBlur = 0;
    g.lineWidth = 1;
    g.strokeStyle = strokePeach;
    g.beginPath();
    for (let i = 0; i <= N; i++) {
      const x = (i / N) * W;
      const y = mid - ys[i] * 0.55;
      if (i) g.lineTo(x, y); else g.moveTo(x, y);
    }
    g.stroke();
  };

  /* ---------- Ciclo di animazione ---------- */
  let prev = performance.now();
  const loop = (now) => {
    raf = 0;
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    if (!dragging) {
      vel += (target - vel) * Math.min(1, dt * (playing ? 1.4 : 2));
      angle += vel * dt;
    }
    disc.style.transform = `rotate(${angle.toFixed(2)}deg)`;

    if (now - lastPointer > 2500) sheenTarget = 196 + Math.sin(now * 0.0004) * 26;
    const diff = ((sheenTarget - sheen + 540) % 360) - 180;
    sheen += diff * Math.min(1, dt * 4);
    vinyl.style.setProperty('--sheen', `${sheen.toFixed(1)}deg`);

    let data = null;
    if (engine && playing) {
      data = engine.wave();
      let s = 0;
      for (let i = 0; i < data.length; i += 8) { const v = (data[i] - 128) / 128; s += v * v; }
      const rms = Math.min(1, Math.sqrt(s / (data.length / 8)) * 4.5);
      level += (rms - level) * 0.25;
    } else {
      level *= 0.9;
    }
    vinyl.style.setProperty('--glow', (1 + level * 0.3).toFixed(3));
    draw(reduce ? 0 : now, data);

    if (visible && !document.hidden) raf = requestAnimationFrame(loop);
  };
  const run = () => {
    if (!raf) { prev = performance.now(); raf = requestAnimationFrame(loop); }
  };
  new IntersectionObserver(([en]) => {
    visible = en.isIntersecting;
    if (visible) run();
    else if (playing) toggle(false);
  }, { threshold: 0.05 }).observe(hero);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && playing) toggle(false);
    if (!document.hidden && visible) run();
  });

  /* ---------- Motore audio generativo (Web Audio, nessun file) ---------- */
  /* Su iPhone l'audio Web Audio è trattato come "ambiente": con l'interruttore
     silenzioso attivo non si sente. Lo spostiamo nella categoria "riproduzione"
     (API audioSession dove esiste, altrimenti un elemento <audio> muto in loop,
     avviato dentro il tocco dell'utente). */
  let unlockEl = null;
  const silentWav = () => {
    const n = 4000;
    const b = new Uint8Array(44 + n);
    const v = new DataView(b.buffer);
    const str = (o, t) => [...t].forEach((c, i) => { b[o + i] = c.charCodeAt(0); });
    str(0, 'RIFF'); v.setUint32(4, 36 + n, true); str(8, 'WAVEfmt ');
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, 8000, true); v.setUint32(28, 8000, true); v.setUint16(32, 1, true); v.setUint16(34, 8, true);
    str(36, 'data'); v.setUint32(40, n, true); b.fill(128, 44);
    let bin = '';
    b.forEach((x) => { bin += String.fromCharCode(x); });
    return `data:audio/wav;base64,${btoa(bin)}`;
  };
  const unlockAudio = (on) => {
    try { if (navigator.audioSession) navigator.audioSession.type = on ? 'playback' : 'auto'; } catch (_) { /* non supportato */ }
    if (!unlockEl) {
      unlockEl = document.createElement('audio');
      unlockEl.src = silentWav();
      unlockEl.loop = true;
      unlockEl.setAttribute('playsinline', '');
      unlockEl.preload = 'auto';
    }
    if (on) { const pr = unlockEl.play(); if (pr) pr.catch(() => {}); } else { unlockEl.pause(); }
  };
  const LOUD = window.matchMedia('(pointer: coarse)').matches ? 0.9 : 0.55;

  const createEngine = () => {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    const ac = new AC();
    const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);

    const master = ac.createGain(); master.gain.value = 0;
    const vari = ac.createGain(); vari.gain.value = 1;
    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -16; comp.ratio.value = 3; comp.attack.value = 0.01; comp.release.value = 0.2;
    const analyser = ac.createAnalyser(); analyser.fftSize = 2048; analyser.smoothingTimeConstant = 0.5;
    master.connect(vari); vari.connect(comp); comp.connect(analyser); analyser.connect(ac.destination);

    // eco a ottavo puntato
    const BPM = 84;
    const STEP = 60 / BPM / 2;
    const delay = ac.createDelay(2); delay.delayTime.value = STEP * 1.5;
    const fb = ac.createGain(); fb.gain.value = 0.33;
    const dlp = ac.createBiquadFilter(); dlp.type = 'lowpass'; dlp.frequency.value = 2300;
    delay.connect(dlp); dlp.connect(fb); fb.connect(delay); dlp.connect(master);
    const send = ac.createGain(); send.gain.value = 0.5; send.connect(delay);

    // bus di intonazione: lo scratch "piega" tutte le note
    const bend = ac.createConstantSource(); bend.offset.value = 0; bend.start();

    const padLP = ac.createBiquadFilter(); padLP.type = 'lowpass'; padLP.frequency.value = 1000; padLP.Q.value = 0.5;
    padLP.connect(master);

    // fruscio del vinile
    const cb = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate);
    const cd = cb.getChannelData(0);
    for (let i = 0; i < cd.length; i++) {
      cd[i] = Math.random() < 0.0008 ? (Math.random() * 2 - 1) * 0.8 : (Math.random() * 2 - 1) * 0.01;
    }
    const crackle = ac.createBufferSource(); crackle.buffer = cb; crackle.loop = true;
    const chp = ac.createBiquadFilter(); chp.type = 'highpass'; chp.frequency.value = 1000;
    const cg = ac.createGain(); cg.gain.value = 0.3;
    crackle.connect(chp); chp.connect(cg); cg.connect(master); crackle.start();

    // rumore filtrato per lo scratch
    const nb = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
    const nd = nb.getChannelData(0);
    for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
    const noise = ac.createBufferSource(); noise.buffer = nb; noise.loop = true;
    const nbp = ac.createBiquadFilter(); nbp.type = 'bandpass'; nbp.Q.value = 2; nbp.frequency.value = 600;
    const ng = ac.createGain(); ng.gain.value = 0;
    noise.connect(nbp); nbp.connect(ng); ng.connect(master); noise.start();

    // Fa maj7, Mi m7, Re m7, Do maj7
    const prog = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]];
    const pattern = [0, 1, 2, 3, 4, 3, 2, 1];

    const voice = (type, freq, t, dur, peak, dest, attack) => {
      const o = ac.createOscillator();
      o.type = type; o.frequency.value = freq;
      bend.connect(o.detune);
      const env = ac.createGain();
      env.gain.setValueAtTime(0.0001, t);
      env.gain.exponentialRampToValueAtTime(peak, t + attack);
      env.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.connect(env); env.connect(dest);
      o.start(t); o.stop(t + dur + 0.05);
      o.onended = () => { try { bend.disconnect(o.detune); } catch (_) { /* già scollegato */ } env.disconnect(); };
      return env;
    };

    let step = 0, nextTime = 0, timer = 0;
    const schedule = (s, t) => {
      const bar = Math.floor(s / 8) % prog.length;
      const pos = s % 8;
      const ch = prog[bar];
      if (pos === 0) {
        ch.forEach((m) => {
          voice('triangle', mtof(m), t, STEP * 8 + 0.8, 0.032, padLP, 0.4);
          voice('sine', mtof(m) * 1.004, t, STEP * 8 + 0.8, 0.022, padLP, 0.6);
        });
        voice('sine', mtof(ch[0] - 12), t, STEP * 3.6, 0.2, master, 0.012);
        // armonica all'ottava: rende il basso udibile anche dagli speaker del telefono
        voice('triangle', mtof(ch[0]), t, STEP * 3, 0.06, master, 0.012);
        if (bar % 2 === 0) voice('sine', mtof(ch[3] + 24), t, 1.8, 0.025, send, 0.01);
      }
      if (pos === 4) voice('sine', mtof(ch[2] - 12), t, STEP * 3, 0.13, master, 0.012);
      const tones = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24];
      const env = voice('triangle', mtof(tones[pattern[pos]]), t, STEP * 1.7, 0.09, master, 0.004);
      env.connect(send);
    };
    const tick = () => {
      while (nextTime < ac.currentTime + 0.12) { schedule(step, nextTime); nextTime += STEP; step++; }
    };
    const buf = new Uint8Array(analyser.fftSize);

    return {
      start() {
        const r = ac.resume();
        if (r) r.catch(() => {});
        const t = ac.currentTime;
        nextTime = t + 0.06; step = 0;
        clearInterval(timer); timer = setInterval(tick, 25); tick();
        master.gain.cancelScheduledValues(t);
        master.gain.setValueAtTime(master.gain.value, t);
        master.gain.linearRampToValueAtTime(LOUD, t + 1.4);
      },
      stop() {
        const t = ac.currentTime;
        master.gain.cancelScheduledValues(t);
        master.gain.setValueAtTime(master.gain.value, t);
        master.gain.linearRampToValueAtTime(0, t + 0.45);
        clearInterval(timer);
        setTimeout(() => { if (!playing) { ac.suspend(); unlockAudio(false); } }, 600);
      },
      wave() { analyser.getByteTimeDomainData(buf); return buf; },
      scratch(on, v = 0) {
        const t = ac.currentTime;
        if (!on) {
          ng.gain.setTargetAtTime(0, t, 0.04);
          bend.offset.setTargetAtTime(0, t, 0.12);
          vari.gain.setTargetAtTime(1, t, 0.12);
          return;
        }
        const speed = Math.abs(v);
        ng.gain.setTargetAtTime(Math.min(0.45, speed / 2400), t, 0.015);
        nbp.frequency.setTargetAtTime(220 + speed * 2.4, t, 0.015);
        bend.offset.setTargetAtTime(Math.max(-2400, Math.min(1200, (v / PLAY - 1) * 1200)), t, 0.025);
        vari.gain.setTargetAtTime(Math.max(0.12, Math.min(1, speed / PLAY)), t, 0.03);
      },
    };
  };

  /* ---------- Play / stop ---------- */
  function toggle(on) {
    if (on) unlockAudio(true);
    if (on && !engine) engine = createEngine();
    if (on && !engine) return;
    playing = on;
    if (on) { engine.start(); target = PLAY; } else { if (engine) engine.stop(); target = IDLE; }
    playBtn.setAttribute('aria-pressed', String(on));
    playLabel.textContent = on ? 'Ferma il disco' : 'Ascolta il disco';
    run();
  }
  playBtn.addEventListener('click', () => toggle(!playing));

  /* Su smartphone il pulsante esce dal disco (che resta libero per lo scratch)
     e si sposta subito sotto la banda che scorre. */
  const dock = document.querySelector('[data-play-dock]');
  const mqDock = window.matchMedia('(max-width: 720px)');
  const placePlay = () => {
    if (!dock) return;
    if (mqDock.matches) dock.appendChild(playBtn);
    else hero.appendChild(playBtn);
  };
  mqDock.addEventListener('change', placePlay);
  placePlay();

  run();
})();
