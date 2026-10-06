(function () {
  const sec = document.getElementById('shot-7'); if (!sec) return;
  const NS = 'http://www.w3.org/2000/svg';
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  // three identical panels: same fibre, same glow size, same brightness. Only the colour differs.
  const cols = [
    { id: 'gb', name: 'blue', nm: '470 nm', at: 4.68 },
    { id: 'gy', name: 'yellow', nm: '590 nm', at: 5.15 },
    { id: 'gr', name: 'red', nm: '635 nm', at: 5.77 },
  ];
  const root = sec.querySelector('.s7-panels'), P = [];
  const rnd = ST.rand('tissue-7');
  cols.forEach((c, i) => {
    const x0 = 180 + i * 560, cx = x0 + 220, tipY = 385;
    const g = mk('g', {}, root);
    mk('rect', { x: x0, y: 290, width: 440, height: 300, rx: 30, class: 's7-tissue' }, g);
    const cp = mk('g', { 'clip-path': `url(#s7-c${i})` }, g);
    for (let k = 0; k < 46; k++) mk('circle', { cx: (x0 + rnd.range(14, 426)).toFixed(0), cy: rnd.range(302, 578).toFixed(0), r: rnd.range(2, 4.5).toFixed(1), fill: '#a4a9c6', opacity: rnd.range(.1, .22).toFixed(2) }, cp);
    const glow = mk('circle', { cx, cy: tipY, r: 1, fill: `url(#s7-${c.id})` }, cp);
    const fib = mk('g', {}, g);
    mk('line', { x1: cx, y1: 214, x2: cx, y2: tipY - 8, class: 's7-fibre' }, fib);
    mk('circle', { cx, cy: tipY, r: 9, fill: '#eef0fb' }, fib);
    const lab = mk('g', {}, g);
    const t1 = mk('text', { x: x0 + 220, y: 528, 'text-anchor': 'middle', class: 's7-t-name' }, lab); t1.textContent = c.name;
    const t2 = mk('text', { x: x0 + 220, y: 570, 'text-anchor': 'middle', class: 's7-t-nm' }, lab); t2.textContent = c.nm;
    P.push({ c, g, glow, fib, lab });
  });
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    sec.querySelector('.s7-art').style.transform = `scale(${(1 + .03 * t / 13.348).toFixed(4)})`;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); el.style.transform = `translateY(${((1 - k) * 12).toFixed(2)}px)`; });
    const pa = eo((t - 1.3) / .8);
    // equal glow: every colour grows to the same radius (230) and breathes in the same rhythm
    const breathe = 1 + .05 * Math.sin(t * 2.2);
    P.forEach((p) => {
      p.g.setAttribute('opacity', pa.toFixed(3)); p.fib.setAttribute('opacity', eo((t - 3.5) / .6).toFixed(3));
      const k = eo((t - p.c.at) / 1.6);
      p.glow.setAttribute('r', (205 * k * (1 + (breathe - 1) * k) + 1).toFixed(1));
      p.glow.setAttribute('opacity', (k > 0 ? 1 : 0));
      p.lab.setAttribute('opacity', eo((t - p.c.at) / .4).toFixed(3));
    });
  });
})();
