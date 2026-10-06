(function () {
  var root = document.querySelector('.roadmap');
  if (!root) return;
  var steps = [].slice.call(root.querySelectorAll('.rm-step'));
  var LIT = [21.284, 42.174, 68.761, 125.764];   // video times: step i lights
  var IN = 13.0, OUT = 135.097, FOUR = 18.84;     // enter, leave, "Four steps" word
  var P = function (t, a, b, e) { return ST.progress(t, a, b, e || ST.ease.linear); };
  ST.onSeek(function (t) {
    var e = P(t, IN, IN + 0.6, ST.ease.outCubic) * (1 - P(t, OUT, OUT + 0.45, ST.ease.inCubic));
    // step aside during a pause-and-think beat (the beat's ring and answer chips use the bottom of the frame)
    var qa = 0;
    (ST.questions || []).forEach(function (q) { qa = Math.max(qa, P(t, q.t - 0.1, q.t + 0.25) * (1 - P(t, q.resume - 0.25, q.resume))); });
    e *= 1 - qa;
    root.style.opacity = e.toFixed(3);
    root.style.transform = 'translateY(' + ((1 - e) * 100).toFixed(2) + '%)';
    var cur = -1;
    LIT.forEach(function (a, i) { if (t >= a) cur = i; });
    steps.forEach(function (s, i) {
      var k = P(t, LIT[i], LIT[i] + 0.5, ST.ease.outCubic);
      var isCur = i === cur ? 1 : 0;
      var nxt = LIT[i + 1] !== undefined ? P(t, LIT[i + 1], LIT[i + 1] + 0.5) : 0;
      var cu = (i === cur ? 1 : 0) * 1 + (i === cur - 1 ? 1 - nxt : 0);
      var bt = t - (FOUR + i * 0.16);
      var bump = bt >= 0 && bt <= 0.5 ? Math.sin(Math.PI * bt / 0.5) : 0;
      s.style.setProperty('--k', k.toFixed(3));
      s.style.setProperty('--cur', Math.min(1, cu * k).toFixed(3));
      s.style.setProperty('--bump', bump.toFixed(3));
    });
  });
})();
