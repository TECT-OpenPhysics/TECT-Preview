/* TECT live site — static shell; ALL content fetched at view time from the
 * repository's main branch (raw.githubusercontent.com). Zero generated
 * content files: the repo itself is the only source of truth
 * (governance/publication-tiers.md, live-fetch architecture).
 *
 * __version__ 1.2.0 · first issued 2026-06-05 · issued 2026-08-10
 * 1.0.1: exclude claims/_TEMPLATE from the live ledger (same defect as build_wiki 1.0.1)
 * 1.1.0: live per-claim Development lineage (LINEAGE.md) + Results-ledger route
 * 1.1.1: strategy/ route (non-tier-bearing analysis notes)
 * 1.2.0: compact catalog-summary bootstrap, exact live-card paths, paginated
 *        catalog rendering, and bounded changelog landing.
 */
"use strict";

/* ---- repository autodetection (owner.github.io/<repo>/) ------------------ */
const REPO_FALLBACK = "";            // "owner/repo" — used off-Pages (e.g. local preview)
const SLUG_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
function repoSlug() {
  const q = new URLSearchParams(location.search).get("repo");
  if (q) return SLUG_RE.test(q) ? q : "";
  const host = location.hostname;        // owner.github.io
  if (host.endsWith(".github.io")) {
    const owner = host.split(".")[0];
    const seg = location.pathname.split("/").filter(Boolean)[0];
    const candidate = seg ? owner + "/" + seg : "";
    if (SLUG_RE.test(candidate)) return candidate;
  }
  return SLUG_RE.test(REPO_FALLBACK) ? REPO_FALLBACK : "";
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
function rewriteRepoLinks(root, sourcePath) {
  if (!root) return;
  const blobBase = BLOB(sourcePath);
  const rawBase = RAW(sourcePath);
  root.querySelectorAll("a[href]").forEach(link => {
    const href = link.getAttribute("href");
    if (!href || /^(?:https?:|mailto:)/i.test(href)) return;
    link.href = href.startsWith("#") ? blobBase + href : new URL(href, blobBase).href;
  });
  root.querySelectorAll("img[src]").forEach(img => {
    const src = img.getAttribute("src");
    if (!src || /^(?:https?:|data:)/i.test(src)) return;
    img.src = new URL(src, rawBase).href;
  });
}

/* ---- data loading --------------------------------------------------------- */
async function loadClaims() {
  const summary = await fetchJSON("verification/catalog-summary.json");
  const paths = summary.claim_status_paths;
  const cards = await Promise.all(paths.map(fetchJSON));
  if (cards.length !== summary.claim_count) {
    throw new Error(`live claim index mismatch: ${cards.length}/${summary.claim_count}`);
  }
  cards.sort((a, b) => a.id.localeCompare(b.id));
  return {cards, catalogSummary: summary};
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
      <p class="muted">Current priorities are read from the live <a href="#/roadmap">roadmap</a>
      and task ledger; this overview does not hardcode a stale gate.</p></div>
    <div class="card"><h3>Falsify us</h3>
      <p>Every claim ships its falsification condition and, where available, a
      one-command reproduction. Start at <a href="#/reviewing">Review TECT</a>.</p></div>
    <div class="card"><h3>Reusable results</h3>
      <p>Standalone lemmas and theorems harvested from the claims — several are
      self-contained harmonic-analysis / additive-combinatorics statements.
      See the <a href="#/results">results ledger</a>.</p></div>
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
  <h3>Statement</h3><p>${esc(c.statement)}</p>
  <h3>Scope</h3><p>${esc(c.scope)}</p>
  ${c.hypotheses.length ? `<h3>Hypotheses</h3><p>${c.hypotheses.map(h => `<span class="pill">${esc(h)}</span>`).join(" ")}
     <a href="#/gates">(registry)</a></p>` : ""}
  ${c.open_gates.length ? `<h3>Open gates</h3><p>${c.open_gates.map(g => `<span class="pill">${esc(g)}</span>`).join(" ")}</p>` : ""}
  <h3>Falsifier</h3><p>${esc(c.falsifier)}</p>
  <h3>Reproduction</h3><p><code>${esc(c.reproduction.command || "package pending")}</code><br>
     <span class="muted">${esc(c.reproduction.expected || "")}</span></p>
  <h3>No-overclaim</h3><p class="notice">${esc(c.no_overclaim)}</p>
  <h3>Evidence</h3><ul>${ev}</ul>
  <details><summary>Full card (claims/${esc(id)}/claim.md)</summary>
    <div id="claim-card-md">${cardMd}</div></details>
  <h3>Development lineage</h3>
  <p class="muted">The ordered theory-development trace for this claim, live from
     <a href="${BLOB(`claims/${id}/LINEAGE.md`)}"><code>claims/${esc(id)}/LINEAGE.md</code></a>
     (generated from note banners).</p>
  <div id="lineage"><p class="muted">Loading lineage…</p></div>`;
  rewriteRepoLinks(document.getElementById("claim-card-md"), `claims/${id}/claim.md`);
  typeset();
  try {
    const lin = await fetchText(`claims/${id}/LINEAGE.md`);
    document.getElementById("lineage").innerHTML =
      `<details open><summary>development arc + chronological note-lineage</summary>${md(lin)}</details>`;
    rewriteRepoLinks(document.getElementById("lineage"), `claims/${id}/LINEAGE.md`);
    typeset();
  } catch (e) {
    document.getElementById("lineage").innerHTML =
      `<p class="muted">No lineage ledger yet for this claim.</p>`;
  }
}

async function mdPage(title, path) {
  app.innerHTML = `<h2>${esc(title)}</h2>
    <p class="muted">Rendered live from <a href="${BLOB(path)}"><code>${esc(path)}</code></a>.</p>
    <div id="md-page-body">${md(await fetchText(path))}</div>`;
  rewriteRepoLinks(document.getElementById("md-page-body"), path);
  typeset();
}

async function viewCatalog() {
  const summary = await fetchJSON("verification/catalog-summary.json");
  const manifest = await fetchJSON("verification/catalog/index.json");
  const kinds = summary.kinds.map(row => row.kind);
  const pageSize = 100;
  let page = 0;
  let loaded = [];
  app.innerHTML = `<h2>Catalog — every tracked artefact (${manifest.total})</h2>
    <p class="muted">The manifest is compact. One kind shard is fetched on selection;
    loading every kind requires an explicit choice.</p>
    <p><select id="ck"><option value="">choose a kind</option>
      <option value="__all__">all kinds (load all shards)</option>${kinds.map(k =>
      `<option value="${esc(k)}">${esc(k)}</option>`).join("")}</select>
      <input id="cq" placeholder="path, claim, or version…"></p>
    <div id="catalog-page"></div>`;
  const render = () => {
    const kind = document.getElementById("ck").value;
    const q = document.getElementById("cq").value.toLowerCase();
    if (!kind) {
      document.getElementById("catalog-page").innerHTML = `<table><thead><tr>
        <th>Kind</th><th>Artefacts</th><th>Canonical bytes</th></tr></thead><tbody>
        ${summary.kinds.map(row => `<tr><td>${esc(row.kind)}</td><td>${row.count}</td>
        <td>${row.bytes.toLocaleString()}</td></tr>`).join("")}</tbody></table>`;
      return;
    }
    const filtered = loaded.filter(e => (!q ||
      `${e.path} ${e.claims.join(" ")} ${e.version || ""}`.toLowerCase().includes(q)));
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages - 1);
    const visible = filtered.slice(page * pageSize, (page + 1) * pageSize);
    const rows = visible.map(e => `<tr><td><a href="${BLOB(e.path)}">${esc(e.path)}</a></td>
      <td>${esc(e.kind)}</td><td>${e.claims.map(esc).join(", ") || "—"}</td>
      <td>${esc(e.version || "—")}</td><td>${esc(e.first_issued || "—")}</td>
      <td>${esc(e.version_issued || "—")}</td><td>${esc(e.lifecycle)}</td></tr>`).join("");
    document.getElementById("catalog-page").innerHTML = `
      <p class="muted">${filtered.length} matches · page ${page + 1}/${pages} · at most ${pageSize} rows</p>
      <p><button id="cp" ${page === 0 ? "disabled" : ""}>previous</button>
         <button id="cn" ${page + 1 >= pages ? "disabled" : ""}>next</button></p>
      <table><thead><tr><th>Path</th><th>Kind</th><th>Claims</th><th>Ver</th>
      <th>First issued</th><th>Version issued</th><th>Lifecycle</th></tr></thead>
      <tbody>${rows}</tbody></table>`;
    document.getElementById("cp").addEventListener("click", () => { page--; render(); });
    document.getElementById("cn").addEventListener("click", () => { page++; render(); });
  };
  document.getElementById("ck").addEventListener("input", async () => {
    page = 0;
    const kind = document.getElementById("ck").value;
    if (!kind) {
      loaded = [];
      render();
      return;
    }
    document.getElementById("catalog-page").innerHTML = `<p class="muted">Loading shard…</p>`;
    const selected = kind === "__all__" ? manifest.shards :
      manifest.shards.filter(row => row.kind === kind);
    const shards = await Promise.all(selected.map(row => fetchJSON(row.path)));
    loaded = shards.flatMap(shard => shard.entries);
    render();
  });
  document.getElementById("cq").addEventListener("input", () => { page = 0; render(); });
  render();
}

/* ---- router ----------------------------------------------------------------- */
const routes = {
  "": viewOverview,
  "claims": viewClaims,
  "gates": () => mdPage("Gate & hypothesis index", "claims/GATES-INDEX.md"),
  "roadmap": () => mdPage("Current research management", "management/INDEX.md"),
  "catalog": viewCatalog,
  "negative": () => mdPage("Negative-result and audit index", "negative-results/INDEX.md"),
  "predictions": () => mdPage("Prediction ledger", "predictions/prediction-ledger.md"),
  "reviewing": () => mdPage("How to review (or attack) TECT", "REVIEWING.md"),
  "results": () => mdPage("Reusable results index", "results/INDEX.md"),
  "evidence": () => mdPage("Proof-evidence entry", "theory/proof-evidence/INDEX.md"),
  "strategy": () => mdPage("Strategy & analysis notes", "strategy/INDEX.md"),
  "lineage-policy": () => mdPage("Development-history policy", "governance/development-history.md"),
  "changelog": () => mdPage("Changelog", "changelog/INDEX.md"),
};
async function route() {
  if (!SLUG) {
    app.innerHTML = `<p class="notice">Repository not detected. Serve from GitHub Pages
      or append <code>?repo=owner/name</code> to the URL.</p>`;
    return;
  }
  const repoLink = document.getElementById("repolink");
  repoLink.textContent = "Repository: ";
  const anchor = document.createElement("a");
  anchor.href = `https://github.com/${SLUG}`;
  anchor.textContent = SLUG;
  repoLink.appendChild(anchor);
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
