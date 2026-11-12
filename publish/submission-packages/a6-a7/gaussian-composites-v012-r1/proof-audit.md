# Internal proof audit and correction record

Date: 2026-11-12. Audit covers editions0.1.0--0.1.2 in the fixed Gaussian scope.
Current review: read-only independent AI reconstruction. Energy review:
read-only independent AI reconstruction. Literature review: primary-source
crosswalk. These are not human external mathematical or novelty reviews.

## Findings applied to the independent draft

1. VALID, repaired: the historical A6 fixed-mode O(N^-3) display is not a
   consequence of arbitrary bounded pointwise-convergent multipliers. A slow
   common amplitude preserves admissibility and violates that universal rate.
   The draft proves qualitative convergence and an extracted a.s. subsequence.
2. VALID, repaired: the full paracontrolled reconstruction needs its explicit
   commutator and polynomial-moment localization. Both are printed with the
   required 2alpha-1<0<3alpha-1 inequalities and spatial/fiber dimensions.
3. VALID, repaired: an auxiliary correlated-field regulator anomaly does not
   demonstrate necessity of the regulator class for the production covariance.
   The draft uses the class as sufficient and makes no stronger inference.
4. VALID, repaired: one-parameter Gaussian rough-path references do not supply
   an unchecked Stratonovich identification for this three-dimensional current.
5. VALID, repaired: the A7 weighted covariance convergence was compressed.
   The draft proves strong Q in L2(G_sdx), P/R in L4(G_sdx), product L1
   convergence and coefficient-expectation convergence before polarization.
6. VALID, repaired: the leading mass slope alone does not justify a uniform
   O(1) finite-cutoff repair. The draft states a leading compensation slope
   and explicitly separates the exact covariance prescription.
7. VALID, repaired: deterministic b is an18-by-18 derivative-bundle matrix;
   the application is I3 tensor B(u), and the operator covariance and scalar
   counterterm use different notation. The determinant HS continuity argument
   and L-infinity norm are explicit.
8. VALID, repaired: bibliography metadata mixed a 2010 Friz--Victoir journal
   article with a different 2007 preprint; the Chandra--Hairer journal assignment
   was not verified. Primary-source metadata now replaces both.
9. VALID, repaired before compilation: two TeX escape defects in the initial
   symbol and determinant displays were identified and corrected.
10. VALID, clarified in edition0.1.1: Xu Theorem1.4 already treats suitable
    nonpolynomial Gaussian functionals. The new exact assumption crosswalk
    distinguishes its scalar singular covariance, amplitude scaling and
    chaos projection from the printed mixed conditional composite. The
    manuscript makes no novelty claim based on nonpolynomiality alone.
    A separate internal read-only diff/source audit found no change to the
    model, full random coefficient, proof statements or quantifiers.

The current, energy covariance identity, strong Bessel-kernel proof, sharp
lower/upper slopes and homogeneous escape survived the separate reviews.
The new explicit deterministic-background bound has the six-real factor6
combined with the determinant factor1/4, yielding3/2.

## Verification scope

verification/verify.py derives coefficients from the frozen A1 snapshot,
checks exact slope residuals and critical escapes, and independently compares
49 scalar nonconstant-coefficient Gaussian-IBP cases against exact Wick-pair
enumeration. All three connection families have nonzero hostile fixtures;
dropping, doubling or reversing each is rejected. Matrix fixtures separately
check the real/complex half factor and Pauli spatial contraction. The cube
integral and ellipticity constant are computed, not pasted as derived inputs.

Run: python -X utf8 publish/papers/a6-a7-canonical-composites/verification/verify.py
--self-test --check claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/runs/2026-11-12-a6-a7-paper/algebra.json

Observed: 80 checks PASS; 13 hostile mutations rejected.
Fresh source-hash/ingredient replay: A6 primary29, independent16, aggregate64;
A7 primary29, independent17, aggregate74. All pass. Legacy area and variance
rows remain ingredient diagnostics, not all-mode proofs. The original
2026-07-20 reports are retained byte-for-byte by the replay wrapper.

## Historical edition0.1.1 review and release items

The revised TeX was compiled with Tectonic0.17.0; all seven PDF pages were
rendered with Poppler and visually inspected. Hash-linked text/geometry and
visual receipts, plus the actual PNG pages, are retained under verification/.
The v011-suffixed receipts and rendered-v011/ pages describe that historical
edition; unsuffixed receipts describe0.1.0. A bibliography-only orphan page
in the intermediate revision was removed by compacting references to nine
point text, without removing a citation or modifying a theorem.
No unresolved reference markers or clipped text were found. Specialist novelty and independent human
mathematical review remain NOT PERFORMED. If either identifies a gap, the
correction must be versioned and tested before the handoff is sealed.
No interacting Gibbs, A13 closure, physical-vacuum or floor-removal result
can be inferred from this internal audit.

## Edition0.1.2 repair and adversarial review

The operator defers actual external review from this package-completion
task, while requiring repeated internal repair/re-review. The independent
AI review assignments, findings and final dispositions are in self-review-v012.md.
They do not constitute a human external report or an absolute-perfection claim.

- VALID-with-mitigation: B is PSD, not necessarily positive definite; its
  common-phase null direction and pure-third-component zero are now explicit.
- VALID-with-mitigation: J and the three centered energy families were not
  explicitly defined. The smooth-cutoff definitions and conditional centering
  are printed; no product of limiting rough currents is presumed.
- VALID-with-mitigation: the finite IBP lemma now requires polynomial growth
  of A,D and their derivatives through order two, not merely the functions.
- VALID-with-mitigation: G_lo, its t-independent quartic growth, the exact
  pinned lambda/gamma production instance and mixed homogeneous witness are
  explicit. The O(t) error is not an unrecorded physical assumption.
- VALID-with-mitigation: the determinant proof now shows the noncommuting
  background order argument and the common-coupling half-HS variance identity.
- VALID-with-mitigation: scalar IBP cases alone do not distinguish tensor
  index transposes. The new dense exact fixture compares independent Wick
  enumeration with the full tensor formula and rejects those transposes.
- VALID-with-mitigation: visual receipts previously admitted inconsistent
  schema/defect/provenance fields and unbound PNGs; schema1.1 binds all pages.
- VALID-with-mitigation: nested output paths could invalidate the delivery
  inventory. Pure disjoint-path admission, copied-identity checks and final
  destination/extraction rechecks now precede the PASS report write.

Sign/factor: full tensor families, real-complex covariance, the quadratic
variance half factor and determinant quarter factor have separate tests.
Domain/units: fixed side/floor, real bundle dimension, deterministic b and
production homogeneous polynomial are distinct. Convergence: all-mode
limits remain analytic; finite spectral/large-t fixtures are diagnostics.
Hardcode masking: coefficients, c0, gamma/lambda and multiplicities are read
or computed from the frozen model; rational fixture values are labelled INPUT.
Limit cases: p=0, B=0 on the third component, the phase kernel, signed cutoffs,
and subcritical escape are exercised. Specialist review remains welcome but
unperformed and is not simulated to complete this author-requested package.

New executable evidence: strengthened-v012.json records59 checks and14
hostile mutations; package-gates-v012.json records35 visual/output mutations.
The package verifier independently rejects14 scope/path mutations. Current
PDF QA and visual identities are the v012-suffixed receipts for eight pages;
the preceding layout discussion is retained historical edition0.1.1 context.
