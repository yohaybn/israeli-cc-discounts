// Tests for the club selection encoded in the URL (?clubs=...) in docs/programs.js.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

// Values from the vm context come from another realm; compare by JSON shape.
const same = (actual, expected) => assert.deepStrictEqual(JSON.parse(JSON.stringify(actual)), expected);

const SRC = fs.readFileSync('docs/programs.js', 'utf8');

function makeContext(search, jar) {
  const cookies = jar || {};
  const document = {
    get cookie() { return Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; '); },
    set cookie(raw) {
      const [pair, ...attrs] = String(raw).split('; ');
      const eq = pair.indexOf('=');
      const name = pair.slice(0, eq);
      const maxAge = attrs.find((a) => a.toLowerCase().startsWith('max-age='));
      if (maxAge && Number(maxAge.slice(8)) <= 0) delete cookies[name];
      else cookies[name] = pair.slice(eq + 1);
    },
  };
  const loc = { href: `https://example.test/site/index.html${search || ''}`, search: search || '' };
  const replaced = [];
  const history = {
    state: null,
    replaceState(_s, _t, url) {
      replaced.push(url);
      const u = new URL(url);
      loc.href = u.toString();
      loc.search = u.search;
    },
  };
  const context = { window: {}, document, location: loc, history, URL, URLSearchParams };
  vm.createContext(context);
  vm.runInContext(SRC, context);
  return { P: context.window.ProgramRegistry, jar: cookies, loc, replaced };
}

const LABELS = ['חבר', 'חבר שלי', 'HOT', 'BUYME', 'HappyGift', 'MAX', 'GiftCard max', 'מפתח דיסקונט'];

// 1. ?clubs=buyme,happygift selects exactly those clubs (short ids work for non-curated clubs).
{
  const { P } = makeContext('?clubs=buyme,happygift');
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  same(Array.from(sel).sort(), ['buyme', 'program-happygift']);
  assert.strictEqual(r.fromUrl, true);
  assert.strictEqual(P.isUnfiltered(r, sel), false);
}

// 2. A top-level club in the URL expands to its sub-clubs that have data.
{
  const { P } = makeContext('?clubs=mcc');
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  same(Array.from(sel).sort(), ['mcc', 'mcc-sheli']);
}

// 3. Encoding compresses full parents and keeps loose sub-clubs.
{
  const { P } = makeContext('');
  const r = P.build(LABELS);
  P.initialSelection(r);
  assert.strictEqual(P.encodeSelection(r, new Set(['mcc', 'mcc-sheli', 'buyme'])), 'mcc,buyme');
  assert.strictEqual(P.encodeSelection(r, new Set(['max-giftcard'])), 'max-giftcard');
  assert.strictEqual(P.encodeSelection(r, new Set(r.selectableIds)), '');
}

// 4. The URL wins over the saved cookie, and opening a link does not overwrite the cookie.
{
  const jar = { icc_selected_clubs: encodeURIComponent(JSON.stringify(['hot'])) };
  const { P } = makeContext('?clubs=discount-key', jar);
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  same(Array.from(sel), ['discount-key']);
  assert.strictEqual(jar.icc_selected_clubs, encodeURIComponent(JSON.stringify(['hot'])));
}

// 5. The URL also wins over a "my clubs" scope and shows the full club list.
{
  const jar = { icc_my_clubs: encodeURIComponent(JSON.stringify(['hot'])) };
  const { P } = makeContext('?clubs=buyme', jar);
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  assert.strictEqual(r.scoped, false);
  same(Array.from(sel), ['buyme']);
  assert.strictEqual(r.scopeIds.length, r.selectableIds.length);
}

// 6. Without a URL the cookie still works as before.
{
  const jar = { icc_selected_clubs: encodeURIComponent(JSON.stringify(['hot'])) };
  const { P } = makeContext('', jar);
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  same(Array.from(sel), ['hot']);
  assert.strictEqual(r.fromUrl, false);
}

// 7. Unknown tokens are ignored; nothing known means no URL selection.
{
  const { P } = makeContext('?clubs=nope,also-nope');
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  assert.strictEqual(r.fromUrl, false);
  assert.strictEqual(sel.size, r.selectableIds.length);
}

// 8. Changing the selection updates the address bar and keeps other params.
{
  const { P, loc } = makeContext('?q=1');
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  sel.clear(); sel.add('buyme'); sel.add('program-happygift');
  P.persistSelection(r, sel);
  assert.strictEqual(loc.href, 'https://example.test/site/index.html?q=1&clubs=buyme,happygift');
  // Back to everything: the parameter is removed.
  r.selectableIds.forEach((id) => sel.add(id));
  P.persistSelection(r, sel);
  assert.strictEqual(loc.href, 'https://example.test/site/index.html?q=1');
}

// 9. shareUrl round-trips through readUrlSelection.
{
  const { P } = makeContext('');
  const r = P.build(LABELS);
  P.initialSelection(r);
  const link = P.shareUrl(r, new Set(['hot', 'max', 'max-giftcard']), 'https://example.test/');
  assert.strictEqual(link, 'https://example.test/?clubs=hot,max');
  same(P.readUrlSelection(r, new URL(link).search).sort(), ['hot', 'max', 'max-giftcard']);
}

// 10. A shared link skips the first-visit picker.
{
  const { P } = makeContext('?clubs=buyme');
  assert.strictEqual(P.needsFirstVisitPicker(), false);
  const { P: P2 } = makeContext('');
  assert.strictEqual(P2.needsFirstVisitPicker(), true);
}

console.log('share link tests passed');
