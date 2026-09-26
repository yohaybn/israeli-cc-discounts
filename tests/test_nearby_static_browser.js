const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const src = fs.readFileSync('docs/nearme.html', 'utf8').match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const index = JSON.parse(fs.readFileSync('docs/data/nearby_index.json', 'utf8'));
let requested = [];
const fetch = async (url) => {
  requested.push(url);
  return { ok: true, json: async () => JSON.parse(fs.readFileSync('docs/' + url, 'utf8')) };
};
const document = { getElementById() { return { innerText: '', classList: { add() {}, remove() {} }, addEventListener() {} }; } };
const registry = { build(labels) { return { labels, resolve(x) { return x; }, selectableIds: labels, byId: new Map() }; },
  initialSelection(r) { return new Set(r.selectableIds); }, renderFilters() {}, syncUrl() {}, maybeShowFirstVisitPicker() {} };
let ctx = { fetch, document, ProgramRegistry: registry, L: { layerGroup() { return {}; } },
  window: { addEventListener() {} }, console, Math, Set, Map, Promise };
// Keep the inline helpers callable from the VM without initializing Leaflet/geolocation.
vm.createContext(ctx);
vm.runInContext(src, ctx);
(async () => {
  const near = await vm.runInContext('loadBusinessesForBounds(32.076, 32.094, 34.770, 34.793)', ctx);
  assert(Array.isArray(near));
  assert(near.length > 0);
  assert(requested[0] === 'data/nearby_index.json');
  assert(!requested.includes('data/businesses_with_discounts.json'));
  assert(requested.every((x) => x === 'data/nearby_index.json' || x.startsWith('data/nearby_shards/')));
  const before = requested.length;
  await vm.runInContext('loadBusinessesForBounds(32.076, 32.094, 34.770, 34.793)', ctx);
  assert.equal(requested.length, before);
  console.log('nearby static cells, filtering and cache passed');
})().catch((err) => { console.error(err); process.exitCode = 1; });
