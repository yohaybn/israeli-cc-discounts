/**
 * Israeli Credit Card Discount Finder - Frontend App
 * Features:
 * - Instant typing search with Hebrew normalization & fuzzy match
 * - Multi-club filtering (MCC, HOT, HTzone, ALL)
 * - Multi-discount store option cards
 * - Direct navigation on click
 * - Responsive pagination / load more
 */

(function () {
    'use strict';

    // State
    const state = {
        allBusinesses: [],
        filteredBusinesses: [],
        searchQuery: '',
        selectedClub: 'ALL',
        sortBy: 'discount_desc',
        fuzzyThreshold: 0.72, // 0.50 to 1.00
        pageSize: 48,
        renderedCount: 0,
        isLoading: true,
        clubCounts: {
            ALL: 0,
            MCC: 0,
            HOT: 0,
            HTzone: 0,
        },
        totalDiscounts: 0,
    };

    // DOM Elements
    const elements = {
        searchInput: document.getElementById('searchInput'),
        clearSearchBtn: document.getElementById('clearSearchBtn'),
        quickTags: document.getElementById('quickTags'),
        filterChips: document.querySelectorAll('.filter-chip'),
        sortSelect: document.getElementById('sortSelect'),
        fuzzyRange: document.getElementById('fuzzyRange'),
        fuzzyValLabel: document.getElementById('fuzzyValLabel'),
        cardsGrid: document.getElementById('cardsGrid'),
        loadingSkeleton: document.getElementById('loadingSkeleton'),
        emptyState: document.getElementById('emptyState'),
        emptyQuery: document.getElementById('emptyQuery'),
        resetSearchBtn: document.getElementById('resetSearchBtn'),
        loadMoreContainer: document.getElementById('loadMoreContainer'),
        loadMoreBtn: document.getElementById('loadMoreBtn'),
        resultsCountText: document.getElementById('resultsCountText'),
        activeFilterBadge: document.getElementById('activeFilterBadge'),
        totalDealsCount: document.getElementById('totalDealsCount'),
        totalStoresCount: document.getElementById('totalStoresCount'),
        countAll: document.getElementById('countAll'),
        countMCC: document.getElementById('countMCC'),
        countHOT: document.getElementById('countHOT'),
        countHTzone: document.getElementById('countHTzone'),
    };

    // Hebrew text normalization for fast & accurate instant search
    function normalizeHebrew(text) {
        if (!text) return '';
        return text
            .toString()
            .toLowerCase()
            .replace(/[\u0591-\u05C7]/g, '') // Remove Hebrew Niqqud
            .replace(/["״'׳\-–—_.,/\\|]/g, ' ') // Remove quotes and punctuation
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
    }

    // Levenshtein / fuzzy similarity score (0 to 1)
    function similarity(s1, s2) {
        if (s1 === s2) return 1.0;
        if (!s1 || !s2) return 0.0;
        const l1 = s1.length;
        const l2 = s2.length;
        if (Math.abs(l1 - l2) > 3 && !s1.includes(s2) && !s2.includes(s1)) return 0.0;

        const track = Array(l2 + 1)
            .fill(null)
            .map(() => Array(l1 + 1).fill(null));

        for (let i = 0; i <= l1; i += 1) track[0][i] = i;
        for (let j = 0; j <= l2; j += 1) track[j][0] = j;

        for (let j = 1; j <= l2; j += 1) {
            for (let i = 1; i <= l1; i += 1) {
                const indicator = s1[i - 1] === s2[j - 1] ? 0 : 1;
                track[j][i] = Math.min(
                    track[j][i - 1] + 1, // deletion
                    track[j - 1][i] + 1, // insertion
                    track[j - 1][i - 1] + indicator // substitution
                );
            }
        }
        const dist = track[l2][l1];
        return 1 - dist / Math.max(l1, l2);
    }

    // Check if query matches a business name
    function matchesQuery(business, normalizedQuery) {
        if (!normalizedQuery) return true;

        const normalizedName = business._normalizedName;
        if (normalizedName.includes(normalizedQuery)) return true;

        const queryWords = normalizedQuery.split(' ');
        if (queryWords.length > 1 && queryWords.every((w) => normalizedName.includes(w))) {
            return true;
        }

        // If threshold is set to 100% (1.0), only exact substring match
        if (state.fuzzyThreshold >= 0.99) return false;

        // Fuzzy match on words
        if (normalizedQuery.length >= 2) {
            const nameWords = normalizedName.split(' ');
            for (const qw of queryWords) {
                if (qw.length < 2) continue;
                for (const nw of nameWords) {
                    if (similarity(qw, nw) >= state.fuzzyThreshold) return true;
                }
            }
        }

        return false;
    }

    // Process raw array of discount items into grouped business records
    function processRawDiscounts(dataList, metadata) {
        const names = new Map();
        const clubCounts = { ALL: 0, MCC: 0, HOT: 0, HTzone: 0 };

        dataList.forEach((d) => {
            if (!d.business_name || !d.club) return;
            const club = d.club;
            clubCounts.ALL += 1;
            clubCounts[club] = (clubCounts[club] || 0) + 1;

            const name = d.business_name.trim();
            if (!names.has(name)) {
                names.set(name, {
                    business_name: name,
                    discounts: [],
                    clubs: new Set(),
                    best_discount: null,
                    best_discount_value: 0,
                    _normalizedName: normalizeHebrew(name),
                });
            }

            const entry = names.get(name);
            entry.discounts.push({
                club: club,
                discount: d.discount || '',
                discount_url: d.discount_url || '',
            });
            entry.clubs.add(club);
        });

        const businesses = [];
        names.forEach((entry) => {
            const percents = [];
            entry.discounts.forEach((disc) => {
                const match = disc.discount.match(/(\d+(?:\.\d+)?)%/);
                if (match) {
                    percents.push(parseFloat(match[1]));
                } else {
                    const matchNum = disc.discount.match(/\d+(?:\.\d+)?/);
                    if (matchNum) percents.push(parseFloat(matchNum[0]));
                }
            });

            if (percents.length > 0) {
                const maxVal = Math.max(...percents);
                entry.best_discount_value = maxVal;
                entry.best_discount = `${maxVal}%`;
            } else {
                entry.best_discount_value = 0;
                entry.best_discount = entry.discounts[0]?.discount || null;
            }

            entry.clubs = Array.from(entry.clubs).sort();
            businesses.push(entry);
        });

        return { businesses, clubCounts, total: clubCounts.ALL };
    }

    // Fetch initial dataset from local API or raw GitHub JSON (GitHub Pages mode)
    async function loadData() {
        const DATA_SOURCES = [
            // 1. If running under GitHub Pages / static hosting with local data folder
            './data/all_combined_discounts.json',
            'data/all_combined_discounts.json',
            // 2. If running under local API server
            '/businesses',
            // 3. Raw GitHub fallback for 100% serverless GitHub Pages
            'https://raw.githubusercontent.com/yohaybn/israeli-cc-discounts/refs/heads/main/data/all_combined_discounts.json',
        ];

        let loaded = false;

        for (const source of DATA_SOURCES) {
            try {
                const res = await fetch(source);
                if (!res.ok) continue;
                const data = await res.json();

                // If response is from /businesses API endpoint
                if (data && data.results && Array.isArray(data.results)) {
                    state.allBusinesses = data.results.map((b) => ({
                        ...b,
                        _normalizedName: normalizeHebrew(b.business_name),
                    }));
                    // Fetch clubs info if from API
                    try {
                        const clubsRes = await fetch('/clubs').then((r) => r.json());
                        state.totalDiscounts = clubsRes.total || 0;
                        const clubCountsMap = {};
                        (clubsRes.clubs || []).forEach((c) => {
                            clubCountsMap[c.club] = c.count;
                        });
                        state.clubCounts = {
                            ALL: state.totalDiscounts,
                            MCC: clubCountsMap['MCC'] || 0,
                            HOT: clubCountsMap['HOT'] || 0,
                            HTzone: clubCountsMap['HTzone'] || 0,
                        };
                    } catch (e) {
                        // ignore API clubs error
                    }
                } else if (Array.isArray(data)) {
                    // Raw discounts array from JSON file
                    const { businesses, clubCounts, total } = processRawDiscounts(data);
                    state.allBusinesses = businesses;
                    state.clubCounts = clubCounts;
                    state.totalDiscounts = total;
                }

                loaded = true;
                break;
            } catch (err) {
                // Try next source
            }
        }

        if (!loaded) {
            elements.resultsCountText.textContent = 'שגיאה בטעינת הנתונים. נסו לרענן את העמוד.';
            elements.loadingSkeleton.classList.add('hidden');
            return;
        }

        // Update stats counters
        elements.totalDealsCount.textContent = state.totalDiscounts.toLocaleString();
        elements.totalStoresCount.textContent = state.allBusinesses.length.toLocaleString();
        elements.countAll.textContent = state.clubCounts.ALL.toLocaleString();
        elements.countMCC.textContent = state.clubCounts.MCC.toLocaleString();
        elements.countHOT.textContent = state.clubCounts.HOT.toLocaleString();
        elements.countHTzone.textContent = state.clubCounts.HTzone.toLocaleString();

        state.isLoading = false;
        elements.loadingSkeleton.classList.add('hidden');
        elements.cardsGrid.classList.remove('hidden');

        applyFiltersAndSort();
    }

    // Filter and sort businesses based on current state
    function applyFiltersAndSort() {
        const query = normalizeHebrew(state.searchQuery);
        const club = state.selectedClub;

        let results = state.allBusinesses.filter((biz) => {
            // Club filter
            if (club !== 'ALL' && !biz.clubs.includes(club)) {
                return false;
            }
            // Search query filter
            return matchesQuery(biz, query);
        });

        // Apply sorting
        if (state.sortBy === 'discount_desc') {
            results.sort((a, b) => (b.best_discount_value || 0) - (a.best_discount_value || 0));
        } else if (state.sortBy === 'name_asc') {
            results.sort((a, b) => a.business_name.localeCompare(b.business_name, 'he'));
        } else if (state.sortBy === 'deals_desc') {
            results.sort((a, b) => (b.discounts ? b.discounts.length : 0) - (a.discounts ? a.discounts.length : 0));
        }

        state.filteredBusinesses = results;
        state.renderedCount = 0;
        elements.cardsGrid.innerHTML = '';

        updateResultsMeta();
        renderNextBatch();
    }

    // Render cards batch
    function renderNextBatch() {
        const total = state.filteredBusinesses.length;
        if (total === 0) {
            elements.cardsGrid.classList.add('hidden');
            elements.loadMoreContainer.classList.add('hidden');
            elements.emptyState.classList.remove('hidden');
            elements.emptyQuery.textContent = state.searchQuery || (state.selectedClub !== 'ALL' ? state.selectedClub : '');
            return;
        }

        elements.emptyState.classList.add('hidden');
        elements.cardsGrid.classList.remove('hidden');

        const nextLimit = Math.min(state.renderedCount + state.pageSize, total);
        const batch = state.filteredBusinesses.slice(state.renderedCount, nextLimit);

        const fragment = document.createDocumentFragment();
        batch.forEach((biz) => {
            fragment.appendChild(createBusinessCard(biz));
        });

        elements.cardsGrid.appendChild(fragment);
        state.renderedCount = nextLimit;

        if (state.renderedCount < total) {
            elements.loadMoreContainer.classList.remove('hidden');
        } else {
            elements.loadMoreContainer.classList.add('hidden');
        }
    }

    // Create DOM card element for a business
    function createBusinessCard(biz) {
        const card = document.createElement('div');
        card.className = 'business-card';

        const hasMultiple = biz.discounts && biz.discounts.length > 1;
        const discountCount = biz.discounts ? biz.discounts.length : 0;

        // Card Header
        const header = document.createElement('div');
        header.className = 'card-header';

        const titleArea = document.createElement('div');
        titleArea.className = 'card-title-area';

        const title = document.createElement('h3');
        title.className = 'business-name';
        title.textContent = biz.business_name;
        titleArea.appendChild(title);

        if (hasMultiple) {
            const multiTag = document.createElement('span');
            multiTag.className = 'multi-badge';
            multiTag.innerHTML = `⚡ ${discountCount} הטבות`;
            titleArea.appendChild(multiTag);
        }

        header.appendChild(titleArea);

        // Best discount pill
        if (biz.best_discount) {
            const bestPill = document.createElement('div');
            bestPill.className = 'best-discount-pill';
            bestPill.innerHTML = `
                <span class="best-disc-val">${escapeHtml(biz.best_discount)}</span>
                <span class="best-disc-lbl">הנחה מרבית</span>
            `;
            header.appendChild(bestPill);
        }

        card.appendChild(header);

        // Discounts List
        const list = document.createElement('div');
        list.className = 'discounts-list';

        // Filter discounts if a specific club is selected
        let discountsToShow = biz.discounts || [];
        if (state.selectedClub !== 'ALL') {
            // Put selected club discounts first
            discountsToShow = [...biz.discounts].sort((a, b) => {
                if (a.club === state.selectedClub && b.club !== state.selectedClub) return -1;
                if (b.club === state.selectedClub && a.club !== state.selectedClub) return 1;
                return 0;
            });
        }

        discountsToShow.forEach((disc) => {
            const clubLower = disc.club.toLowerCase();
            const optionLink = document.createElement('a');
            optionLink.className = `discount-option-item club-${clubLower}`;
            optionLink.href = disc.discount_url || '#';
            optionLink.target = '_blank';
            optionLink.rel = 'noopener noreferrer';
            optionLink.title = `מעבר להטבה במועדון ${disc.club}`;

            const clubFullName = getClubFullName(disc.club);

            optionLink.innerHTML = `
                <div class="option-left-content">
                    <span class="option-club-badge ${clubLower}">${escapeHtml(disc.club)}</span>
                    <div class="option-text-wrap">
                        <span class="option-discount-title">${escapeHtml(disc.discount)}</span>
                        <span class="option-club-name">${escapeHtml(clubFullName)}</span>
                    </div>
                </div>
                <span class="option-action-btn">
                    <span>להטבה</span>
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="7" y1="17" x2="17" y2="7"></line>
                        <polyline points="7 7 17 7 17 17"></polyline>
                    </svg>
                </span>
            `;

            list.appendChild(optionLink);
        });

        card.appendChild(list);
        return card;
    }

    function getClubFullName(club) {
        switch (club) {
            case 'MCC':
                return 'מועדון מורות וגננות';
            case 'HOT':
                return 'מועדון הוט';
            case 'HTzone':
                return 'הייטק זון';
            default:
                return club;
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Update status meta line
    function updateResultsMeta() {
        const total = state.filteredBusinesses.length;
        let countDiscounts = 0;
        state.filteredBusinesses.forEach((b) => {
            countDiscounts += b.discounts ? b.discounts.length : 0;
        });

        if (state.searchQuery || state.selectedClub !== 'ALL') {
            elements.resultsCountText.innerHTML = `נמצאו <strong>${total.toLocaleString()}</strong> עסקים עם <strong>${countDiscounts.toLocaleString()}</strong> הטבות מתאימות`;
        } else {
            elements.resultsCountText.innerHTML = `מציג <strong>${total.toLocaleString()}</strong> עסקים ורשתות (סה״כ ${countDiscounts.toLocaleString()} הטבות)`;
        }

        if (state.selectedClub !== 'ALL') {
            elements.activeFilterBadge.textContent = `מסונן לפי: ${getClubFullName(state.selectedClub)}`;
            elements.activeFilterBadge.classList.remove('hidden');
        } else {
            elements.activeFilterBadge.classList.add('hidden');
        }
    }

    // Debounce utility
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Event Listeners
    function setupEvents() {
        // Instant typing search
        const debouncedSearch = debounce((val) => {
            state.searchQuery = val;
            applyFiltersAndSort();
        }, 120);

        elements.searchInput.addEventListener('input', (e) => {
            const val = e.target.value;
            if (val.length > 0) {
                elements.clearSearchBtn.classList.remove('hidden');
            } else {
                elements.clearSearchBtn.classList.add('hidden');
            }
            debouncedSearch(val);
        });

        // Clear search button
        elements.clearSearchBtn.addEventListener('click', () => {
            elements.searchInput.value = '';
            elements.clearSearchBtn.classList.add('hidden');
            state.searchQuery = '';
            elements.searchInput.focus();
            applyFiltersAndSort();
        });

        // Quick tags
        if (elements.quickTags) {
            elements.quickTags.addEventListener('click', (e) => {
                const tag = e.target.closest('.quick-tag');
                if (!tag) return;
                const query = tag.getAttribute('data-query');
                elements.searchInput.value = query;
                elements.clearSearchBtn.classList.remove('hidden');
                state.searchQuery = query;
                elements.searchInput.focus();
                applyFiltersAndSort();
            });
        }

        // Club filter chips
        elements.filterChips.forEach((chip) => {
            chip.addEventListener('click', () => {
                elements.filterChips.forEach((c) => {
                    c.classList.remove('active');
                    c.setAttribute('aria-selected', 'false');
                });
                chip.classList.add('active');
                chip.setAttribute('aria-selected', 'true');
                state.selectedClub = chip.getAttribute('data-club');
                applyFiltersAndSort();
            });
        });

        // Sort dropdown
        elements.sortSelect.addEventListener('change', (e) => {
            state.sortBy = e.target.value;
            applyFiltersAndSort();
        });

        // Fuzzy search sensitivity slider
        if (elements.fuzzyRange) {
            elements.fuzzyRange.addEventListener('input', (e) => {
                const val = parseInt(e.target.value, 10);
                state.fuzzyThreshold = val / 100;

                let labelText = `${val}%`;
                if (val >= 95) {
                    labelText += ' (מדויק)';
                } else if (val >= 78) {
                    labelText += ' (קפדני)';
                } else if (val >= 68) {
                    labelText += ' (מאוזן)';
                } else {
                    labelText += ' (גמיש מאוד)';
                }
                elements.fuzzyValLabel.textContent = labelText;
                applyFiltersAndSort();
            });
        }

        // Load more button
        elements.loadMoreBtn.addEventListener('click', () => {
            renderNextBatch();
        });

        // Reset search button from empty state
        elements.resetSearchBtn.addEventListener('click', () => {
            elements.searchInput.value = '';
            elements.clearSearchBtn.classList.add('hidden');
            state.searchQuery = '';
            state.selectedClub = 'ALL';
            elements.filterChips.forEach((c) => {
                const isAll = c.getAttribute('data-club') === 'ALL';
                c.classList.toggle('active', isAll);
                c.setAttribute('aria-selected', isAll ? 'true' : 'false');
            });
            applyFiltersAndSort();
            elements.searchInput.focus();
        });

        // Keyboard Shortcuts: '/' to focus search, 'Escape' to clear
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement !== elements.searchInput) {
                e.preventDefault();
                elements.searchInput.focus();
                elements.searchInput.select();
            } else if (e.key === 'Escape' && document.activeElement === elements.searchInput) {
                if (elements.searchInput.value) {
                    elements.searchInput.value = '';
                    elements.clearSearchBtn.classList.add('hidden');
                    state.searchQuery = '';
                    applyFiltersAndSort();
                } else {
                    elements.searchInput.blur();
                }
            }
        });
    }

    // Initialize
    setupEvents();
    loadData();
})();
