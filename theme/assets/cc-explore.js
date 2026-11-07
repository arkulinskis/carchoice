/* cc-explore.js: CarChoice's Explore engine (the filter rail + the data table), wrapped by Components/Explorer.

   CC.explorer(root, {json, state, picked, hooks}) -> api
     json    the catalogue as one JSON string {v, fields: [...], cars: [{id, s: {key: value}}]} (Cars.get_catalog)
     state   {q, f: {key: [lo, hi] | [values] | 1/0}, sort: [key, 1|-1], cols: [keys], units: 'metric'|'imperial', dense}
     picked  ids in the member's five (stars)
     hooks   change(jsonText), pick(id), open(id): Python functions (Explore page)
   api: setPicked(ids), setState(state), getState(), reset(), destroy()
   CC.encodeState / CC.decodeState: state <-> the URL-safe text after #explore/
   Everything is drawn here because it changes on every slider move; the page around it is Python Forms. */
(function () {
  'use strict';
  var CC = window.CC = window.CC || {};

  // ------------------------------------------------------------------ units and formatting
  var IMP = {
    'km': { u: 'mi', k: 0.621371 }, 'mm': { u: 'in', k: 0.0393701 }, 'kg': { u: 'lb', k: 2.20462 },
    'litres': { u: 'cu ft', k: 0.0353147 }, 'Nm': { u: 'lb-ft', k: 0.737562 }, 'km/h': { u: 'mph', k: 0.621371 },
    'L/100km': { u: 'mpg', inv: 235.215 }
  };
  function conv(field, units) { return units === 'imperial' ? IMP[field.unit] || null : null; }
  function toDisp(field, v, units) {
    var c = conv(field, units);
    if (!c || typeof v !== 'number') return v;
    return c.inv ? (v ? c.inv / v : v) : v * c.k;
  }
  function fromDisp(field, d, units) {
    var c = conv(field, units);
    if (!c || typeof d !== 'number') return d;
    return c.inv ? (d ? c.inv / d : d) : d / c.k;
  }
  function unitLabel(field, units) {
    var c = conv(field, units);
    if (c) return c.u;
    if (field.unit === 'litres') return 'L';
    if (field.unit === 'USD') return '$';
    return field.unit || '';
  }
  function decs(field, units) {
    var c = conv(field, units);
    if (c && c.u === 'mpg') return 0;
    if (c && c.u === 'in') return field.key === 'ground' ? 1 : 0;
    if (c && c.u === 'cu ft') return 1;
    return field.dec || 0;
  }
  function numText(field, v, units) {
    if (typeof v !== 'number') return '';
    var x = toDisp(field, v, units), d = decs(field, units);
    var year = !field.unit && x >= 1800 && x <= 2200 && x === Math.round(x);  /* 2026, not 2,026 */
    var s = x.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: !year });
    return field.unit === 'USD' ? '$' + s : s;
  }
  CC.fmt = function (field, v, units) {
    if (v === null || v === undefined || v === '' || (Array.isArray(v) && !v.length)) return '';
    if (field.kind === 'bool') return v ? 'Yes' : 'No';
    if (Array.isArray(v)) return v.join(' / ');
    if (typeof v === 'number') {
      var u = field.unit === 'USD' ? '' : unitLabel(field, units);
      return numText(field, v, units) + (u ? ' ' + u : '');
    }
    return String(v);
  };
  function esc(s) {
    return String(s === null || s === undefined ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function nice(span) {
    var raw = span / 120, p = Math.pow(10, Math.floor(Math.log10(raw || 1)));
    var m = raw / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  }
  function store(k, v) { try { if (v === undefined) return window.localStorage.getItem(k); window.localStorage.setItem(k, v); } catch (e) { return null; } }

  CC.encodeState = function (st) {
    try { return window.btoa(unescape(encodeURIComponent(JSON.stringify(st)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
    catch (e) { return ''; }
  };
  CC.decodeState = function (txt) {
    try {
      var b = String(txt || '').replace(/-/g, '+').replace(/_/g, '/');
      while (b.length % 4) b += '=';
      return JSON.parse(decodeURIComponent(escape(window.atob(b))));
    } catch (e) { return null; }
  };

  var ICON = {
    star: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.2l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/></svg>',
    search: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>',
    sliders: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>',
    cols: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><rect x="3.5" y="4.5" width="17" height="15" rx="1.5"/><path d="M9.5 4.5v15M15 4.5v15"/></svg>'
  };

  /* The Python wrapper's entry point: primitives and callbacks only (no Python dicts cross over). */
  CC.mountExplorer = function (root, json, stateText, pickedText, change, pick, open) {
    var st = null, pk = [];
    try { st = stateText ? JSON.parse(stateText) : null; } catch (e) { st = null; }
    try { pk = pickedText ? JSON.parse(pickedText) : []; } catch (e) { pk = []; }
    return CC.explorer(root, { json: json, state: st || {}, picked: pk, hooks: { change: change, pick: pick, open: open } });
  };

  // ------------------------------------------------------------------ the engine
  CC.explorer = function (root, opts) {
    var data = JSON.parse(opts.json);
    var fields = data.fields, cars = data.cars, hooks = opts.hooks || {};
    var F = {};
    fields.forEach(function (f) { F[f.key] = f; });
    var filterFields = fields.filter(function (f) { return f.filter && f.key !== 'model'; });
    var colFields = fields.filter(function (f) { return f.key !== 'make' && f.key !== 'model'; });
    var DEFAULT_COLS = colFields.filter(function (f) { return f.show; }).map(function (f) { return f.key; });
    var picked = {};
    var st = norm(opts.state || {});
    var blocks = {}, limit = 150, matches = [], lastSent = '', sendTimer = 0, drawTimer = 0, alive = true;
    (opts.picked || []).forEach(function (id) { picked[id] = 1; });

    // per-field domains (stable axes for sliders) and every option of choice fields
    var DOM = {};
    filterFields.forEach(function (f) {
      if (f.kind === 'number') {
        var vals = cars.map(function (c) { return c.s[f.key]; }).filter(function (v) { return typeof v === 'number'; });
        DOM[f.key] = vals.length ? { min: Math.min.apply(null, vals), max: Math.max.apply(null, vals), n: vals.length } : null;
      } else if (f.kind === 'choice' || f.kind === 'multi') {
        var cnt = {};
        cars.forEach(function (c) {
          var v = c.s[f.key];
          (Array.isArray(v) ? v : (v === undefined || v === null || v === '' ? [] : [v])).forEach(function (x) { cnt[x] = (cnt[x] || 0) + 1; });
        });
        var opts_ = Object.keys(cnt);
        if (f.key === 'make') opts_.sort(function (a, b) { return a.localeCompare(b); });
        else opts_.sort(function (a, b) { return cnt[b] - cnt[a] || a.localeCompare(b); });
        DOM[f.key] = { options: opts_, n: opts_.length ? 1 : 0 };
      } else if (f.kind === 'bool') {
        DOM[f.key] = { n: cars.some(function (c) { return c.s[f.key] === true; }) ? 1 : 0 };
      }
    });

    function norm(s) {
      var out = { q: typeof s.q === 'string' ? s.q : '', f: {}, sort: Array.isArray(s.sort) && F[s.sort[0]] ? s.sort : ['price', 1],
        cols: Array.isArray(s.cols) ? s.cols.filter(function (k) { return F[k] && k !== 'make' && k !== 'model'; }) : null,
        units: s.units === 'imperial' ? 'imperial' : (s.units === 'metric' ? 'metric' : (store('cc.units') === 'imperial' ? 'imperial' : 'metric')),
        dense: !!s.dense };
      if (!out.cols || !out.cols.length) out.cols = DEFAULT_COLS.slice();
      var f = s.f || {};
      Object.keys(f).forEach(function (k) {
        var fd = F[k];
        if (!fd) return;
        var v = f[k];
        if (fd.kind === 'number' && Array.isArray(v) && v.length === 2) out.f[k] = [typeof v[0] === 'number' ? v[0] : null, typeof v[1] === 'number' ? v[1] : null];
        else if ((fd.kind === 'choice' || fd.kind === 'multi') && Array.isArray(v) && v.length) out.f[k] = v.map(String);
        else if (fd.kind === 'bool' && (v === 1 || v === 0)) out.f[k] = v;
      });
      return out;
    }

    // ---------------------------------------------------------------- matching
    function test(c, k, cond) {
      var fd = F[k], v = c.s[k];
      if (fd.kind === 'number') {
        if (typeof v !== 'number') return false;
        if (cond[0] !== null && v < cond[0] - 1e-9) return false;
        if (cond[1] !== null && v > cond[1] + 1e-9) return false;
        return true;
      }
      if (fd.kind === 'bool') return cond === 1 ? v === true : v !== true;
      var have = Array.isArray(v) ? v : (v === undefined || v === null ? [] : [String(v)]);
      for (var i = 0; i < cond.length; i++) if (have.indexOf(cond[i]) >= 0) return true;
      return false;
    }
    var QF = ['make', 'model', 'body', 'size', 'tier', 'origin'];
    function hay(c) {
      if (!c._h) {
        var parts = QF.map(function (k) { return c.s[k] || ''; });
        ['fuel', 'drive', 'trans'].forEach(function (k) { parts.push((c.s[k] || []).join(' ')); });
        c._h = parts.join(' ').toLowerCase();
      }
      return c._h;
    }
    function passes(c, skip) {
      if (st.q) {
        var toks = st.q.toLowerCase().split(/\s+/);
        for (var t = 0; t < toks.length; t++) if (toks[t] && hay(c).indexOf(toks[t]) < 0) return false;
      }
      for (var k in st.f) if (k !== skip && !test(c, k, st.f[k])) return false;
      return true;
    }
    function active() { return Object.keys(st.f).length + (st.q ? 1 : 0); }

    // ---------------------------------------------------------------- skeleton
    root.innerHTML = '';
    root.classList.add('cx');
    var el = function (tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; };
    var bar = el('div', 'cx-bar');
    bar.innerHTML =
      '<button type="button" class="cx-btn cx-filters-btn" aria-controls="cx-rail">' + ICON.sliders + '<span>Filters</span><b class="cx-nact"></b></button>' +
      '<label class="cx-search">' + ICON.search + '<span class="ui-sr">Search the models</span><input type="search" placeholder="Search: make, model, body, fuel" autocomplete="off"></label>' +
      '<div class="cx-count" role="status" aria-live="polite"></div>' +
      '<div class="cx-tools">' +
      '<div class="cx-seg" role="group" aria-label="Units"><button type="button" data-u="metric">Metric</button><button type="button" data-u="imperial">Imperial</button></div>' +
      '<button type="button" class="cx-btn cx-dense-btn" aria-pressed="false">Compact rows</button>' +
      '<div class="cx-colwrap"><button type="button" class="cx-btn cx-col-btn" aria-expanded="false" aria-haspopup="true">' + ICON.cols + '<span>Columns</span></button><div class="cx-colpop" hidden></div></div>' +
      '</div>';
    var chips = el('div', 'cx-chips');
    var body = el('div', 'cx-body');
    var rail = el('div', 'cx-rail');
    rail.id = 'cx-rail';
    rail.setAttribute('aria-label', 'Filters');
    rail.setAttribute('role', 'region');
    var tableBox = el('div', 'cx-tablebox');
    body.appendChild(rail);
    body.appendChild(tableBox);
    root.appendChild(bar);
    root.appendChild(chips);
    root.appendChild(body);
    var qInput = bar.querySelector('input[type=search]');
    var countEl = bar.querySelector('.cx-count');
    var colPop = bar.querySelector('.cx-colpop');
    var colBtn = bar.querySelector('.cx-col-btn');

    // ---------------------------------------------------------------- the filter rail
    var railHead = el('div', 'cx-rail-head', '<b>Filters</b><span class="cx-rail-n"></span><button type="button" class="cx-link cx-clear-all">Clear all</button><button type="button" class="cx-btn cx-rail-close">Show results</button>');
    rail.appendChild(railHead);
    var openGroups = {};
    try { openGroups = JSON.parse(store('cc.groups') || '{}') || {}; } catch (e) { openGroups = {}; }
    var groups = [];
    filterFields.forEach(function (f) {
      var g = groups.filter(function (x) { return x.name === f.group; })[0];
      if (!g) { g = { name: f.group, fields: [] }; groups.push(g); }
      g.fields.push(f);
    });
    groups.forEach(function (g, gi) {
      var d = el('details', 'cx-group');
      var isOpen = openGroups[g.name] !== undefined ? openGroups[g.name] : gi < 3;
      if (isOpen) d.open = true;
      d.innerHTML = '<summary><span>' + esc(g.name) + '</span><b class="cx-gn"></b></summary>';
      d.addEventListener('toggle', function () { openGroups[g.name] = d.open; store('cc.groups', JSON.stringify(openGroups)); });
      var inner = el('div', 'cx-group-in');
      g.fields.forEach(function (f) { inner.appendChild(makeBlock(f)); });
      d.appendChild(inner);
      g.el = d;
      rail.appendChild(d);
    });

    function head(f) {
      var u = f.kind === 'number' ? unitLabel(f, st.units) : '';
      return '<div class="cx-fh"><span class="cx-fl" id="cxl-' + f.key + '">' + esc(f.label) +
        (u && u !== '$' ? ' <i class="cx-fu">' + esc(u) + '</i>' : '') + '</span>' +
        '<button type="button" class="cx-fx" aria-label="Clear ' + esc(f.label) + '" hidden>Clear</button></div>' +
        (f.help ? '<p class="cx-help">' + esc(f.help) + '</p>' : '');
    }

    function makeBlock(f) {
      var b = el('div', 'cx-f cx-f-' + f.kind);
      b.setAttribute('data-key', f.key);
      var dom = DOM[f.key];
      var blk = { f: f, el: b };
      blocks[f.key] = blk;
      if (!dom || !dom.n) {
        b.innerHTML = head(f) + '<p class="cx-nodata">No data yet. Admins can upload it.</p>';
        b.classList.add('cx-empty');
        blk.update = function () {};
        return b;
      }
      if (f.kind === 'number') buildNumber(blk, dom);
      else if (f.kind === 'bool') buildBool(blk);
      else buildChoice(blk, dom);
      b.querySelector('.cx-fx').addEventListener('click', function () { delete st.f[f.key]; changed(true); });
      return b;
    }

    function buildNumber(blk, dom) {
      var f = blk.f, b = blk.el;
      b.innerHTML = head(f) +
        '<div class="cx-hist" aria-hidden="true"></div>' +
        '<div class="cx-range"><input type="range" class="cx-lo" aria-label="' + esc(f.label) + ' from"><input type="range" class="cx-hi" aria-label="' + esc(f.label) + ' to"></div>' +
        '<div class="cx-mm"><input type="number" inputmode="decimal" class="cx-min" aria-label="' + esc(f.label) + ' minimum"><span aria-hidden="true">to</span>' +
        '<input type="number" inputmode="decimal" class="cx-max" aria-label="' + esc(f.label) + ' maximum"></div>' +
        '<p class="cx-unk"></p>';
      var lo = b.querySelector('.cx-lo'), hi = b.querySelector('.cx-hi'), mn = b.querySelector('.cx-min'), mx = b.querySelector('.cx-max');
      var hist = b.querySelector('.cx-hist'), unk = b.querySelector('.cx-unk');
      var bars = [];
      for (var i = 0; i < 24; i++) { var s = el('i'); hist.appendChild(s); bars.push(s); }
      function axis() {
        var a = toDisp(f, dom.min, st.units), z = toDisp(f, dom.max, st.units);
        var lo_ = Math.min(a, z), hi_ = Math.max(a, z), step = nice(hi_ - lo_ || 1);
        lo_ = Math.floor(lo_ / step) * step; hi_ = Math.ceil(hi_ / step) * step;
        if (hi_ === lo_) hi_ = lo_ + step;
        return { lo: lo_, hi: hi_, step: step };
      }
      function round(x, step) { var r = Math.round(x / step) * step; return parseFloat(r.toFixed(6)); }
      function setFromDisp(dLo, dHi) {
        var ax = axis();
        if (dLo > dHi) { var t = dLo; dLo = dHi; dHi = t; }
        var openLo = dLo <= ax.lo + ax.step / 2, openHi = dHi >= ax.hi - ax.step / 2;
        if (openLo && openHi) { delete st.f[f.key]; return; }
        var m1 = openLo ? null : fromDisp(f, dLo, st.units), m2 = openHi ? null : fromDisp(f, dHi, st.units);
        if (conv(f, st.units) && conv(f, st.units).inv) { var t2 = m1; m1 = m2; m2 = t2; }  // mpg runs the other way
        if (m1 !== null && m2 !== null && m1 > m2) { var t3 = m1; m1 = m2; m2 = t3; }
        st.f[f.key] = [m1 === null ? null : parseFloat(m1.toFixed(4)), m2 === null ? null : parseFloat(m2.toFixed(4))];
      }
      function onSlide() { setFromDisp(parseFloat(lo.value), parseFloat(hi.value)); changed(false); }
      lo.addEventListener('input', onSlide);
      hi.addEventListener('input', onSlide);
      lo.addEventListener('change', function () { changed(true); });
      hi.addEventListener('change', function () { changed(true); });
      function onType() {
        var ax = axis();
        var a = mn.value === '' ? ax.lo : parseFloat(mn.value), z = mx.value === '' ? ax.hi : parseFloat(mx.value);
        if (isNaN(a)) a = ax.lo;
        if (isNaN(z)) z = ax.hi;
        setFromDisp(a, z);
        changed(true);
      }
      mn.addEventListener('change', onType);
      mx.addEventListener('change', onType);
      blk.update = function (subset) {
        var ax = axis(), cond = st.f[f.key];
        [lo, hi].forEach(function (r) { r.min = ax.lo; r.max = ax.hi; r.step = ax.step; });
        var dLo = ax.lo, dHi = ax.hi;
        if (cond) {
          var a = cond[0] === null ? null : toDisp(f, cond[0], st.units), z = cond[1] === null ? null : toDisp(f, cond[1], st.units);
          if (conv(f, st.units) && conv(f, st.units).inv) { var t = a; a = z; z = t; }
          dLo = a === null ? ax.lo : a; dHi = z === null ? ax.hi : z;
        }
        if (document.activeElement !== lo) lo.value = dLo;
        if (document.activeElement !== hi) hi.value = dHi;
        var d = decs(f, st.units);
        if (document.activeElement !== mn) mn.value = cond && dLo > ax.lo ? round(dLo, Math.pow(10, -d)) : '';
        if (document.activeElement !== mx) mx.value = cond && dHi < ax.hi ? round(dHi, Math.pow(10, -d)) : '';
        mn.placeholder = numText(f, fromDisp(f, ax.lo, st.units), st.units).replace('$', '') || String(ax.lo);
        mx.placeholder = numText(f, fromDisp(f, ax.hi, st.units), st.units).replace('$', '') || String(ax.hi);
        mn.step = mx.step = String(ax.step);
        var pct1 = (dLo - ax.lo) / (ax.hi - ax.lo) * 100, pct2 = (dHi - ax.lo) / (ax.hi - ax.lo) * 100;
        b.querySelector('.cx-range').style.setProperty('--a', Math.max(0, pct1) + '%');
        b.querySelector('.cx-range').style.setProperty('--b', Math.min(100, pct2) + '%');
        // histogram of what the OTHER filters leave, the chosen band in colour
        var counts = new Array(bars.length).fill(0), missing = 0, maxc = 1;
        subset.forEach(function (c) {
          var v = c.s[f.key];
          if (typeof v !== 'number') { missing++; return; }
          var x = toDisp(f, v, st.units);
          var i2 = Math.min(bars.length - 1, Math.max(0, Math.floor((x - ax.lo) / (ax.hi - ax.lo) * bars.length)));
          counts[i2]++;
        });
        counts.forEach(function (n) { if (n > maxc) maxc = n; });
        bars.forEach(function (s, i3) {
          var mid = ax.lo + (i3 + 0.5) / bars.length * (ax.hi - ax.lo);
          s.style.height = (counts[i3] ? Math.max(8, counts[i3] / maxc * 100) : 0) + '%';
          s.className = mid >= dLo && mid <= dHi ? 'on' : '';
        });
        unk.textContent = cond && missing ? missing + ' without this figure are hidden' : (missing === subset.length && subset.length ? 'None of these have this figure' : '');
        b.querySelector('.cx-fx').hidden = !cond;
        b.classList.toggle('is-on', !!cond);
      };
    }

    function buildBool(blk) {
      var f = blk.f, b = blk.el;
      b.innerHTML = head(f) + '<div class="cx-tri" role="group" aria-labelledby="cxl-' + f.key + '">' +
        '<button type="button" data-v="">Any</button><button type="button" data-v="1">Yes <b></b></button><button type="button" data-v="0">No <b></b></button></div>';
      var btns = b.querySelectorAll('.cx-tri button');
      Array.prototype.forEach.call(btns, function (btn) {
        btn.addEventListener('click', function () {
          var v = btn.getAttribute('data-v');
          if (v === '') delete st.f[f.key]; else st.f[f.key] = parseInt(v, 10);
          changed(true);
        });
      });
      blk.update = function (subset) {
        var yes = 0;
        subset.forEach(function (c) { if (c.s[f.key] === true) yes++; });
        var cond = st.f[f.key];
        Array.prototype.forEach.call(btns, function (btn) {
          var v = btn.getAttribute('data-v');
          var on = v === '' ? cond === undefined : cond === parseInt(v, 10);
          btn.setAttribute('aria-pressed', on ? 'true' : 'false');
          var n = btn.querySelector('b');
          if (n) n.textContent = v === '1' ? yes : subset.length - yes;
        });
        b.querySelector('.cx-fx').hidden = cond === undefined;
        b.classList.toggle('is-on', cond !== undefined);
      };
    }

    function buildChoice(blk, dom) {
      var f = blk.f, b = blk.el, many = dom.options.length > 7, expanded = false;
      b.innerHTML = head(f) + (dom.options.length > 12 ? '<input type="search" class="cx-find" placeholder="Find a ' + esc(f.label.toLowerCase()) + '" aria-label="Find a ' + esc(f.label.toLowerCase()) + '">' : '') +
        '<div class="cx-opts" role="group" aria-labelledby="cxl-' + f.key + '"></div>' + (many ? '<button type="button" class="cx-link cx-more-opts"></button>' : '');
      var box = b.querySelector('.cx-opts'), find = b.querySelector('.cx-find'), more = b.querySelector('.cx-more-opts');
      var rows = dom.options.map(function (opt, i) {
        var lab = el('label', 'cx-opt');
        lab.innerHTML = '<input type="checkbox"><span>' + esc(opt) + '</span><b></b>';
        var cb = lab.querySelector('input');
        cb.value = opt;
        cb.addEventListener('change', function () {
          var cur = (st.f[f.key] || []).slice();
          var at = cur.indexOf(opt);
          if (cb.checked && at < 0) cur.push(opt);
          if (!cb.checked && at >= 0) cur.splice(at, 1);
          if (cur.length) st.f[f.key] = cur; else delete st.f[f.key];
          changed(true);
        });
        box.appendChild(lab);
        return { opt: opt, el: lab, cb: cb, n: lab.querySelector('b'), i: i };
      });
      if (find) find.addEventListener('input', function () { blk.update(blk.subset || cars); });
      if (more) more.addEventListener('click', function () { expanded = !expanded; blk.update(blk.subset || cars); });
      blk.update = function (subset) {
        blk.subset = subset;
        var cnt = {};
        subset.forEach(function (c) {
          var v = c.s[f.key];
          (Array.isArray(v) ? v : (v === undefined || v === null ? [] : [String(v)])).forEach(function (x) { cnt[x] = (cnt[x] || 0) + 1; });
        });
        var sel = st.f[f.key] || [], term = find ? find.value.trim().toLowerCase() : '', shown = 0;
        rows.forEach(function (r) {
          var on = sel.indexOf(r.opt) >= 0, n = cnt[r.opt] || 0;
          r.cb.checked = on;
          r.n.textContent = n;
          r.el.classList.toggle('zero', !n && !on);
          var match = !term || r.opt.toLowerCase().indexOf(term) >= 0;
          var visible = match && (on || expanded || term || !many || r.i < 6);
          r.el.hidden = !visible;
          if (visible) shown++;
        });
        if (more) { more.hidden = !!term; more.textContent = expanded ? 'Show fewer' : 'Show all ' + rows.length; }
        b.querySelector('.cx-fx').hidden = !sel.length;
        b.classList.toggle('is-on', !!sel.length);
      };
    }

    // ---------------------------------------------------------------- table
    tableBox.innerHTML = '<div class="cx-scroll" tabindex="0" role="region" aria-label="Matching models"><table class="cx-table"><thead></thead><tbody></tbody><tfoot></tfoot></table></div><div class="cx-foot"></div>';
    var scroller = tableBox.querySelector('.cx-scroll');
    var thead = tableBox.querySelector('thead'), tbody = tableBox.querySelector('tbody'), tfoot = tableBox.querySelector('tfoot');
    var foot = tableBox.querySelector('.cx-foot');

    function sortVal(c, k) {
      if (k === 'model') return (c.s.make + ' ' + c.s.model).toLowerCase();
      var v = c.s[k];
      if (Array.isArray(v)) return v.join('/').toLowerCase();
      if (typeof v === 'boolean') return v ? 1 : 0;
      return v;
    }
    function sortList(list) {
      var k = st.sort[0], dir = st.sort[1] || 1;
      return list.slice().sort(function (a, b) {
        var x = sortVal(a, k), y = sortVal(b, k);
        var nx = x === undefined || x === null || x === '', ny = y === undefined || y === null || y === '';
        if (nx && ny) return 0;
        if (nx) return 1;
        if (ny) return -1;
        if (x < y) return -dir;
        if (x > y) return dir;
        return (a.s.make + a.s.model).localeCompare(b.s.make + b.s.model);
      });
    }
    function th(key, label, unit, numeric) {
      var on = st.sort[0] === key;
      return '<th scope="col" class="' + (numeric ? 'num' : '') + (key === 'model' ? ' cx-name' : '') + '" aria-sort="' +
        (on ? (st.sort[1] > 0 ? 'ascending' : 'descending') : 'none') + '"><button type="button" data-sort="' + key + '">' +
        esc(label) + (unit ? ' <i>' + esc(unit) + '</i>' : '') + '<span class="cx-arrow" aria-hidden="true">' + (on ? (st.sort[1] > 0 ? '↑' : '↓') : '') + '</span></button></th>';
    }
    function median(list, k) {
      var v = list.map(function (c) { return c.s[k]; }).filter(function (x) { return typeof x === 'number'; }).sort(function (a, b) { return a - b; });
      if (!v.length) return null;
      var m = Math.floor(v.length / 2);
      return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
    }
    function drawTable() {
      var cols = st.cols.map(function (k) { return F[k]; }).filter(Boolean);
      thead.innerHTML = '<tr><th scope="col" class="cx-pickh"><span class="ui-sr">In your five</span></th>' + th('model', 'Model', '', false) +
        cols.map(function (f) { var u = f.kind === 'number' ? unitLabel(f, st.units) : ''; return th(f.key, f.label, u, f.kind === 'number'); }).join('') + '</tr>';
      var list = sortList(matches);
      var rows = list.slice(0, limit).map(function (c) {
        var name = esc(c.s.make) + ' <b>' + esc(c.s.model) + '</b>';
        var sub = [c.s.body, (c.s.fuel || []).join(' / ')].filter(Boolean).join(' · ');
        var on = !!picked[c.id];
        return '<tr data-id="' + esc(c.id) + '"' + (on ? ' class="picked"' : '') + '><td class="cx-pickc"><button type="button" class="cx-star" aria-pressed="' + on +
          '" aria-label="' + (on ? 'Remove ' : 'Add ') + esc(c.s.make + ' ' + c.s.model) + (on ? ' from' : ' to') + ' your five">' + ICON.star + '</button></td>' +
          '<td class="cx-name"><a href="#car/' + encodeURIComponent(c.id) + '" data-open="' + esc(c.id) + '">' + name + '</a><small>' + esc(sub) +
          (c.s.status === 'Discontinued' ? ' · <em>discontinued</em>' : '') + '</small></td>' +
          cols.map(function (f) {
            var v = c.s[f.key];
            if (v === undefined || v === null || v === '' || (Array.isArray(v) && !v.length)) return '<td class="' + (f.kind === 'number' ? 'num ' : '') + 'nil">–</td>';
            if (f.kind === 'number') return '<td class="num">' + esc(numText(f, v, st.units)) + '</td>';
            if (f.kind === 'bool') return '<td class="' + (v ? 'yes' : 'nil') + '">' + (v ? 'Yes' : '–') + '</td>';
            return '<td>' + esc(Array.isArray(v) ? v.join(' / ') : v) + '</td>';
          }).join('') + '</tr>';
      });
      if (!list.length) {
        rows = ['<tr class="cx-none"><td colspan="' + (cols.length + 2) + '"><b>No models match every filter.</b> Loosen one of the filters above, or <button type="button" class="cx-link cx-clear-all">clear them all</button>.</td></tr>'];
      }
      tbody.innerHTML = rows.join('');
      tfoot.innerHTML = list.length > 1 ? '<tr><th scope="row" colspan="2">Median of ' + list.length + '</th>' + cols.map(function (f) {
        if (f.kind !== 'number') return '<td></td>';
        var m = median(list, f.key);
        return '<td class="num">' + (m === null ? '' : esc(numText(f, m, st.units))) + '</td>';
      }).join('') + '</tr>' : '';
      foot.innerHTML = list.length > limit ? '<button type="button" class="cx-btn cx-show-more">Show ' + Math.min(150, list.length - limit) + ' more (' + (list.length - limit) + ' hidden)</button>' : '';
    }

    // ---------------------------------------------------------------- chips, counts, toolbar state
    function condText(k) {
      var f = F[k], c = st.f[k];
      if (f.kind === 'bool') return f.label + ': ' + (c === 1 ? 'yes' : 'no');
      if (f.kind === 'number') {
        var a = c[0] === null ? null : CC.fmt(f, c[0], st.units), z = c[1] === null ? null : CC.fmt(f, c[1], st.units);
        if (conv(f, st.units) && conv(f, st.units).inv) { var t = a; a = z; z = t; }
        if (a !== null && z !== null) return f.label + ' ' + a + ' to ' + z;
        return f.label + (a !== null ? ' from ' + a : ' up to ' + z);
      }
      return f.label + ': ' + c.join(', ');
    }
    function drawChips() {
      var keys = Object.keys(st.f);
      var parts = keys.map(function (k) {
        return '<button type="button" class="cx-chip" data-k="' + esc(k) + '" aria-label="Remove filter: ' + esc(condText(k)) + '">' + esc(condText(k)) + '<span aria-hidden="true">×</span></button>';
      });
      if (st.q) parts.unshift('<button type="button" class="cx-chip" data-k="__q" aria-label="Clear search ' + esc(st.q) + '">“' + esc(st.q) + '”<span aria-hidden="true">×</span></button>');
      chips.innerHTML = parts.length ? parts.join('') + '<button type="button" class="cx-link cx-clear-all">Clear all</button>' : '<span class="cx-hint">Use the filters (or search) to narrow the list. Star up to five cars.</span>';
    }
    function drawCounts() {
      countEl.innerHTML = '<b>' + matches.length + '</b> of ' + cars.length + ' models';
      var n = active();
      bar.querySelector('.cx-nact').textContent = n ? n : '';
      railHead.querySelector('.cx-rail-n').textContent = n ? n + ' on' : '';
      railHead.querySelector('.cx-rail-close').textContent = 'Show ' + matches.length + ' results';
      Array.prototype.forEach.call(bar.querySelectorAll('.cx-seg button'), function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-u') === st.units ? 'true' : 'false'); });
      bar.querySelector('.cx-dense-btn').setAttribute('aria-pressed', st.dense ? 'true' : 'false');
      root.classList.toggle('dense', st.dense);
      groups.forEach(function (g) {
        var on = g.fields.filter(function (f) { return st.f[f.key] !== undefined; }).length;
        g.el.querySelector('.cx-gn').textContent = on ? on : '';
      });
      if (document.activeElement !== qInput) qInput.value = st.q;
    }
    function drawColPop() {
      var gs = {};
      colFields.forEach(function (f) { (gs[f.group] = gs[f.group] || []).push(f); });
      colPop.innerHTML = '<div class="cx-colhead"><b>Columns</b><button type="button" class="cx-link cx-col-default">Default</button></div>' + Object.keys(gs).map(function (g) {
        return '<fieldset><legend>' + esc(g) + '</legend>' + gs[g].map(function (f) {
          return '<label class="cx-opt"><input type="checkbox" value="' + esc(f.key) + '"' + (st.cols.indexOf(f.key) >= 0 ? ' checked' : '') + '><span>' + esc(f.label) + '</span></label>';
        }).join('') + '</fieldset>';
      }).join('');
    }

    // ---------------------------------------------------------------- the update cycle
    function refresh() {
      matches = cars.filter(function (c) { return passes(c, null); });
      filterFields.forEach(function (f) {
        var blk = blocks[f.key];
        if (!blk || !blk.update) return;
        var sub = st.f[f.key] !== undefined ? cars.filter(function (c) { return passes(c, f.key); }) : matches;
        blk.update(sub);
      });
      drawCounts();
      drawChips();
    }
    function changed(now) {
      limit = 150;
      refresh();
      window.clearTimeout(drawTimer);
      if (now) drawTable(); else drawTimer = window.setTimeout(drawTable, 60);
      send();
    }
    function send() {
      window.clearTimeout(sendTimer);
      sendTimer = window.setTimeout(function () {
        if (!alive || !hooks.change) return;
        var list = sortList(matches);
        var tally = function (k) {
          var cnt = {};
          matches.forEach(function (c) { var v = c.s[k]; (Array.isArray(v) ? v : (v ? [v] : [])).forEach(function (x) { cnt[x] = (cnt[x] || 0) + 1; }); });
          return cnt;
        };
        var payload = JSON.stringify({
          state: st, count: matches.length, total: cars.length, active: active(),
          names: list.slice(0, 12).map(function (c) { return c.s.make + ' ' + c.s.model; }),
          makes: tally('make'), bodies: tally('body'), fuels: tally('fuel'), drives: tally('drive'),
          chips: Object.keys(st.f).map(condText), encoded: CC.encodeState(st)
        });
        if (payload !== lastSent) { lastSent = payload; hooks.change(payload); }
      }, 280);
    }

    // ---------------------------------------------------------------- events
    var qTimer = 0;
    qInput.addEventListener('input', function () {
      window.clearTimeout(qTimer);
      qTimer = window.setTimeout(function () { st.q = qInput.value.trim().slice(0, 80); changed(true); }, 160);
    });
    function onRootClick(e) {
      var t = e.target;
      var sortBtn = t.closest('[data-sort]');
      if (sortBtn) {
        var k = sortBtn.getAttribute('data-sort');
        st.sort = [k, st.sort[0] === k ? -st.sort[1] : (F[k] && F[k].better === 'high' ? -1 : 1)];
        drawTable(); send();
        var again = thead.querySelector('[data-sort="' + k + '"]');
        if (again) again.focus();
        return;
      }
      var star = t.closest('.cx-star');
      if (star) {
        var id = star.closest('tr').getAttribute('data-id');
        if (hooks.pick) hooks.pick(id);
        return;
      }
      var open = t.closest('[data-open]');
      if (open && !e.metaKey && !e.ctrlKey && !e.shiftKey && e.button === 0) {
        e.preventDefault();
        if (hooks.open) hooks.open(open.getAttribute('data-open'));
        return;
      }
      var chip = t.closest('.cx-chip');
      if (chip) {
        var ck = chip.getAttribute('data-k');
        if (ck === '__q') st.q = ''; else delete st.f[ck];
        changed(true);
        var next = chips.querySelector('.cx-chip') || qInput;
        next.focus();
        return;
      }
      if (t.closest('.cx-clear-all')) { st.f = {}; st.q = ''; changed(true); qInput.focus(); return; }
      if (t.closest('.cx-show-more')) { limit += 150; drawTable(); return; }
      var seg = t.closest('.cx-seg [data-u]');
      if (seg) { st.units = seg.getAttribute('data-u'); store('cc.units', st.units); rebuildHeads(); changed(true); return; }
      if (t.closest('.cx-dense-btn')) { st.dense = !st.dense; changed(true); return; }
      if (t.closest('.cx-col-btn')) { toggleCols(colPop.hidden); return; }
      if (t.closest('.cx-col-default')) { st.cols = DEFAULT_COLS.slice(); drawColPop(); drawTable(); send(); return; }
      if (t.closest('.cx-filters-btn')) { root.classList.add('rail-open'); document.documentElement.classList.add('cx-lock'); var first = rail.querySelector('summary'); if (first) first.focus(); return; }
      if (t.closest('.cx-rail-close')) { closeRail(); return; }
    }
    function closeRail() {
      if (!root.classList.contains('rail-open')) return;
      root.classList.remove('rail-open');
      document.documentElement.classList.remove('cx-lock');
      bar.querySelector('.cx-filters-btn').focus();
    }
    function toggleCols(show) {
      colPop.hidden = !show;
      colBtn.setAttribute('aria-expanded', show ? 'true' : 'false');
      if (show) drawColPop();
    }
    colPop.addEventListener('change', function (e) {
      var cb = e.target;
      if (!cb || cb.type !== 'checkbox') return;
      var k = cb.value, at = st.cols.indexOf(k);
      if (cb.checked && at < 0) {
        var order = colFields.map(function (f) { return f.key; });
        st.cols.push(k);
        st.cols.sort(function (a, b) { return order.indexOf(a) - order.indexOf(b); });
      }
      if (!cb.checked && at >= 0) st.cols.splice(at, 1);
      drawTable(); send();
    });
    function onDocClick(e) {
      if (!colPop.hidden && !e.target.closest('.cx-colwrap')) toggleCols(false);
    }
    function onKey(e) {
      if (e.key !== 'Escape') return;
      if (!colPop.hidden) { toggleCols(false); colBtn.focus(); }
      else closeRail();
    }
    function rebuildHeads() {
      filterFields.forEach(function (f) {
        var blk = blocks[f.key];
        if (!blk) return;
        var u = blk.el.querySelector('.cx-fu');
        if (u) u.textContent = unitLabel(f, st.units);
      });
    }
    root.addEventListener('click', onRootClick);
    document.addEventListener('click', onDocClick, true);
    document.addEventListener('keydown', onKey);

    refresh();
    drawTable();
    send();

    return {
      setPicked: function (ids) {
        picked = {};
        (ids || []).forEach(function (id) { picked[id] = 1; });
        Array.prototype.forEach.call(tbody.querySelectorAll('tr[data-id]'), function (tr) {
          var id = tr.getAttribute('data-id'), on = !!picked[id], b = tr.querySelector('.cx-star');
          tr.classList.toggle('picked', on);
          if (b) {
            b.setAttribute('aria-pressed', on ? 'true' : 'false');
            var nm = tr.querySelector('.cx-name a').textContent;
            b.setAttribute('aria-label', (on ? 'Remove ' : 'Add ') + nm + (on ? ' from' : ' to') + ' your five');
          }
        });
      },
      setState: function (s) { st = norm(s || {}); rebuildHeads(); changed(true); },
      getState: function () { return JSON.stringify(st); },
      reset: function () { st.f = {}; st.q = ''; changed(true); },
      count: function () { return matches.length; },
      destroy: function () {
        alive = false;
        window.clearTimeout(sendTimer); window.clearTimeout(drawTimer);
        root.removeEventListener('click', onRootClick);
        document.removeEventListener('click', onDocClick, true);
        document.removeEventListener('keydown', onKey);
        document.documentElement.classList.remove('cx-lock');
      }
    };
  };
})();
