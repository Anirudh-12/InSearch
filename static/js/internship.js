/**
 * InSearch — Internship detail page JavaScript
 *
 * Reads internship ID from the URL path (/internship/{id}),
 * fetches full details from /api/internships/{id}, and renders the page.
 */

'use strict';

// ─── DOM refs ────────────────────────────────────────────────────────────────

const stateLoading   = document.getElementById('state-loading');
const stateError     = document.getElementById('state-error');
const detailContent  = document.getElementById('detail-content');
const errorMessage   = document.getElementById('error-message');

// ─── Init ────────────────────────────────────────────────────────────────────

(async function init() {
  const internshipId = getInternshipIdFromPath();
  if (!internshipId) {
    showError('Invalid internship URL.');
    return;
  }

  try {
    const res = await fetch(`/api/internships/${internshipId}`);
    if (res.status === 404) throw new Error('Internship not found');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderDetail(data);
  } catch (err) {
    showError(err.message || 'Could not load this internship.');
  }
})();

// ─── Path parsing ────────────────────────────────────────────────────────────

function getInternshipIdFromPath() {
  const match = window.location.pathname.match(/\/internship\/(\d+)/);
  return match ? match[1] : null;
}

// ─── Render ──────────────────────────────────────────────────────────────────

function renderDetail(job) {
  // Update page title and meta
  document.getElementById('page-title').textContent = `${job.title} at ${job.company_name} — InSearch`;
  document.getElementById('page-desc').setAttribute('content',
    `${job.title} at ${job.company_name}. Remote internship. ${(job.skills || []).join(', ')}`
  );

  // Title & company
  document.getElementById('detail-title').textContent = job.title;
  const companyEl = document.getElementById('detail-company');
  companyEl.textContent = job.company_name;

  // Badges
  const badgesEl = document.getElementById('detail-badges');
  badgesEl.innerHTML = [
    buildEligBadge(job.india_eligibility),
    buildCompBadge(job.compensation_type, job.salary_min, job.salary_max, job.salary_currency, job.salary_period),
    `<span class="skill-chip">🌐 Remote</span>`,
  ].filter(Boolean).join('');

  // Apply buttons
  const sourceUrl = job.source_url || '#';
  document.getElementById('detail-apply-btn').href = sourceUrl;
  document.getElementById('detail-apply-btn-bottom').href = sourceUrl;

  // Description
  const descEl = document.getElementById('detail-description');
  if (job.description) {
    descEl.textContent = job.description;
  } else {
    document.getElementById('desc-section').hidden = true;
  }

  // Skills
  const skillsEl = document.getElementById('detail-skills');
  if (job.skills && job.skills.length) {
    skillsEl.innerHTML = job.skills.map(s =>
      `<span class="skill-chip">${esc(s)}</span>`
    ).join('');
  } else {
    document.getElementById('skills-section').hidden = true;
  }

  // Detail grid fields
  setText('detail-company-url', job.company_url
    ? `<a href="${esc(job.company_url)}" target="_blank" rel="noopener noreferrer">${esc(job.company_url)}</a>`
    : '—', true);
  setText('detail-remote', job.remote ? 'Yes — Remote' : 'Not remote');
  setText('detail-location', job.location || 'Not specified');
  setText('detail-eligibility', formatEligibility(job.india_eligibility));
  setText('detail-internship-type', formatInternshipType(job.internship_type));
  setText('detail-employment-type', formatEmploymentType(job.employment_type));
  setText('detail-compensation', formatCompensation(
    job.compensation_type, job.salary_min, job.salary_max, job.salary_currency, job.salary_period
  ));
  setText('detail-experience', formatExperience(job.experience_min, job.experience_max));
  setText('detail-posted', job.posted_at ? formatDate(job.posted_at) : 'Unknown');
  setText('detail-deadline', job.deadline ? formatDate(job.deadline) : 'Not specified');
  setText('detail-source',
    `<a href="${esc(job.source_url)}" target="_blank" rel="noopener noreferrer">${esc(job.source)}</a>`,
    true
  );

  // Back link — preserve search state
  const backLink = document.getElementById('back-link');
  const ref = document.referrer;
  if (ref && new URL(ref).host === window.location.host) {
    backLink.href = ref;
  } else {
    backLink.href = '/';
  }

  // Show content
  showContent();
}

// ─── State ───────────────────────────────────────────────────────────────────

function showContent() {
  stateLoading.hidden = true;
  stateError.hidden   = true;
  detailContent.hidden = false;
}

function showError(msg) {
  stateLoading.hidden = true;
  stateError.hidden   = false;
  detailContent.hidden = true;
  errorMessage.textContent = msg;
}

// ─── Formatters ──────────────────────────────────────────────────────────────

function buildEligBadge(eligibility) {
  const map = {
    likely:  { cls: 'likely',  icon: '✓', label: 'Likely available from India' },
    unclear: { cls: 'unclear', icon: '?', label: 'India eligibility unclear' },
    unlikely:{ cls: 'unlikely',icon: '✕', label: 'Likely not available from India' },
  };
  const e = map[eligibility] || map.unclear;
  return `<span class="elig-badge ${e.cls}">${e.icon} ${e.label}</span>`;
}

function buildCompBadge(compType, salMin, salMax, currency, period) {
  if (compType === 'paid') {
    return `<span class="comp-badge paid">Paid</span>`;
  }
  if (compType === 'unpaid') return `<span class="comp-badge unpaid">Unpaid</span>`;
  return `<span class="comp-badge unknown">Compensation unknown</span>`;
}

function formatEligibility(e) {
  const map = {
    likely:  '✓ Likely available from India',
    unclear: '? India eligibility unclear',
    unlikely:'✕ Likely not available from India',
  };
  return map[e] || 'Unknown';
}

function formatInternshipType(t) {
  const map = { summer: 'Summer internship', winter: 'Winter internship', general: 'General internship', unknown: 'Not specified' };
  return map[t] || 'Not specified';
}

function formatEmploymentType(t) {
  const map = { full_time: 'Full-time', part_time: 'Part-time', contract: 'Contract', unknown: 'Not specified' };
  return map[t] || 'Not specified';
}

function formatCompensation(compType, salMin, salMax, currency, period) {
  if (compType === 'unpaid') return 'Unpaid';
  if (compType === 'unknown') return 'Not specified';
  if (salMin == null || !currency) return 'Paid (amount not specified)';

  const fmt = (n) => {
    if (currency === 'INR') return '₹' + Math.round(n).toLocaleString('en-IN');
    return '$' + Math.round(n).toLocaleString();
  };

  const range = salMin === salMax ? fmt(salMin) : `${fmt(salMin)} – ${fmt(salMax)}`;
  const per   = period || 'month';
  return `${currency} ${range} / ${per}`;
}

function formatExperience(min, max) {
  if (min == null && max == null) return 'Not specified';
  if (min === 0 && (max == null || max === 0)) return 'No experience required';
  if (min != null && max != null) return `${min}–${max} years`;
  if (min != null) return `${min}+ years`;
  return `Up to ${max} years`;
}

function formatDate(isoString) {
  if (!isoString) return 'Not specified';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });
}

function setText(id, value, html = false) {
  const el = document.getElementById(id);
  if (!el) return;
  if (html) el.innerHTML = value;
  else el.textContent = value;
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
