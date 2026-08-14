# B3-BCC-STRUCT legacy research view

<!-- AUTO-GENERATED. Current claim cards remain authoritative. -->

Current claim: **BCC structural selection among tested ordered condensates** | tier `T0` | lifecycle `REFUTED`.

Linked reviewed records: **4**.

### LEG-MATH194 -- Crystallographic competitor ranking refutation

Assessment: `refuted` | role: `counterevidence` | re-validation: `fail`

Rank ten single-shell crystallographic competitors and argue for BCC uniqueness.

Legacy conclusion: The prose claimed BCC uniqueness, but the executable ranking places BCC ninth and lamellar first.

Sources:

- `Contents/Docs/math/TECT-Math194-BCC-uniqueness-among-3D-crystallographic-competitors.tex.txt (compatibility copy: archive/legacy/notes/Math194/TECT-Math194-BCC-uniqueness-among-3D-crystallographic-competitors.tex.txt)`
- `Contents/Codes/supplementary/Math194_brazovskii_lattice_ranking.py (compatibility copy: archive/legacy/scripts/Math194_brazovskii_lattice_ranking.py)`

Achievements:

- Supplies a reproducible competitor table that functions as direct counterevidence.

Negative or inconclusive findings:

- Fresh execution refutes the note's own BCC-uniqueness interpretation.

Reusable elements:

- Competitor enumeration
- Regression fixture for verdict-versus-number consistency

Boundary: Neither this refutation nor its finite competitor list proves which structure is the physical vacuum.

### LEG-MATH383 -- One-mode BCC coefficient lineage refuted by Math400

Assessment: `refuted` | role: `counterevidence` | re-validation: `fail`

Use one-mode interaction coefficients to claim BCC dominance over competitor patterns.

Legacy conclusion: The main BCC-selection conclusion and part of the coefficient table were later refuted by Math400.

Sources:

- `Contents/Docs/math/TECT-Math383-BCC-vs-Competitors-Analytical-and-Numerical.tex.txt (compatibility copy: archive/legacy/notes/Math383/TECT-Math383-BCC-vs-Competitors-Analytical-and-Numerical.tex.txt)`

Achievements:

- Provides a clear historical hypothesis and coefficients that can be regression-tested.

Negative or inconclusive findings:

- The claimed coefficient ordering and global BCC conclusion do not survive the corrected calculation.

Reusable elements:

- Historical coefficient table as a hostile test fixture

Boundary: The corrected refutation removes a BCC premise but does not select an alternative physical vacuum.

### LEG-MATH400 -- Corrected Brazovskii one-loop dependency and BCC refutation

Assessment: `reusable` | role: `counterevidence` | re-validation: `pass`

Supply corrected one-loop calculations used by the kernel chain and reassess claimed BCC selection.

Legacy conclusion: The executable is a dependency for surviving scoped results and counterevidence against the old BCC global-minimum claim.

Sources:

- `Contents/Codes/supplementary/Math400_AddE_brazovskii_one_loop.py (compatibility copy: archive/legacy/scripts/Math400_AddE_brazovskii_one_loop.py)`

Achievements:

- Corrects interaction coefficients and exposes the canonical BCC point as a saddle in the tested reduction.

Negative or inconclusive findings:

- Refutes the Math383 BCC-selection conclusion within the tested model.

Reusable elements:

- Corrected coefficient engine
- BCC saddle diagnostic

Boundary: This calculation refutes one BCC route but does not prove a different physical vacuum or continuum theory.

### LEG-T055-BCC-SELECTION-LINEAGE-001 -- T-055 legacy BCC global-selection, hostile-audit, and refutation lineage

Assessment: `revalidate-required` | role: `counterevidence` | re-validation: `not-run`

Collect the claimed global 12-star BCC closure, its hostile audits, numerical reversals, corrected arithmetic, and later one-loop branches in one gate-sized lineage.

Legacy conclusion: The source set contains mutually incompatible positive and negative BCC verdicts; current records already establish that the old unconditional BCC premise cannot be restored by citation alone.

Sources:

