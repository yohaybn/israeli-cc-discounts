(function (global) {
  'use strict';

  const CURATED = [
    { id: 'mcc', parent_id: null, display_name: 'חבר', short_name: 'חבר', aliases: ['MCC', 'mcc', 'חבר'], color: '#f59e0b', sort_order: 10 },
    { id: 'mcc-sheli', parent_id: 'mcc', display_name: 'חבר שלי', short_name: 'חבר שלי', aliases: ['חבר שלי'], color: '#f59e0b', sort_order: 11 },
    { id: 'mcc-teamim', parent_id: 'mcc', display_name: 'חבר טעמים', short_name: 'חבר טעמים', aliases: ['חבר טעמים'], color: '#f59e0b', sort_order: 12 },
    { id: 'hot', parent_id: null, display_name: 'מועדון הוט', short_name: 'HOT', aliases: ['HOT', 'hot', 'מועדון הוט'], color: '#f43f5e', sort_order: 20 },
    { id: 'htzone', parent_id: null, display_name: 'הייטק זון', short_name: 'HTzone', aliases: ['HTzone', 'htzone'], color: '#06b6d4', sort_order: 30 },
    { id: 'buyme', parent_id: null, display_name: 'Buyme', short_name: 'BUYME', aliases: ['BUYME'], alias_patterns: ['BUYME'], color: '#3b82f6', sort_order: 40 },
    { id: 'max', parent_id: null, display_name: 'MAX', short_name: 'MAX', aliases: ['MAX'], color: '#8b5cf6', sort_order: 50 },
    { id: 'max-giftcard', parent_id: 'max', display_name: 'GiftCard max', short_name: 'GiftCard max', aliases: ['GiftCard max'], color: '#8b5cf6', sort_order: 51 },
    { id: 'max-super-giftcard', parent_id: 'max', display_name: 'Super GiftCard max', short_name: 'Super GiftCard max', aliases: ['Super GiftCard max'], color: '#8b5cf6', sort_order: 52 },
    { id: 'max-food', parent_id: 'max', display_name: 'Giftcard Food', short_name: 'Giftcard Food', aliases: ['Giftcard Food'], color: '#8b5cf6', sort_order: 53 },
    { id: 'max-executive', parent_id: 'max', display_name: 'כרטיס הטבות executive', short_name: 'MAX executive', aliases: ['כרטיס הטבות executive'], color: '#8b5cf6', sort_order: 54 },
    { id: 'discount-key', parent_id: null, display_name: 'מפתח דיסקונט', short_name: 'מפתח דיסקונט', aliases: ['מפתח דיסקונט'], color: '#0ea765', sort_order: 60 }
  ];

  function slug(value) {
    const normalized = String(value || '').trim().toLowerCase()
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\u0590-\u05ff]+/g, '-').replace(/^-|-$/g, '');
    if (normalized) return `program-${normalized}`;
    let hash = 2166136261;
    for (const ch of String(value || 'program')) hash = Math.imul(hash ^ ch.charCodeAt(0), 16777619);
    return `program-${(hash >>> 0).toString(36)}`;
  }

  function fallbackColor(id) {
    let hash = 0;
    for (const ch of id) hash = ((hash << 5) - hash + ch.charCodeAt(0)) | 0;
    return `hsl(${Math.abs(hash) % 360} 68% 52%)`;
  }

  function build(sourceLabels) {
    const programs = CURATED.map((p) => ({ ...p, aliases: [...(p.aliases || [])] }));
    const aliases = new Map();
    programs.forEach((p) => p.aliases.forEach((a) => aliases.set(String(a).trim().toLowerCase(), p.id)));

    function resolve(label) {
      const raw = String(label || '').trim();
      const exact = aliases.get(raw.toLowerCase());
      if (exact) return exact;
      const pattern = programs.find((p) => (p.alias_patterns || []).some((x) => raw.toUpperCase().includes(x.toUpperCase())));
      if (pattern) return pattern.id;
      const id = slug(raw);
      if (!programs.some((p) => p.id === id)) {
        programs.push({ id, parent_id: null, display_name: raw || 'מועדון', short_name: raw || 'מועדון', aliases: raw ? [raw] : [], color: fallbackColor(id), sort_order: 1000 });
        if (raw) aliases.set(raw.toLowerCase(), id);
      }
      return id;
    }

    const observedIds = new Set((sourceLabels || []).filter(Boolean).map(resolve));
    const byId = new Map(programs.map((p) => [p.id, p]));
    const children = new Map();
    programs.forEach((p) => {
      if (p.parent_id) children.set(p.parent_id, [...(children.get(p.parent_id) || []), p.id]);
    });
    const parents = programs.filter((p) => !p.parent_id).sort((a, b) => (a.sort_order || 999) - (b.sort_order || 999) || a.display_name.localeCompare(b.display_name, 'he'));
    const descendants = (id) => {
      const direct = children.get(id) || [];
      return direct.length ? direct.flatMap((child) => [child, ...descendants(child)]) : [];
    };
    const selectableIds = Array.from(observedIds);
    const matches = (selected, programId) => selected.has(programId);
    return { programs, byId, parents, children, descendants, selectableIds, observedIds, resolve, matches };
  }

  function aggregateCounts(registry, directCounts) {
    const result = { ...directCounts };
    registry.parents.forEach((parent) => {
      const ids = [parent.id, ...registry.descendants(parent.id)];
      result[parent.id] = ids.reduce((sum, id) => sum + (directCounts[id] || 0), 0);
    });
    return result;
  }


  // --- Club selection persistence (cookies) -------------------------------
  // Stores only program/club identifiers (e.g. "mcc", "discount-key") so the
  // visitor's club filter choice survives between sessions. No personal data
  // is ever written. Everything is best-effort: when cookies are unavailable
  // or blocked the site simply falls back to the default (all clubs).
  const SELECTION_COOKIE = 'icc_selected_clubs';
  const SELECTION_COOKIE_MAX_AGE = 60 * 60 * 24 * 365; // one year

  function cookiesAvailable() {
    return typeof document !== 'undefined' && typeof document.cookie === 'string';
  }

  function readSavedSelection() {
    if (!cookiesAvailable()) return null;
    try {
      const prefix = `${SELECTION_COOKIE}=`;
      const entry = document.cookie.split('; ').find((row) => row.startsWith(prefix));
      if (!entry) return null;
      const parsed = JSON.parse(decodeURIComponent(entry.slice(prefix.length)));
      if (!Array.isArray(parsed)) return null;
      const ids = parsed.filter((id) => typeof id === 'string' && id);
      return ids.length ? ids : null;
    } catch (e) {
      return null; // corrupted cookie: ignore and use the default selection
    }
  }

  function writeSelectionCookie(value, maxAge) {
    if (!cookiesAvailable()) return;
    try {
      document.cookie = `${SELECTION_COOKIE}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
    } catch (e) {
      // Cookies blocked (private mode, browser settings): persistence is skipped.
    }
  }

  function saveSelection(ids) {
    writeSelectionCookie(JSON.stringify(ids), SELECTION_COOKIE_MAX_AGE);
  }

  function clearSavedSelection() {
    writeSelectionCookie('', 0);
  }

  // The initial selection for a page: the saved subset when one exists and is
  // still valid for the clubs in scope (the visitor's "my clubs" when chosen,
  // otherwise every observed club), otherwise every club in scope.
  function initialSelection(registry) {
    applyScope(registry);
    const scope = registry.scopeIds || registry.selectableIds || [];
    const saved = readSavedSelection();
    if (saved) {
      const valid = saved.filter((id) => scope.includes(id));
      if (valid.length && valid.length < scope.length) return new Set(valid);
      // A saved selection that no longer matches anything (or that matches
      // everything) is stale: drop it so new clubs are selected by default.
      clearSavedSelection();
    }
    return new Set(scope);
  }

  // Persist after a user change. Selecting every club in scope is the default
  // state, so it clears the cookie instead of freezing today's club list (which
  // would hide clubs added to the data later).
  function persistSelection(registry, selected) {
    const scope = registry.scopeIds || registry.selectableIds || [];
    if (!scope.length) return;
    const allSelected = scope.every((id) => selected.has(id));
    if (allSelected || selected.size === 0) {
      clearSavedSelection();
      return;
    }
    saveSelection(Array.from(selected).filter((id) => scope.includes(id)));
  }

  // --- "My clubs" (first-visit picker) ------------------------------------
  // A separate cookie holds the top-level club ids the visitor said they have,
  // or the string "all" when they chose to see every club. Only ids, one year.
  // When it holds ids, only those clubs are shown in the filter row and used
  // for results; the per-session filter chips then work inside that scope.
  const MY_CLUBS_COOKIE = 'icc_my_clubs';

  function readCookie(name) {
    if (!cookiesAvailable()) return null;
    try {
      const prefix = `${name}=`;
      const entry = document.cookie.split(';').map((c) => c.trim()).find((row) => row.startsWith(prefix));
      return entry ? decodeURIComponent(entry.slice(prefix.length)) : null;
    } catch (e) {
      return null;
    }
  }

  function writeCookie(name, value, maxAge) {
    if (!cookiesAvailable()) return;
    try {
      document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
    } catch (e) {
      // Cookies blocked: the picker simply shows again next visit.
    }
  }

  // null = never chosen, 'all' = every club, array = chosen top-level ids.
  function readMyClubs() {
    const raw = readCookie(MY_CLUBS_COOKIE);
    if (raw == null || raw === '') return null;
    if (raw === 'all') return 'all';
    try {
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return null;
      const ids = parsed.filter((id) => typeof id === 'string' && id);
      return ids.length ? ids : null;
    } catch (e) {
      return null;
    }
  }

  function saveMyClubs(value) {
    writeCookie(MY_CLUBS_COOKIE, value === 'all' ? 'all' : JSON.stringify(value), SELECTION_COOKIE_MAX_AGE);
  }

  // Leaf ids (observed in the data) covered by a top-level program.
  function idsForParent(registry, parentId) {
    return [parentId, ...registry.descendants(parentId)].filter((id) => registry.observedIds.has(id));
  }

  // Top-level programs that actually have data, in display order.
  function visibleParents(registry) {
    return registry.parents.filter((p) => idsForParent(registry, p.id).length);
  }

  // Compute registry.scopeIds / registry.scoped from the "my clubs" cookie.
  function applyScope(registry) {
    const mine = readMyClubs();
    registry.myClubs = mine;
    registry.scoped = false;
    registry.scopeIds = registry.selectableIds.slice();
    if (Array.isArray(mine)) {
      const ids = mine.flatMap((pid) => (registry.byId.has(pid) ? idsForParent(registry, pid) : []));
      const unique = Array.from(new Set(ids));
      if (unique.length && unique.length < registry.selectableIds.length) {
        registry.scoped = true;
        registry.scopeIds = unique;
      }
    }
    return registry;
  }

  // True when results should not be filtered by club at all.
  function isUnfiltered(registry, selected) {
    if (registry.scoped) return false;
    return registry.selectableIds.every((id) => selected.has(id));
  }

  // First visit: no "my clubs" choice yet and no filter saved by an earlier
  // version of the site (those visitors already chose; don't interrupt them).
  function needsFirstVisitPicker() {
    if (!cookiesAvailable()) return false;
    return readMyClubs() === null && readSavedSelection() === null;
  }

  function escapeText(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // Open the club picker. Applies the choice to `selected` in place, saves it,
  // then calls onChange(). Closing without choosing on a first visit means
  // "show all" so the picker doesn't keep coming back.
  function openClubPicker(registry, directCounts, selected, onChange, opts) {
    if (typeof document === 'undefined' || !document.body) return;
    const options = opts || {};
    const existing = document.getElementById('clubPickerOverlay');
    if (existing) existing.remove();
    const counts = aggregateCounts(registry, directCounts || {});
    const parents = visibleParents(registry);
    const hasCounts = parents.some((p) => counts[p.id]);
    const chosen = new Set(Array.isArray(registry.myClubs) && registry.scoped ? registry.myClubs.filter((id) => registry.byId.has(id)) : []);

    const overlay = document.createElement('div');
    overlay.id = 'clubPickerOverlay';
    overlay.className = 'club-picker-overlay';
    overlay.innerHTML = `
      <div class="club-picker" role="dialog" aria-modal="true" aria-labelledby="clubPickerTitle" dir="rtl">
        <div class="club-picker-head">
          <div>
            <h2 id="clubPickerTitle">${options.firstVisit ? 'באילו מועדונים אתם חברים?' : 'המועדונים שלי'}</h2>
            <p class="club-picker-sub">נציג הטבות רק מהמועדונים שתבחרו. הבחירה נשמרת בדפדפן הזה ואפשר לשנות אותה בכל רגע.</p>
          </div>
          <button type="button" class="club-picker-close" aria-label="סגירה">✕</button>
        </div>
        <div class="club-picker-search-wrap">
          <input type="search" class="club-picker-search" placeholder="חיפוש מועדון…" aria-label="חיפוש מועדון" autocomplete="off">
          <button type="button" class="club-picker-link club-picker-clear">ניקוי בחירה</button>
        </div>
        <div class="club-picker-list" role="group" aria-label="רשימת מועדונים"></div>
        <p class="club-picker-empty" hidden>לא נמצאו מועדונים</p>
        <div class="club-picker-foot">
          <button type="button" class="club-picker-secondary club-picker-all">הצג את כל המועדונים</button>
          <button type="button" class="club-picker-primary club-picker-save"></button>
        </div>
      </div>`;

    const list = overlay.querySelector('.club-picker-list');
    const saveBtn = overlay.querySelector('.club-picker-save');
    const search = overlay.querySelector('.club-picker-search');
    const empty = overlay.querySelector('.club-picker-empty');

    function refreshSave() {
      saveBtn.disabled = chosen.size === 0;
      saveBtn.textContent = chosen.size ? `שמירה (${chosen.size})` : 'בחרו מועדון אחד לפחות';
    }

    parents.forEach((program) => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'club-picker-item';
      item.dataset.programId = program.id;
      item.dataset.search = `${program.display_name} ${program.short_name} ${(program.aliases || []).join(' ')}`.toLowerCase();
      item.style.setProperty('--program-color', program.color || fallbackColor(program.id));
      const count = counts[program.id] || 0;
      item.innerHTML = `<span class="club-picker-check" aria-hidden="true"></span><span class="club-picker-name">${escapeText(program.display_name)}</span>${hasCounts ? `<span class="club-picker-count">${count.toLocaleString()} הטבות</span>` : ''}`;
      const sync = () => {
        const on = chosen.has(program.id);
        item.classList.toggle('selected', on);
        item.setAttribute('aria-pressed', on ? 'true' : 'false');
      };
      sync();
      item.addEventListener('click', () => {
        if (chosen.has(program.id)) chosen.delete(program.id); else chosen.add(program.id);
        sync();
        refreshSave();
      });
      list.appendChild(item);
    });
    refreshSave();

    search.addEventListener('input', () => {
      const q = search.value.trim().toLowerCase();
      let shown = 0;
      list.querySelectorAll('.club-picker-item').forEach((item) => {
        const match = !q || item.dataset.search.includes(q);
        item.hidden = !match;
        if (match) shown += 1;
      });
      empty.hidden = shown > 0;
    });

    overlay.querySelector('.club-picker-clear').addEventListener('click', () => {
      chosen.clear();
      list.querySelectorAll('.club-picker-item').forEach((item) => { item.classList.remove('selected'); item.setAttribute('aria-pressed', 'false'); });
      refreshSave();
    });

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    function close() {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', onKey);
      overlay.remove();
    }

    function apply(value) {
      saveMyClubs(value);
      applyScope(registry);
      clearSavedSelection();
      selected.clear();
      registry.scopeIds.forEach((id) => selected.add(id));
      close();
      if (onChange) onChange();
    }

    function dismiss() {
      if (options.firstVisit || registry.myClubs === null) apply('all');
      else close();
    }

    function onKey(e) { if (e.key === 'Escape') dismiss(); }
    document.addEventListener('keydown', onKey);

    overlay.querySelector('.club-picker-close').addEventListener('click', dismiss);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) dismiss(); });
    overlay.querySelector('.club-picker-all').addEventListener('click', () => apply('all'));
    saveBtn.addEventListener('click', () => { if (chosen.size) apply(Array.from(chosen)); });

    document.body.appendChild(overlay);
    try { search.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
  }

  function maybeShowFirstVisitPicker(registry, directCounts, selected, onChange) {
    if (!needsFirstVisitPicker()) return false;
    openClubPicker(registry, directCounts, selected, onChange, { firstVisit: true });
    return true;
  }
  // -------------------------------------------------------------------------

  function renderFilters(container, registry, directCounts, selected, onChange, showCounts, opts) {
    if (!container) return;
    const options = opts || {};
    if (!registry.scopeIds) registry.scopeIds = registry.selectableIds.slice();
    const scope = registry.scopeIds;
    const inScope = new Set(scope);
    const counts = aggregateCounts(registry, directCounts);
    const allSelected = scope.every((id) => selected.has(id));
    container.innerHTML = '';
    const makeButton = (program, ids, child) => {
      const chosen = ids.filter((id) => selected.has(id)).length;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `filter-chip program-filter${child ? ' child-program-filter' : ''}`;
      button.dataset.programId = program.id;
      button.setAttribute('aria-pressed', chosen === ids.length ? 'true' : 'false');
      if (chosen === ids.length) button.classList.add('active');
      if (chosen > 0 && chosen < ids.length) button.classList.add('partial');
      button.style.setProperty('--program-color', program.color || fallbackColor(program.id));
      button.innerHTML = `<span class="chip-checkbox">${chosen === ids.length ? '✓' : chosen ? '−' : ''}</span><span class="club-logo-tag">${program.short_name}</span><span class="chip-name">${program.display_name}</span>${showCounts ? `<span class="chip-count">${(counts[program.id] || 0).toLocaleString()}</span>` : ''}`;
      button.addEventListener('click', () => {
        const shouldSelect = !ids.every((id) => selected.has(id));
        ids.forEach((id) => shouldSelect ? selected.add(id) : selected.delete(id));
        if (selected.size === 0) scope.forEach((id) => selected.add(id));
        persistSelection(registry, selected);
        onChange();
      });
      return button;
    };
    const allCount = registry.scoped
      ? scope.reduce((sum, id) => sum + (directCounts[id] || 0), 0)
      : (directCounts.ALL != null ? directCounts.ALL : Object.entries(directCounts).filter(([id]) => id !== 'ALL').reduce((sum, [,count]) => sum + count, 0));
    const all = document.createElement('button');
    all.type = 'button'; all.className = `filter-chip${allSelected ? ' active' : ''}`; all.dataset.programId = 'ALL';
    all.innerHTML = `<span class="chip-checkbox">${allSelected ? '✓' : ''}</span><span class="chip-name">${registry.scoped ? 'כל המועדונים שלי' : 'כל המועדונים'}</span>${showCounts ? `<span class="chip-count">${allCount.toLocaleString()}</span>` : ''}`;
    all.addEventListener('click', () => { selected.clear(); scope.forEach((id) => selected.add(id)); persistSelection(registry, selected); onChange(); });
    container.appendChild(all);
    registry.parents.forEach((parent) => {
      const descendants = registry.descendants(parent.id);
      const ids = [parent.id, ...descendants].filter((id) => registry.observedIds.has(id) && inScope.has(id));
      if (!ids.length) return;
      const group = document.createElement('div'); group.className = 'program-filter-group';
      group.appendChild(makeButton(parent, ids, false));
      // Child programs remain distinct in records/cards, but filters are parent-only.
      container.appendChild(group);
    });
    if (options.editable !== false && registry.selectableIds.length && typeof document !== 'undefined') {
      const edit = document.createElement('button');
      edit.type = 'button';
      edit.className = 'filter-chip club-picker-open';
      edit.dataset.programId = 'EDIT';
      edit.innerHTML = `<span class="chip-name">${registry.scoped ? '✎ עריכת המועדונים שלי' : '✎ בחירת המועדונים שלי'}</span>`;
      edit.addEventListener('click', () => openClubPicker(registry, directCounts, selected, onChange, { firstVisit: false }));
      container.appendChild(edit);
    }
  }

  global.ProgramRegistry = { CURATED, build, aggregateCounts, renderFilters, fallbackColor, initialSelection, persistSelection, clearSavedSelection, readSavedSelection, SELECTION_COOKIE, MY_CLUBS_COOKIE, applyScope, isUnfiltered, readMyClubs, saveMyClubs, needsFirstVisitPicker, openClubPicker, maybeShowFirstVisitPicker, visibleParents };
})(window);
