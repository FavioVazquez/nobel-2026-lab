(function () {
  var sec = document.getElementById('shot-12');
  if (!sec) return;
  var q = function (s) { return sec.querySelector(s); };
  var NS = 'http://www.w3.org/2000/svg';
  var P = function (t, a, b, e) { return ST.progress(t, a, b, e || ST.ease.linear); };
  // deterministic tissue cells
  var cells = q('.cells'), r = ST.rand('shot-12-cells');
  for (var i = 0; i < 160; i++) {
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', (1060 + r() * 720).toFixed(1)); c.setAttribute('cy', (190 + r() * 560).toFixed(1));
    c.setAttribute('r', (2 + r() * 5).toFixed(1)); c.setAttribute('fill', '#cdb8ff'); c.setAttribute('opacity', (0.08 + r() * 0.16).toFixed(2));
    cells.appendChild(c);
  }
  var ca = q('.c-a'), cb = q('.c-b'), cone = q('.cone'), tip = q('.tip');
  var axon = q('#s12-axon'), L = axon.getTotalLength();
  var glow = q('.sp-glow'), core = q('.sp-core'), head = q('.sp-head');
  [glow, core].forEach(function (p) { p.setAttribute('d', axon.getAttribute('d')); });
  var SP = 8.28, SPEED = 1500, TAIL = 220, HIT = 8.0;
  ST.onSeek(function (t) {
    var cl = ST.clips().filter(function (k) { return k.id === 'shot-12'; })[0];
    var s = t - (cl ? cl.start : 0);
    // tissue + fading light: in on "Visible", the cone dies away by "tissue", all leaves before "Not any more"
    var tin = P(s, 1.8, 2.5, ST.ease.outCubic), tout = 1 - P(s, 7.3, 7.9);
    var tis = Math.min(tin, tout);
    q('.tissue').style.opacity = tis.toFixed(3); q('.tcap').style.opacity = tis.toFixed(3);
    var fade = P(s, 2.3, 4.6, ST.ease.inOutSine);
    cb.setAttribute('offset', (0.9 - 0.55 * fade).toFixed(3));
    ca.setAttribute('stop-opacity', (0.9 - 0.35 * fade).toFixed(3));
    cone.setAttribute('opacity', (0.95 - 0.1 * fade).toFixed(3));
    tip.setAttribute('opacity', (0.75 + 0.2 * Math.sin(s * 3.0)).toFixed(3));
    // cards leave
    var co = 1 - P(s, 7.6, 7.95);
    ['.txt'].forEach(function (k) { q(k).style.opacity = co.toFixed(3); });
    // closing: the opening neuron and blue pulse again (same drawing as shot 1)
    q('.neuron').style.opacity = P(s, 7.4, 8.0).toFixed(3);
    var hit = s - HIT, burst = hit >= 0 ? Math.exp(-hit * 1.6) : 0, base = P(s, HIT, HIT + 0.3, ST.ease.outCubic);
    var breath = (1 - base) * (0.10 + 0.07 * Math.sin(s * 2.1));
    q('.halo').style.opacity = Math.min(1, breath + base * (0.55 + 0.45 * burst)).toFixed(3);
    var rp = P(s, HIT, HIT + 0.9, ST.ease.outCubic), ring = q('.ring');
    ring.setAttribute('r', (60 + rp * 220).toFixed(1)); ring.style.opacity = (hit >= 0 ? (1 - rp) * 0.9 : 0).toFixed(3);
    q('.lit').style.opacity = (0.9 * base).toFixed(3);
    q('.idle').style.opacity = (0.75 - 0.35 * base).toFixed(3);
    var d = (s - SP) * SPEED, sg = q('.spikes'), vis = 0, hx = 0, hy = 0;
    if (d >= 0 && d <= L + TAIL) {
      var h = Math.min(d, L), st = Math.max(0, d - TAIL);
      glow.style.strokeDasharray = core.style.strokeDasharray = (h - st) + ' ' + (L * 2);
      glow.style.strokeDashoffset = core.style.strokeDashoffset = (-st) + 'px';
      var pt = axon.getPointAtLength(h); hx = pt.x; hy = pt.y; vis = d > L ? Math.max(0, 1 - (d - L) / TAIL) : 1;
      head.style.opacity = d > L ? 0 : 1;
    }
    sg.style.opacity = vis.toFixed(3);
    head.setAttribute('cx', hx.toFixed(1)); head.setAttribute('cy', hy.toFixed(1));
    var ta = SP + L / SPEED, bo = 0.25;
    if (s >= ta) bo = 0.45 + 0.55 * Math.exp(-(s - ta) * 2.2);
    q('.boutons').style.opacity = bo.toFixed(3);
  });
})();
