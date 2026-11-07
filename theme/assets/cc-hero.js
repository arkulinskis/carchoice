/* cc-hero.js: the landing page's live example (Components/HeroDemo). Three filters tighten one after another, the
   rows that don't fit fade out, and the five that are left drop into "Your five". Loops; with reduced motion it shows
   the finished state with a fade only. CC.hero(el) -> {destroy}. The template holds a static copy if this never runs. */
(function () {
  'use strict';
  var CC = window.CC = window.CC || {};
  var ROWS = [
    ['Toyota', 'RAV4', 31900, 'Hybrid', 5, 0],
    ['BMW', 'X5', 67000, 'Plug-in hybrid', 5, 1],
    ['Honda', 'CR-V', 30900, 'Hybrid', 5, 0],
    ['Mazda', 'MX-5', 30000, 'Petrol', 2, 2],
    ['Hyundai', 'Tucson', 29000, 'Hybrid', 5, 0],
    ['Jeep', 'Wrangler', 33000, 'Petrol', 5, 3],
    ['Tesla', 'Model Y', 40000, 'Electric', 5, 0],
    ['Kia', 'EV9', 55000, 'Electric', 7, 1],
    ['Chevrolet', 'Equinox EV', 35000, 'Electric', 5, 0]
  ];
  var STEPS = ['Price up to $40,000', 'At least 5 seats', 'Hybrid or electric'];
  function money(n) { return '$' + n.toLocaleString('en-US'); }

  CC.hero = function (el) {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var timers = [], alive = true;
    el.innerHTML =
      '<div class="hd-card" aria-label="An example: three filters narrow nine cars down to five" role="img">' +
      '<div class="hd-top"><span class="hd-title">Explore</span><span class="hd-count"><b>9</b> models</span></div>' +
      '<div class="hd-filters">' + STEPS.map(function (s, i) { return '<span class="hd-pill" data-i="' + i + '">' + s + '</span>'; }).join('') + '</div>' +
      '<div class="hd-slider"><span class="hd-label">Price</span><span class="hd-track"><i class="hd-band"></i><i class="hd-knob"></i></span><span class="hd-val">$70,000</span></div>' +
      '<table class="hd-table"><thead><tr><th><span class="ui-sr">Picked</span></th><th>Model</th><th class="num">Price</th><th>Fuel</th><th class="num">Seats</th></tr></thead><tbody>' +
      ROWS.map(function (r, i) {
        return '<tr data-i="' + i + '"><td class="hd-star"><svg viewBox="0 0 24 24"><path d="M12 3.2l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/></svg></td>' +
          '<td><span class="hd-make">' + r[0] + '</span> <b>' + r[1] + '</b></td><td class="num">' + money(r[2]) + '</td><td>' + r[3] + '</td><td class="num">' + r[4] + '</td></tr>';
      }).join('') + '</tbody></table>' +
      '<div class="hd-tray"><span class="hd-tray-label">Your five</span><div class="hd-slots">' +
      [0, 1, 2, 3, 4].map(function () { return '<span class="hd-slot"></span>'; }).join('') + '</div></div></div>';
    var rows = el.querySelectorAll('tbody tr'), pills = el.querySelectorAll('.hd-pill'), slots = el.querySelectorAll('.hd-slot');
    var count = el.querySelector('.hd-count b'), knob = el.querySelector('.hd-knob'), band = el.querySelector('.hd-band');
    var val = el.querySelector('.hd-val');
    function at(ms, fn) { timers.push(window.setTimeout(function () { if (alive) fn(); }, ms)); }
    function left(step) { return ROWS.filter(function (r) { return !r[5] || r[5] > step; }).length; }
    function setStep(step) {
      Array.prototype.forEach.call(pills, function (p, i) { p.classList.toggle('on', i < step); });
      Array.prototype.forEach.call(rows, function (tr, i) { var f = ROWS[i][5]; tr.classList.toggle('out', !!f && f <= step); });
      count.textContent = step ? left(step) : ROWS.length;
      var pos = step >= 1 ? 52 : 100;
      knob.style.transform = 'translateX(' + (pos - 100) + '%)';  /* the knob layer spans the track; its dot sits at the right end */
      band.style.transform = 'scaleX(' + pos / 100 + ')';
      val.textContent = step >= 1 ? '$40,000' : '$70,000';
    }
    function fill(n) {
      var keep = ROWS.map(function (r, i) { return [r, i]; }).filter(function (t) { return !t[0][5]; });
      Array.prototype.forEach.call(slots, function (s, i) {
        var on = i < n;
        s.classList.toggle('on', on);
        s.textContent = on ? keep[i][0][1] : '';
      });
      keep.forEach(function (t, i) { rows[t[1]].classList.toggle('picked', i < n); });
    }
    function cycle() {
      setStep(0); fill(0);
      at(900, function () { setStep(1); });
      at(2100, function () { setStep(2); });
      at(3300, function () { setStep(3); });
      for (var i = 1; i <= 5; i++) (function (n) { at(4300 + n * 380, function () { fill(n); }); })(i);
      at(9800, cycle);
    }
    if (reduce) { setStep(3); fill(5); el.classList.add('hd-still'); }
    else { el.classList.add('hd-live'); cycle(); }
    return { destroy: function () { alive = false; timers.forEach(window.clearTimeout); timers = []; } };
  };
})();
