# Q3LOCK A1--A23 independent-review matrix

**Status:** T0 review handoff instrument; not a mathematical acceptance  
**Date:** 2026-09-07  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Package:** `publish/papers/q3lock-phase-coexistence` v0.1.7  
**PDF:** deferred until every content and external-review gate is closed

## 1. Purpose and disposition rule

This matrix gives an independent reviewer one complete, bounded checklist for
the load-bearing proof rows A1--A23.  It is intentionally separate from the
manuscript theorem statement: a row is not closed by appearing in this table,
by a finite verifier PASS, or by an internal reread.  A reviewer must return a
location-specific disposition for every row:

```text
PASS                 no load-bearing defect found in the stated scope;
PASS WITH REPAIR     exact replacement text/equation and a new source hash;
FAIL                 the row or downstream theorem must be weakened or removed;
NOT REVIEWED         no scientific disposition.
```

The repository proof-audit table remains the authoritative status surface.  At
the time of this packet every row is `OPEN`, the paper is `T0`,
`claim_bearing=false`, and `INTERNAL_REVIEW_ONLY`.

## 2. How to use the packet

The reviewer should read the manuscript in the order A1--A23, then inspect the
listed strategy notes and primary-source locators.  For each row, the response
must state:

1. the exact equation/section reviewed;
2. whether the imported theorem's hypotheses match the Q3LOCK field space,
   source, boundary condition, topology, and limit order;
3. any missing uniformity, common-domain, measurability, or integrability
   estimate;
4. the downstream rows affected by a repair; and
5. a signed or institutionally verifiable record.

Finite scripts are regression diagnostics.  They cannot replace a proof of an
unbounded operator passage, an infinite-volume limit, a DLR theorem, a source
cusp, or phase coexistence.

## 3. Complete load-bearing matrix

