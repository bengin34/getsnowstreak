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

  // Close the language menu on outside click
  const langs = document.querySelector('.langs');
  if (langs) document.addEventListener('click', (e) => { if (!langs.contains(e.target)) langs.open = false; });
}
