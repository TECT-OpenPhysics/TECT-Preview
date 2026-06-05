/* TECT live site — static shell; ALL content fetched at view time from the
 * repository's main branch (raw.githubusercontent.com). Zero generated
 * content files: the repo itself is the only source of truth
 * (governance/publication-tiers.md, live-fetch architecture).
 *
 * __version__ 1.0.1 · first issued 2026-06-05 · issued 2026-06-05
 * 1.0.1: exclude claims/_TEMPLATE from the live ledger (same defect as build_wiki 1.0.1)
 */
"use strict";

/* ---- repository autodetection (owner.github.io/<repo>/) ------------------ */
const REPO_FALLBACK = "";            // "owner/repo" — used off-Pages (e.g. local preview)
function repoSlug() {
  const q = new URLSearchParams(location.search).get("repo");
  if (q) return q;
  const host = location.hostname;        // owner.github.io
  if (host.endsWith(".github.io")) {
    const owner = host.split(".")[0];
    const seg = location.pathname.split("/").filter(Boolean)[0];
    if (seg) return owner + "/" + seg;
  }
  return REPO_FALLBACK;
}
const SLUG = repoSlug();
const RAW  = s => `https://raw.githubusercontent.com/${SLUG}/main/${s}`;
const BLOB = s => `https://github.com/${SLUG}/blob/main/${s}`;

const app = document.getElementById("app");
const cache = {};
async function fetchText(path) {
  if (cache[path] !== undefined) return cache[path];
  const r = await fetch(RAW(path));
  if (!r.ok) throw new Error(`fetch ${path}: ${r.status}`);
  return (cache[path] = await r.text());
}
const fetchJSON = async p => JSON.parse(await fetchText(p));
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const tierClass = (t, life) => life === "REFUTED" ? "refuted" : (t || "").toLowerCase();
function typeset() { if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([app]); }
function md(text) { return marked.parse(text, {mangle: false, headerIds: false}); }

/* ---- data loading --------------------------------------------------------- */
async function loadClaims() {
  const cat = await fetchJSON("verification/catalog.json");
  const paths = cat.entries.filter(e => e.kind === "claim-card" && e.path.endsWith("status.json")
    && !e.path.includes("/_")).map(e => e.path);
  const cards = await Promise.all(paths.map(fetchJSON));
  cards.sort((a, b) => a.id.localeCompare(b.id));
  return {cards, catalog: cat};
}

/* ---- views ----------------------------------------------------------------- */
async function viewOverview() {
  const {cards} = await loadClaims();
  const tiers = {};
  cards.forEach(c => { tiers[c.tier] = (tiers[c.tier] || 0) + 1; });
  const t7c = cards.filter(c => c.t7_candidate).length;
  const open = {};
  cards.forEach(c => c.open_gates.forEach(g => { open[g] = (open[g] || 0) + 1; }));
  const gateRows = Object.entries(open).sort((a, b) => b[1] - a[1])
    .map(([g, n]) => `<span class="pill">${esc(g)} × ${n}</span>`).join(" ");
  app.innerHTML = `
  <h2>What this is</h2>
  <p>TECT is operated as a <em>Unified Classical Field Theory / partial-TOE research
  programme</em>. No TOE-level claim is made. Every result is a <strong>claim card</strong> with a
  precise statement, pinned scope, named hypotheses, a falsifier, and a maturity tier
  (TSv2, T0–T7) — and nothing on this site can say more than the card does, because
  this site renders the cards themselves, live from the repository.</p>
  <p class="notice">Reading rules: <strong>T5</strong> = closed only within its pinned scope ·
  <strong>T6</strong> = theorem modulo the listed hypotheses · <strong>T7-cand.</strong> = legacy-proved,
  re-entering at T6 until its reproduction package is rebuilt (no-auto-T7 rule).</p>
  <h2>Ledger at a glance</h2>
  <div class="cards">
    <div class="card"><h3>${cards.length} claims</h3>
      ${Object.entries(tiers).sort().map(([t, n]) => `<span class="pill ${tierClass(t)}">${t}: ${n}</span>`).join(" ")}
      <p class="muted">${t7c} T7-candidates awaiting verification packages</p></div>
    <div class="card"><h3>Open gates (by citing claims)</h3>${gateRows}
      <p class="muted">Top priority: STEP-5B — the gateway for any whole-Reading-H T6 discussion.</p></div>
    <div class="card"><h3>Falsify us</h3>
      <p>Every claim ships its falsification condition and, where available, a
      one-command reproduction. Start at <a href="#/reviewing">Review TECT</a>.</p></div>
  </div>
  <h2>Claims</h2>${claimsTable(cards)}`;
  typeset();
}

