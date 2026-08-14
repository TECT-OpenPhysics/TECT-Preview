# B4-MASS-GAP legacy research view

<!-- AUTO-GENERATED. Current claim cards remain authoritative. -->

Current claim: **BCC ground-state uniqueness within the single-mode constraint cone** | tier `T1` | lifecycle `ACTIVE`.

Linked reviewed records: **3**.

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

## No-overclaim

This generated view is a retrieval surface. It cannot change the current claim tier, lifecycle, scope, dependencies, or open gates.
