(function () {
  const sec = document.getElementById('shot-5'); if (!sec) return;
  const NS = 'http://www.w3.org/2000/svg';
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const io = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const $ = (s) => sec.querySelector(s);
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  // membrane: two rows of lipid heads with tails between; the protein sits in a gap
  const mem = $('.s5-mem'), MY = 640;
  for (let x = 110; x < 1830; x += 34) {
    if (Math.abs(x - 960) < 120) continue;
    for (const [y, dir] of [[MY - 56, 1], [MY + 56, -1]]) {
      mk('line', { x1: x, y1: y + dir * 14, x2: x, y2: y + dir * 44, stroke: '#5a5f86', 'stroke-width': 4 }, mem);
      mk('circle', { cx: x, cy: y, r: 15, fill: '#8f95c8' }, mem);
    }
  }
  // photons: wavy diagonal streaks aimed at the protein
  const rays = $('.s5-rays'), RY = [];
  for (let i = 0; i < 5; i++) {
    const x0 = 1300 - i * 36, y0 = 250 + i * 18, p = mk('path', { d: `M${x0} ${y0} L${x0 - 250} ${y0 + 190}`, stroke: '#58a9ff', 'stroke-width': 7, fill: 'none', 'stroke-linecap': 'round', 'stroke-dasharray': '36 28' }, rays);
    RY.push(p);
  }
  // protein sits at (960, 640)
  const prot = $('.s5-prot'); prot.style.transformBox = 'view-box';
  const hx = [...sec.querySelectorAll('.s5-hx')], pore = $('.s5-pore'), ret = $('.s5-ret');
  // frog egg: pills on the membrane ring, gene squiggles, seeded once
  const r = ST.rand('egg-genes'), EC = { x: 1250, y: 650, r: 220 };
  const pills = $('.s5-pills'), PL = [];
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * Math.PI * 2 + .1, g0 = mk('g', {}, pills), g = mk('g', {}, g0);
    const x = EC.x + Math.cos(a) * EC.r, y = EC.y + Math.sin(a) * EC.r, deg = a * 180 / Math.PI + 90;
    g0.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${deg.toFixed(1)})`);
    const w = mk('rect', { x: -9, y: -17, width: 18, height: 34, rx: 8, fill: '#9d8cff', stroke: '#eef0fb', 'stroke-width': 2 }, g);
    const hole = mk('rect', { x: -3.5, y: -17, width: 7, height: 34, rx: 3, fill: '#58a9ff' }, g);
    PL.push({ g, w, hole, d: 10.45 + (i % 8) * .06 });
  }
  const genes = $('.s5-genes'), GN = [];
  for (let i = 0; i < 9; i++) {
    const ang = r.range(0, 6.28), rad = r.range(20, 120);
    const e = mk('path', { d: 'M-12 0 q4 -9 8 0 t8 0 t8 0', fill: 'none', stroke: '#6fd6a0', 'stroke-width': 4, 'stroke-linecap': 'round' }, genes);
    GN.push({ e, x: EC.x + Math.cos(ang) * rad, y: EC.y + Math.sin(ang) * rad * .8 - 20, rot: r.range(-40, 40), d: 9.15 + i * .08 });
  }
  const pip = $('.s5-pipette'), light = $('.s5-light polygon'), glow = $('.s5-eggglow');
  const p1 = $('.s5-p1'), p2 = $('.s5-p2');
  const rimLight = [];
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); el.style.transform = `translateY(${((1 - k) * 12).toFixed(2)}px)`; });
    $('.s5-art').style.transform = `scale(${(1 + .03 * t / 13.58).toFixed(4)})`;
    // phase 1 -> 2 handover
    const out1 = eo((t - 7.5) / .35);
    p1.style.opacity = (1 - out1).toFixed(3); p2.style.opacity = eo((t - 7.7) / .4).toFixed(3);
    p1.style.visibility = out1 >= 1 ? 'hidden' : ''; p2.style.visibility = t < 7.7 ? 'hidden' : '';
    // the title block and the name slot: phase-2 name replaces phase 1's (both at y=300)
    // protein at (960,640): scale in, photons at "catch light" 4.47, retinal flash, pore opens at "form a channel" 5.3
    const open = io((t - 5.3) / .7);
    prot.style.transform = `translate(960px,${MY}px) scale(1.4)`;
    hx.forEach((h) => h.style.transform = `translateX(${(h.dataset.s * 22 * open).toFixed(1)}px)`);
    pore.setAttribute('x', (-16 * open - 0.1).toFixed(1)); pore.setAttribute('width', (32 * open + .2).toFixed(1));
    pore.style.opacity = (open > .01 ? .55 + .35 * Math.sin(t * 5) * open : 0).toFixed(3);
    const fl = cl((t - 4.8) / .5); ret.style.opacity = (.55 + .45 * Math.sin(Math.PI * Math.min(1, fl * 1.4))).toFixed(3);
    ret.setAttribute('r', (20 + 7 * Math.sin(Math.PI * cl((t - 4.8) / .6))).toFixed(1));
    const ra = cl((t - 4.47) / .35) * (1 - cl((t - 5.5) / .4));
    RY.forEach((p, i) => { p.style.opacity = ra.toFixed(3); p.setAttribute('stroke-dashoffset', (-(t - 4.47) * 90 - i * 6).toFixed(1)); });
    // egg: pipette in 8.58-9.0, genes drift into the egg, pipette out at 10.1
    const pin = eo((t - 8.4) / .6) * (1 - eo((t - 10.0) / .5));
    pip.style.transform = `translate(${((1 - pin) * 260).toFixed(1)}px,${((1 - pin) * -190).toFixed(1)}px)`; pip.style.opacity = (pin > 0 ? 1 : 0);
    GN.forEach((g) => { const k = eo((t - g.d) / .8), x0 = 1300, y0 = 530; const x = x0 + (g.x - x0) * k, y = y0 + (g.y - y0) * k;
      g.e.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(g.rot + 30 * Math.sin(t * 1.5 + g.d)).toFixed(1)})`); g.e.style.opacity = (cl((t - g.d) / .2)).toFixed(3); });
    // proteins built in the membrane
    const lt = eo((t - 11.1) / .6), op = io((t - 11.93) / .5);
    PL.forEach((p) => { const k = eo((t - p.d) / .4); p.g.style.opacity = k.toFixed(3);
      p.hole.setAttribute('opacity', (op).toFixed(3)); p.w.setAttribute('fill', op > .1 ? '#b5c9ff' : '#9d8cff'); p.g.style.transform = `scale(${(1 + .25 * op).toFixed(3)})`; });
    // blue light from above: from 11.12 ("light")
    light.setAttribute('opacity', lt.toFixed(3)); glow.setAttribute('opacity', (lt * (.45 + .1 * Math.sin(t * 3))).toFixed(3));
  });
})();