| ID | Load-bearing question | Manuscript evidence and review source | Required reviewer decision |
|---|---|---|---|
| A1 | Does the eight-component Hamiltonian, source convention, form domain, and fixed-volume self-adjoint realization match the declared model? | `manuscript.tex#eq:hamiltonian`, `manuscript.tex#eq:form-domain`, `strategy/q3lock-finite-volume-pressure-content-260905.md`; Simon source map | Check coercivity, form closure/core, mass convention, and no hidden continuum claim. |
| A2 | Does min--max give the absolute heat-trace bound while only the partition function, not a global complex logarithm, is called entire? | `manuscript.tex#eq:trace-bound`, `manuscript.tex#eq:source-derivatives`; EXP-001604 repair note | Check trace finiteness, complex source majorant, local real analyticity, and the zero-set qualification. |
| A3 | Are the cyclic determinant, Gaussian tightness, residual Riemann-sum limit, and absolute harmonic factor all proved in the stated order? | `manuscript.tex#eq:cyclic-det`, `manuscript.tex#eq:gaussian-weak-limit`, `manuscript.tex#eq:weighted-loop-limit`; EXP-001605 | Check covariance factors, periodic interpolation, Kolmogorov estimate, compact residual passage, and normalized versus absolute laws. |
| A4 | Is the periodic seam count and quartic Young allocation exactly 288, including every endpoint occurrence? | `manuscript.tex#eq:seam`, `manuscript.tex#eq:seam-trace-sandwich`; EXP-001589 | Recount bonds/endpoints and verify the form inequality and trace sandwich. |
| A5 | Do arbitrary even rectangular exhaustions, subadditivity, periodic transfer, moving-beta secants, and derivative squeezing prove the pressure limit? | `manuscript.tex#eq:open-pressure`, `manuscript.tex#eq:pressure-seam-rate`, `manuscript.tex#eq:pressure-limit`; EXP-001632 | Check remainder tiling, finite lower bounds, local uniformity, and no illicit derivative/volume exchange. |
| A6 | Do KP's general-vector assumptions hold for the non-radial eight-component Q3LOCK potential without importing scalar or radial phase theorems? | `manuscript.tex#sec:dlr-specification`, `manuscript.tex#eq:dlr-potential-envelope`; KP crosswalk | Check `nu=8`, `r_KP=2`, finite-range norm, weighted hypotheses, and source line typing. |
| A7 | Is source-window exponential moment finiteness established before the Holder recursion is divided? | `manuscript.tex#eq:one-site-exponential`, `manuscript.tex#eq:periodic-holder-closure`; source-window moment audit | Check positive normalizers, boundary terms, Gaussian Fernique input, and common constants in `h`, volume, and state. |
| A8 | Is the projective compactness direction correct and is one diagonal compact set obtained for the entire source window? | `manuscript.tex#eq:dlr-compact-set`, `manuscript.tex#eq:weighted-tail-direction`; projective diagonal audit | Check `alpha_(k+1)<alpha_k`, Holder compact embedding, lower semicontinuity, and cofinality. |
| A9 | Does the finite specification pass to a source-zero DLR limit on a determining class? | `manuscript.tex#eq:dlr-normalizer-lower`, `manuscript.tex#eq:kernel-source-lipschitz`, `manuscript.tex#sec:dlr-source-tangents`; Feller audit | Check compact-boundary coercivity, normalizer lower bound, Feller topology, Borel extension, and source-limit order. |
| A10 | Is the log-density mixed Hessian nonnegative with the correct sign for temporal, spatial, and Q3 locking bonds? | `manuscript.tex#eq:log-supermodular`; FKG mixed-derivative audit | Recompute the Q3 identity and verify finite-grid supermodularity without radiality. |
| A11 | Does association pass from finite grids to continuous loops, bounded Borel tests, selected spatial limits, and clipped products? | `manuscript.tex#sec:fkg-loop-passage`, `manuscript.tex#eq:fkg-product-clipping`; FKG content audits | Check order-preserving wrap interpolation, closed-cone approximation, uniform integrability, and the explicit mixture nonclaim. |
| A12 | Do Hilbert-valued reflection positivity and the finite-dimensional FSS theorem use exactly the stated finite-mesh prior and edge source? | `manuscript.tex#eq:hilbert-kernel-positive`, `manuscript.tex#eq:spatial-reflection-positive`, `manuscript.tex#eq:fss-poisson-energy`; FSS source audit | Check finite-rank Gaussian kernel passage, spatial-only scope, `J=c`, source pairing, and no mesh-uniform prior constant. |
| A13 | Does the FSS-to-loop UI passage yield the correctly normalized nonzero-mode Duhamel bound and convergent three-dimensional sum while excluding the zero mode? | `manuscript.tex#eq:fss-source-ui`, `manuscript.tex#eq:duhamel-poisson`, `manuscript.tex#eq:infrared-bound`, `manuscript.tex#eq:infrared-subtraction`; FSS/infrared audit | Check truncation/UI, β factors, eigenvalue `2E(p)`, shell tails, and the missing zero-mode lower-bound boundary. |
| A14 | Is scalar Jensen valid on the translated form domain and does it give the collective Hessian expectation without differentiating an unbounded trace? | `manuscript.tex#eq:collective-jensen-chain`, `manuscript.tex#eq:collective-hessian`; EXP-001628 | Check translated form-domain invariance, polynomial integrability, spectral Jensen, and the global minimum argument. |
| A15 | Are the collective form identity, absolute energy-weighted sums, finite spectral cutoffs, and ordered coordinate cutoffs valid? | `manuscript.tex#eq:form-identity`, `manuscript.tex#eq:collective-absolute-energy-sums`, `manuscript.tex#eq:collective-spectral-cutoff`; EXP-001628 | Check common form core, row/column interchange, nonnegative regrouping, and fixed-R then R-limit order. |
| A16 | Does FKG supply exactly the expectation inequalities used in the collective moment chain, rather than pointwise graph inequalities? | `manuscript.tex#eq:moment-chain`, `manuscript.tex#eq:collective-graph-expectation`; EXP-001628 | Check parity, selected-state scope, coordinate clipping, graph degree, and the direction of every expectation inequality. |
| A17 | Does the squared-tail lemma bound the thermodynamic second moment at a nondifferentiable even pressure? | `manuscript.tex#lem:griffiths-endpoint`, `manuscript.tex#eq:griffiths-squared-tail`, `manuscript.tex#eq:composition-liminf-limsup`; EXP-001628 | Check Chernoff signs, fixed-source order, layer-cake integral, and `limsup` versus `liminf` use. |
| A18 | Does the source-window limit preserve the local unbounded expectation in a zero-source DLR state? | `manuscript.tex#eq:dlr-local-clipping`, `manuscript.tex#eq:source-zero-tangent`, `manuscript.tex#eq:mu-plus`; source-tangent audit | Check compact split, kernel continuity, clipped convergence, and no weak-limit passage for an unbounded observable without UI. |
| A19 | Are the conclusions restricted to the strict sufficient regime and do they avoid identifying an exact critical temperature? | `manuscript.tex#eq:threshold-algebra`, `manuscript.tex#eq:beta-star`, `manuscript.tex#eq:cusp`; regime audit | Check `r<0`, `A_0>I_3`, `beta>beta_*`, nonempty parameter set, equality case, and undecided complement. |
| A20 | Are citations, nonclaims, and the two branch limit orders synchronized throughout the manuscript and literature comparison? | `manuscript.tex#sec:composition-dictionary`, `manuscript.tex#sec:crosswalk`, `literature-crosswalk.md`; primary literature audit | Check no scalar/radial shortcut, no priority claim, no KMS/ground-state/continuum overclaim, and exact authority chain. |
| A21 | Are the half measures finite and is the Hilbert-kernel proof valid for bounded Borel spatial reflection tests? | `manuscript.tex#eq:rp-local-measure`, `manuscript.tex#eq:hilbert-kernel-positive`, `manuscript.tex#eq:spatial-reflection-positive`; reflection audit | Check residual allocation, crossing-bond factorization, finite complex pushforward, and bounded-Borel extension. |
| A22 | Does the finite logarithmic-mean proof give the exact Falk--Bruch normalization, including degenerate energies and `c=0`? | `manuscript.tex#eq:falk-phi-concavity`, `manuscript.tex#eq:falk-spectral-weights`, `manuscript.tex#eq:finite-falk-bruch`; EXP-001628 | Check concavity signs, weights, energy degeneracy, homogeneity, and endpoint continuity. |
| A23 | Does parity preserve the full zero-source specification and does a bounded local observable distinguish the two constructed states? | `manuscript.tex#eq:parity-specification-intertwining`, `manuscript.tex#eq:bounded-phase-witness`; EXP-001629 | Check pushforward direction, tempered-space invariance, local clipping bound, and strict witness inequality. |

