(function () {
  var sec = document.getElementById('shot-10');
  if (!sec) return;
  var plate = sec.querySelector('.plate'), imgs = [];
  for (var i = 0; i < 60; i++) {
    var im = document.createElement('img');
    im.src = 'assets/s10/r' + (i < 10 ? '0' : '') + i + '.jpg'; im.alt = ''; im.decoding = 'sync';
    plate.appendChild(im); imgs.push(im);
  }
  var fill = sec.querySelector('.g-fill'), val = sec.querySelector('.g-val'), cur = -1;
  var P = function (t, a, b, e) { return ST.progress(t, a, b, e || ST.ease.linear); };
  ST.onSeek(function (t) {
    var c = ST.clips().filter(function (k) { return k.id === 'shot-10'; })[0];
    var s = t - (c ? c.start : 0);
    // power rises through the asking line; the model's frames run 0 .. 1 degree C (frame 59 = limit)
    var p = P(s, 0.5, 6.0, ST.ease.inOutSine), idx = Math.round(p * 59);
    if (idx !== cur) { if (cur >= 0) imgs[cur].style.display = 'none'; imgs[idx].style.display = 'block'; cur = idx; }
    var gone = 1 - P(s, 6.0, 6.3);
    sec.querySelector('.txt').style.opacity = gone.toFixed(3); sec.querySelector('.plate-tag').style.opacity = gone.toFixed(3);
    plate.style.opacity = (P(s, 0.1, 0.9) * (0.55 + 0.45 * gone)).toFixed(3);
    // while the viewer thinks (the pause-and-think beat) the picture keeps drifting slowly: no frozen hold
    var dr = P(s, 5.5, 9.9);
    plate.style.transform = 'scale(' + (1 + 0.06 * dr).toFixed(4) + ') translateY(' + (-1.5 * dr).toFixed(2) + '%)';
    fill.style.width = (p * 100).toFixed(2) + '%';
    val.textContent = '+' + (idx / 59).toFixed(2) + ' °C';
  });
})();
