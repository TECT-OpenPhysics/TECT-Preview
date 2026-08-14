# Sector B legacy research -- Vacuum / Reading Selection

<!-- AUTO-GENERATED. Legacy material is not current proof. -->

Linked reviewed records: **21**.

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

### LEG-MATH427 -- Diagonal Gaussian isotropy theorem and audit

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Test whether diagonal Gaussian trial variation can lower the isotropic comparison state.

Legacy conclusion: The restricted diagonal trial class retains the isotropic infimum almost everywhere.

Sources:

- `Contents/Docs/math/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec.tex.txt (compatibility copy: archive/legacy/notes/Math427/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec.tex.txt)`
- `Contents/Codes/supplementary/Math427_g1prime_diagonal_isotropy.py (compatibility copy: archive/legacy/scripts/Math427_g1prime_diagonal_isotropy.py)`
- `Contents/Docs/math/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math427/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec-260604-v1.1.tex.txt)`
- `Contents/Runs/math/Math427/g1prime_diagonal_isotropy.json (compatibility copy: archive/legacy/artefacts/Math427/g1prime_diagonal_isotropy.json)`

Achievements:

- Fresh migration execution passed 5/5 checks.

Negative or inconclusive findings:

- The result does not cover off-diagonal, non-Gaussian, or full physical-vacuum competitors.

Reusable elements:

- Variational isotropy reduction
- Five-check regression script

Boundary: Restricted isotropy is not global vacuum selection.

### LEG-MATH428 -- Continuum-anchored BCC Bloch log-determinant race

Assessment: `reusable` | role: `method` | re-validation: `pass`

Audit a finite-basis sign artifact in a BCC Bloch log-determinant comparison.

Legacy conclusion: The continuum-anchored estimator passed within its registered error bands.

Sources:

- `Contents/Docs/math/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored.tex.txt (compatibility copy: archive/legacy/notes/Math428/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored.tex.txt)`
- `Contents/Codes/supplementary/Math428_g1doubleprime_bloch_logdet.py (compatibility copy: archive/legacy/scripts/Math428_g1doubleprime_bloch_logdet.py)`
- `Contents/Runs/math/Math428/g1doubleprime_bloch_logdet.json (compatibility copy: archive/legacy/artefacts/Math428/g1doubleprime_bloch_logdet.json)`
- `Contents/Docs/math/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math428/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored-260604-v1.1.tex.txt)`

Achievements:

- Fresh migration execution passed 21/21 checks and reproduced the archived JSON.

Negative or inconclusive findings:

- The result is estimator-grade and does not prove BCC or Reading-H beats an empty/disordered reference.

Reusable elements:

- Finite-basis artifact diagnostic
- Log-determinant comparison code

Boundary: This is not BCC structural selection, a global minimum, or a physical-vacuum theorem.

### LEG-MATH429 -- Inhomogeneous exact-Wick scan

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Replace a uniform-Wick boundary test by an inhomogeneous exact-Wick scan.

Legacy conclusion: The tested inhomogeneous family did not overturn the registered Reading-H comparison.

Sources:

- `Contents/Docs/math/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math429/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.0.tex.txt)`
- `Contents/Runs/math/Math429/g1pp1prime_inhomwick.json (compatibility copy: archive/legacy/artefacts/Math429/g1pp1prime_inhomwick.json)`
- `Contents/Codes/supplementary/Math429_g1pp1prime_inhomogeneous_wick.py (compatibility copy: archive/legacy/scripts/Math429_g1pp1prime_inhomogeneous_wick.py)`
- `Contents/Docs/math/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math429/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.1.tex.txt)`

Achievements:

- Fresh migration execution passed 19/19 checks.

Negative or inconclusive findings:

- Only the declared finite scan and Wick family were tested.

Reusable elements:

- Inhomogeneous covariance scan

Boundary: A finite inhomogeneous scan is not exhaustive vacuum selection.

### LEG-MATH430 -- Dense-surface convergence test

Assessment: `reusable` | role: `method` | re-validation: `pass`

Check a dense finite parameter surface and cutoff convergence against an analytic small-amplitude bound.

Legacy conclusion: The sampled surface passed and its minimum agreed with the analytic restricted-family bound.

Sources:

- `Contents/Codes/supplementary/Math430_g1pp2_dense_surface_convergence.py (compatibility copy: archive/legacy/scripts/Math430_g1pp2_dense_surface_convergence.py)`
- `Contents/Runs/math/Math430/g1pp2_surface_convergence.json (compatibility copy: archive/legacy/artefacts/Math430/g1pp2_surface_convergence.json)`
- `Contents/Docs/math/TECT-Math430-G1pp2-Dense-Surface-Convergence-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math430/TECT-Math430-G1pp2-Dense-Surface-Convergence-PASS-260604-v1.0.tex.txt)`

Achievements:

- Fresh migration execution passed 11/11 checks.

Negative or inconclusive findings:

- Dense sampling is not a class theorem or continuum error proof.

Reusable elements:

- Convergence regression and surface sampler

Boundary: Sampling density does not prove exhaustiveness or physical-vacuum selection.

### LEG-MATH431 -- LAM, HEX, and FCC enumerated races

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Compare Reading-H against three named ordered competitor channels.

Legacy conclusion: All tested channels passed under the declared estimators and parameter bounds.

