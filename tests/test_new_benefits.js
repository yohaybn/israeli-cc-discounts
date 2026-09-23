// Tests for docs/new_benefits.js ("new in my clubs since the last visit").
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

// Values from the vm context come from another realm; compare by JSON shape.
const same = (actual, expected) => assert.deepStrictEqual(JSON.parse(JSON.stringify(actual)), expected);

const SRC = fs.readFileSync('docs/new_benefits.js', 'utf8');

function memoryStorage() {
  const data = new Map();
  return {
    getItem: (k) => (data.has(k) ? data.get(k) : null),
    setItem: (k, v) => data.set(k, String(v)),
    removeItem: (k) => data.delete(k),
    _data: data,
  };
}

function makeContext(local, session) {
  const window = { localStorage: local || memoryStorage(), sessionStorage: session || memoryStorage() };
  const context = { window };
  vm.createContext(context);
  vm.runInContext(SRC, context);
  return { N: window.NewBenefits, window };
}

const resolve = (label) => label.toLowerCase();
const rec = (club, name, discount) => ({ club, business_name: name, discount, discount_url: `https://x.test/${name}` });

const day1 = [rec('A', 'Shop 1', '10%'), rec('A', 'Shop 2', '5%'), rec('B', 'Shop 3', '15%')];
const day2 = [...day1, rec('A', 'Shop 4', '20%'), rec('B', 'Shop 5', '7%'), rec('C', 'Shop 6', '1%')];

// 1. First visit ever: nothing is new, a snapshot is stored.
{
  const local = memoryStorage();
  const { N } = makeContext(local);
  const res = N.init(day1, resolve, ['a', 'b'], new Date('2026-09-20T10:00:00Z'));
  assert.strictEqual(res.items.length, 0);
  assert.strictEqual(res.since, null);
  const snap = JSON.parse(local.getItem(N.STORAGE_KEY));
  assert.strictEqual(snap.visited_at, '2026-09-20T10:00:00.000Z');
  same(Object.keys(snap.clubs).sort(), ['a', 'b']);
}

// 2. Next session: only records added in clubs with a baseline are new.
{
  const local = memoryStorage();
  makeContext(local).N.init(day1, resolve, ['a', 'b'], new Date('2026-09-20T10:00:00Z'));
  const { N } = makeContext(local, memoryStorage());
  const res = N.init(day2, resolve, ['a', 'b', 'c'], new Date('2026-09-22T10:00:00Z'));
  same(res.items.map((r) => r.business_name).sort(), ['Shop 4', 'Shop 5']);
  assert.strictEqual(res.since, '2026-09-20T10:00:00.000Z');
  // Club C had no baseline: none of it counts as new, but it is now recorded.
  const snap = JSON.parse(local.getItem(N.STORAGE_KEY));
  assert.ok(typeof snap.clubs.c === 'string');
}

// 3. A reload in the same session shows the same list, even though the snapshot moved on.
{
  const local = memoryStorage();
  makeContext(local).N.init(day1, resolve, ['a', 'b'], new Date('2026-09-20T10:00:00Z'));
  const session = memoryStorage();
  const first = makeContext(local, session).N.init(day2, resolve, ['a', 'b'], new Date('2026-09-22T10:00:00Z'));
  const again = makeContext(local, session).N.init(day2, resolve, ['a', 'b'], new Date('2026-09-22T10:05:00Z'));
  assert.strictEqual(JSON.stringify(again.items.map((r) => r._hash)), JSON.stringify(first.items.map((r) => r._hash)));
  assert.strictEqual(again.items.length, 2);
  assert.strictEqual(again.since, first.since);
  // A new session after that has nothing new.
  const later = makeContext(local, memoryStorage()).N.init(day2, resolve, ['a', 'b'], new Date('2026-09-23T10:00:00Z'));
  assert.strictEqual(later.items.length, 0);
}

// 4. Clubs outside this visit's scope keep their older baseline.
{
  const { N } = makeContext();
  const byClub = N.indexRecords(day1, resolve);
  const prev = { clubs: { z: 'abcdefg' } };
  const snap = N.nextSnapshot(byClub, prev, ['a'], '2026-09-23T00:00:00.000Z');
  assert.strictEqual(snap.clubs.z, 'abcdefg');
  assert.ok(snap.clubs.a.length === 14);
  assert.strictEqual(snap.clubs.b, undefined);
}

// 5. A club where most records suddenly look new (text format change) is skipped.
{
  const { N } = makeContext();
  const before = Array.from({ length: 60 }, (_, i) => rec('A', `S${i}`, `${i}%`));
  const after = Array.from({ length: 60 }, (_, i) => rec('A', `S${i}`, `${i} אחוז`));
  const prev = N.nextSnapshot(N.indexRecords(before, resolve), null, ['a'], 'x');
  assert.strictEqual(N.diff(N.indexRecords(after, resolve), prev, ['a']).length, 0);
}

// 6. Hash is stable, fixed width, and ignores whitespace/case differences.
{
  const { N } = makeContext();
  const h1 = N.benefitKey({ business_name: 'Shop  1', discount: '10%' }, 'a');
  const h2 = N.benefitKey({ business_name: 'shop 1', discount: ' 10% ' }, 'a');
  assert.strictEqual(h1, h2);
  assert.strictEqual(h1.length, 7);
  assert.notStrictEqual(h1, N.benefitKey({ business_name: 'shop 1', discount: '10%' }, 'b'));
}

// 7. Blocked storage: the feature stays off without throwing.
{
  const broken = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); }, removeItem() {} };
  const { N } = makeContext(broken, broken);
  const res = N.init(day2, resolve, ['a'], new Date());
  same(res.items.length, 0);
  assert.strictEqual(N.isDismissed(), false);
}

console.log('new benefits tests passed');
