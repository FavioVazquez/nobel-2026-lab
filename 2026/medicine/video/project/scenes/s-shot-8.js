(function () {
  const sec = document.getElementById('shot-8'); if (!sec) return;
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  const ring = sec.querySelector('.s8-ring');
  const warm = sec.querySelector('.s8-warm'), th = sec.querySelector('.s8-th'), merc = sec.querySelector('.s8-merc');
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    sec.querySelector('.s8-art').style.transform = `scale(${(1 + .012 * t / 12.715).toFixed(4)})`;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); if (el.tagName !== 'svg' && el.tagName !== 'foreignObject') el.style.transform = `translateY(${((1 - k) * 10).toFixed(2)}px)`; });
    // the ring around the red crossing pulses once it lands
    const k = eo((t - 1.04) / .5), pulse = 1 + .12 * Math.sin(Math.max(0, t - 1.5) * 4) * k;
    // tail: warm glow fades in on "more light" (9.98), the thermometer warms on "heat" (11.64)
    const gl = eo((t - 9.98) / 1.2), hot = eo((t - 11.64) / .9);
    warm.setAttribute('opacity', (gl * (.45 + .55 * hot)).toFixed(3));
    th.setAttribute('opacity', eo((t - 10.85) / .5).toFixed(3));
    const mh = 46 * (.15 + .85 * hot); merc.setAttribute('height', mh.toFixed(1)); merc.setAttribute('y', (270 - mh).toFixed(1)); merc.setAttribute('fill', '#ff7a45');
    ring.setAttribute('r', (30 * pulse).toFixed(1));
  });
})();