Sources:

- `Contents/Docs/math/TECT-Math431-G1pp3-LAM-HEX-FCC-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math431/TECT-Math431-G1pp3-LAM-HEX-FCC-PASS-260604-v1.0.tex.txt)`
- `Contents/Runs/math/Math431/g1pp3_lam_hex_fcc.json (compatibility copy: archive/legacy/artefacts/Math431/g1pp3_lam_hex_fcc.json)`
- `Contents/Codes/supplementary/Math431_g1pp3_lam_hex_fcc.py (compatibility copy: archive/legacy/scripts/Math431_g1pp3_lam_hex_fcc.py)`

Achievements:

- Fresh migration execution passed 15/15 checks.

Negative or inconclusive findings:

- LAM and HEX remain estimator-grade and the candidate list is not exhaustive.

Reusable elements:

- Named-competitor fixtures and comparison code

Boundary: Relative tested-candidate ranking does not show Reading-H is below the empty/disordered reference.

### LEG-MATH432 -- Two-shell enumerated ensemble race

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Extend the tested Reading-H comparison to a declared two-shell ensemble.

Legacy conclusion: The enumerated two-shell race passed under mandatory qualifiers.

Sources:

- `Contents/Docs/math/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math432/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.0.tex.txt)`
- `Contents/Codes/supplementary/Math432_g3prime_multishell_ensemble.py (compatibility copy: archive/legacy/scripts/Math432_g3prime_multishell_ensemble.py)`
- `Contents/Docs/math/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math432/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.1.tex.txt)`
- `Contents/Runs/math/Math432/g3prime_multishell_ensemble.json (compatibility copy: archive/legacy/artefacts/Math432/g3prime_multishell_ensemble.json)`

Achievements:

- Fresh migration execution passed 25/25 checks.

Negative or inconclusive findings:

- No exhaustiveness theorem covers arbitrary multi-shell or multi-condensate states.

Reusable elements:

- Two-shell generator and comparison fixture

Boundary: The finite two-shell result does not close the full admissible class or the empty-reference sign.

### LEG-MATH434 -- Reading-H independent audit and legacy promotion record

Assessment: `reusable` | role: `provenance` | re-validation: `pass`

Audit the enumerated Reading-H evidence chain and record the legacy scoped promotion decision.

Legacy conclusion: The independent attack tasks passed within the enumerated/estimator scope; the promotion record added no new mathematics.

Sources:

- `Contents/Runs/math/Math434/state.json (compatibility copy: archive/legacy/artefacts/Math434/state.json)`
- `Contents/Docs/math/TECT-Math434-AddA-T5-Promotion-Record-ReadingH-Selection-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math434/TECT-Math434-AddA-T5-Promotion-Record-ReadingH-Selection-260604-v1.0.tex.txt)`
- `Contents/Runs/math/Math434/lam_exact_wick_bracket.json (compatibility copy: archive/legacy/artefacts/Math434/lam_exact_wick_bracket.json)`
- `Contents/Docs/math/TECT-Math434-Section15p5-Independent-Audit-ReadingH-T5-Candidacy-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math434/TECT-Math434-Section15p5-Independent-Audit-ReadingH-T5-Candidacy-PASS-260604-v1.0.tex.txt)`
- `Contents/Codes/supplementary/Math434_lam_exact_wick_bracket.py (compatibility copy: archive/legacy/scripts/Math434_lam_exact_wick_bracket.py)`

Achievements:

- Fresh migration execution passed 22/22 checks and preserved checkpoint state.

Negative or inconclusive findings:

- The audit explicitly does not establish exhaustiveness or a physical vacuum.

Reusable elements:

- Independent audit checklist
- Exact-Wick lamellar bracket

Boundary: The legacy promotion wording cannot override the current TSv2 claim cards or physical-empty-reference gate.

### LEG-MATH436 -- HEX exact-Wick transverse-continuum bracket

Assessment: `reusable` | role: `candidate-support` | re-validation: `pass`

Replace the HEX estimator bracket by an exact-Wick transverse-continuum calculation.

Legacy conclusion: The declared HEX channel passed after the exact-Wick correction.

Sources:

- `Contents/Docs/math/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.0.tex.txt (compatibility copy: archive/legacy/notes/Math436/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.0.tex.txt)`
- `Contents/Docs/math/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.1.tex.txt (compatibility copy: archive/legacy/notes/Math436/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.1.tex.txt)`
- `Contents/Runs/math/Math436/state.json (compatibility copy: archive/legacy/artefacts/Math436/state.json)`
- `Contents/Codes/supplementary/Math436_hex_exact_wick_bracket.py (compatibility copy: archive/legacy/scripts/Math436_hex_exact_wick_bracket.py)`
- `Contents/Runs/math/Math436/hex_exact_wick_bracket.json (compatibility copy: archive/legacy/artefacts/Math436/hex_exact_wick_bracket.json)`

Achievements:

- Fresh migration execution passed 49/49 checks; both the result and checkpoint state are preserved.

Negative or inconclusive findings:

- The result is channel-specific and not a global structure theorem.

Reusable elements:

- Exact-Wick HEX calculation
- Checkpoint-resumable verification

Boundary: The HEX channel result does not establish a complete competitor class or physical-vacuum sign.

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
