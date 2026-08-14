# C6-BCC-PREMISE-BLOCKED legacy research view

<!-- AUTO-GENERATED. Gate closure requires current proof authorities. -->

Actionable reviewed records: **9**.

### LEG-MATH01 -- Single-mode BCC uniqueness lineage

Assessment: `partially-reusable` | role: `method` | re-validation: `waived`

Derive BCC selection inside a scalar single-mode Landau-Brazovskii reduction and identify its Voronoi cell.

Legacy conclusion: The note claimed BCC uniqueness within its restricted mode cone and connected the real-space BCC Voronoi cell to a truncated octahedron.

Sources:

- `Contents/Docs/math/TECT-Math01-v2-BCC-uniqueness-rigorous.tex.txt (compatibility copy: archive/legacy/notes/Math01/TECT-Math01-v2-BCC-uniqueness-rigorous.tex.txt)`

Achievements:

- Provides an explicit single-mode variational comparison and exact BCC Voronoi-cell geometry.

Negative or inconclusive findings:

- The calculation does not establish global selection over the current admissible class or a below-empty-reference sign.

Reusable elements:

- Exact BCC Voronoi/truncated-octahedron combinatorics
- Restricted-cone variational formulas

Boundary: This record does not establish BCC as the physical vacuum, a global minimum, or the origin of spacetime.

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

### LEG-MATH56 -- Guarded quotient and Hessian-jump audit lineage

Assessment: `partially-reusable` | role: `method` | re-validation: `waived`

Define acceptance guards that distinguish genuine BCC continuation solutions from numerical artifacts.

Legacy conclusion: Guarded residual, Hessian, and cutoff tests were proposed as a restricted continuation protocol.

Sources:

- `Contents/Docs/math/TECT-Math56-AddB-ClassII-guarded-quotient-analytical.tex.txt (compatibility copy: archive/legacy/notes/Math56/TECT-Math56-AddB-ClassII-guarded-quotient-analytical.tex.txt)`
- `Contents/Docs/math/TECT-Math56-HessJump-audit.tex.txt (compatibility copy: archive/legacy/notes/Math56/TECT-Math56-HessJump-audit.tex.txt)`
- `Contents/Docs/math/TECT-Math56-Addendum.tex.txt (compatibility copy: archive/legacy/notes/Math56/TECT-Math56-Addendum.tex.txt)`

Achievements:

- Separates several numerical false positives from admissible restricted-cone solutions.

Negative or inconclusive findings:

- The protocol does not turn a local Hessian eigenvalue into a thermodynamic or Yang-Mills mass gap.

Reusable elements:

- Residual and Hessian guard definitions
- Failure diagnostics for continuation

Boundary: No global vacuum selection or physical spectral gap follows.

### LEG-MATH82 -- BCC continuation curve and curvature-anchor audits

Assessment: `partially-reusable` | role: `provenance` | re-validation: `waived`

Track a seven-point BCC continuation branch and audit the solver stall and vacuum-floor guards.

Legacy conclusion: A positive local curvature anchor was reported on a restricted BCC branch, with Regime III unresolved.

Sources:

- `Contents/Docs/math/TECT-Math82-Addendum-G3-vacuum-floor-guard-implementation.tex.txt (compatibility copy: archive/legacy/notes/Math82/TECT-Math82-Addendum-G3-vacuum-floor-guard-implementation.tex.txt)`
- `Contents/Runs/continuation/math82H_groundstate_N32_Lbcc7_2026-04-24/MANIFEST.md (compatibility copy: archive/legacy/artefacts/Math82/math82H_groundstate_N32_Lbcc7_MANIFEST.md)`
- `Contents/Docs/math/TECT-Math82-Addendum-G-Phase-Z-7point-bifurcation-curve.tex.txt (compatibility copy: archive/legacy/notes/Math82/TECT-Math82-Addendum-G-Phase-Z-7point-bifurcation-curve.tex.txt)`
- `Contents/Docs/math/TECT-Math82-Addendum-G2-PCG-and-stall-mechanism-audit.tex.txt (compatibility copy: archive/legacy/notes/Math82/TECT-Math82-Addendum-G2-PCG-and-stall-mechanism-audit.tex.txt)`

Achievements:

- Preserves a fully hashed continuation manifest and a local positive-curvature data point.

Negative or inconclusive findings:

- The archived point has positive free-energy difference and is metastable relative to the reference; production re-execution remains waived.
- The deep Regime III branch was not resolved.

Reusable elements:

- Continuation provenance
- Vacuum-floor and stall diagnostics

Boundary: The local curvature anchor is not a physical vacuum, global stability theorem, or physical mass gap.

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

### LEG-T055-COMMON-BOHR-FDECL-001 -- T-055 reconstructed common-Bohr scalar moment and radial-owner revalidation

Assessment: `partially-reusable` | role: `counterevidence` | re-validation: `pass`

Revalidate a narrow nine-source legacy single-mode chain on one reconstructed common-Bohr owner and separate reusable arithmetic from nonapplicable finite-grid or full-Hartree interpretations.

Legacy conclusion: The sources contain reusable exact counting and polynomial-minimization machinery, but their physical hierarchy and collapse language mix coefficient, grid and variational-owner conventions and are not imported unchanged.

Sources:

