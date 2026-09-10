/**
 * InSearch — Main search page JavaScript
 *
 * Responsibilities:
 *  - Read/write URL query params to synchronize state
 *  - Fetch internships from /api/internships
 *  - Render result cards
 *  - Handle filter sidebar interactions
 *  - Handle pagination
 *  - Handle loading / empty / error states
 *  - Popular search chips
 */

'use strict';

// ─── Constants ──────────────────────────────────────────────────────────────

const API_BASE = '/api/internships';
const SKILLS_FILTER_COUNT = 20; // How many skills to show in sidebar

// ─── State ──────────────────────────────────────────────────────────────────

let currentPage = 1;
let currentTotal = 0;
let currentPages = 1;
let isLoading = false;

// ─── DOM refs ────────────────────────────────────────────────────────────────

const searchInput    = document.getElementById('search-input');
const searchBtn      = document.getElementById('search-btn');
const searchForm     = document.getElementById('search-form');
const internshipList = document.getElementById('internship-list');
const resultsCount   = document.getElementById('results-count');
const paginationEl   = document.getElementById('pagination');
const stateLoading   = document.getElementById('state-loading');
const stateEmpty     = document.getElementById('state-empty');
const stateError     = document.getElementById('state-error');
const errorMessage   = document.getElementById('error-message');
const sortSelect     = document.getElementById('sort-select');
const filterToggle   = document.getElementById('filter-toggle-btn');
const filtersSidebar = document.getElementById('filters-sidebar');
const filtersReset   = document.getElementById('filters-reset-btn');
const skillsFilter   = document.getElementById('skills-filter');

// ─── Init ────────────────────────────────────────────────────────────────────

(async function init() {
  await loadFilterSkills();
  syncFromURL();
  await fetchAndRender();
  bindEvents();
})();

// ─── URL State ───────────────────────────────────────────────────────────────

function getParams() {
  const p = new URLSearchParams(window.location.search);
  return {
    q:                p.get('q') || '',
    skills:           p.get('skills') || '',
    india_eligibility:p.get('india_eligibility') || '',
    employment_type:  p.get('employment_type') || '',
    internship_type:  p.get('internship_type') || '',
    compensation_type:p.get('compensation_type') || '',
    page:             parseInt(p.get('page') || '1', 10),
    sort:             p.get('sort') || '',
  };
}

function buildParams(overrides = {}) {
  const base = getParams();
  return { ...base, ...overrides };
}

function syncFromURL() {
  const p = getParams();
  searchInput.value = p.q;
  if (p.sort) sortSelect.value = p.sort;

  setCheckboxValues('eligibility-filter', p.india_eligibility);
  setCheckboxValues('employment-type-filter', p.employment_type);
  setCheckboxValues('internship-type-filter', p.internship_type);
  setCheckboxValues('compensation-filter', p.compensation_type);
  setCheckboxValues('skills-filter', p.skills);

  currentPage = p.page || 1;
}

function pushURL(params) {
  const p = new URLSearchParams();
  if (params.q)                 p.set('q', params.q);
  if (params.skills)            p.set('skills', params.skills);
  if (params.india_eligibility) p.set('india_eligibility', params.india_eligibility);
  if (params.employment_type)   p.set('employment_type', params.employment_type);
  if (params.internship_type)   p.set('internship_type', params.internship_type);
  if (params.compensation_type) p.set('compensation_type', params.compensation_type);
  if (params.page && params.page > 1) p.set('page', params.page);
  if (params.sort && params.sort !== 'relevance') p.set('sort', params.sort);
  const qs = p.toString();
  const url = qs ? `?${qs}` : window.location.pathname;
  history.pushState({}, '', url);
}

// ─── Filter helpers ──────────────────────────────────────────────────────────

function getCheckboxValues(groupId) {
  const group = document.getElementById(groupId);
  if (!group) return '';
  const checked = Array.from(group.querySelectorAll('input[type=checkbox]:checked'));
  return checked.map(c => c.value).join(',');
}