function claimsTable(cards, f = {}) {
  const rows = cards.filter(c =>
    (!f.sector || c.sector === f.sector) &&
    (!f.tier || c.tier === f.tier) &&
    (!f.q || (c.id + " " + c.title).toLowerCase().includes(f.q.toLowerCase())))
    .map(c => `<tr>
      <td><a href="#/claim/${esc(c.id)}">${esc(c.id)}</a></td>
      <td>${esc(c.title)}</td><td>${esc(c.sector)}</td>
      <td class="${tierClass(c.tier, c.lifecycle)}">${esc(c.tier)}${c.t7_candidate ? " (T7-cand.)" : ""}</td>
      <td>${esc(c.lifecycle)}</td>
      <td>${c.open_gates.map(esc).join(", ") || "—"}</td></tr>`).join("");
  return `<table><thead><tr><th>ID</th><th>Title</th><th>Sector</th><th>Tier</th>
    <th>Lifecycle</th><th>Open gates</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function viewClaims() {
  const {cards} = await loadClaims();
  const sectors = [...new Set(cards.map(c => c.sector))].sort();
  const tiers = [...new Set(cards.map(c => c.tier))].sort();
  app.innerHTML = `<h2>Claim ledger</h2>
    <p class="muted">Source of truth: <code>claims/&lt;ID&gt;/status.json</code> — rendered live.</p>
    <p>
      <select id="fs"><option value="">all sectors</option>${sectors.map(s => `<option>${s}</option>`).join("")}</select>
      <select id="ft"><option value="">all tiers</option>${tiers.map(t => `<option>${t}</option>`).join("")}</select>
      <input id="fq" placeholder="search…">
    </p><div id="tbl"></div>`;
  const render = () => {
    document.getElementById("tbl").innerHTML = claimsTable(cards, {
      sector: document.getElementById("fs").value,
      tier: document.getElementById("ft").value,
      q: document.getElementById("fq").value});
    typeset();
  };
  ["fs", "ft", "fq"].forEach(id => document.getElementById(id).addEventListener("input", render));
  render();
}

async function viewClaim(id) {
  const c = await fetchJSON(`claims/${id}/status.json`);
  const ev = c.legacy_evidence.map(p => p.startsWith("archive/")
      ? `<li><a href="${BLOB(p)}">${esc(p)}</a></li>`
      : `<li class="muted">${esc(p)} (migration pending)</li>`).join("");
  let cardMd = "";
  try { cardMd = md(await fetchText(`claims/${id}/claim.md`)); } catch (e) { /* optional */ }
  app.innerHTML = `
  <h2>${esc(c.id)} — ${esc(c.title)}</h2>
  <p><span class="pill ${tierClass(c.tier, c.lifecycle)}">${esc(c.tier)}${c.t7_candidate ? " · T7-candidate" : ""}</span>
     <span class="pill">${esc(c.lifecycle)}</span>
     <span class="pill">sector ${esc(c.sector)}</span>
     <span class="pill">reviewed ${esc(c.last_review)}</span></p>
  <h3>Statement</h3><p>${c.statement}</p>
  <h3>Scope</h3><p>${esc(c.scope)}</p>
  ${c.hypotheses.length ? `<h3>Hypotheses</h3><p>${c.hypotheses.map(h => `<span class="pill">${esc(h)}</span>`).join(" ")}
     <a href="#/gates">(registry)</a></p>` : ""}
  ${c.open_gates.length ? `<h3>Open gates</h3><p>${c.open_gates.map(g => `<span class="pill">${esc(g)}</span>`).join(" ")}</p>` : ""}
  <h3>Falsifier</h3><p>${c.falsifier}</p>
  <h3>Reproduction</h3><p><code>${esc(c.reproduction.command || "package pending")}</code><br>
     <span class="muted">${esc(c.reproduction.expected || "")}</span></p>
  <h3>No-overclaim</h3><p class="notice">${esc(c.no_overclaim)}</p>
  <h3>Evidence</h3><ul>${ev}</ul>
  <details><summary>Full card (claims/${esc(id)}/claim.md)</summary>${cardMd}</details>`;
  typeset();
}

async function mdPage(title, path) {
  app.innerHTML = `<h2>${esc(title)}</h2>
    <p class="muted">Rendered live from <a href="${BLOB(path)}"><code>${esc(path)}</code></a>.</p>
    <div>${md(await fetchText(path))}</div>`;
  typeset();
}

async function viewCatalog() {
  const cat = await fetchJSON("verification/catalog.json");
  const kinds = [...new Set(cat.entries.map(e => e.kind))];
  const rows = cat.entries.map(e => `<tr><td><a href="${BLOB(e.path)}">${esc(e.path)}</a></td>
    <td>${esc(e.kind)}</td><td>${e.claims.map(esc).join(", ") || "—"}</td>
    <td>${esc(e.version || "—")}</td><td>${esc(e.first_issued || "—")}</td>
    <td>${esc(e.version_issued || "—")}</td><td>${esc(e.lifecycle)}</td></tr>`).join("");
  app.innerHTML = `<h2>Catalog — every tracked artefact (${cat.entries.length})</h2>
    <p class="muted">Generated ${esc(cat.generated)} · kinds: ${kinds.map(esc).join(", ")}</p>
    <table><thead><tr><th>Path</th><th>Kind</th><th>Claims</th><th>Ver</th>
    <th>First issued</th><th>Version issued</th><th>Lifecycle</th></tr></thead>
    <tbody>${rows}</tbody></table>`;
}

/* ---- router ----------------------------------------------------------------- */
const routes = {
  "": viewOverview,
  "claims": viewClaims,
  "gates": () => mdPage("Gate & hypothesis registry", "claims/GATES.md"),
  "roadmap": () => mdPage("Roadmap", "ROADMAP.md"),
  "catalog": viewCatalog,
  "negative": () => mdPage("Negative-result registry", "negative-results/registry.md"),
  "predictions": () => mdPage("Prediction ledger", "predictions/prediction-ledger.md"),
  "reviewing": () => mdPage("How to review (or attack) TECT", "REVIEWING.md"),
  "changelog": () => mdPage("Changelog", "CHANGELOG.md"),
};
async function route() {
  if (!SLUG) {
    app.innerHTML = `<p class="notice">Repository not detected. Serve from GitHub Pages
      or append <code>?repo=owner/name</code> to the URL.</p>`;
    return;
  }
  document.getElementById("repolink").innerHTML =
    `Repository: <a href="https://github.com/${SLUG}">${SLUG}</a>`;
  const h = location.hash.replace(/^#\/?/, "");
  app.innerHTML = `<p class="muted">Loading…</p>`;
  try {
    if (h.startsWith("claim/")) await viewClaim(decodeURIComponent(h.slice(6)));
    else await (routes[h] || viewOverview)();
  } catch (e) {
    app.innerHTML = `<p class="notice">Failed to load live data: ${esc(e.message)}.
      The repository may not be public yet, or the path moved.</p>`;
  }
}
addEventListener("hashchange", route);
addEventListener("DOMContentLoaded", route);
