(function () {
  var sec = document.getElementById('shot-11');
  if (!sec) return;
  var P = function (t, a, b, e) { return ST.progress(t, a, b, e || ST.ease.linear); };
  // [row selector, appears (word "blue," / "yellow,"), count from, count to (lands on "thousand")]
  var rows = [['.r-blue', 0, 1.45, 2.42, 16441, 16441 / 31136], ['.r-yel', 3.20, 3.35, 4.55, 31136, 1]];
  var els = rows.map(function (r) { var e = sec.querySelector(r[0]); return { e: e, n: e.querySelector('.n'), b: e.querySelector('.bar i') }; });
  var fmt = function (v) { return Math.round(v).toLocaleString('en-US'); };
  ST.onSeek(function (t) {
    var c = ST.clips().filter(function (k) { return k.id === 'shot-11'; })[0];
    var s = t - (c ? c.start : 0);
    rows.forEach(function (r, i) {
      var a = i ? 0.3 + 0.7 * P(s, r[1], r[1] + 0.5, ST.ease.outCubic) : 1, k = P(s, r[2], r[3], ST.ease.outCubic);
      els[i].e.style.opacity = a.toFixed(3);
      els[i].e.style.transform = 'translateY(0)';
      els[i].n.textContent = fmt(r[4] * k);
      els[i].b.style.width = (k * r[5] * 100).toFixed(2) + '%';
    });
  });
})();
