(function (global) {
  'use strict';

  // Benefit type labels shown as a chip on each discount row. Keys are the
  // schema's discount_type values; unknown types get no chip.
  const TYPES = {
    billing_discount: { id: 'billing_discount', label: 'הנחה בחיוב', cls: 'type-billing' },
    rechargeable_card: { id: 'rechargeable_card', label: 'בטעינת כרטיס נטען', cls: 'type-recharge' },
    voucher: { id: 'voucher', label: 'שובר', cls: 'type-voucher' },
    gift_card: { id: 'gift_card', label: 'גיפטקארד', cls: 'type-giftcard' },
    club_card: { id: 'club_card', label: 'כרטיס מועדון', cls: 'type-clubcard' },
  };

  function typeInfo(type) {
    return TYPES[String(type || '').toLowerCase()] || null;
  }

  function formatPercent(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n <= 0) return null;
    return `${Number.isInteger(n) ? n : Number(n.toFixed(2))}%`;
  }

  // What one discount row shows: the main text, the terms line (or ''), and the
  // type chip. `text` is the already-cleaned discount text.
  function rowDisplay(disc, text) {
    const clean = String(text || '').trim();
    const type = typeInfo(disc && disc.discount_type);
    const percent = formatPercent(disc && disc.discount_value);
    if (type && type.id === 'rechargeable_card' && percent) {
      // The chip says "on the prepaid card load"; the row leads with the rate
      // and keeps the store terms on a second line.
      return { main: percent, isValue: true, terms: String((disc && disc.limitations) || '').trim(), type };
    }
    const isValue = /^\d+(?:\.\d+)?\s*%$/.test(clean);
    return { main: clean, isValue, terms: '', type };
  }

  global.BenefitTypes = { TYPES, typeInfo, formatPercent, rowDisplay };
})(typeof window !== 'undefined' ? window : globalThis);