## 4. Required cross-cutting checks

The reviewer must also answer these questions globally rather than repeating a
local PASS:

* Are all uses of the finite-dimensional Simon, KP, FKG, FSS, and KKK inputs
  accompanied by a hypothesis-to-model map, with no hidden boundedness,
  radiality, or finite-dimensional shortcut?
* Is every limit ordered as stated, and is every uniform estimate used outside
  its declared fixed-volume/source window rejected?
* Are the source units and normalizations consistent across `h`, `X_L`,
  `p_L`, `P_L`, the Duhamel matrix, `m=chi/hbar^2`, and `2E(p)`?
* Does the threshold prove only a sufficient strict cusp, leaving the equality
  and complement undecided?
* Do the DLR states arise from a specification identity, not just a weak
  subsequential law, and are the two states only parity-related rather than
  asserted extremal or complete?
* Is the literature comparison bounded to primary sources and explicit about
  scalar/vector/radial/classical differences, with no priority assertion?

## 5. Reviewer response block

Reviewer name and affiliation: ____________________________________________

Version and source snapshot reviewed: _____________________________________

Rows reviewed: ____________________________________________________________

Row dispositions (attach a line for every A1--A23):

```text
A1 ____  A2 ____  A3 ____  A4 ____  A5 ____  A6 ____  A7 ____  A8 ____
A9 ____  A10 ___  A11 ___  A12 ___  A13 ___  A14 ___  A15 ___  A16 ___
A17 ___  A18 ___  A19 ___  A20 ___  A21 ___  A22 ___  A23 ___
```

Load-bearing repairs, with exact replacement locations:

___________________________________________________________________________

___________________________________________________________________________

Literature or citation corrections:

___________________________________________________________________________

Claims that must be removed or weakened:

___________________________________________________________________________

The reviewer confirms that finite diagnostics were not treated as theorem
certification: YES / NO

Overall disposition: PASS / PASS WITH REPAIRS / NOT ACCEPTED

Signature or verifiable institutional record: ______________________________

Until this block is completed by an independent reviewer, A1--A23 remain OPEN,
the claim/result decision remains pending, and the paper PDF gate remains
closed.