- `Contents/Docs/math/TECT-Math320-AddB-Turn3-Computational-Verification-Bezout-Bound.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn3-Computational-Verification-Bezout-Bound.tex.txt)`
- `Contents/Runs/math400/math400_AddE_brazovskii_sweep_-2.0to0.5.json (reference copy: archive/legacy/references/Runs/math400/math400_AddE_brazovskii_sweep_-2.0to0.5.json)`
- `Contents/Docs/math/TECT-Math400-AddE-AddA-Two-Loop-Brazovskii-Path-Alpha-Robust.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddE-AddA-Two-Loop-Brazovskii-Path-Alpha-Robust.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn8-Consolidation-and-Final-Status.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn8-Consolidation-and-Final-Status.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn6-Algebraic-Closure-via-Groebner-Systems.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn6-Algebraic-Closure-via-Groebner-Systems.tex.txt)`
- `Contents/Docs/math/TECT-Math400-AddD-Lattice-Enumeration-Rejected-Naturalness-h-Effects-Brazovskii-Audit.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddD-Lattice-Enumeration-Rejected-Naturalness-h-Effects-Brazovskii-Audit.tex.txt.source.json)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn1-Geometric-Fiber-Circle-Bound-on-r_v.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn1-Geometric-Fiber-Circle-Bound-on-r_v.tex.txt)`
- `Contents/Docs/math/TECT-Math396-Math383-Numerical-NEAR-REFUTATION-BCC-Global-Min.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math396-Math383-Numerical-NEAR-REFUTATION-BCC-Global-Min.tex.txt.source.json)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn5-Second-Order-Audit-Turns1-4.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn5-Second-Order-Audit-Turns1-4.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn11-20-Session-Summary-and-Final-Verdict.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn11-20-Session-Summary-and-Final-Verdict.tex.txt)`
- `Contents/Docs/math/TECT-Math400-AddA-Cosmological-Isotropy-Filter-Rejects-Lamellar.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddA-Cosmological-Isotropy-Filter-Rejects-Lamellar.tex.txt.source.json)`
- `Contents/Codes/supplementary/Math396_AddA_symmetry_preserved.py (reference copy: archive/legacy/references/Codes/supplementary/Math396_AddA_symmetry_preserved.py.source.json)`
- `Contents/Docs/math/TECT-Math320-BCC-Global-12-Star-Optimality-Closure.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-BCC-Global-12-Star-Optimality-Closure.tex.txt)`
- `Contents/Docs/math/TECT-Math400-AddB-N64-Tighter-All-Local-Minima-FCC-Deepest-Among-Cubic.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddB-N64-Tighter-All-Local-Minima-FCC-Deepest-Among-Cubic.tex.txt)`
- `Contents/Docs/math/TECT-Math400-AddC-Extended-Candidates-and-Condensate-Free-Scenarios.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddC-Extended-Candidates-and-Condensate-Free-Scenarios.tex.txt.source.json)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_-1.0000_N32.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_-1.0000_N32.json)`
- `Contents/Runs/math400/math400_AddE_brazovskii_mu2_+0.0050.json (reference copy: archive/legacy/references/Runs/math400/math400_AddE_brazovskii_mu2_+0.0050.json)`
- `Contents/Codes/supplementary/Math320_AddB_Turn3_Groebner_Fiber_Verification.py (reference copy: archive/legacy/references/Codes/supplementary/Math320_AddB_Turn3_Groebner_Fiber_Verification.py)`
- `Contents/Codes/supplementary/Math320_global_12star_optimality.py (reference copy: archive/legacy/references/Codes/supplementary/Math320_global_12star_optimality.py)`
- `Contents/Docs/math/TECT-Math339-BCC-Global-12-Star-Optimality-Final-Consolidation.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math339-BCC-Global-12-Star-Optimality-Final-Consolidation.tex.txt)`
- `Contents/Codes/supplementary/Math400_AddE_brazovskii_one_loop.py (compatibility copy: archive/legacy/scripts/Math400_AddE_brazovskii_one_loop.py)`
- `Contents/Docs/math/TECT-Math320-AddA-Hostile-Audit-Acknowledgment-Status-Downgrade.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddA-Hostile-Audit-Acknowledgment-Status-Downgrade.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn4-Direct-Enumeration-Quadruple-Count.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn4-Direct-Enumeration-Quadruple-Count.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn7-Cauchy-Rigidity-for-L2-Closure.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn7-Cauchy-Rigidity-for-L2-Closure.tex.txt)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32_perturb.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32_perturb.json)`
- `Contents/Docs/math/TECT-Math399-Math383-Arithmetic-Audit-and-SMA-Hierarchy-Reversal.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math399-Math383-Arithmetic-Audit-and-SMA-Hierarchy-Reversal.tex.txt.source.json)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32.json)`
- `Contents/Docs/math/TECT-Math400-AddE-One-Loop-Brazovskii-Self-Consistency-PATH-ALPHA-CONFIRMED.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddE-One-Loop-Brazovskii-Self-Consistency-PATH-ALPHA-CONFIRMED.tex.txt.source.json)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn2-Algebraic-Closure-of-Fiber-Intersection.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn2-Algebraic-Closure-of-Fiber-Intersection.tex.txt)`
- `Contents/Docs/math/TECT-Math400-AddF-N64-Canonical-mu2-0p005-BCC-Stable-FCC-Saddle.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-AddF-N64-Canonical-mu2-0p005-BCC-Stable-FCC-Saddle.tex.txt)`
- `Contents/Docs/math/TECT-Math320-AddB-Turn9-10-Status-Propagation-Roadmap.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math320-AddB-Turn9-10-Status-Propagation-Roadmap.tex.txt)`
- `Contents/Docs/math/TECT-Math400-Math82-AddH-BCC-Refuted-Lamellar-Is-True-Vacuum.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-Math82-AddH-BCC-Refuted-Lamellar-Is-True-Vacuum.tex.txt.source.json)`

Achievements:

- Preserves the complete initial source set, proof attempts, hostile audits, corrected coefficient calculations, scripts, and available run JSONs for one comparison.

Negative or inconclusive findings:

- The Archimedean/completeness step in the global 12-star route requires re-audit.
- Math396/399/400 contain reversal and refutation evidence that must be reconciled with earlier positive verdicts.
- No source has yet been accepted as closing the current same-Hamiltonian candidate-minus-empty-reference inequality.

Reusable elements:

- Groebner and finite-enumeration proof attempts
- Hostile competitor scripts
- Symmetry-preserving and one-loop counterexamples
- Available run artifacts

Boundary: This intake does not revive or newly refute every BCC model, select an alternative vacuum, prove a truncated-octahedron microstructure, or close T-055/C6.

## No-overclaim

This generated view is a retrieval surface. It cannot change the current claim tier, lifecycle, scope, dependencies, or open gates.
