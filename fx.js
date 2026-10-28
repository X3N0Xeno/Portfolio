/* ------------------------------------------------------------------
   fx.js — the "bond network" background + cursor interactions.
   Injected once by app.py (st.html with unsafe_allow_javascript).
   Idempotent: running it twice tears down the first run.
   Calm mode is read from the CSS variable --calm (1 = calm).
------------------------------------------------------------------- */
(() => {
  const root = document.documentElement;
  if (window.__xeno && window.__xeno.destroy) window.__xeno.destroy();

  const cleanups = [];
  const on = (t, e, f, o) => { t.addEventListener(e, f, o); cleanups.push(() => t.removeEventListener(e, f, o)); };
  const mk = (tag, id) => {
    const el = document.createElement(tag);
    el.id = id;
    document.body.appendChild(el);
    cleanups.push(() => el.remove());
    return el;
  };

  // ---- fonts (head link element, survives Streamlit re-renders) ---------
  if (!document.getElementById('xeno-fonts')) {
    const l = document.createElement('link');
    l.id = 'xeno-fonts';
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap';
    document.head.appendChild(l);
  }

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const isCalm = () => reduce || getComputedStyle(root).getPropertyValue('--calm').trim() === '1';
  const accent = () => {
    const rgb = getComputedStyle(root).getPropertyValue('--accent-rgb').trim() || '225,29,72';
    return rgb;
  };

  // ---- layers --------------------------------------------------------------
  const canvas = mk('canvas', 'xeno-bg');
  const tone = mk('div', 'xeno-tone');
  const bar = mk('div', 'xeno-progress');
  const ring = fine ? mk('div', 'xeno-ring') : null;
  const dot = fine ? mk('div', 'xeno-dot') : null;
  const ctx = canvas.getContext('2d');

  let W = 0, H = 0, DPR = 1;
  const mouse = { x: -9999, y: -9999, tx: -9999, ty: -9999, on: false };
  let nodes = [];
  const pulses = [];

  const seed = () => {
    const n = Math.max(28, Math.min(84, Math.round((W * H) / 22000)));
    nodes = Array.from({ length: n }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.22,
      vy: (Math.random() - 0.5) * 0.22,
      r: 1 + Math.random() * 1.6,
    }));
  };
  const resize = () => {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  };
  resize();
  on(window, 'resize', resize);

  // ---- pointer -------------------------------------------------------------
  let rafPending = false;
  on(document, 'pointermove', (e) => {
    mouse.tx = e.clientX; mouse.ty = e.clientY; mouse.on = true;
    if (!mouse.init) { mouse.x = mouse.tx; mouse.y = mouse.ty; mouse.init = true; }
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(() => {
        rafPending = false;
        root.style.setProperty('--mx', mouse.tx + 'px');
        root.style.setProperty('--my', mouse.ty + 'px');
      });
    }
  }, { passive: true });
  on(document, 'pointerleave', () => { mouse.on = false; });
  on(document, 'pointerdown', (e) => {
    if (isCalm()) return;
    pulses.push({ x: e.clientX, y: e.clientY, r: 0, a: 0.55 });
    nodes.forEach((n) => {
      const dx = n.x - e.clientX, dy = n.y - e.clientY, d = Math.hypot(dx, dy) || 1;
      if (d < 220) { n.vx += (dx / d) * (1 - d / 220) * 2.2; n.vy += (dy / d) * (1 - d / 220) * 2.2; }
    });
  }, { passive: true });

  // ---- main loop -----------------------------------------------------------
  let raf = 0, frame = 0, rgb = accent();
  const LINK = 128, BOND = 190;
  const tick = () => {
    raf = requestAnimationFrame(tick);
    if (document.hidden) return;
    frame++;
    if (frame % 40 === 0) rgb = accent();
    const calm = isCalm();
    canvas.style.opacity = calm ? '0.35' : '1';
    tone.style.opacity = calm ? '0' : '1';

    mouse.x += (mouse.tx - mouse.x) * 0.18;
    mouse.y += (mouse.ty - mouse.y) * 0.18;

    ctx.clearRect(0, 0, W, H);
    const live = mouse.on && !calm;

    for (const n of nodes) {
      if (!calm) {
        n.x += n.vx; n.y += n.vy;
        n.vx *= 0.994; n.vy *= 0.994;
        // keep a gentle baseline drift
        if (Math.abs(n.vx) < 0.05) n.vx += (Math.random() - 0.5) * 0.01;
        if (Math.abs(n.vy) < 0.05) n.vy += (Math.random() - 0.5) * 0.01;
        if (n.x < -20) n.x = W + 20; if (n.x > W + 20) n.x = -20;
        if (n.y < -20) n.y = H + 20; if (n.y > H + 20) n.y = -20;
        if (live) {
          const dx = mouse.x - n.x, dy = mouse.y - n.y, d = Math.hypot(dx, dy);
          if (d < BOND && d > 40) { n.vx += (dx / d) * 0.012; n.vy += (dy / d) * 0.012; }
          else if (d <= 40) { n.vx -= (dx / (d || 1)) * 0.05; n.vy -= (dy / (d || 1)) * 0.05; }
        }
        const sp = Math.hypot(n.vx, n.vy);
        if (sp > 1.6) { n.vx = (n.vx / sp) * 1.6; n.vy = (n.vy / sp) * 1.6; }
      }
    }

    // node-to-node links
    ctx.lineWidth = 1;
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        if (dx > LINK || dx < -LINK || dy > LINK || dy < -LINK) continue;
        const d = Math.hypot(dx, dy);
        if (d < LINK) {
          ctx.strokeStyle = `rgba(243,238,228,${(1 - d / LINK) * 0.11})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }
    // bonds to the cursor
    if (live) {
      for (const n of nodes) {
        const d = Math.hypot(n.x - mouse.x, n.y - mouse.y);
        if (d < BOND) {
          const k = 1 - d / BOND;
          ctx.strokeStyle = `rgba(${rgb},${k * 0.75})`;
          ctx.lineWidth = 0.6 + k * 1.2;
          ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
      }
    }
    // nodes
    for (const n of nodes) {
      let near = 0;
      if (live) { const d = Math.hypot(n.x - mouse.x, n.y - mouse.y); if (d < BOND) near = 1 - d / BOND; }
      ctx.fillStyle = near > 0 ? `rgba(${rgb},${0.45 + near * 0.55})` : 'rgba(243,238,228,0.30)';
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r + near * 1.8, 0, Math.PI * 2); ctx.fill();
    }
    // click pulses
    for (let i = pulses.length - 1; i >= 0; i--) {
      const p = pulses[i];
      p.r += 5; p.a *= 0.94;
      if (p.a < 0.02) { pulses.splice(i, 1); continue; }
      ctx.strokeStyle = `rgba(${rgb},${p.a})`;
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.stroke();
    }

    // cursor ring + dot
    if (ring) {
      const show = mouse.on && !calm;
      ring.style.opacity = show ? '1' : '0';
      dot.style.opacity = show ? '1' : '0';
      ring.style.transform = `translate(${mouse.x}px, ${mouse.y}px) translate(-50%, -50%)`;
      dot.style.transform = `translate(${mouse.tx}px, ${mouse.ty}px) translate(-50%, -50%)`;
    }
  };
  tick();
  cleanups.push(() => cancelAnimationFrame(raf));

  // ---- ring grows over anything clickable ---------------------------------
  const HOT = 'a, button, [role="tab"], [role="button"], [role="slider"], summary, label, input, textarea, [data-baseweb="select"], [data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-segmentedControlActive"], .x-tech-tile, .x-hot';
  on(document, 'pointerover', (e) => {
    if (!ring) return;
    const hot = e.target.closest && e.target.closest(HOT);
    ring.classList.toggle('hot', !!hot);
  }, { passive: true });

  // ---- card spotlight + tilt + magnetic buttons ---------------------------
  const CARD = '[class*="st-key-card"], .x-card, [data-testid="stMetric"]';
  const TILT = '.x-tilt, [class*="st-key-card-p"]';
  const MAG = '.stButton button, .stLinkButton a, .stDownloadButton button, [data-testid="stFormSubmitButton"] button';
  on(document, 'pointermove', (e) => {
    const t = e.target;
    if (!t || !t.closest) return;
    const card = t.closest(CARD);
    if (card) {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--cx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--cy', (e.clientY - r.top) + 'px');
    }
    if (isCalm()) return;
    const tilt = t.closest(TILT);
    if (tilt) {
      const r = tilt.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
      tilt.style.setProperty('--rx', (-py * 5).toFixed(2) + 'deg');
      tilt.style.setProperty('--ry', (px * 6).toFixed(2) + 'deg');
    }
    const mag = t.closest(MAG);
    if (mag) {
      const r = mag.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      mag.style.transform = `translate(${(dx * 0.12).toFixed(1)}px, ${(dy * 0.18).toFixed(1)}px)`;
    }
  }, { passive: true });
  on(document, 'pointerout', (e) => {
    const t = e.target;
    if (!t || !t.closest) return;
    const tilt = t.closest(TILT);
    if (tilt && !tilt.contains(e.relatedTarget)) { tilt.style.setProperty('--rx', '0deg'); tilt.style.setProperty('--ry', '0deg'); }
    const mag = t.closest(MAG);
    if (mag && !mag.contains(e.relatedTarget)) mag.style.transform = '';
  }, { passive: true });

  // ---- reading progress (Streamlit scrolls an inner container) ------------
  on(document, 'scroll', (e) => {
    const s = e.target === document ? document.documentElement : e.target;
    if (!s || s.scrollHeight === undefined) return;
    const max = s.scrollHeight - s.clientHeight;
    if (max < 40 || s.clientHeight < H * 0.5) return;
    bar.style.transform = `scaleX(${Math.min(1, Math.max(0, s.scrollTop / max))})`;
  }, { capture: true, passive: true });

  // ---- jump back to the top when the round changes ------------------------
  let lastRound = null;
  const iv = setInterval(() => {
    const m = document.querySelector('[data-round]');
    const v = m && m.dataset.round;
    if (v && v !== lastRound) {
      if (lastRound !== null) {
        const s = document.querySelector('[data-testid="stMain"]');
        if (s) s.scrollTo({ top: 0, behavior: 'smooth' });
      }
      lastRound = v;
    }
  }, 200);
  cleanups.push(() => clearInterval(iv));

  window.__xeno = { destroy: () => { cleanups.forEach((f) => { try { f(); } catch (_) {} }); window.__xeno = null; } };
})();
