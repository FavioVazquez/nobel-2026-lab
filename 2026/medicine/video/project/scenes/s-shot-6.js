(function () {
  const sec = document.getElementById('shot-6'); if (!sec) return;
  const NS = 'http://www.w3.org/2000/svg';
  const cl = (x) => Math.min(1, Math.max(0, x));
  const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
  const io = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const $ = (s) => sec.querySelector(s);
  const titles = ['Light arrives', 'Channel opens', 'Ions flow in', 'Neuron fires'];
  const T0 = [4.3, 5.9, 6.4, 6.76], OPEN = [0, 6.41, 6.41, 6.41];
  const host = $('.s6-panels'); let html = '';
  for (let i = 0; i < 4; i++) {
    html += `<g transform="translate(${115 + i * 430} 330)"><g class="s6-pn" data-i="${i}">
      <rect width="400" height="560" rx="26" fill="#1a1c31" stroke="#3a3d5e" stroke-width="3"/>
      <circle cx="42" cy="48" r="22" fill="#58a9ff"/><text x="42" y="58" text-anchor="middle" class="s6-t-n">${i + 1}</text>
      <text x="78" y="58" class="s6-t-ttl">${titles[i]}</text>
      <rect x="24" y="322" width="140" height="52" fill="#2b3b5f" stroke="#5873ac" stroke-width="2.5"/>
      <rect x="236" y="322" width="140" height="52" fill="#2b3b5f" stroke="#5873ac" stroke-width="2.5"/>
      <g class="s6-ray">${[170, 200, 230].map((x, k) => `<path d="M${x} 110 L${x} 290" stroke="#58a9ff" stroke-width="7" stroke-linecap="round" stroke-dasharray="26 22" data-k="${k}"/>`).join('')}</g>
      <rect class="s6-pore" x="198" y="300" width="4" height="96" fill="#58a9ff" opacity="0"/>
      <rect class="s6-hl" x="160" y="300" width="40" height="96" rx="16" fill="url(#s6-prot)"/>
      <rect class="s6-hr" x="200" y="300" width="40" height="96" rx="16" fill="url(#s6-prot)"/>
      <circle class="s6-ret" cx="200" cy="348" r="9" fill="#ff9e7a"/>
      <g class="s6-ions"></g>
      ${i === 0 ? `<g class="s6-tag" data-in="5.45,0.5"><path d="M200 408 L200 438" stroke="#9af0bf" stroke-width="3"/><text x="200" y="476" text-anchor="middle" class="s6-t-sp2">Chlamydomonas</text><text x="200" y="514" text-anchor="middle" class="s6-t-sp2">reinhardtii</text></g>` : ''}
      ${i === 3 ? `<path class="s6-spk" d="M30 470 L150 470 L175 430 L205 520 L235 440 L255 470 L370 470" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>` : ''}
    </g></g>`;
  }
  host.innerHTML = html;
  const P = [...sec.querySelectorAll('.s6-pn')].map((g, i) => {
    const ions = g.querySelector('.s6-ions'), arr = [];
    if (i === 2) for (let k = 0; k < 6; k++) { const c = document.createElementNS(NS, 'circle'); c.setAttribute('r', 9); c.setAttribute('fill', '#ffb38f'); ions.appendChild(c); arr.push(c); }
    const spk = g.querySelector('.s6-spk'); if (spk) spk.style.strokeDasharray = 700;
    return { g, i, ions: arr, rays: [...g.querySelectorAll('.s6-ray path')], pore: g.querySelector('.s6-pore'), hl: g.querySelector('.s6-hl'), hr: g.querySelector('.s6-hr'), ret: g.querySelector('.s6-ret'), spk };
  });
  const ins = [...sec.querySelectorAll('[data-in]')].map((el) => { const [a, d] = el.dataset.in.split(',').map(Number); return { el, a, d }; });
  const card = $('.s6-card'), chip = $('.s6-chip'), nm = $('.s6-name'), panels = $('.s6-panels'), C = $('.s6-c');
  const fib = $('.s6-fib'), tip = $('.s6-tip'), tipc = $('.s6-tipc'), wh = $('.s6-whisk');
  const fl = fib.getTotalLength ? fib.getTotalLength() : 500; fib.style.strokeDasharray = fl;
  ST.onSeek(() => {
    const t = parseFloat(getComputedStyle(sec).getPropertyValue('--t')) || 0;
    ins.forEach(({ el, a, d }) => { const k = eo((t - a) / d); let o = k;
      if (el.classList.contains('s6-name')) o = k * (1 - eo((t - 7.9) / .4));
      el.style.opacity = o.toFixed(3); el.style.transform = `translateY(${((1 - k) * 12).toFixed(2)}px)`; });
    // the card: in, then out to the chip
    const cin = eo((t - 0.2) / .6), cout = eo((t - 3.1) / .5);
    card.style.opacity = (cin * (1 - cout)).toFixed(3); card.style.transform = `translateY(${(-30 * cout + (1 - cin) * 16).toFixed(1)}px) scale(${(1 - .06 * cout).toFixed(3)})`;
    card.style.transformOrigin = '960px 510px'; card.style.visibility = cout >= 1 ? 'hidden' : '';
    // chip stays until the mice
    chip.style.opacity = (eo((t - 3.5) / .6) * (1 - eo((t - 7.9) / .4))).toFixed(3);
    // panels
    const pout = eo((t - 7.85) / .45);
    panels.style.opacity = (1 - pout).toFixed(3); panels.style.visibility = pout >= 1 ? 'hidden' : '';
    const pulse = Math.sin(Math.PI * cl((t - 7.33) / .9));
    P.forEach((p) => {
      const k = eo((t - T0[p.i]) / .6); p.g.style.opacity = k.toFixed(3); p.g.style.transform = `translateY(${((1 - k) * 18).toFixed(1)}px)`;
      const open = p.i === 0 ? 0 : io((t - OPEN[p.i] + (p.i === 1 ? 0 : 1.2)) / .5 + (p.i === 1 ? 0 : 0));
      const o = p.i === 0 ? 0 : (p.i === 1 ? io((t - 6.41) / .5) : 1);
      p.hl.setAttribute('x', (160 - 14 * o).toFixed(1)); p.hr.setAttribute('x', (200 + 14 * o).toFixed(1));
      p.pore.setAttribute('x', (200 - 14 * o).toFixed(1)); p.pore.setAttribute('width', (28 * o + .1).toFixed(1)); p.pore.setAttribute('opacity', (.8 * o).toFixed(3));
      p.ret.setAttribute('r', (9 + 4 * pulse).toFixed(1));
      p.rays.forEach((r, kk) => { r.setAttribute('stroke-dashoffset', (-(t * 70) - kk * 9).toFixed(1)); r.style.opacity = (p.i === 0 || p.i === 1 ? .55 + .45 * Math.max(pulse, p.i === 0 ? .6 : 0) : .35 + .4 * pulse).toFixed(3); });
      if (p.ions.length) p.ions.forEach((c, n) => {
        const on = p.i === 2 ? cl((t - 6.55) / .3) : 1;
        const ph = ((t * .9 + n / 6) % 1), y = 150 + ph * 330, sx = 200 + Math.sin(n * 2 + ph * 5) * (y > 290 && y < 400 ? 4 : 28);
        c.setAttribute('cx', sx.toFixed(1)); c.setAttribute('cy', y.toFixed(1));
        c.setAttribute('opacity', (on * (p.i === 3 ? .45 : 1) * Math.min(1, ph * 6, (1 - ph) * 6)).toFixed(3));
      });
      if (p.spk) p.spk.style.strokeDashoffset = (700 * (1 - eo((t - 6.8) / 1.0))).toFixed(1);
    });
    // phase C: mouse
    const cin2 = eo((t - 8.7) / .6);
    C.style.opacity = cin2.toFixed(3);
    const fd = eo((t - 9.0) / .8); fib.style.strokeDashoffset = (fl * (1 - fd)).toFixed(1);
    const on = eo((t - 11.05) / .4), br = .85 + .15 * Math.sin(t * 3);
    tip.setAttribute('opacity', (on * br).toFixed(3)); tipc.setAttribute('opacity', on.toFixed(3));
    tip.setAttribute('r', (90 + 20 * on).toFixed(1));
    wh.style.transform = `rotate(${(Math.sin(t * 2.4) * 2).toFixed(2)}deg)`; wh.style.transformOrigin = '985px 715px';
    $('.s6-art').style.transform = `scale(${(1 + .03 * t / 13.01).toFixed(4)})`;
  });
})();
