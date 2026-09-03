# Proof-audit record — A2/R-157/R-158

Status: `INTERNAL-AUDIT-DRAFT` (2026-09-03).  This document is a structured
adversarial checklist for an eventual independent mathematician.  It is not
an external referee report, an operator sign-off, or a claim-tier promotion.

## Audit scope

The audit covers the explicitly declared side-16 periodic three-torus,
six-real-component field, positive density floor, pinned coefficients, and
`eta_shell=0` functional in `manuscript.tex`.  It does not audit a removed
regulariser, a historical backend, a thermodynamic or continuum limit, a
quantum/KMS construction, a physical charge, a physical vacuum, BCC selection,
or any Sector-A interpretation.

The source claims are `A2-FULL-PRODUCTION-WELLPOSED`, `R-157`, and `R-158`.
`R-472` is an assurance-only exact/Lean sidecar and is not load-bearing.

## Theorem-by-theorem checklist

| item | proof obligation | current evidence | internal disposition | external review |
|---|---|---|---|---|
| A2-1 | The fourth-order symbol is positive and the form domain is `H^2`, operator domain `H^4`. | `manuscript.tex`, Sec. 4.1; A2 full-production audits | exact constants and operator statement are recorded | required: check self-adjoint realization and norm equivalence |
| A2-2 | The regularised Class-II Euler map has order two and is locally Lipschitz `H^2 -> L^2`. | `manuscript.tex`, Sec. 4.2; nonlinear-mapping audit | argument is explicit but uses product/Sobolev estimates | required: verify every product exponent and coefficient dependence |
| A2-3 | Analytic-semigroup mild theory gives local existence and continuation. | `manuscript.tex`, Sec. 4.2; A2 wrapper | conditional on the declared operator realization | required: check sectorial hypotheses and the singular-kernel contraction |
| A2-4 | Galerkin solutions pass to a global weak/strong solution and satisfy the exact energy identity. | `manuscript.tex`, Sec. 4.3; energy-continuation audit | executable lanes pass; analytic compactness/chain rule are not machine-proved | required: audit projection, compactness, and chain-rule passage |
| A2-5 | Endpoint Duhamel cancellation yields `H^4` for positive time and Moser iteration yields smoothness. | `manuscript.tex`, Sec. 4.4; smoothing audit | cancellation is stated with the required Hölder remainder | required: verify endpoint integrability and iteration domains |
| A2-6 | Uniqueness and finite-time continuous dependence hold in `H^2`. | `manuscript.tex`, Secs. 4.2 and 4.4 | weakly singular Gronwall route is recorded | required: check common energy ball and time-uniform constants |
| R-157-1 | Exact quadratic/polynomial completion gives `F >= g ||Psi||_2^2`, with `g>1/8`. | R-157 primary `26/26`, independent `24/24`, integrated `144/144` | PASS at declared finite scope | required: independently recompute coefficient matching and equality case |
| R-157-2 | The Class-II radial derivative matrix is positive for every `theta in [0,1]`. | exact rational primary/independent lanes | PASS; concave determinant endpoint test | required: check scaling from `y=t^2` and floor derivative |
| R-157-3 | No nonzero critical point exists and the canonical flow decays exponentially. | R-157 integrated result and manuscript Sec. 5 | PASS at declared unconstrained scope | required: verify differentiability along rays and decay identity |
| R-158-1 | The finite-torus spectral bottom lies on the `|n|^2=3` shell. | R-158 primary/independent lanes | PASS with exact Sturm and rational `pi` enclosure | required: check integer-shell comparison and internal eigenvalue isolation |
| R-158-2 | The polynomial/Bregman decomposition is nonnegative and plane-wave saturation is exact. | R-158 primary/independent lanes; manuscript Sec. 6 | PASS for `Q/|T| >= rho_*`; below `Q_*` intentionally not claimed | required: audit constraint normalization and equality conditions |
| R-158-3 | The imposed grand potential has zero/nonzero coexistence at `mu_t` and strict ordering with the saddle-node and linear spinodal. | R-158 integrated `155/155` and R-157/A2 regression | PASS for the imposed mathematical ensemble | required: check global-minimizer existence for `mu>mu_t` and first-order terminology |

## Cross-cutting adversarial questions

1. **Could the conditional H3 identification be silently treated as an
   unconditional physical law?**  No.  The manuscript repeats the named H3
   hypothesis and the limitations section blocks physical transfer.
2. **Could R-158's nonzero plane wave be reported as an R-157 equilibrium?**
   No.  Section 6.3 distinguishes `D F(Psi_*) = mu_t Psi_*` from
   `D F(Psi_*) = 0` and records that the original neutral energy remains higher
   or equal in the stated direction.
3. **Could executable PASS counts be mistaken for analytic proof?**  No.  The
   verification section explicitly says that semigroup, compactness, chain
   rule, and literature steps remain proof-text obligations.
4. **Could finite shell coexistence be promoted to infinite-volume or BCC
   selection?**  No.  The scope and falsifier sections exclude both.
5. **Could the positive density floor be removed without changing the theorem?**
   No.  Its removal is explicitly a different theorem and is outside scope.

## Required external review questions

An independent mathematician should either answer these questions in writing
or identify a precise repair:

* Is the Class-II first variation well-defined as an `L^2` map on the stated
  `H^2` domain, including all denominator derivatives?
* Do the claimed semigroup and quasilinear estimates apply to the exact
  self-adjoint fourth-order operator with the displayed domains?
* Does the Galerkin/Aubin–Lions argument provide the stated strong convergence
  and justify the nonlinear chain rule without an unlisted time-regularity
  hypothesis?
* Is the endpoint cancellation formula valid with the stated Hölder modulus,
  and does its iteration really imply `C^infty` positive-time regularity?
* Are the equality cases in the neutral completion and the ensemble Bregman
  completion exactly as claimed, including the finite-volume normalization?
* Does the global-minimizer argument for `mu>mu_t` use a coercivity statement
  strong enough to prevent loss of mass on the fixed torus?

## Current acceptance decision

The repository-local executable and exact-arithmetic gates are passing, and the
two former integrated record failures were repaired in verifier v1.0.2 and
recorded as `EXP-001372`.  This is sufficient to advance the package from
`REPRODUCTION-SYNC-OPEN` to `INTERNAL-AUDIT-READY`; it is not sufficient to
mark the paper `internal-review`, `submitted`, or `published`.

The following remain open by design: an independent mathematician's signed
proof audit, specialist novelty/literature review, operator adversarial
confirmation, the operator-gated PUBLISHED capstone bundle, and a clean
repository release check.  Any objection from those reviews must be recorded
here and in the appropriate governed ledger before the lifecycle advances.