function setCheckboxValues(groupId, csv) {
  const group = document.getElementById(groupId);
  if (!group) return;
  const values = csv ? csv.split(',').map(v => v.trim()) : [];
  group.querySelectorAll('input[type=checkbox]').forEach(cb => {
    cb.checked = values.includes(cb.value);
  });
}

function collectFilters() {
  return {
    q:                 searchInput.value.trim(),
    skills:            getCheckboxValues('skills-filter'),
    india_eligibility: getCheckboxValues('eligibility-filter'),
    employment_type:   getCheckboxValues('employment-type-filter'),
    internship_type:   getCheckboxValues('internship-type-filter'),
    compensation_type: getCheckboxValues('compensation-filter'),
    sort:              sortSelect.value,
    page:              currentPage,
  };
}

// ─── Fetch ───────────────────────────────────────────────────────────────────

async function fetchAndRender() {
  if (isLoading) return;
  isLoading = true;
  showState('loading');

  const filters = collectFilters();
  pushURL(filters);

  const url = buildAPIUrl(filters);

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    currentTotal = data.total;
    currentPages = data.pages;
    currentPage  = data.page;

    if (data.results.length === 0) {
      showState('empty');
      resultsCount.textContent = 'No internships found';
    } else {
      showState('results');
      renderResults(data.results, data.total, data.query);
      renderPagination(data.page, data.pages);
    }
  } catch (err) {
    console.error(err);
    showState('error');
    errorMessage.textContent = `Could not load internships: ${err.message}`;
  } finally {
    isLoading = false;
  }
}

function buildAPIUrl(filters) {
  const p = new URLSearchParams();
  if (filters.q)                 p.set('q', filters.q);
  if (filters.skills)            p.set('skills', filters.skills);
  if (filters.india_eligibility) p.set('india_eligibility', filters.india_eligibility);
  if (filters.employment_type)   p.set('employment_type', filters.employment_type);
  if (filters.internship_type)   p.set('internship_type', filters.internship_type);
  if (filters.compensation_type) p.set('compensation_type', filters.compensation_type);
  if (filters.sort)              p.set('sort', filters.sort);
  p.set('page', String(filters.page || 1));
  p.set('limit', '20');
  return `${API_BASE}?${p.toString()}`;
}

// ─── Render ──────────────────────────────────────────────────────────────────

function renderResults(results, total, query) {
  const q = query ? ` for "${query}"` : '';
  resultsCount.innerHTML = `<strong>${total.toLocaleString()}</strong> internship${total !== 1 ? 's' : ''}${q}`;

  internshipList.innerHTML = results.map(renderCard).join('');
}

function renderCard(job) {
  const eligBadge = buildEligBadge(job.india_eligibility);
  const skills    = (job.skills || []).slice(0, 5).map(s =>
    `<span class="skill-chip">${esc(s)}</span>`
  ).join('');
  const compBadge = buildCompBadge(job.compensation_type, job.salary_min, job.salary_max, job.salary_currency);
  const typeLabel = formatInternshipType(job.internship_type);
  const posted    = job.posted_at ? timeAgo(job.posted_at) : null;
  const sourceUrl = job.source_url || '#';

  return `
  <li>
    <article class="internship-card">
      <div class="card-header">
        <div class="card-title-block">
          <h2 class="card-title">
            <a href="/internship/${job.id}" aria-label="View details for ${esc(job.title)} at ${esc(job.company_name)}">
              ${esc(job.title)}
            </a>
          </h2>
          <p class="card-company">
            ${job.company_url
              ? `<a href="${esc(job.company_url)}" target="_blank" rel="noopener noreferrer">${esc(job.company_name)}</a>`
              : esc(job.company_name)
            }
          </p>
        </div>
        ${eligBadge}
      </div>

      <div class="card-meta">
        <span class="meta-tag">🌐 Remote</span>
        ${job.location ? `<span class="meta-dot">·</span><span class="meta-tag">${esc(job.location)}</span>` : ''}
        ${typeLabel ? `<span class="meta-dot">·</span><span class="meta-tag">${typeLabel}</span>` : ''}
        ${compBadge ? `<span class="meta-dot">·</span>${compBadge}` : ''}
      </div>

      ${skills ? `<div class="skills-row">${skills}</div>` : ''}

      <div class="card-footer">
        <div class="card-footer-meta">
          ${posted ? `<span class="card-posted">Posted ${posted}</span>` : ''}
          <span class="card-source">Source: ${esc(job.source)}</span>
        </div>
        <a
          href="${esc(sourceUrl)}"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-view"
          aria-label="View internship at ${esc(job.company_name)} on ${esc(job.source)}"
        >View Internship ↗</a>
      </div>
    </article>
  </li>`;
}

