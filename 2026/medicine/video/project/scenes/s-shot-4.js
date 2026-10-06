(function () {
  const sec = document.getElementById('shot-4'); if (!sec) return;
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const $ = (s) => sec.querySelector(s);
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  const spike = $('.s4-spike'), len = spike.getTotalLength ? spike.getTotalLength() : 200;
  spike.style.strokeDasharray = len; 
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); el.style.opacity = k.toFixed(3); el.style.transform = `translateY(${((1 - k) * 12).toFixed(2)}px)`; });
    $('.s4-art').style.transform = `scale(${(1 + .03 * t / 9.05).toFixed(4)})`;
    // both start on "faster" (2.8 s): the alga bar is done in a blink, the eye's keeps filling
    const r = cl((t - 2.8) / .14), e = cl((t - 2.8) / 2.9);
    $('.s4-alg').setAttribute('width', (70 * eo(r)).toFixed(1));
    $('.s4-eye').setAttribute('width', (1460 * (1 - Math.pow(1 - e, 1.6))).toFixed(1));
    const pu = cl((t - 2.9) / 1.2);
    $('.s4-pulse').style.opacity = (pu > 0 ? Math.sin(Math.PI * pu) * .9 + .1 * (t > 4 ? 1 : 0) : 0).toFixed(3);
    const sp = cl((t - 6.58) / .9);
    spike.style.strokeDashoffset = (len * (1 - eo(sp))).toFixed(1);
  });
})();
