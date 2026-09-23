(function (global) {
  'use strict';

  // "New in my clubs": benefits that appeared since the visitor's previous
  // visit, for the clubs they selected.
  //
  // The data has no per-record "added on" date, so the browser keeps a small
  // snapshot of what it saw last time: the visit time plus a short hash of
  // every benefit, grouped by club id, in localStorage. On the first page load
  // of a new browser session the current data is compared with that snapshot
  // and the snapshot is replaced. The result is kept in sessionStorage so
  // reloading the page in the same session shows the same list.
  //
  // Only club ids and hashes are stored. No personal data.
  const STORAGE_KEY = 'icc_seen_benefits';
  const SESSION_KEY = 'icc_new_benefits_session';
  const DISMISS_KEY = 'icc_new_benefits_dismissed';
  const HASH_WIDTH = 7;
  // A club where most records look new at once almost always changed its
  // text format, not its offers. Skip it instead of flooding the list.
  const FLOOD_MIN = 50;
  const FLOOD_SHARE = 0.5;

  function storage(kind) {
    try {
      const s = global[kind];
      if (!s) return null;
      const probe = '__icc_probe__';
      s.setItem(probe, '1');
      s.removeItem(probe);
      return s;
    } catch (e) {
      return null; // private mode or blocked storage: the feature just stays off
    }
  }

  function readJson(store, key) {
    if (!store) return null;
    try {
      const raw = store.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeJson(store, key, value) {
    if (!store) return false;
    try {
      store.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      return false;
    }
  }

  function norm(value) {
    return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().toLowerCase();
  }

  // Stable 7-char base36 hash (FNV-1a, 32 bit) of what makes a benefit distinct.
  function benefitKey(record, clubId) {
    const text = `${clubId}|${norm(record.business_name)}|${norm(record.discount)}`;
    let hash = 2166136261;
    for (let i = 0; i < text.length; i += 1) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(36).padStart(HASH_WIDTH, '0');
  }

  function splitHashes(packed) {
    const out = new Set();
    if (typeof packed !== 'string') return out;
    for (let i = 0; i + HASH_WIDTH <= packed.length; i += HASH_WIDTH) out.add(packed.slice(i, i + HASH_WIDTH));
    return out;
  }

  // Group records by resolved club id, each with its hash (duplicates dropped).
  function indexRecords(records, resolveClub) {
    const byClub = new Map();
    (records || []).forEach((record) => {
      if (!record || !record.business_name || !record.club) return;
      const club = resolveClub(record.club);
      const hash = benefitKey(record, club);
      if (!byClub.has(club)) byClub.set(club, new Map());
      const bucket = byClub.get(club);
      if (!bucket.has(hash)) bucket.set(hash, { ...record, club, _hash: hash });
    });
    return byClub;
  }

  // Pure comparison: which records are new relative to a previous snapshot.
  // Clubs without a previous snapshot have no baseline, so nothing in them
  // counts as new (a club added to "my clubs" today is not a flood of news).
  function diff(byClub, previous, scopeIds) {
    const fresh = [];
    const prevClubs = (previous && previous.clubs) || {};
    (scopeIds || Array.from(byClub.keys())).forEach((club) => {
      const bucket = byClub.get(club);
      if (!bucket || typeof prevClubs[club] !== 'string') return;
      const seen = splitHashes(prevClubs[club]);
      const added = [];
      bucket.forEach((record, hash) => { if (!seen.has(hash)) added.push(record); });
      if (added.length >= FLOOD_MIN && added.length > bucket.size * FLOOD_SHARE) return;
      fresh.push(...added);
    });
    return fresh;
  }

  // Snapshot to store after this visit: clubs in scope are replaced with what
  // is shown now, clubs outside the scope keep their older baseline.
  function nextSnapshot(byClub, previous, scopeIds, nowIso) {
    const clubs = { ...((previous && previous.clubs) || {}) };
    (scopeIds || Array.from(byClub.keys())).forEach((club) => {
      const bucket = byClub.get(club);
      if (bucket) clubs[club] = Array.from(bucket.keys()).join('');
    });
    return { v: 1, visited_at: nowIso, clubs };
  }

  // Run once per page load. Returns { since, items } where items are the new
  // benefit records (with .club set to the resolved id).
  function init(records, resolveClub, scopeIds, now) {
    const local = storage('localStorage');
    const session = storage('sessionStorage');
    const byClub = indexRecords(records, resolveClub);
    const all = new Map();
    byClub.forEach((bucket) => bucket.forEach((record, hash) => all.set(hash, record)));

    const cached = readJson(session, SESSION_KEY);
    if (cached && Array.isArray(cached.keys)) {
      return { since: cached.since || null, items: cached.keys.map((h) => all.get(h)).filter(Boolean) };
    }

    const previous = readJson(local, STORAGE_KEY);
    const items = previous ? diff(byClub, previous, scopeIds) : [];
    const nowIso = (now || new Date()).toISOString();
    const snapshot = nextSnapshot(byClub, previous, scopeIds, nowIso);
    if (!writeJson(local, STORAGE_KEY, snapshot)) {
      // Over quota: keep only the clubs in scope.
      writeJson(local, STORAGE_KEY, nextSnapshot(byClub, null, scopeIds, nowIso));
    }
    const since = previous && previous.visited_at ? previous.visited_at : null;
    writeJson(session, SESSION_KEY, { since, keys: items.map((r) => r._hash) });
    return { since, items };
  }

  function isDismissed() {
    const session = storage('sessionStorage');
    try { return !!(session && session.getItem(DISMISS_KEY)); } catch (e) { return false; }
  }

  function dismiss() {
    const session = storage('sessionStorage');
    try { if (session) session.setItem(DISMISS_KEY, '1'); } catch (e) { /* ignore */ }
  }

  global.NewBenefits = { init, diff, nextSnapshot, indexRecords, benefitKey, splitHashes, isDismissed, dismiss, STORAGE_KEY, SESSION_KEY, DISMISS_KEY };
})(window);
