# TECT TOE Proof Governance — v2.0

**Status**: binding constitution of this repository
**Issued**: 2026-06-05 (supersedes draft "TECT TOE Proof Governance v1.0" and the
"Verification-First operating rules" draft; integrates both)
**Maintainer**: Jusang Lee (jtkor@outlook.com)

This document is the constitution. Detailed binding policies live in
`governance/` and are referenced per section. Where this document and a
`governance/` policy disagree, the `governance/` policy is canonical and the
disagreement is a synchronisation defect to be fixed.

---

## 0. Purpose

Do not prove "TOE" as a vague slogan. Define a Master Theorem, decompose it into
sector theorems, track dependencies, and close falsification gates one by one.
Every question about TECT progress is answered by four questions:

1. Which theorem is proved?
2. What does it depend on?
3. What would falsify it?
4. What tier is justified by the evidence?

## 1. Master Theorem

$$
\begin{aligned}
\textbf{TECT-TOE Master Theorem:}\quad
&\text{Given the microscopic TECT functional } \mathcal F_{\rm TECT},\\
&\text{with fixed production kernel, admissible bundle data,}\\
&\text{UV regularisation, and renormalisation prescription,}\\
&\text{the low-energy limit of TECT derives } \mathrm{SM}+\mathrm{GR}+\text{cosmological sector}\\
&\text{with controlled deviations and falsifiable predictions.}
\end{aligned}
$$

The Master Theorem is never proved directly. It is proved through the dependency
DAG of sector theorems:

$$
\text{Master Theorem} = \text{Sector Theorems} + \text{Dependency DAG}
+ \text{Falsification Gates} + \text{Verification Packages}
+ \text{Observable Predictions}.
$$

## 2. Sectors (top-level research units)

The 11 legacy pillars are retained as sub-theorem folders, not as the top-level
classification. The top-level units are six sectors:

| Sector | Scope | Legacy pillars absorbed |
|---|---|---|
| **A — Microscopic Foundation** | $\mathcal F_{\rm TECT}$ well-defined: fields, kernel convention, regularisation, counterterms, renormalisation, PDE well-posedness | (foundation layer of all pillars) |
| **B — Vacuum / Reading Selection** | $\mathcal R_H = \operatorname{arg\,min}_{\mathcal R \in \mathcal A_{\rm adm}} F_{\rm TECT}[\mathcal R]$ | P1 (mass/ground state) |
| **C — Spacetime / Lorentz / Gravity** | Lorentz symmetry, metric structure, spin-2, Einstein limit, Newton $G$, equivalence principle | P2, P3, P8, P9 |
| **D — Gauge / Matter / Topology** | $SU(3)\times SU(2)\times U(1)$, fermion representations, chirality, families, anomaly cancellation | P4, P5, P7 |
| **E — Spectrum / Couplings / Constants** | $m_i$, $\theta_{\rm CKM}$, $\theta_{\rm PMNS}$, $g_{1,2,3}$, $G$, $\Lambda$, Higgs/EW scale, origin of $\hbar$ | P6, P10 |
| **F — Cosmology / Falsifiability** | phase-transition history, dark matter, dark energy, baryogenesis, CMB constraints, testable deviations | P11 |

Sector B is the current critical blocker (vacuum uniqueness feeds C, D, E).

## 3. GAPs are promotion gates, not residual holes

| Gate | Statement | Closing consequence |
|---|---|---|
| **GAP-1 Vacuum Uniqueness** | $\mathcal R_H$ is the admissible-class minimiser | C1 structural closure → T6/T7 candidate |
| **GAP-2 Continuum / Error Control** | $\left|\Delta F_{\rm true} - \Delta F_{\rm est}\right| \le \varepsilon_{\rm ctrl}$ with $\Delta F_{\rm est} - \varepsilon_{\rm ctrl} > 0$ | estimator-grade → theorem-grade |
| **GAP-3 Constants / Spectrum** | every constant carries a derived/matched/inserted/predicted label with ledger row | quantitative closure C2 |
| **GAP-4 Cosmology / Falsification** | TECT predicts an observable deviation **before** fitting it | observational closure C3 |