function renderPagination(page, pages) {
  if (pages <= 1) { paginationEl.innerHTML = ''; return; }

  const buttons = [];

  // Prev
  buttons.push(`
    <button class="page-btn" id="page-prev" ${page <= 1 ? 'disabled' : ''} aria-label="Previous page">
      ← Prev
    </button>
  `);

  // Page numbers
  const range = getPageRange(page, pages);
  range.forEach(p => {
    if (p === '…') {
      buttons.push(`<span class="page-btn" style="cursor:default;">…</span>`);
    } else {
      buttons.push(`
        <button class="page-btn ${p === page ? 'active' : ''}" data-page="${p}" aria-label="Page ${p}" aria-current="${p === page ? 'page' : 'false'}">
          ${p}
        </button>
      `);
    }
  });

  // Next
  buttons.push(`
    <button class="page-btn" id="page-next" ${page >= pages ? 'disabled' : ''} aria-label="Next page">
      Next →
    </button>
  `);

  paginationEl.innerHTML = buttons.join('');

  // Bind events
  paginationEl.querySelector('#page-prev')?.addEventListener('click', () => {
    if (currentPage > 1) { currentPage--; fetchAndRender(); }
  });
  paginationEl.querySelector('#page-next')?.addEventListener('click', () => {
    if (currentPage < currentPages) { currentPage++; fetchAndRender(); }
  });
  paginationEl.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = parseInt(btn.dataset.page, 10);
      if (p !== currentPage) { currentPage = p; fetchAndRender(); }
    });
  });
}

function getPageRange(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages = [];
  if (current <= 4) {
    pages.push(1, 2, 3, 4, 5, '…', total);
  } else if (current >= total - 3) {
    pages.push(1, '…', total - 4, total - 3, total - 2, total - 1, total);
  } else {
    pages.push(1, '…', current - 1, current, current + 1, '…', total);
  }
  return pages;
}

// ─── State management ────────────────────────────────────────────────────────

function showState(state) {
  stateLoading.hidden = state !== 'loading';
  stateEmpty.hidden   = state !== 'empty';
  stateError.hidden   = state !== 'error';
  internshipList.hidden = state !== 'results';
  paginationEl.hidden   = state !== 'results';
  if (state !== 'results') resultsCount.textContent = '';
}

// ─── Events ──────────────────────────────────────────────────────────────────

