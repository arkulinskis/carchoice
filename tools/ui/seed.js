/* For screenshots of member pages: sign up a fresh account, star five cars, save listings (incl. worst-case data: a
   very long title, an unbroken link, one without a price), a saved search. Resolves to window.SEED. */
(async function () {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 30000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const vis = (e) => e && e.getBoundingClientRect().width > 0;
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  async function go(hash, ready) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash && ready(), hash, 40000);
    await sleep(300);
  }
  try {
    try { localStorage.removeItem('cc.picks'); } catch (e) {}
    await go('#auth/signup', () => $$('.au-card input').length >= 3);
    const inputs = $$('.au-card input[type=text], .au-card input[type=email], .au-card input[type=password]');
    type(inputs[0], 'Sam Rivera'); type(inputs[1], 'shots' + Date.now() + '@example.com'); type(inputs[2], 'Hb-' + Math.random().toString(36).slice(2) + '-Kq7');
    const tick = $('.au-card input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    $$('.anvil-role-btn-block button').find((b) => /Create account/.test(b.textContent)).click();
    await until(() => location.hash === '#explore' && window.UI_READY, 'explore', 60000);
    await until(() => $$('.cx-table tbody tr[data-id]').length > 20, 'table');
    for (const name of ['Toyota RAV4', 'Honda CR-V', 'Hyundai Ioniq 5', 'Mazda CX-5', 'Subaru Forester']) {
      const row = $$('.cx-table tbody tr[data-id]').find((r) => r.querySelector('.cx-name a').textContent.trim() === name);
      if (!row) continue;
      const before = $$('.tr-slot:not(.empty)').length;
      row.querySelector('.cx-star').click();
      await until(() => $$('.tr-slot:not(.empty)').length === before + 1, 'star ' + name);
    }
    window.UI_READY = false;
    await go('#picks', () => $$('.pk-card:not(.is-empty)').length >= 3);
    const listings = [
      ['https://www.autotrader.ca/a/toyota/rav4/montreal/quebec/5_61234567_on20250312', '2022 Toyota RAV4 XLE Hybrid AWD, one owner, full service history, winter tyres included, no accidents, certified pre-owned with extended warranty until 2027', '33900', '2022', '38000'],
      ['https://www.kijijiautos.ca/cars/toyota/rav4/used/#vip=98765432', '', '29500', '2021', '61000'],
      ['https://www.facebook.com/marketplace/item/1234567890123456789012345678901234567890/', 'RAV4 from a private seller', '', '2020', ''],
    ];
    for (const [url, title, price, year, km] of listings) {
      const btn = $$('.pk-card:not(.is-empty) .anvil-role-btn button').find((b) => /Add a listing/.test(b.textContent));
      btn.click();
      const box = await until(() => $$('.add-listing input[placeholder="https://..."]').find(vis), 'dialog');
      type(box, url);
      if (title) type($('.add-listing input[placeholder="e.g. 2022 RAV4 XLE, one owner"]'), title);
      if (price) type($('.add-listing input[placeholder="27500"]'), price);
      if (year) type($('.add-listing input[placeholder="2022"]'), year);
      if (km) type($('.add-listing input[placeholder="45000"]'), km);
      $('.add-listing .anvil-role-btn-primary button').click();
      await until(() => !$$('.add-listing').some(vis), 'saved');
      await sleep(500);
    }
    await go('#explore', () => $$('.cx-f[data-key="fuel"] .cx-opt').length > 0);
    const opt = $$('.cx-f[data-key="fuel"] .cx-opt').find((l) => /^Hybrid/.test(l.textContent.trim()));
    if (opt) opt.querySelector('input').click();
    await sleep(800);
    $('.ex-actions .anvil-role-btn-primary button').click();
    const nb = await until(() => $$('.save-search input').find(vis), 'save dialog');
    type(nb, 'Hybrids for the family, under thirty-five thousand, with room for a stroller and two dogs');
    $('.save-search .anvil-role-btn-primary button').click();
    await until(() => !$$('.save-search').some(vis), 'search saved');
    window.SEED = { home: '#explore' };
    return window.SEED;
  } catch (e) {
    return { error: String(e && e.message || e) };
  }
})();