Named sub-gates (Step-5b, G3'-b(iii), H-suppression, …) are registered in
`claims/GATES.md`.

## 4. Closure depth (C) and proof maturity (S)

- **C1 structural / C2 dynamical-quantitative / C3 cosmological-observational**
  are closure depths, not subject areas.
- **S1 existence / S2 selection / S3 stability-universality** are proof maturity
  levels. A TOE-level claim requires the core sectors at S3.

## 5. Tier scale (TSv2) — summary

Full definitions, the legacy translation table, and the lifecycle flags are in
`governance/tier-system.md` (binding).

| Tier | Meaning |
|---|---|
| T0 | idea / unformalised conjecture |
| T1 | qualitative mechanism |
| T2 | partial formalisation |
| T3 | computable scaffold |
| T4 | strong evidence (numerics, analytic bounds, partial audit — not a theorem) |
| T5 | closed within pinned scope (scope stated exactly, e.g. `T5 CLOSED@ESTIMATOR-GRADE`) |
| T6 | conditional theorem under named hypotheses |
| T7 | discharged theorem in the declared physical domain |

**T7 prohibition list** — T7 is forbidden while any of the following holds:
unexecuted script; estimator-only result with no error bound; hidden inherited
assumption; single-point result without declared scope; observed value inserted
but called predicted; unclosed admissible competitor class; unresolved convention
ambiguity; **no public reproducibility package**.

**Rejection is orthogonal to maturity**: refuted claims carry the lifecycle flag
`REFUTED` (with a `negative-results/` entry), they do not occupy a tier slot.

**Tier monotonicity along the DAG**: a claim at tier ≥ T6 may depend on inputs
below T6 only by promoting each such input to an explicit named hypothesis in
its statement. The linter enforces this (`governance/claim-standard.md` §4).

## 6. Evidence grades

Every result carries at least one of:
`ANALYTIC`, `EXACT`, `EXECUTED`, `ESTIMATOR` (error-bound status mandatory),
`INHERITED` (breaks with its source), `CONDITIONAL`, `MATCHED`, `INSERTED`,
`PREDICTED`.

**Constants firewall (binding)**: every numerical constant is labelled exactly
one of `DERIVED` / `MATCHED` / `INSERTED` / `PREDICTED` as defined in
`governance/tier-system.md` §5. Confusing `derived` with `matched` in a TOE-level
statement is a registry-grade defect. Canonical example: Newton constant —

$$
G=\frac{c^3 a_{\rm BCC}^2}{16\pi\hbar}:\quad
\mathrm{RELATION\ DERIVED},\quad \mathrm{VALUE\ MATCHED},\quad
\mathrm{NOT\ YET\ PREDICTED}
$$

unless $a_{\rm BCC}$ is computed without $G_{\rm obs}$.

## 7. Claim registration (the only way results enter the record)

No result exists in TECT unless it has a claim card under `claims/<ID>/` with
`claim.md` + `status.json` containing all of: Claim ID; precise statement; scope;
dependencies; hypotheses; evidence grade; falsification gate; reproduction
command + expected output; tier (before/after); no-overclaim statement; next
required action. Schema and footer template: `governance/claim-standard.md`.

`CLAIMS.md` is **generated** from `claims/*/status.json` by
`verification/scripts/lint_claims.py --render`. Hand-editing `CLAIMS.md` is
forbidden (single-source-of-truth rule; this kills the mirror-drift failure
class of the legacy repository).

## 8. Verification packages

A claim is only as credible as its verification package:

$$
\text{Claim} + \text{Assumptions} + \text{Proof} + \text{Code} + \text{Data}
+ \text{Expected Output} + \text{Falsification Condition}.
$$

One-command reproduction is the target for every claim at T5+:

```bash
python verification/scripts/verify_claim.py --claim <ID>
```

with the standardised PASS/FAIL output contract of
`governance/verification-standard.md` §3. Internal verification is tripled:
each core result needs at least two of {analytic proof, independent numerical
script, alternative formulation / limiting-case check}.

## 9. Competition closure

Infinitely many competitor states are never checked one by one. The order is:

$$
\text{dangerous representatives} \rightarrow \text{class theorem}
\rightarrow \text{exhaustiveness theorem}.
$$

Dangerous representatives first (LAM, HEX, FCC, BCC, BCC {110}+{200},
Bloch/off-diagonal, inhomogeneous Wick, dense surface), then general bounds
(higher-shell dominance, generic-phase bound, large-amplitude $\phi^6$ growth,
small-amplitude positivity).

## 10. No-overclaim rule

Every significant result records what may **not** be said next to what may be
said. Example:

- Allowed: "Reading-H is closed at estimator grade within enumerated ensembles."
- Forbidden: "Reading-H is the full global minimum over all possible states."

Forbidden phrases anywhere in P1/P2 content: "essentially proved", "almost
closed", "at theorem level", "near closure", and any promotional adjective
stronger than the registered tier.

## 11. Negative results

Failed branches are recorded in `negative-results/registry.md` in the format
(branch | failure mode | evidence | consequence). Failures are trust assets.
When a falsification gate fires, the theorem statement moves — the theory is
not protected. The only protected object is the inequality
$F[\mathcal R]-F[\mathcal R_H]>0$; if an admissible branch violates it, the
conclusion moves.

## 12. Publication tiers

Three tiers, defined in `governance/publication-tiers.md` (binding):

- **P0 `internal/`** — local-only; gitignored; never reaches GitHub.
- **P1 repository** — the public verification surface (GitHub).
- **P2 `publish/`** — curated outward publication: `publish/website/` and
  `publish/papers/`, strictly derived from P1 claims. Nothing enters P2 without
  a claim-card backing at the cited tier.

## 13. Migration from the legacy corpus

Pull-based, re-validated, ledgered. Policy: `governance/migration-plan.md`.
Bulk copying is forbidden.

## 14. AI-collaborator protocol

Session-entry sequence, write discipline, and archival duties for AI sessions
working in this repository: `CLAUDE.md` (repo root).

## 15. Final governance principle

$$
\text{Do not protect a preferred interpretation. Protect only the inequality } F[\mathcal R]-F[\mathcal R_H]>0.
$$

$$
\text{Do not hide open assumptions. Turn every open assumption into a named gate.}
$$

$$
\text{Do not claim prediction unless the input set was frozen first.}
$$
