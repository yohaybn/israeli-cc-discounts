// Tests for the "my clubs" scope used by the first-visit club picker.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const SRC = fs.readFileSync('docs/programs.js', 'utf8');

function makeContext(jar) {
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
  const context = { window: {}, document };
  vm.createContext(context);
  vm.runInContext(SRC, context);
  return { P: context.window.ProgramRegistry, jar: cookies };
}

const LABELS = ['חבר', 'חבר שלי', 'חבר טעמים', 'HOT', 'מפתח דיסקונט', 'GiftCard max', 'MAX'];

// 1. Brand-new visitor: picker needed, no scope, everything selected, unfiltered.
{
  const { P } = makeContext();
  assert.strictEqual(P.needsFirstVisitPicker(), true);
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  assert.strictEqual(r.scoped, false);
  assert.strictEqual(sel.size, r.selectableIds.length);
  assert.strictEqual(P.isUnfiltered(r, sel), true);
}

// 2. Visitor with a filter saved by the previous site version: no picker.
{
  const { P } = makeContext({ icc_selected_clubs: encodeURIComponent(JSON.stringify(['hot'])) });
  assert.strictEqual(P.needsFirstVisitPicker(), false);
}

// 3. "Show all" choice: no picker again, no scope.
{
  const { P, jar } = makeContext();
  P.saveMyClubs('all');
  assert.strictEqual(jar.icc_my_clubs, 'all');
  assert.strictEqual(P.needsFirstVisitPicker(), false);
  const r = P.build(LABELS);
  P.initialSelection(r);
  assert.strictEqual(r.scoped, false);
}

// 4. Chosen clubs: scope expands parents to observed sub-programs; results are filtered.
{
  const { P, jar } = makeContext();
  P.saveMyClubs(['mcc', 'hot']);
  const stored = JSON.parse(decodeURIComponent(jar.icc_my_clubs));
  assert.deepStrictEqual(stored, ['mcc', 'hot']);
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  assert.strictEqual(r.scoped, true);
  assert.deepStrictEqual(Array.from(sel).sort(), ['hot', 'mcc', 'mcc-sheli', 'mcc-teamim']);
  assert.strictEqual(P.isUnfiltered(r, sel), false);
  assert.strictEqual(P.needsFirstVisitPicker(), false);

  // Narrowing inside the scope is persisted; selecting the whole scope clears it.
  sel.delete('hot');
  P.persistSelection(r, sel);
  assert(jar.icc_selected_clubs, 'subset of scope should be saved');
  const next = makeContext(jar);
  const r2 = next.P.build(LABELS);
  const sel2 = next.P.initialSelection(r2);
  assert.deepStrictEqual(Array.from(sel2).sort(), ['mcc', 'mcc-sheli', 'mcc-teamim']);
  sel2.add('hot');
  next.P.persistSelection(r2, sel2);
  assert.strictEqual(jar.icc_selected_clubs, undefined);
}

// 5. Stale or corrupted "my clubs" values fall back to all clubs.
{
  const { P } = makeContext({ icc_my_clubs: encodeURIComponent(JSON.stringify(['no-such-club'])) });
  const r = P.build(LABELS);
  const sel = P.initialSelection(r);
  assert.strictEqual(r.scoped, false);
  assert.strictEqual(sel.size, r.selectableIds.length);
}
{
  const { P } = makeContext({ icc_my_clubs: '%7Bbroken' });
  assert.strictEqual(P.readMyClubs(), null);
}

// 6. Cookie holds only club ids.
{
  const { P, jar } = makeContext();
  P.saveMyClubs(['discount-key']);
  assert.deepStrictEqual(JSON.parse(decodeURIComponent(jar.icc_my_clubs)), ['discount-key']);
}

console.log('first-visit picker scope tests passed');
