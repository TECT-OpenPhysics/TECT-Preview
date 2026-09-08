# Q3LOCK remaining-block reread and source-delimiter repair

Date: 2026-09-08. Internal review, not signed mathematical acceptance.
The research authority is EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
Tier T0, claim_bearing=false, RESEARCH_ONLY and PDF DEFERRED are unchanged.

## Reviewed snapshot and exact edit boundary

Two read-only AI reviewers independently inspected the parts not covered by
the preceding EXP-001684 split. Both used manuscript SHA-256
3b119cce87d3e80c72abee6d224cc91afdc48563ad74e0659e309e313aed0b51.
Neither reported a confirmed local mathematical defect in its assigned block.
No new theorem, counterexample, signed disposition, or gate closure follows.

Separate source inspection found bare infinity commands outside math mode in
the Schneider--Beck--Stoll comparison table and prose (lines 2251 and 2271).
The exact expression n=1,2,infinity was enclosed in inline math in both places.
The draft version changed from 0.1.37 to 0.1.38. No Hamiltonian, proof formula,
quantifier, citation role, source limit, threshold, or nonclaim was changed.
The resulting manuscript SHA-256 is
3d72ab56074d8c4ca8c4f078eb669f4ef631cf9516f343050d8002df64b8d13d.

## Bounded mathematical rereads

| Block and original line range | Independently checked points | Boundary |
|---|---|---|
| Finite forms and mesh, 117-520 | Upper residual truncation uses harmonic, not uniform quartic, control; variational resolvent limit; cyclic determinant, covariance normalization and fixed-volume tightness; compact-uniform Riemann weights and positive normalizers | Fixed spatial volume in the mesh passage; not a spatially uniform loop-moment theorem |
| Feynman--Kac and sources, 521-652 | Simon Theorem 1.1 bounded-below continuous potential; unitary mass scaling; harmonic kernel domination, trace normalization and source exponential moments; entire partition versus real-analytic pressure | Theorem 1.2 is not substituted; no final external applicability signature |
| Pressure, 654-807 | Bond-deletion min--max direction, rectangular tiling remainder, two-sided volume bounds, seam coefficient 288, moving-beta secants and derivative squeeze at differentiability points | No derivative convergence asserted at the zero-source cusp |
| Hilbert reflection positivity, 1352-1434 | Finite local measure without double allocating the spatial diagonal; positive Hilbert Gaussian kernel; bounded Borel tests via pushed-forward signed measures; two crossing planes on even L >= 4 | L=2 is outside this theorem sequence; arbitrary interior-dependent tests remain included |
| FSS and loop source transfer, 1439-1560 | Common arbitrary nonradial finite-mesh prior with quadratic exponential moments; spatial diagonal included in this representation; Poisson source and c-scaling; exact polygonal source integral and exponential UI | Fixed-mesh theorem first, fixed-volume loop passage second; no mesh-uniform prior-moment hypothesis is added |
| Infrared and singular sum, 1565-1658 | Duhamel/time factors, Laplacian symbol 2E(p), real/imaginary Fourier tests, excluded zero mode, continuous and discrete 3D tail bounds | Nonconstant-mode upper bound and zero-mode subtraction only; positivity of the zero-mode lower bound comes from the separate collective argument |

The reviewers consulted [Simon Theorem 1.1](https://arxiv.org/pdf/math-ph/9907022v1)
and [FSS Section 2](https://math.caltech.edu/SimonPapers/65.pdf) in primary
sources. The FSS check in this reread used extracted source text, not a new
visual inspection of its page images. Existing source-capture records are
not replaced. The prior EXP-001684 report covers DLR/FKG and collective/cusp;
combining bounded AI reports still does not create an external signature.

## Source-only regression and adversarial limits

The new test module is
verification/tests/test_q3lock_manuscript_math_delimiters.py. It recognizes
the math delimiters and environments used in this manuscript, flags a bare
infinity command in text, and tests comments, escaped dollars, nested math
environments, and unmatched delimiters. The two real defects were reproduced
before editing. After editing, all five test methods pass; deliberately
removing the two repairs reproduces two located faults.

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 -m unittest discover -s verification/tests -p test_q3lock_manuscript_math_delimiters.py -v
```

This is a bounded lexical regression, not a general TeX interpreter, macro
expansion checker, successful compilation, visual inspection, or proof test.
It never invokes a TeX engine or writes a PDF. External readers are invited
to run it and challenge its coverage.

- Objection: a lexical PASS certifies TeX compilation or layout. UPHELD as a
  limitation; those final checks are explicitly deferred, not simulated.
- Objection: ignored comments or escaped dollars can hide the reported fault.
  DISMISSED for the supported fixtures; comments and escaped-dollar controls
  are tested, and both actual manuscript regressions are reconstructed.
- Objection: the count two is a hidden mathematical constant. DISMISSED;
  it is a labelled regression oracle for two observed source faults, not a
  physical input, threshold, or mathematical proof output.
- Objection: repeated AI rereads close independent-review obligations.
  UPHELD as a limitation; no A1-A23 disposition or reviewer response is signed.

## Current evidence and next gate

The source-review-v1 replay family is a new no-overwrite tooling snapshot of
the edited source. Its result JSON files record the actual replay outcomes;
the earlier portability-v1 and collective-Jensen results remain history.
The manuscript's mathematical content is unchanged by the source repair.

The inspected proof-audit response block and external-review handoff still
have blank reviewer identity, disposition and signature fields. Submission
readiness R12 and R13 are OPEN; R9/R10 final content/hash freeze is NOT STARTED.
The current main theorem explicitly remains a conditional composition of
upstream analytic inputs. This is not the requested final accepted theorem.

The remaining acceptance step requires a completed, attributable independent
mathematical review and a specialist literature disposition, with exact
source/equation findings and any resulting repairs. After those responses,
recheck affected proofs, make the final clean snapshot and hash freeze, and
only then build/render-review the PDF. More unchanged-status reports or
cosmetic checkpoint refreshes are not a substitute for those missing inputs.