function bindEvents() {
  // Search form submit
  searchForm.addEventListener('submit', onSearch);
  searchBtn.addEventListener('click', onSearch);

  // Popular chips
  document.querySelectorAll('.popular-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      searchInput.value = chip.dataset.query;
      currentPage = 1;
      fetchAndRender();
    });
  });

  // Filter checkboxes — any change triggers search
  document.querySelectorAll('.filters-sidebar input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', () => { currentPage = 1; fetchAndRender(); });
  });

  // Sort
  sortSelect.addEventListener('change', () => { currentPage = 1; fetchAndRender(); });

  // Reset filters
  filtersReset.addEventListener('click', () => {
    document.querySelectorAll('.filters-sidebar input[type=checkbox]').forEach(cb => { cb.checked = false; });
    sortSelect.value = 'relevance';
    currentPage = 1;
    fetchAndRender();
  });

  // Mobile filter toggle
  filterToggle?.addEventListener('click', () => {
    const open = filtersSidebar.classList.toggle('open');
    filterToggle.setAttribute('aria-expanded', String(open));
    filterToggle.textContent = open ? '✕ Close Filters' : '⚙ Filters';
  });

  // Back/forward navigation
  window.addEventListener('popstate', () => {
    syncFromURL();
    fetchAndRender();
  });
}

function onSearch() {
  currentPage = 1;
  fetchAndRender();
}

// ─── Load filter skill checkboxes from API ───────────────────────────────────

async function loadFilterSkills() {
  try {
    const res = await fetch('/api/filters');
    if (!res.ok) return;
    const data = await res.json();
    const skills = (data.skills || []).slice(0, SKILLS_FILTER_COUNT);
    const currentSelected = getCheckboxValues('skills-filter').split(',').filter(Boolean);

    skillsFilter.innerHTML = skills.map(skill => {
      const id = `skill-${skill.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
      const checked = currentSelected.includes(skill) ? 'checked' : '';
      return `
        <li class="filter-checkbox-item">
          <input type="checkbox" id="${id}" value="${esc(skill)}" ${checked} />
          <label for="${id}">${esc(skill)}</label>
        </li>`;
    }).join('');

    // Bind events for newly created checkboxes
    skillsFilter.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', () => { currentPage = 1; fetchAndRender(); });
    });
  } catch (e) {
    console.warn('Could not load filter options:', e);
  }
}

// ─── Formatting helpers ──────────────────────────────────────────────────────

function buildEligBadge(eligibility) {
  const map = {
    likely:  { cls: 'likely',  icon: '✓', label: 'Likely from India' },
    unclear: { cls: 'unclear', icon: '?', label: 'India eligibility unclear' },
    unlikely:{ cls: 'unlikely',icon: '✕', label: 'Likely not from India' },
  };
  const e = map[eligibility] || map.unclear;
  return `<span class="elig-badge ${e.cls}" title="${e.label}" aria-label="${e.label}">${e.icon} ${e.label}</span>`;
}

function buildCompBadge(compType, salMin, salMax, currency) {
  if (compType === 'paid') {
    let label = 'Paid';
    if (salMin != null && currency) {
      const fmt = formatSalary(salMin, salMax, currency);
      label = `Paid · ${fmt}`;
    }
    return `<span class="comp-badge paid">${label}</span>`;
  }
  if (compType === 'unpaid') return `<span class="comp-badge unpaid">Unpaid</span>`;
  return '';
}

function formatSalary(min, max, currency) {
  if (currency === 'INR') {
    const fmt = n => '₹' + Math.round(n / 1000) + 'k';
    if (min === max) return fmt(min) + '/mo';
    return `${fmt(min)}–${fmt(max)}/mo`;
  }
  const fmt = n => '$' + Math.round(n).toLocaleString();
  if (min === max) return fmt(min) + '/mo';
  return `${fmt(min)}–${fmt(max)}/mo`;
}

function formatInternshipType(t) {
  const map = { summer: 'Summer', winter: 'Winter', general: 'General', unknown: '' };
  return map[t] || '';
}

function timeAgo(isoString) {
  const date = new Date(isoString);
  const now  = new Date();
  const diffMs = now - date;
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (days === 0) return 'today';
  if (days === 1) return '1 day ago';
  if (days < 7)  return `${days} days ago`;
  if (days < 14) return '1 week ago';
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 60) return '1 month ago';
  return `${Math.floor(days / 30)} months ago`;
}

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
