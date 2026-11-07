/* The main user journeys, run inside the real app (Anvil App Server) by tools/ui_test.py through tools/live/drive.mjs.
   Resolves to {ok, log}. Keep log lines ASCII (the Windows console).
   Visitor: landing -> Explore (search, a choice filter, a number filter, stars) -> tray -> compare -> a car page ->
   members-only page asks to sign in -> sign up -> the visitor's five moved into the account -> preferences, note ->
   two listings with the price check -> save a search, open it again -> brands -> where to buy -> profile, theme, sign out. */
(async function () {
  const log = [], t0 = Date.now();
  const say = (m) => log.push(((Date.now() - t0) / 1000).toFixed(1) + 's ' + m);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 20000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => e && e.getBoundingClientRect().width > 0;
  const byText = (sel, text) => $$(sel).find((e) => vis(e) && e.textContent.trim().replace(/\s+/g, ' ') === text);
  async function click(sel, text) {
    const el = await until(() => (text ? byText(sel, text) : $$(sel).find(vis)), sel + (text ? ' "' + text + '"' : ''));
    el.scrollIntoView({ block: 'center' });
    el.click();
    return el;
  }
  function type(input, value) {
    input.focus();
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function blur(input) { input.dispatchEvent(new Event('blur', { bubbles: false })); input.dispatchEvent(new FocusEvent('focusout', { bubbles: true })); input.blur(); }
  async function page(hash, ready, what) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && ready(), what || hash, 40000);
    await sleep(300);
  }
  const ok = (cond, msg) => { if (!cond) throw new Error('FAILED: ' + msg); say('ok   ' + msg); };
  const count = () => parseInt(($('.cx-count b') || {}).textContent || '0', 10);
  const rows = () => $$('.cx-table tbody tr[data-id]');

  try {
    try { localStorage.removeItem('cc.picks'); localStorage.removeItem('cc.prefs'); localStorage.setItem('cc.units', 'metric'); } catch (e) {}
    // ---- landing
    await page('#landing', () => $('.lp-hero'), 'landing');
    ok($('.lp-hero a[href="#auth/signup"]'), 'landing: hero with a sign-up link');
    ok($('.ui-header .ui-btn.primary'), 'landing: Create account in the header');
    await until(() => $('.hd-card:not(.hd-static) tbody tr') || $('.hd-static'), 'the hero example');
    ok($$('.hd-card tbody tr').length >= 5, 'landing: the live example draws its table');

    // ---- Explore as a visitor
    await page('#explore', () => rows().length > 20, 'explore');
    const total = count();
    ok(total >= 250, 'explore: the whole catalogue is in the table (' + total + ' models)');
    ok($$('.cx-f').length >= 30, 'explore: at least 30 filters in the rail (' + $$('.cx-f').length + ')');
    type($('.cx-search input'), 'hybrid');
    await until(() => count() < total && count() > 0, 'search narrows');
    const afterSearch = count();
    ok(true, 'explore: search "hybrid" leaves ' + afterSearch);
    $('.cx-chip').click();
    await until(() => count() === total, 'search chip clears');
    const suv = await until(() => $$('.cx-f[data-key="body"] .cx-opt').find((l) => /^SUV/.test(l.textContent.trim())), 'SUV option');
    suv.querySelector('input').click();
    await until(() => count() < total && $$('.cx-chip').some((c) => /Body: SUV/.test(c.textContent)), 'body filter');
    const suvs = count();
    ok(true, 'explore: Body SUV leaves ' + suvs + ' and shows a chip');
    const maxBox = $('.cx-f[data-key="price"] .cx-max');
    type(maxBox, '40000');
    await until(() => count() < suvs && $$('.cx-chip').some((c) => /Base price/.test(c.textContent)), 'price filter');
    ok(rows().every((r) => { const t = r.cells[2].textContent.replace(/[^0-9]/g, ''); return !t || parseInt(t, 10) <= 40000; }), 'explore: every row is $40,000 or less (' + count() + ')');
    await until(() => /^#explore\/.+/.test(location.hash), 'the address to follow the filters');
    ok(true, 'explore: the address keeps the filters');
    await until(() => $$('.ql-row').length >= 2, 'marketplace searches');
    ok($$('.ql-row a').every((a) => /^https:\/\//.test(a.href)), 'explore: the side panel lists marketplace searches');
    const sortBtn = $('.cx-table thead [data-sort="hp"]');
    if (sortBtn) { sortBtn.click(); await sleep(300); sortBtn.isConnected || 1; }
    // stars
    const first = rows()[0], second = rows()[1];
    const n1 = first.querySelector('.cx-name a').textContent.trim();
    first.querySelector('.cx-star').click();
    await until(() => $$('.tr-slot:not(.empty)').length === 1, 'first star');
    rows()[1].querySelector('.cx-star').click();
    await until(() => $$('.tr-slot:not(.empty)').length === 2, 'second star');
    ok($$('.cx-star[aria-pressed="true"]').length === 2, 'explore: two stars, two cars in the tray');
    ok(JSON.parse(localStorage.getItem('cc.picks') || '[]').length === 2, 'explore: a visitor\'s five is kept in the browser');
    // compare
    await click('.ex-tray-act .anvil-role-btn-primary button');
    await until(() => location.hash === '#compare' && window.UI_READY && $$('.cm-head .cm-cell').filter(vis).length === 2, 'compare', 30000);
    ok($$('.cm-row').length > 15 && $$('.cm-cell.best').length > 3, 'compare: two columns, best values marked');
    // a car page
    await page('#explore', () => rows().length > 5, 'explore again');
    ok($$('.cx-chip').length === 0, 'explore: a plain #explore starts without filters');
    const link = rows().find((r) => r.querySelector('.cx-name a').textContent.trim() === n1) || rows()[0];
    link.querySelector('.cx-name a').click();
    await until(() => /^#car\//.test(location.hash) && window.UI_READY && $$('.sp-row').length > 15, 'car page', 30000);
    ok($('.anvil-role-cr-model') && $$('.sg').length >= 4, 'car page: spec sheet in groups (' + $$('.sp-row').length + ' specs)');
    ok($$('.sp-rank').filter(vis).length > 5, 'car page: numbers show where the car ranks');
    ok($$('.mc-row').length === 6, 'car page: six similar models');
    await click('.cr-buttons .anvil-role-btn button', 'Find for sale');
    await until(() => $$('.find-listings .ql-row').length >= 2, 'find dialog');
    ok(true, 'car page: Find for sale lists marketplace searches');
    await click('.find-listings .anvil-role-btn button', 'Done');
    await until(() => !$$('.find-listings').some(vis), 'dialog closed');

    // ---- members-only page -> sign up -> the visitor's five comes along
    await page('#picks', () => true);
    await until(() => window.UI_READY && $$('.au-card input').length >= 2, 'redirected to sign in');
    ok(true, 'a members-only page asks visitors to sign in');
    await click('.au-card .ui-seg button', 'Create account');
    await until(() => $$('.au-card input').filter(vis).length >= 3, 'sign-up form');
    const inputs = $$('.au-card input[type=text], .au-card input[type=email], .au-card input[type=password]').filter(vis);
    type(inputs[0], 'Flow Tester'); type(inputs[1], 'flow' + Date.now() + '@example.com'); type(inputs[2], 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.au-card input[type=checkbox]');
    if (tick && !tick.checked) tick.click();
    await click('.anvil-role-btn-block button', 'Create account');
    await until(() => location.hash === '#picks' && window.UI_READY && $$('.pk-card').length === 5, 'back on Your five', 40000);
    ok($$('.pk-card:not(.is-empty)').length === 2, 'sign-up: the two cars picked as a visitor are in the account');
    ok($('.anvil-role-avatar button') && /FT/.test($('.anvil-role-avatar button').textContent), 'header: account button with initials');

    // ---- preferences + a note
    type($('.pk-prefs input[placeholder="30000"]'), '35000');
    type($('.pk-prefs input[placeholder="City or postcode"]'), 'Montreal');
    await click('.pk-prefs .anvil-role-btn button', 'Save');
    await until(() => /Saved\. Your searches use them now/.test(document.body.textContent), 'prefs saved');
    ok(true, 'your five: preferences saved');
    const note = $('.pk-card:not(.is-empty) textarea');
    type(note, 'Test drive on Saturday');
    note.dispatchEvent(new Event('blur'));
    blur(note);
    await until(() => /Note saved/.test(document.body.textContent), 'note saved', 15000);
    ok(true, 'your five: a note saves itself');

    // ---- two listings for the first car, then the price check
    for (const [price, year, km] of [['31000', '2022', '40000'], ['26500', '2022', '43000']]) {
      await click('.pk-card:not(.is-empty) .anvil-role-btn button', 'Add a listing');
      const url = await until(() => $$('.add-listing input[placeholder="https://..."]').find(vis), 'listing dialog');
      type(url, 'https://www.autotrader.ca/a/test-' + price);
      type($('.add-listing input[placeholder="27500"]'), price);
      type($('.add-listing input[placeholder="2022"]'), year);
      type($('.add-listing input[placeholder="45000"]'), km);
      await click('.add-listing .anvil-role-btn-primary button');
      await until(() => !$$('.add-listing').some(vis), 'listing saved', 20000);
      await sleep(400);
    }
    await until(() => /2 saved listings/.test(($('.pk-card:not(.is-empty)') || {}).textContent || ''), 'card counts listings');
    ok(/Best:/.test($('.pk-card:not(.is-empty)').textContent), 'your five: the card shows the best price so far');
    await page('#listings', () => $$('.ls-row').length === 2, 'listings');
    const verdicts = $$('.ls-score .anvil-role-badge').filter(vis).map((b) => b.textContent.trim());
    ok(verdicts.includes('Good price'), 'listings: the cheaper one is marked Good price (' + verdicts.join(', ') + ')');
    const dd = $('.ls-row select');
    dd.selectedIndex = 1; dd.dispatchEvent(new Event('change', { bubbles: true }));
    await until(() => /Marked: Contacted/.test(document.body.textContent), 'status saved');
    ok(true, 'listings: status changes save');

    // ---- save a search, open it again
    await page('#explore', () => rows().length > 5, 'explore for saving');
    const fuel = await until(() => $$('.cx-f[data-key="fuel"] .cx-opt').find((l) => /^Electric/.test(l.textContent.trim())), 'Electric option');
    fuel.querySelector('input').click();
    await until(() => $$('.cx-chip').some((c) => /Fuel: Electric/.test(c.textContent)), 'fuel filter');
    await sleep(500);
    await click('.ex-actions .anvil-role-btn-primary button');
    const nameBox = await until(() => $$('.save-search input').find(vis), 'save dialog');
    type(nameBox, 'Electric cars');
    await click('.save-search .anvil-role-btn-primary button');
    await until(() => !$$('.save-search').some(vis), 'search saved');
    await page('#searches', () => $$('.sr-row').length === 1, 'searches');
    ok(/Electric cars/.test($('.sr-row').textContent) && /Fuel: Electric/.test($('.sr-row').textContent), 'searches: the saved search is listed with its filters');
    await click('.sr-row .anvil-role-btn-primary button');
    await until(() => /^#explore\//.test(location.hash) && window.UI_READY && $$('.cx-chip').some((c) => /Fuel: Electric/.test(c.textContent)), 'search reopened', 30000);
    ok(rows().length > 0 && rows().every((r) => /Electric/.test(r.querySelector('.cx-name small').textContent)), 'searches: Open brings the filters back');

    // ---- brands, where to buy
    await page('#brands', () => $$('.br-row').length > 60, 'brands');
    type($('.br-bar input'), 'subaru');
    await until(() => $$('.br-row:not(.br-head)').length === 1, 'brand search');
    ok(/Subaru/.test($$('.br-row:not(.br-head)')[0].textContent), 'brands: search finds one brand');
    await page('#markets', () => $$('.mk-row').length > 3, 'markets');
    await click('.mk-regions .anvil-role-seg button', 'UK');
    await until(() => $$('.mk-row').length > 3 && /Auto Trader UK/.test(document.body.textContent), 'UK region');
    ok(true, 'where to buy: the region switch shows that region\'s sites');

    // ---- profile, theme, sign out
    await page('#profile', () => $('.pf-grid'), 'profile');
    type($('.pf-grid input'), 'Flow Tester Two');
    await click('.pf-grid .anvil-role-btn-primary button', 'Save');
    await until(() => /Flow Tester Two/.test($('.pf-head').textContent), 'name saved');
    ok(true, 'profile: name saved');
    await click('.anvil-role-avatar button');
    await click('.ui-menu .ui-seg button', 'Dark');
    ok(document.documentElement.classList.contains('ui-dark'), 'menu: Dark switches the theme');
    await click('.ui-menu .ui-seg button', 'Auto');
    await click('.ui-menu button', 'Sign out');
    await until(() => location.hash === '#landing' && window.UI_READY && $('.ui-header .ui-btn.primary'), 'signed out');
    ok(true, 'sign out: back to the landing page as a visitor');

    say('PASSED');
    return { ok: true, log: log };
  } catch (e) {
    say(String(e && e.message || e));
    return { ok: false, log: log };
  }
})();