- `Contents/Codes/supplementary/Math424_AddA_reading_uniqueness.py (compatibility copy: archive/legacy/scripts/Math424_AddA_reading_uniqueness.py)`
- `Contents/Docs/math/TECT-Math396-Math383-Numerical-NEAR-REFUTATION-BCC-Global-Min.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math396-Math383-Numerical-NEAR-REFUTATION-BCC-Global-Min.tex.txt.source.json)`
- `Contents/Codes/supplementary/Math396_AddA_symmetry_preserved.py (reference copy: archive/legacy/references/Codes/supplementary/Math396_AddA_symmetry_preserved.py.source.json)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_-1.0000_N32.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_-1.0000_N32.json)`
- `Contents/Codes/supplementary/Math400_AddE_brazovskii_one_loop.py (compatibility copy: archive/legacy/scripts/Math400_AddE_brazovskii_one_loop.py)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32_perturb.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32_perturb.json)`
- `Contents/Docs/math/TECT-Math399-Math383-Arithmetic-Audit-and-SMA-Hierarchy-Reversal.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math399-Math383-Arithmetic-Audit-and-SMA-Hierarchy-Reversal.tex.txt.source.json)`
- `Contents/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32.json (reference copy: archive/legacy/references/Runs/math396/math396_AddA_symmetry_mu2_+0.0050_N32.json)`
- `Contents/Docs/math/TECT-Math400-Math82-AddH-BCC-Refuted-Lamellar-Is-True-Vacuum.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math400-Math82-AddH-BCC-Refuted-Lamellar-Is-True-Vacuum.tex.txt.source.json)`

Achievements:

- Revalidates the exact signed-mode zero-sum counts N2, N4 and N6 for the declared LAM, HEX, FCC and BCC single-shell families.
- Derives the normalized reconstructed common-Bohr bare polynomials, exact production-endpoint values and derivatives, and the exact nonzero radial minima and ordering.
- Pins a narrow nine-source set, including the preserved Math396 runs, and classifies their finite periodic collapse as off-grid-confounded evidence that does not transfer to the exact on-shell common-Bohr owner.

Negative or inconclusive findings:

- The Math396 production wave numbers are not reciprocal modes of its finite periodic box, so its stored collapse is off-grid-confounded and is not exact on-shell Bohr or continuum evidence; this audit does not establish the sole cause of the collapse.
- The Math400 trial-mass construction belongs to a different quadratic/Hartree owner and is not substitutable for the on-shell Bohr coefficient.
- Bare radial negativity supplies neither a full Reading-H Hartree comparison nor an A1/P1 or physical-empty sign, transverse stability, candidate completeness, or controlled limits.

Reusable elements:

- Exact zero-sum mode-count enumeration
- Normalized moment-ratio conversion
- Cubic radial stationary-point algebra
- Finite-grid commensurability diagnostics

Boundary: Revalidation pass means that this narrow nine-source current audit and exact arithmetic passed. It does not revalidate the broad lineage, accept every legacy conclusion, identify the bare zero with physical empty space, establish a full Reading-H Hartree or A1/P1 minimizer, resurrect BCC selection, close C6, or close Pre-A.

### LEG-T055-TRUNCATED-OCTAHEDRON-BZ-001 -- T-055 truncated-octahedron Brillouin-zone and anisotropy method lineage

Assessment: `revalidate-required` | role: `method` | re-validation: `not-run`

Collect exact truncated-octahedron Brillouin-zone geometry, interval integration, cubic-harmonic, and anisotropy-suppression sources separately from physical BCC selection.

Legacy conclusion: The lineage offers potentially reusable geometry and interval methods, but many physical statements are conditional on a BCC lattice or H-suppression premise.

Sources:

- `Contents/Docs/math/TECT-Math_IR_Bound-v4-J1-lower-bound-tier3.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-J1-lower-bound-tier3.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-final-formalization.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-final-formalization.tex.txt)`
- `Contents/Codes/supplementary/Math57_shell_angular_interval.py (reference copy: archive/legacy/references/Codes/supplementary/Math57_shell_angular_interval.py)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-BZ-integrator.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-BZ-integrator.tex.txt)`
- `Contents/Codes/supplementary/Math_IR_Bound_v4_BZ_interval.py (reference copy: archive/legacy/references/Codes/supplementary/Math_IR_Bound_v4_BZ_interval.py)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-peer-review-audit.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-peer-review-audit.tex.txt)`
- `Contents/Docs/math/TECT-Math57-AddA-Pillar2-Shell-Isotropy.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math57-AddA-Pillar2-Shell-Isotropy.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-anisotropy-separation.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-anisotropy-separation.tex.txt)`
- `Contents/Docs/math/TECT-Math57-v2-Pillar2-Inertia-RG.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math57-v2-Pillar2-Inertia-RG.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-shell-adaptive.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-shell-adaptive.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-3.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-3.tex.txt)`
- `Contents/Docs/math/TECT-Math57-Pillar2-Inertia-RG.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math57-Pillar2-Inertia-RG.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-PC-3A-L6-closure-attempt.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-PC-3A-L6-closure-attempt.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-1.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-1.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-H-suppression-closure.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-H-suppression-closure.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-outline.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-outline.tex.txt)`
- `Contents/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-L6-suppression-rigorous.tex.txt (reference copy: archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-L6-suppression-rigorous.tex.txt)`
- `Contents/Codes/supplementary/Math57_v2_cubic_anisotropy_interval.py (reference copy: archive/legacy/references/Codes/supplementary/Math57_v2_cubic_anisotropy_interval.py)`

Achievements:

- Preserves the BZ integrator, interval scripts, shell-isotropy analysis, formalization chain, and peer-review audit as one method package.

Negative or inconclusive findings:

- Exact truncated-octahedron geometry does not imply that Nature selects that cell.
- Cubic symmetry cancellations and anisotropy bounds do not discharge the current BCC premise, common-cone, or physical-vacuum gates.

Reusable elements:

- Exact truncated-octahedron support/radial geometry
- Interval BZ integration
- Cubic-harmonic representation filters
- Anisotropy error bounds

Boundary: This method lineage does not prove a truncated-octahedron vacuum, emergent spacetime, mono-metricity, Lorentz invariance, or a below-empty-reference energy sign.
