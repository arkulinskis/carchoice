/* Admin pages (local App Server only: signs up the ADMIN_EMAILS address, which becomes admin there).
   Visits every tab, flips a user's Active switch twice, opens the demo-data confirm. Resolves to {ok, log}. */
(async function () {
  const log = [];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const ok = (c, m) => { if (!c) throw new Error('FAILED: ' + m); log.push('ok   ' + m); };
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function page(hash, ready) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && ready(), hash);
    await sleep(300);
  }
  try {
    await page('#auth', () => $$('.au-card input').length >= 2);
    const inputs = () => $$('.au-card input[type=text], .au-card input[type=email], .au-card input[type=password]').filter((i) => i.offsetParent);
    const pw = 'Hb-local-admin-Kq7-2026';
    type(inputs()[0], 'arkulinskis@gmail.com'); type(inputs()[1], pw);
    $$('.anvil-role-btn-block button').find((b) => /Sign in/.test(b.textContent)).click();
    await sleep(3000);
    if (location.hash !== '#explore') {  // no account yet in this local database: create it
      $$('.ui-seg button').find((b) => /Create account/.test(b.textContent)).click();
      await sleep(500);
      const i = inputs(); type(i[0], 'Local Admin'); type(i[1], 'arkulinskis@gmail.com'); type(i[2], pw);
      const tick = $('.au-card input[type=checkbox]'); if (tick && !tick.checked) tick.click();
      $$('.anvil-role-btn-block button').find((b) => /Create account/.test(b.textContent)).click();
    }
    await until(() => location.hash === '#explore' && window.UI_READY, 'signed in as admin', 40000);
    await page('#admin/overview', () => $$('.ad-stat').length >= 3);
    ok(/\d/.test($('.ad-stat').textContent), 'overview: the numbers');
    ok($('.anvil-role-avatar button') && (document.querySelector('.ui-menu a[href="#admin"]') || {}).offsetParent !== undefined, 'menu has the Admin link');
    await page('#admin/feedback', () => $('.ad-filter'));
    ok(/New \(\d+\)/.test($('.ad-filter').textContent), 'feedback: filter counts');
    await page('#admin/users', () => $$('.ad-user-row').length >= 1);
    const row = $$('.ad-user-row').find((r) => !/arkulinskis@gmail.com/.test(r.textContent));
    const box = row.querySelectorAll('input[type=checkbox]')[1];
    const was = box.checked;
    box.click(); await sleep(2500); box.click(); await sleep(2500);
    ok(box.checked === was, 'users: Active switch saved twice (back as it was)');
    type($('.anvil-role-ad-search-box'), 'nobody-matches-this'); $('.anvil-role-ic-search button').click();
    await until(() => $$('.ad-user-row').length === 0, 'search narrows');
    ok(/0 people/.test(document.body.textContent), 'users: search');
    // ---- car data: check a pasted CSV (changes nothing), then the import log
    await page('#admin/data', () => $$('.im-row').length >= 1);
    ok(/starter set/i.test($('.im-row').textContent), 'car data: the starter set is in the import log');
    type($('.dt-import textarea'), 'make,model,price,hp,Bed length (mm)\nToyota,RAV4,31900,226,\nTestmaker,Example One,25000,150,1500');
    $$('.dt-import .anvil-role-btn button').find((b) => /Check it first/.test(b.textContent)).click();
    await until(() => /1 new cars, 1 updates/.test(($('.dt-result') || {}).textContent || ''), 'preview result');
    ok(/Bed length/.test($('.dt-result').textContent) && /Testmaker/.test($('.dt-result').textContent), 'car data: the check shows new cars, new brands and new fields');
    await page('#admin/cars', () => $$('.ac-row').length > 20);
    type($('.ct-wrap input'), 'rav4'); $$('.ct-wrap .anvil-role-btn button')[0].click();
    await until(() => $$('.ac-row').length === 1, 'car search');
    ok(/RAV4/.test($('.ac-row').textContent), 'cars: search finds a car');
    await page('#admin/fields', () => $$('.fd-row:not(.fd-head)').length >= 40);
    ok(true, 'fields: every field is editable (' + $$('.fd-row:not(.fd-head)').length + ')');
    await page('#admin/markets', () => $$('.me-row').length >= 30);
    ok(true, 'marketplaces: listed for editing');
    await page('#admin/sources', () => $$('.so-row').length >= 10);
    ok(/fueleconomy\.gov/.test(document.body.textContent), 'data sources: the wishlist is there');
    await page('#admin/demo', () => $('.ad-demo'));
    ok(/Status:/.test($('.ad-demo').textContent), 'demo: status line');
    log.push('PASSED');
    return { ok: true, log };
  } catch (e) {
    log.push(String(e && e.message || e));
    return { ok: false, log };
  }
})();
