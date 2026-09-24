const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('docs/benefit_types.js', 'utf8'), context);
const B = context.window.BenefitTypes;

// Labels for every schema type; unknown types get no chip.
assert.strictEqual(B.typeInfo('billing_discount').label, 'הנחה בחיוב');
assert.strictEqual(B.typeInfo('rechargeable_card').label, 'בטעינת כרטיס נטען');
assert.strictEqual(B.typeInfo('voucher').label, 'שובר');
assert.strictEqual(B.typeInfo('gift_card').label, 'גיפטקארד');
assert.strictEqual(B.typeInfo('club_card').label, 'כרטיס מועדון');
assert.strictEqual(B.typeInfo('card_benefit'), null);
assert.strictEqual(B.typeInfo(''), null);
assert.strictEqual(B.typeInfo(null), null);

// חבר credit card: "4%" billing row shows the value with the billing chip.
let r = B.rowDisplay({ discount_type: 'billing_discount', discount_value: 4 }, '4%');
assert.strictEqual(r.main, '4%');
assert.strictEqual(r.isValue, true);
assert.strictEqual(r.type.id, 'billing_discount');
assert.strictEqual(r.terms, '');

// חבר שלי prepaid card: row leads with the rate, terms go to the second line.
r = B.rowDisplay(
  { discount_type: 'rechargeable_card', discount_value: 30, limitations: 'עד 1000 שח לעסקה' },
  '30% הנחה בטעינת כרטיס חבר שלי'
);
assert.strictEqual(r.main, '30%');
assert.strictEqual(r.isValue, true);
assert.strictEqual(r.type.id, 'rechargeable_card');
assert.strictEqual(r.terms, 'עד 1000 שח לעסקה');

// Descriptive text stays as-is.
r = B.rowDisplay({ discount_type: 'billing_discount', discount_value: 8 }, '8% הנחה במעמד החיוב');
assert.strictEqual(r.main, '8% הנחה במעמד החיוב');
assert.strictEqual(r.isValue, false);

// Voucher text keeps its wording and gets the voucher chip.
r = B.rowDisplay({ discount_type: 'voucher', discount_value: null }, 'שובר 100 ב-85');
assert.strictEqual(r.main, 'שובר 100 ב-85');
assert.strictEqual(r.type.id, 'voucher');

// Prepaid row without a value falls back to its text.
r = B.rowDisplay({ discount_type: 'rechargeable_card', discount_value: null }, 'הטבה בכרטיס');
assert.strictEqual(r.main, 'הטבה בכרטיס');

assert.strictEqual(B.formatPercent(12.5), '12.5%');
assert.strictEqual(B.formatPercent(0), null);

console.log('benefit_types: ok');
