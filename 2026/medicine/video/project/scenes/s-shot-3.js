(function () {
  const sec = document.getElementById('shot-3'); if (!sec) return;
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const io = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const $ = (s) => sec.querySelector(s);
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  // drifting motes, seeded once
  const r = ST.rand('alga-motes'), motes = $('.s3-motes'), M = [];
  for (let i = 0; i < 16; i++) {
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    const m = { x: r.range(60, 1860), y: r.range(80, 680), r: r.range(2, 5), ph: r.range(0, 6.28), sp: r.range(.2, .5), c };
    c.setAttribute('r', m.r); c.setAttribute('fill', '#a4a9c6'); c.setAttribute('opacity', r.range(.12, .3).toFixed(2)); motes.appendChild(c); M.push(m);
  }
  const A = { x: 300, y: 520 }, B = { x: 1150, y: 215 }, L = { x: 1500, y: 236 };
  const base = Math.atan2(L.y - A.y, L.x - A.x) * 180 / Math.PI;
  const fl = (t, ph) => { const w = Math.sin(t * 14 + ph) * 12; return `M44 -14 C64 ${-30 + w} 80 ${-6 - w} 100 ${-20 + w}`; };
  function pos(t) {
    const s = io((t - 4.55) / 3.1);
    const wob = Math.sin(s * 11) * Math.sin(Math.PI * s) * 34;
    const dx = B.x - A.x, dy = B.y - A.y, n = Math.hypot(dx, dy);
    return { x: A.x + dx * s - dy / n * wob, y: A.y + dy * s + dx / n * wob + Math.sin(t * 1.7) * 5 * (1 - s) + Math.sin(t * 2.1) * 9 * s, s };
  }
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); el.style.transform = `translateY(${((1 - k) * 12).toFixed(2)}px)`; });
    M.forEach((m) => { m.c.setAttribute('cx', (m.x + Math.sin(t * m.sp + m.ph) * 18).toFixed(1)); m.c.setAttribute('cy', (m.y + Math.cos(t * m.sp * .8 + m.ph) * 14).toFixed(1)); });
    $('.s3-art').style.transform = `scale(${(1 + .035 * t / 11.84).toFixed(4)})`;
    // lamp switches on at 3.9 s
    const on = eo((t - 3.9) / .5);
    $('.s3-beam').style.opacity = (on * (1 - .55 * eo((t - 8) / .6))).toFixed(3);
    $('.s3-halo').style.opacity = ((.25 + .75 * on) * (1 + .06 * Math.sin(t * 2.2))).toFixed(3);
    $('.s3-bulb').style.opacity = (.45 + .55 * on).toFixed(3);
    // alga: idles facing away, turns to the light at "toward" (4.3 s), then swims
    const p = pos(t), turn = io((t - 4.2) / .7);
    const head = (base + 160) + (0 - 160) * turn + Math.sin(p.s * 11 + 1) * 10 * Math.sin(Math.PI * p.s);
    const alga = $('.s3-alga'); alga.style.transform = `translate(${p.x.toFixed(1)}px,${p.y.toFixed(1)}px)`;
    $('.s3-rot').style.transform = `rotate(${head.toFixed(1)}deg) scale(1.45)`;
    $('.s3-fl1').setAttribute('d', fl(t, 0)); $('.s3-fl2').setAttribute('d', fl(t, 2.1));
    // the label stays upright: undo nothing, it sits outside the rotating group
    // eyespot glint on the word "light" (4.61 s)
    const g = cl((t - 4.61) / .9), gl = g > 0 && g < 1 ? Math.sin(Math.PI * Math.pow(g, .6)) : 0;
    const gEl = $('.s3-glint'); gEl.style.opacity = gl.toFixed(3);
    gEl.style.transformOrigin = '30px -18px'; gEl.style.transform = `scale(${(.6 + .6 * gl).toFixed(3)})`;
  });
})();
