// Pure math first (tested by scripts/selftest.mjs), DOM wiring below.
const DAY = 86400000;
export const PROGRAM_WEEKS = 6;

export function daysUntil(target, today) {
  return Math.round((Date.UTC(target.getFullYear(), target.getMonth(), target.getDate()) -
    Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())) / DAY);
}

// Next mid-December first ski day; after mid-December, next season's.
export function defaultFirstDay(today) {
  const d = new Date(today.getFullYear(), 11, 13);
  return daysUntil(d, today) < 7 ? new Date(today.getFullYear() + 1, 11, 13) : d;
}

export function passMath(pass, ticket, days) {
  if (!(pass > 0 && ticket > 0 && days > 0)) return null;
  const even = Math.ceil(pass / ticket);
  return { even, cost: pass / days, diff: days * ticket - pass, more: Math.max(0, even - days) };
}

// Slalom line in a 100x1000 box: n turns, alternating sides, starting top-centre.
export function slalomPath(n) {
  let d = 'M50,0';
  for (let i = 0, step = 1000 / n; i < n; i++) {
    const y = i * step, x = i % 2 ? 18 : 82;
    d += ` C${x},${y + step * 0.25} ${x},${y + step * 0.75} 50,${y + step}`;
  }
  return d;
}

// Flat riders facing right; colours from the app palette.
const RIDERS = {
  ski: `<svg viewBox="0 0 64 64" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 51 Q30 55 58 54 q4 0 5-3" stroke="#7fb4ff" stroke-width="3"/>
    <path d="M7 47 Q32 51 57 50 q4 0 5-3" stroke="#7fb4ff" stroke-width="3"/>
    <path d="M45 30 L30 52" stroke="#c7daf4" stroke-width="1.6"/>
    <path d="M28 34 L35 42 L31 50 M30 34 L39 41 L37 49" stroke="#1b2a55" stroke-width="6"/>
    <path d="M29 34 L37 21" stroke="#ff8a3d" stroke-width="10"/>
    <path d="M37 23 L46 30" stroke="#ff8a3d" stroke-width="5"/>
    <circle cx="42" cy="14" r="6" fill="#f2f6fb"/><path d="M42 13 h6" stroke="#7fe0f5" stroke-width="3"/>
  </svg>`,
  board: `<svg viewBox="0 0 64 64" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 52 Q32 57 58 52" stroke="#ff8a3d" stroke-width="5"/>
    <path d="M22 50 L20 41 L32 36 L42 41 L42 50" stroke="#1b2a55" stroke-width="6"/>
    <path d="M32 36 L32 22" stroke="#7fb4ff" stroke-width="10"/>
    <path d="M30 24 L18 30 M34 24 L46 21" stroke="#7fb4ff" stroke-width="5"/>
    <circle cx="33" cy="14" r="6" fill="#f2f6fb"/><path d="M34 13 h6" stroke="#7fe0f5" stroke-width="3"/>
  </svg>`,
};

