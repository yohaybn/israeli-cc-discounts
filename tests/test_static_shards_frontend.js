const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const index = JSON.parse(fs.readFileSync('docs/data/business_index.json', 'utf8'));
const hashes = JSON.parse(fs.readFileSync('docs/data/' + index.benefit_hashes, 'utf8'));
const raw = JSON.parse(fs.readFileSync('docs/data/all_combined_discounts.json', 'utf8'));
const local = new Map();
const store = {
  getItem(k) { return local.get(k) || null; },
  setItem(k, v) { local.set(k, String(v)); },
  removeItem(k) { local.delete(k); },
};
const window = { localStorage: store, sessionStorage: store };
vm.runInNewContext(fs.readFileSync('docs/new_benefits.js', 'utf8'), { window });
const NewBenefits = window.NewBenefits;
assert.equal(hashes.catalog_version, index.catalog_version);
const examples = raw.filter((r) => r.club === 'חבר').slice(0, 20);
for (const row of examples) {
  assert(hashes.clubs.mcc.includes(NewBenefits.benefitKey(row, 'mcc')));
}
const first = NewBenefits.initHashes(hashes.clubs, (x) => x, ['mcc'], new Date('2026-09-26'));
assert.equal(first.items.length, 0);
const snapshot = JSON.parse(local.get(NewBenefits.STORAGE_KEY));
assert.equal(snapshot.clubs.mcc, hashes.clubs.mcc);
// The old snapshot is compatible with the new compact hash list.
assert(NewBenefits.splitHashes(hashes.clubs.mcc).size > 0);
console.log('static shard hash parity and snapshot tests passed');
