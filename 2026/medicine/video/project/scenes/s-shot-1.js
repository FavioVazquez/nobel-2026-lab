(function () {
  var sec = document.getElementById('shot-1');
  if (!sec) return;
  var q = function (s) { return sec.querySelector(s); };
  var NS = 'http://www.w3.org/2000/svg';
  var P = function (t, a, b, e) { return ST.progress(t, a, b, e || ST.ease.linear); };
  // deterministic sky dots
  var sky = q('.sky'), r = ST.rand('shot-1-sky'), dots = [];
  for (var i = 0; i < 70; i++) {
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', (r() * 1920).toFixed(1)); c.setAttribute('cy', (r() * 1080).toFixed(1));
    c.setAttribute('r', (0.8 + r() * 1.6).toFixed(2)); c.setAttribute('fill', '#cdd3ff');
    sky.appendChild(c); dots.push([c, r() * 100, 0.12 + r() * 0.25]);
  }
  // drifting blue sparks toward the cell, and glints running in along the dendrites
  var parts = [], pr = ST.rand('shot-1-sparks');
  for (var j = 0; j < 46; j++) {
    var pc = document.createElementNS(NS, 'circle'); pc.setAttribute('fill', j % 3 ? '#8fc8ff' : '#cdbfff'); sky.appendChild(pc);
    parts.push({ el: pc, ph: pr(), per: 3.4 + pr() * 2.6, ang: pr() * Math.PI * 2, rad: 420 + pr() * 520, sw: (pr() - 0.5) * 1.6, sz: 1.6 + pr() * 2.4 });
  }
  var dd = [].slice.call(sec.querySelectorAll('#s1-lines path:not(#s1-soma):not(#s1-axon)')).map(function (p) { return p.getAttribute('d'); }).join(' ').split('M').filter(Boolean).slice(0, 14);
  var glints = dd.map(function (d, n) {
    var p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + d);
    var c2 = document.createElementNS(NS, 'circle'); c2.setAttribute('r', 5); c2.setAttribute('fill', '#cfe7ff');
    q('.neuron').insertBefore(c2, q('.halo'));
    return { path: p, L: p.getTotalLength(), el: c2, ph: (n * 0.37) % 1, per: 2.2 + (n % 5) * 0.45 };
  });
  var axon = q('#s1-axon'), L = axon.getTotalLength();
  var glow = q('.sp-glow'), core = q('.sp-core'), head = q('.sp-head');
  var ig = q('.ig-glow'), ic = q('.ig-core');
  [ig, ic].forEach(function (p) { p.setAttribute('d', axon.getAttribute('d')); });
  [glow, core].forEach(function (p) { p.setAttribute('d', axon.getAttribute('d')); });
  var orbG = q('.orb'), ghosts = [];
  for (var g = 0; g < 9; g++) {
    var o = document.createElementNS(NS, 'circle'); o.setAttribute('fill', 'url(#s1-halo)'); orbG.appendChild(o); ghosts.push(o);
  }
  var SPIKES = [8.80, 10.35], SPEED = 1000, TAIL = 190;
  var A = { x: 150, y: 1010 }, B = { x: 525, y: 780 };
  var orbPos = function (p) { var e = ST.ease.inQuad(p); return { x: A.x + (B.x - A.x) * e, y: A.y + (B.y - A.y) * e - Math.sin(p * Math.PI) * 60 }; };
  var HIT = 8.72;
  ST.onSeek(function (t) {
    var c = ST.clips().filter(function (k) { return k.id === 'shot-1'; })[0];
    var s = t - (c ? c.start : 0);
    dots.forEach(function (d) { d[0].setAttribute('transform', 'translate(' + (26 * ST.noise(s * 0.45 + d[1], 3)).toFixed(1) + ' ' + (-s * 3 + 12 * ST.noise(s * 0.25 + d[1], 5)).toFixed(1) + ')'); d[0].setAttribute('opacity', (d[2] * (0.6 + 0.4 * ST.noise(s * 0.4 + d[1], 7))).toFixed(3)); });
    var calm = 1 - P(s, 8.0, 8.7);
    parts.forEach(function (p) {
      var u = (s / p.per + p.ph) % 1, e = u * u * (3 - 2 * u), rr = p.rad * (1 - e) + 40, a = p.ang + p.sw * e;
      p.el.setAttribute('cx', (525 + Math.cos(a) * rr * 1.25).toFixed(1)); p.el.setAttribute('cy', (772 + Math.sin(a) * rr * 0.8).toFixed(1));
      var early = 1 - P(s, 3, 5);
      p.el.setAttribute('r', (p.sz * (1 + 0.9 * early)).toFixed(2));
      p.el.setAttribute('opacity', (Math.sin(Math.PI * u) * (0.95 * early + (0.35 + 0.5 * P(s, 0, 7)) * (1 - early)) * calm).toFixed(3));
    });
    glints.forEach(function (g) {
      var u = (s / g.per + g.ph) % 1, pt = g.path.getPointAtLength(g.L * (1 - u));
      g.el.setAttribute('cx', pt.x.toFixed(1)); g.el.setAttribute('cy', pt.y.toFixed(1));
      g.el.setAttribute('opacity', (Math.sin(Math.PI * u) * 0.85 * calm).toFixed(3));
    });
    var calm2 = 1 - P(s, 7.5, 8.3);
    var sw = q('.sweep'); sw.style.transform = 'translateX(' + (-25 + 70 * P(s, 0, 8.3, ST.ease.inOutSine)).toFixed(2) + '%)';
    sw.style.opacity = (0.85 * P(s, 0, 0.6) * calm2 * (0.8 + 0.2 * Math.sin(s * 2 * Math.PI / 1.6))).toFixed(3);
    var nu = q('.neuron'); nu.style.transform = 'translateX(' + (25 * P(s, 0, 6, ST.ease.inOutSine)).toFixed(2) + 'px) scale(' + (1 + 0.012 * Math.sin(s * 1.9) * calm2).toFixed(4) + ')';
    // idle signals: a soft 120 px pulse along the axon every second, 0.2 s to 7.5 s
    var k = Math.floor(s - 0.2), ts = s - 0.2 - k, idle = s >= 0.2 && s < 8.15 && k <= 7 ? 1 : 0;
    if (idle) {
      var hd = ts / 0.95 * (L + 120), stt = Math.max(0, hd - 120), hh = Math.min(hd, L), sg2 = hh - stt;
      if (sg2 > 0 && stt < L) {
        ig.style.strokeDasharray = ic.style.strokeDasharray = sg2 + ' ' + (L * 2);
        ig.style.strokeDashoffset = ic.style.strokeDashoffset = (-stt) + 'px';
      } else idle = 0;
    }
    q('.idle-sig').style.opacity = idle ? (0.55 * (1 - P(s, 7.6, 8.2))).toFixed(3) : 0;
    // orb flight
    var fl = P(s, 7.9, HIT);
    orbG.style.opacity = fl > 0 && s < HIT + 0.05 ? Math.min(1, fl * 4).toFixed(3) : 0;
    ghosts.forEach(function (o, k) {
      var pp = Math.max(0, fl - k * 0.045), pos = orbPos(pp);
      o.setAttribute('cx', pos.x.toFixed(1)); o.setAttribute('cy', pos.y.toFixed(1));
      o.setAttribute('r', (46 - k * 3.4).toFixed(1)); o.setAttribute('opacity', (1 - k / 10).toFixed(2));
    });
    // soma halo + burst ring + lit network
    var hit = s - HIT, burst = hit >= 0 ? Math.exp(-hit * 1.6) : 0;
    var again = s - SPIKES[1], burst2 = again >= 0 ? 0.55 * Math.exp(-again * 2.2) : 0;
    var base = P(s, HIT, HIT + 0.3, ST.ease.outCubic);
    var breath = (1 - base) * calm2 * 0.40 * (1 + 0.25 * Math.sin(s * 2 * Math.PI / 1.6));
    q('.halo').style.opacity = Math.min(1, breath + base * (0.55 + 0.45 * burst) + burst2).toFixed(3);
    var rp = P(s, HIT, HIT + 0.9, ST.ease.outCubic);
    var ring = q('.ring'); ring.setAttribute('r', (60 + rp * 220).toFixed(1));
    ring.style.opacity = (hit >= 0 ? (1 - rp) * 0.9 : 0).toFixed(3);
    q('.lit').style.opacity = (0.9 * base).toFixed(3);
    q('.idle').style.opacity = (0.75 - 0.35 * base).toFixed(3);
    // spikes along the axon
    var sg = q('.spikes'), vis = 0, hx = 0, hy = 0, arr = 0;
    SPIKES.forEach(function (t0, n) {
      var d = (s - t0) * SPEED;
      if (d >= 0 && d <= L + TAIL) {
        var h = Math.min(d, L), st = Math.max(0, d - TAIL);
        var seg = h - st;
        glow.style.strokeDasharray = core.style.strokeDasharray = seg + ' ' + (L * 2);
        glow.style.strokeDashoffset = core.style.strokeDashoffset = (-st) + 'px';
        var pt = axon.getPointAtLength(h); hx = pt.x; hy = pt.y; vis = n === 1 && d > L ? 0 : 1;
        if (d > L) vis = Math.max(0, 1 - (d - L) / TAIL);
        head.style.opacity = d > L ? 0 : 1;
      }
    });
    sg.style.opacity = vis.toFixed(3);
    head.setAttribute('cx', hx.toFixed(1)); head.setAttribute('cy', hy.toFixed(1));
    // boutons: flash on arrival, rest glow
    var arrive = SPIKES.map(function (t0) { return t0 + L / SPEED; }), bo = 0.25;
    arrive.forEach(function (ta) { if (s >= ta) bo = Math.max(bo, 0.45 + 0.55 * Math.exp(-(s - ta) * 2.2)); });
    q('.boutons').style.opacity = bo.toFixed(3);
  });
})();
