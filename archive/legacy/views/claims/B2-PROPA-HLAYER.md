# B2-PROPA-HLAYER legacy research view

<!-- AUTO-GENERATED. Current claim cards remain authoritative. -->

Current claim: **Proposition A: the isotropic Gaussian-Hartree layer is the strict comparison infimum (T7, H-LAYER discharged)** | tier `T7` | lifecycle `ACTIVE`.

Linked reviewed records: **8**.

### LEG-MATH374 -- Canonical BCC Hessian dependency

Assessment: `reusable` | role: `dependency` | re-validation: `not-applicable`

Provide a shared Hessian implementation imported by later verification scripts.

Legacy conclusion: The code is an executable dependency rather than an independent physical conclusion.

Sources:

- `Contents/Codes/supplementary/Math374_canonical_BCC_hessian.py (compatibility copy: archive/legacy/scripts/Math374_canonical_BCC_hessian.py)`

Achievements:

- Preserves a byte-exact runnable dependency used by revalidated batches.

Negative or inconclusive findings:

- None recorded.

Reusable elements:

- Canonical Hessian implementation

Boundary: Import success is not an independent theorem or physical validation.

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

### LEG-MATH424 -- Reading-H uniqueness implementation dependency

Assessment: `reusable` | role: `dependency` | re-validation: `not-applicable`

Provide shared functions imported by the kernel and H-layer verification scripts.

Legacy conclusion: The script is preserved as a dependency; its interpretation is controlled by the consuming current claims.

Sources:

- `Contents/Codes/supplementary/Math424_AddA_reading_uniqueness.py (compatibility copy: archive/legacy/scripts/Math424_AddA_reading_uniqueness.py)`

Achievements:

- Keeps the archived verification chain runnable without replacing it by a mimic.

Negative or inconclusive findings:

- None recorded.

Reusable elements:

- Reading comparison helper functions

Boundary: The dependency alone does not establish Reading-H as the physical vacuum.

### LEG-MATH437 -- Pattern-universal isotropic H-layer restoration

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Prove a pattern-free lower bound for the declared Gaussian-Hartree comparison layer.

Legacy conclusion: The repaired v1.2 argument certifies the isotropic comparison infimum under its pinned hypotheses.

Sources:

- `Contents/Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.0.tex.txt)`
- `Contents/Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.1.tex.txt)`
- `Contents/Runs/math/Math437/step5_class_closure.json (compatibility copy: archive/legacy/artefacts/Math437/step5_class_closure.json)`
- `Contents/Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt (compatibility copy: archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt)`
- `Contents/Codes/supplementary/Math437_step5_class_closure.py (compatibility copy: archive/legacy/scripts/Math437_step5_class_closure.py)`
- `Contents/Docs/math/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math441/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt)`
- `Contents/Docs/math/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt)`

Achievements:

- Fresh migration execution passed 91/91 checks; the repaired proof chain is preserved.

Negative or inconclusive findings:

- The archived run JSON contains a stale verdict string; current fresh claim-run output is canonical.

Reusable elements:

- Pattern-free dip bound
- Repaired all-m-positive proof

Boundary: An H-layer comparison infimum is not full physical-vacuum selection or a below-empty-reference theorem.

### LEG-MATH440 -- Second-wave consolidated audit

Assessment: `partially-reusable` | role: `provenance` | re-validation: `pass`

Adversarially audit the Math435--438 second-wave chain.

Legacy conclusion: The audit was partial: the Proposition A conclusion survived, but this note did not certify the claimed tier by itself.

Sources:

- `Contents/Docs/math/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math440/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt)`
- `Contents/Codes/supplementary/Math440_audit_secondwave_recheck.py (compatibility copy: archive/legacy/scripts/Math440_audit_secondwave_recheck.py)`
- `Contents/Runs/math/Math440/audit_recheck.json (compatibility copy: archive/legacy/artefacts/Math440/audit_recheck.json)`

Achievements:

- Fresh migration execution passed 75/75 mechanical checks and identified the exact documentation repair debt.

Negative or inconclusive findings:

- Audit status remained PARTIAL until the Math441/442 repair and certification sequence.

Reusable elements:

- Independent attack checklist
- Second-wave recheck script

Boundary: A partial audit cannot independently certify B2 or any physical conclusion.

### LEG-MATH441 -- Math437 repair second look

Assessment: `partially-reusable` | role: `provenance` | re-validation: `not-applicable`

Verify the mathematical repair requested by the Math440 audit and isolate remaining documentation fixes.

Legacy conclusion: The mathematical repair was judged complete, while the record remained partial pending two named documentation fixes.

Sources:

- `Contents/Docs/math/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math441/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt)`

Achievements:

- Separates mathematical repair from documentation and certification status.

Negative or inconclusive findings:

- This note deliberately did not issue final certification.

Reusable elements:

- Repair-completeness audit

Boundary: Repair verification is not a new theorem or tier action.

### LEG-MATH442 -- Legacy Proposition A certification record

Assessment: `context-only` | role: `provenance` | re-validation: `not-applicable`

Close the documentation and operator-certification step after the Math437 repair lineage.

Legacy conclusion: The note recorded certification at the legacy scoped grade and added no new mathematics.

Sources:

- `Contents/Docs/math/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt)`

Achievements:

- Preserves the exact endpoint and scope wording of the historical audit chain.

Negative or inconclusive findings:

- A historical certification record cannot override current TSv2 scope or later falsifiers.

Reusable elements:

- Certification provenance

Boundary: This note is not independent evidence and does not establish physical vacuum selection.

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

## No-overclaim

This generated view is a retrieval surface. It cannot change the current claim tier, lifecycle, scope, dependencies, or open gates.