if (typeof document !== 'undefined') {
  const data = document.getElementById('i18n'); // home only; guide pages have none
  const t = data ? JSON.parse(data.textContent) : {};
  const fmt = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
  const today = new Date();

  // Countdown to the first ski day
  const input = document.getElementById('first-day');
  if (input) {
    const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    input.value = iso(defaultFirstDay(today));
    const render = () => {
      const [y, m, d] = input.value.split('-').map(Number);
      const days = y ? daysUntil(new Date(y, m - 1, d), today) : NaN;
      const msg = document.getElementById('count-msg');
      document.getElementById('count-days').textContent = Number.isFinite(days) && days >= 0 ? days : '–';
      if (!Number.isFinite(days)) msg.textContent = '';
      else if (days < 0) msg.innerHTML = t.past;
      else if (days >= PROGRAM_WEEKS * 7) {
        const start = new Date(y, m - 1, d - PROGRAM_WEEKS * 7);
        msg.innerHTML = fmt(t.ok, { date: start.toLocaleDateString(t.lang, { day: 'numeric', month: 'long' }) });
      } else if (days >= 7) msg.innerHTML = fmt(t.late, { weeks: Math.floor(days / 7) });
      else msg.innerHTML = t.now;
    };
    input.addEventListener('input', render);
    render();
  }

  // Season pass break-even
  const calc = document.getElementById('calc');
  if (calc) {
    const money = new Intl.NumberFormat(t.lang, { style: 'currency', currency: t.currency, maximumFractionDigits: 0 });
    const num = (id) => parseFloat(document.getElementById(id).value);
    const render = () => {
      const days = Math.round(num('c-days'));
      const r = passMath(num('c-pass'), num('c-ticket'), days);
      const even = document.getElementById('c-even');
      const line = document.getElementById('c-line');
      if (!r) { even.innerHTML = t.bad; line.textContent = ''; return; }
      even.innerHTML = fmt(t.even, { n: r.even });
      line.innerHTML = r.diff >= 0
        ? fmt(t.saved, { days, cost: money.format(r.cost), saved: money.format(r.diff) })
        : fmt(t.short, { days, cost: money.format(r.cost), extra: money.format(-r.diff), more: r.more });
      const max = Math.max(days, r.even) * 1.15;
      document.getElementById('c-bar').style.width = `${(days / max) * 100}%`;
      document.getElementById('c-bar').classList.toggle('ok', r.diff >= 0);
      document.getElementById('c-mark').style.left = `${(r.even / max) * 100}%`;
    };
    calc.addEventListener('input', render);
    render();
  }

  // Snowfall in the hero; paused off-screen, off for reduced motion
  const canvas = document.querySelector('.snow');
  if (canvas && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const ctx = canvas.getContext('2d');
    let w, h, flakes, raf, visible = true;
    const size = () => {
      const dpr = Math.min(devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      flakes = Array.from({ length: Math.round(w / 9) }, () => ({
        x: Math.random() * w, y: Math.random() * h, r: Math.random() * 2.2 + 0.6,
        v: Math.random() * 0.6 + 0.35, s: Math.random() * Math.PI * 2,
      }));
    };
    const tick = () => {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = 'rgba(220,234,251,0.85)';
      for (const f of flakes) {
        f.y += f.v * f.r; f.s += 0.01; f.x += Math.sin(f.s) * 0.35;
        if (f.y > h + 4) { f.y = -4; f.x = Math.random() * w; }
        ctx.globalAlpha = f.r / 3;
        ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2); ctx.fill();
      }
      raf = visible ? requestAnimationFrame(tick) : 0;
    };
    size();
    addEventListener('resize', () => { if (canvas.clientWidth !== w) size(); });
    new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      if (visible && !raf) raf = requestAnimationFrame(tick);
    }).observe(canvas);
  }

  // First visit: pick ski or snowboard; the rider then carves down a slalom lane as the page scrolls
  const hero = document.querySelector('.hero');
  if (hero && t.ride_h && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const KEY = 'snowstreak-ride';
    let stored = null;
    try { stored = localStorage.getItem(KEY); } catch {}
    const mount = (ride, drop) => {
      const lane = document.createElement('div');
      lane.className = 'ride' + (drop ? ' drop' : '');
      lane.setAttribute('aria-hidden', 'true');
      lane.innerHTML = `<svg class="ride-trail" viewBox="0 0 100 1000" preserveAspectRatio="none"><path d="${slalomPath(5)}"/></svg><div class="rider">${RIDERS[ride] || RIDERS.ski}</div>`;
      document.body.append(lane);
      const path = lane.querySelector('path'), rider = lane.querySelector('.rider');
      const len = path.getTotalLength();
      path.style.strokeDasharray = len;
      let raf = 0, last = 0;
      const place = () => {
        raf = 0;
        const max = document.documentElement.scrollHeight - innerHeight;
        const p = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
        const sx = lane.clientWidth / 100, sy = lane.clientHeight / 1000;
        const a = path.getPointAtLength(p * len), b = path.getPointAtLength(Math.min(len, p * len + 4));
        const dx = (b.x - a.x) * sx, dy = (b.y - a.y) * sy;
        const tilt = Math.max(-28, Math.min(28, (Math.atan2(dy, Math.abs(dx) || 1e-3) * 180) / Math.PI - 50));
        rider.style.transform = `translate(${a.x * sx}px, ${a.y * sy}px) scaleX(${dx < 0 ? -1 : 1}) rotate(${tilt}deg)`;
        path.style.strokeDashoffset = len - p * len;
        rider.classList.toggle('carve', Math.abs(scrollY - last) > 2);
        last = scrollY;
      };
      const queue = () => { if (!raf) raf = requestAnimationFrame(place); };
      addEventListener('scroll', queue, { passive: true });
      addEventListener('resize', queue);
      place();
    };
    if (stored) mount(stored, false);
    else {
      const intro = document.createElement('div');
      intro.className = 'intro';
      intro.setAttribute('role', 'dialog');
      intro.setAttribute('aria-modal', 'true');
      intro.setAttribute('aria-labelledby', 'intro-h');
      intro.innerHTML = `<div class="intro-in"><h2 id="intro-h">${t.ride_h}</h2><p>${t.ride_p}</p><div class="intro-picks">
        <button type="button" data-ride="ski">${RIDERS.ski}<span>${t.ride_ski}</span></button>
        <button type="button" data-ride="board">${RIDERS.board}<span>${t.ride_board}</span></button>
        </div><button type="button" class="intro-skip">${t.ride_skip}</button></div>`;
      document.body.append(intro);
      document.documentElement.classList.add('intro-open');
      intro.querySelector('[data-ride]').focus({ preventScroll: true });
      const close = (ride) => {
        try { localStorage.setItem(KEY, ride); } catch {}
        removeEventListener('keydown', esc);
        intro.querySelector(`[data-ride="${ride}"]`)?.classList.add('picked');
        intro.classList.add('out');
        document.documentElement.classList.remove('intro-open');
        setTimeout(() => { intro.remove(); mount(ride, true); }, 650);
      };
      const esc = (e) => { if (e.key === 'Escape') close('ski'); };
      addEventListener('keydown', esc);
      intro.addEventListener('click', (e) => {
        const b = e.target.closest('button');
        if (b && !intro.classList.contains('out')) close(b.dataset.ride || 'ski');
      });
    }
  }

  // Close the language menu on outside click
  const langs = document.querySelector('.langs');
  if (langs) document.addEventListener('click', (e) => { if (!langs.contains(e.target)) langs.open = false; });
}
