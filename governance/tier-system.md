# Tier System TSv2, Evidence Grades, Lifecycle Flags (binding)

**Issued**: 2026-06-05. Replaces the legacy `STATUS_NOMENCLATURE.md` 8-tier
scale (T0=REFUTED … T7=PROVED, 2026-04-29) for all new registrations. The two
scales are **not** identical; the translation table in §4 is the only sanctioned
bridge. Scale identifier `TSv2` appears in every `status.json`
(`"tier_scale": "TSv2"`), so a future scale change cannot silently corrupt the
record.

## 1. Maturity tiers (TSv2)

| Tier | Label | Definition | Promotion requirement (additional to lower tiers) |
|---|---|---|---|
| T0 | IDEA | idea / unformalised conjecture | — |
| T1 | MECHANISM | qualitative mechanism | stated mechanism with at least one worked example |
| T2 | PARTIAL-FORM | partial formalisation | explicit equations; pre-registered falsification gate |
| T3 | SCAFFOLD | computable scaffold | runnable computation path; gaps named |
| T4 | STRONG-EVIDENCE | numerics + analytic bounds + partial audit; not a theorem | ≥1 executed script or independent calculation |
| T5 | PINNED-CLOSURE | closed within pinned scope (scope string mandatory, e.g. `CLOSED@ESTIMATOR-GRADE`, `CLOSED@1-LOOP`, `CLOSED@SINGLE-MODE-CONE`) | reproduction package |
| T6 | CONDITIONAL-THEOREM | theorem under named hypotheses $H_1,\dots,H_n$ | full proof + hypotheses each textbook-grade or separately tracked as claims/gates + independent check |
| T7 | DISCHARGED-THEOREM | unconditional within the declared physical domain | no hidden assumption + **public reproducibility package** + external reproduction possible + dual independent audit |

**T7 prohibition list** (any one blocks T7): unexecuted script; estimator-only
with no error bound; hidden inherited assumption; single-point result without
declared scope; observed value inserted but called predicted; unclosed
admissible competitor class; unresolved convention ambiguity; missing public
reproducibility package.

**Promotion path** is strict T(n) → T(n+1) unless the result is a one-shot
textbook argument (justify in the card). Every promotion to T6/T7 requires the
card's devil's-advocate section (≥3 concrete objections, each
DISMISSED / VALID-with-mitigation / UPHELD) and at least one quantitative
sanity check when numbers are involved.

## 2. Lifecycle flags (orthogonal to tier)

`ACTIVE` | `SUPERSEDED` (points to successor claim) | `REFUTED` (points to
`negative-results/` entry). A refuted claim keeps its last tier for the
historical record; the flag, not the tier, carries the rejection. This removes
the legacy ambiguity where T0 meant both "idea" and "refuted".

## 3. Tier monotonicity along the dependency DAG

Let $D$ be the hard dependencies of claim $X$.

- If $\mathrm{tier}(X) \le \mathrm{T5}$: no constraint beyond DAG acyclicity —
  the pinned scope declares its inputs.
- If $\mathrm{tier}(X) \ge \mathrm{T6}$: every $d \in D$ with
  $\mathrm{tier}(d) < \mathrm{T6}$ must be promoted to a **named hypothesis**
  listed in `status.json:hypotheses` and in the theorem statement. A T6 claim
  silently resting on a T3 input is the legacy Pillar-4 failure mode; the
  linter rejects it.
- `soft_dependencies` (motivation/context only, proof does not use them) are
  exempt and must be marked as such.

## 4. Legacy → TSv2 translation table (binding for migration)

| Legacy (STATUS_NOMENCLATURE 2026-04-29) | TSv2 entry tier | Notes |
|---|---|---|
| T7 PROVED | **T6** + `t7_candidate: true` | **No auto-T7.** T7 requires the TSv2 reproducibility package, which no legacy result has yet. Restored to T7 only after package + dual audit under this governance. |
| T6 PROVED CONDITIONAL | T6 (hypotheses re-listed explicitly) | |
| T5 CLOSED@N-LOOP | T5, scope = `CLOSED@N-LOOP` | |
| T4 STRONG EVIDENCE | T4 | |
| T3 PROOF SKETCH | T3 | |
| T2 CONJECTURE | T2 (falsification gate must be re-registered) | |
| T1 OPEN | T1 if a mechanism exists, else T0 | judgement recorded in migration ledger |
| T0 REFUTED | lifecycle `REFUTED` + tier at pre-refutation maturity | + `negative-results/` row |
| legacy free-text labels (PARTIAL-ADVANCED, NEAR-CLOSURE, STRONG CLOSURE DRAFT, …) | per legacy §3 translation, then this table | forbidden going forward |

## 5. Evidence grades

Each claim lists ≥1 grade; ESTIMATOR additionally must state
`error_bound: controlled | uncontrolled`.

| Grade | Meaning |
|---|---|
| ANALYTIC | proof by derivation |
| EXACT | closed-form arithmetic / exact identity |
| EXECUTED | script run with persisted artefact (`claims/<ID>/runs/…`) |
| ESTIMATOR | estimator result; error-bound status mandatory |
| INHERITED | inherited from another claim; breaks with its source |
| CONDITIONAL | holds under stated assumptions |
| MATCHED | one observed value fixes one TECT scale/parameter |
| INSERTED | observed/external value assumed without derivation |
| PREDICTED | computed internally before comparison with data |

### Constants firewall

Every numerical constant appearing anywhere in P1/P2 carries exactly one of
`DERIVED / MATCHED / INSERTED / PREDICTED`. The four definitions:

- DERIVED — computed from TECT equations without observational calibration.
- MATCHED — one observed value fixes one TECT scale or parameter.
- INSERTED — the observed value is assumed directly.
- PREDICTED — computed before comparison with data, under a registered freeze
  (`predictions/` ledger + freeze protocol).

A relation can be DERIVED while its numerical value is MATCHED — say both,
never collapse them. Canonical example: $G = c^3 a_{\rm BCC}^2/(16\pi\hbar)$,
managed as **T6/T7-SPLIT**: the relation may reach theorem grade while the
independent numerical prediction remains OPEN until $a_{\rm BCC}$ is computed
without $G_{\rm obs}$.

## 6. Closure depth and proof maturity (unchanged semantics)

C1 structural / C2 dynamical-quantitative / C3 cosmological-observational;
S1 existence / S2 selection / S3 stability-universality. Both are recorded on
cards where meaningful (`closure_depth`, `proof_maturity`); TOE-level language
requires core sectors at S3 — and is suspended programme-wide until then.
