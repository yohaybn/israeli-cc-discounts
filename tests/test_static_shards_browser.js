// Browser-independent fake-DOM exercise of the index path, including 48 cards.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const index = JSON.parse(fs.readFileSync('docs/data/business_index.json', 'utf8'));
let requested = [];
const elements = new Map();
class El {
  constructor() { this.children = []; this.classList = { add() {}, remove() {} }; this.style = { setProperty() {} }; this.dataset = {}; this.isConnected = true; }
  appendChild(child) { this.children.push(child); return child; }
  append(...kids) { kids.forEach((kid) => this.appendChild(kid)); }
  replaceWith(node) { this.replacement = node; }
  addEventListener() {}
  set innerHTML(x) { this.children = []; this._html = x; }
  get innerHTML() { return this._html || ''; }
  set textContent(x) { this._text = x; }
  get textContent() { return this._text || ''; }
}
const document = {
  cookie: '', addEventListener() {},
  getElementById(id) { if (!elements.has(id)) elements.set(id, new El()); return elements.get(id); },
  createElement() { return new El(); },
  createDocumentFragment() { return new El(); },
};
const programRegistry = {
  build(labels) {
    const byId = new Map(labels.map((x) => [x, { id: x, display_name: x, short_name: x, color: '#000' }]));
    return { byId, resolve(x) { return x; }, selectableIds: labels, scopeIds: labels, scoped: false, parents: [], descendants() { return []; } };
  },
  initialSelection(r) { return new Set(r.selectableIds); },
  renderFilters() {}, syncUrl() {}, maybeShowFirstVisitPicker() {},
  isUnfiltered() { return true; }, visibleParents() { return []; }, fallbackColor() { return '#000'; },
};
const fetch = async (url) => {
  requested.push(url);
  if (url === 'data/business_index.json') return { ok: true, json: async () => index };
  if (url.startsWith('data/discount_shards/')) return { ok: true, json: async () =>
    JSON.parse(fs.readFileSync('docs/' + url, 'utf8')) };
  if (url.startsWith('data/benefit_hashes-')) return { ok: true, json: async () =>
    JSON.parse(fs.readFileSync('docs/' + url, 'utf8')) };
  throw Error('unexpected fetch ' + url);
};
const window = { isSecureContext: false, addEventListener() {} };
const context = { document, window, navigator: {}, location: { search: '', href: '' }, ProgramRegistry: programRegistry,
  BenefitTypes: { rowDisplay(d) { return { main: d.discount || '', terms: '', type: null, isValue: false }; } },
  NewBenefits: undefined, fetch, setTimeout, clearTimeout, console, Intl, Set, Map, URLSearchParams };
vm.runInNewContext(fs.readFileSync('docs/app.js', 'utf8'), context);
(async () => {
  await new Promise((resolve) => setTimeout(resolve, 250));
  const grid = elements.get('cardsGrid');
  assert(grid.children.length === 1);
  const cards = grid.children[0].children;
  assert.equal(cards.length, 48);
  assert(cards.every((c) => c.replacement));
  assert(!requested.includes('data/all_combined_discounts.json'));
  assert(requested.filter((x) => x.includes('discount_shards/')).length <= 48);
  console.log('static index 48-card browser path passed');
})().catch((err) => { console.error(err); process.exitCode = 1; });
