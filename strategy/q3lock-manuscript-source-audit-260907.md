# Q3LOCK current-source and model-comparison audit

Date: 2026-09-07. EXP-001611. T0, claim_bearing=false, INTERNAL_REVIEW_ONLY.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782, R-497 / EXP-001598.
This is a content checkpoint, not a theorem promotion or external signature.
The Q3LOCK paper PDF remains deferred until final content review.

## Findings

The v0.1.7 manuscript replaces an unnamed finite Feynman--Kac input with
Simon's exact Theorem 1.1 / (1.1)--(1.3), page 2, in
https://arxiv.org/pdf/math-ph/9907022v1. It derives the positive-mass
coordinate transformation, normalized harmonic bridge density, and diagonal
trace identity. The stronger unbounded-semigroup theorem is not needed.

The paper-local imported-source-ledger.md gives individual hypothesis
matches for this input, KP Proposition 2.2, KP Theorem 3.1 and FSS Theorem
2.1. The old source-freeze note remains unchanged: its allowed-source list
is not mistaken for the current imports. Independent acceptance remains OPEN.

The literature-crosswalk.md records primary locators, discovery queries and
the remaining broader-theorem search. The manuscript identifies two direct
import obstructions by exact algebra: unequal Q3 quartic values on the unit
sphere, and a nonconstant mixed Hessian on each locking edge. These do not
exclude every reduction or comparison theorem.

FSS already permits nonradial priors. KKK (3.71)--(3.75) already contains
the same threshold mechanism. The candidate contribution is the actual
positive-lambda collective lower bound and its loop/DLR composition, not a
new infrared principle or new threshold functional form.

## Adversarial review

1. Sign/convention: the edge mixed derivative is nonconstant, but its
   negativity is compatible with the earlier log-density FKG sign. Do not
   confuse a failed bilinear rewriting with failed ferromagnetic association.
   DISMISSED by symbolic differentiation of the printed edge polynomial.
2. Factor/units: the mass-one free bridge is not our physical bridge.
   z=sqrt(m)q gives the m^(-D/4) unitary factor and m^(D/2) kernel factor.
   DISMISSED algebraically; analytic kernel application still requires review.
3. Model substitution: lambda=0 or restriction to q parallel to u would
   change the model. Nonradiality alone does not establish novel mathematics.
   UPHELD as an explicit prohibition; neither change is used.
4. Domain/limit: all Simon and FSS applications are finite dimensional before
   time or space limits. Their constants do not authorize an unproved limit.
   VALID with the separate manuscript loop/UI/domain proofs and OPEN review.
5. Hardcode masking: graph vertices and edges, quartic values and derivatives
   are computed from Q3; printed constants are labelled comparison oracles.
   Threshold eight is derived as two times four, not from eight components.
   DISMISSED at diagnostic scope.
6. Convergence/novelty: symbolic checks contain no quadrature or thermodynamic
   simulation. They cannot certify a theorem, source applicability, or
   absence of an earlier covering theorem. UPHELD; signed audits stay open.

## Reproduction

Run with the repository environment:

    E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_manuscript_source_audit.py

The run is stored under
claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-manuscript-source-audit/result.json.
It computes exact Q3 energies, mixed derivatives, threshold and mass scaling,
checks citations including optional theorem locators, and invokes the six
earlier manuscript checkers in memory. Historical outputs and frozen R-497
sources are preserved. Counts include structural/provenance checks.
An external reviewer should inspect the displayed analytic implications
independently of this script and attempt to falsify every hypothesis match.

## Remaining work

Complete the broader anisotropic comparison-theorem search, obtain signed
mathematical and literature reviews, capture all final source bytes including
Simon, make the bounded scope-admission decision, and replay on a clean frozen
snapshot. Only after content acceptance and final organization may the Q3LOCK
PDF be generated and visually reviewed. No sector or physical claim changes.
