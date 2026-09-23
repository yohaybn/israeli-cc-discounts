(function () {
    'use strict';

    const element = document.getElementById('dataFreshness');
    if (!element) return;

    function formatTimestamp(value) {
        const timestamp = new Date(value);
        if (Number.isNaN(timestamp.getTime())) return null;
        return new Intl.DateTimeFormat('he-IL', {
            dateStyle: 'short',
            timeStyle: 'short',
        }).format(timestamp);
    }

    function staleSummary(data) {
        const status = data && data.source_status;
        if (!status) return '';
        const stale = Object.values(status).filter((s) => s && s.status && s.status !== 'ok');
        if (!stale.length) return '';
        const items = stale.map((s) => {
            const when = s.last_successful_scrape ? formatTimestamp(s.last_successful_scrape) : null;
            return `${s.club}: ${when ? `נתונים מ-${when}` : 'אין נתונים עדכניים'}`;
        });
        const shown = items.slice(0, 5).join('; ');
        const more = items.length > 5 ? `; ועוד ${items.length - 5}` : '';
        return ` · ${stale.length} מקורות לא התעדכנו בריצה האחרונה (${shown}${more})`;
    }

    function renderFreshness(value, data) {
        const timestamp = new Date(value);
        const formatted = formatTimestamp(value);
        if (!formatted) throw new Error('Invalid freshness timestamp');

        const ageHours = Math.max(0, (Date.now() - timestamp.getTime()) / 3600000);
        element.classList.remove('is-stale', 'is-outdated');
        if (ageHours >= 168) {
            element.classList.add('is-outdated');
            element.textContent = `הנתונים לא עודכנו יותר משבוע · עדכון אחרון: ${formatted}`;
        } else if (ageHours >= 48) {
            element.classList.add('is-stale');
            element.textContent = `ייתכן שהנתונים אינם עדכניים · עדכון אחרון: ${formatted}`;
        } else {
            element.textContent = `עדכון נתונים אחרון: ${formatted}`;
        }
        const suffix = staleSummary(data);
        if (suffix) {
            element.textContent += suffix;
            element.classList.add('has-stale-sources');
        }
    }

    async function loadFreshness() {
        const sources = ['data/data_freshness.json', '/api/info'];
        for (const source of sources) {
            try {
                const response = await fetch(source);
                if (!response.ok) continue;
                const data = await response.json();
                const value = data.published_at || data.metadata?.all_combined?.last_updated;
                if (value) {
                    renderFreshness(value, data);
                    return;
                }
            } catch (error) {
                // Try the next source.
            }
        }
        element.textContent = 'מועד עדכון הנתונים אינו זמין כרגע';
        element.classList.add('is-stale');
    }

    loadFreshness();
}());
