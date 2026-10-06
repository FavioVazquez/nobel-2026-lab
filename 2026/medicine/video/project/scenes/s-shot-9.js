(function () {
  const sec = document.getElementById('shot-9'); if (!sec) return;
  const NS = 'http://www.w3.org/2000/svg';
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const $ = (s) => sec.querySelector(s);
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  const rnd = ST.rand('tissue-9'), dots = $('.s9-dots'), rings = $('.s9-rings');
  for (let k = 0; k < 90; k++) mk('circle', { cx: rnd.range(910, 1770).toFixed(0), cy: rnd.range(160, 780).toFixed(0), r: rnd.range(2, 4.5).toFixed(1), fill: '#a4a9c6', opacity: rnd.range(.1, .22).toFixed(2) }, dots);
  const R = []; for (let i = 0; i < 4; i++) R.push(mk('circle', { cx: 1340, cy: 360, r: 10, class: 's9-ring', 'stroke-width': 4 }, rings));
  const heatpic = $('.s9-heatpic'), hg = $('.s9-hglow'), bg = $('.s9-bglow'), merc = $('.s9-merc');
  const r1 = $('.s9-r1'), r2 = $('.s9-r2'), r3 = $('.s9-r3');
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    sec.querySelector('.s9-art').style.transform = `scale(${(1 + .03 * t / 15.187).toFixed(4)})`;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); if (el.tagName !== 'svg') el.style.transform = `translateY(${((1 - k) * 10).toFixed(2)}px)`; });
    // heat picture: blue light from the tip at once, orange warmth spreading from "heat:" (2.35 s), gone as the chart arrives
    const pic = eo((t - .33) / .6) * (1 - eo((t - 7.5) / .6));
    heatpic.setAttribute('opacity', pic.toFixed(3));
    bg.setAttribute('r', (120 * eo((t - .6) / 1) + 1).toFixed(1));
    const w = eo((t - 2.35) / 2.2);
    hg.setAttribute('r', (330 * w + 1).toFixed(1)); hg.setAttribute('opacity', (w * (1 + .1 * Math.sin(t * 2))).toFixed(3));
    R.forEach((c, i) => { const ph = Math.max(0, (t - 2.35) * .45 + i / R.length) % 1, on = t > 2.35 ? 1 : 0;
      c.setAttribute('r', (30 + 330 * ph).toFixed(1)); c.setAttribute('opacity', (on * (1 - ph) * .7).toFixed(3)); });
    // thermometer: mercury climbs to the low end on "0.2", then to the high end on "2"
    const m = .12 + .1 * eo((t - 5.04) / .6) + .78 * eo((t - 6.2) / .8) - 0.12 * 0, mh = 150 * (t < 3.2 ? 0 : (.1 + .12 * eo((t - 5.04) / .6) + .7 * eo((t - 6.2) / .8)));
    merc.setAttribute('height', mh.toFixed(1)); merc.setAttribute('y', (506 - mh).toFixed(1));
    r1.style.opacity = eo((t - 5.04) / .4).toFixed(3); r2.style.opacity = eo((t - 6.03) / .4).toFixed(3); r3.style.opacity = eo((t - 6.34) / .4).toFixed(3);
  });
})();
