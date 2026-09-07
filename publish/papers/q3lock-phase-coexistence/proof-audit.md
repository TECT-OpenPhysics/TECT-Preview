# Q3LOCK proof audit and adversarial review form

Status: INTERNAL CHECKLIST / NOT SIGNED / PDF DEFERRED.

## Reviewer disposition legend

OPEN means no independent disposition has been received.  PASS may be written
only by an independent reviewer with a location-specific explanation.  REPAIR
must name the changed equation and trigger a new source hash and exploration
record.  FAIL moves the theorem statement or records a negative result; it
does not get hidden by changing prose.

## Load-bearing audit table

| ID | Question | Evidence to inspect | Disposition |
|---|---|---|---|
| A1 | Is the Hamiltonian/form domain exactly the printed eight-component model? | `eq:hamiltonian`, `eq:form-domain`; EXP-001587 | OPEN |
| A2 | Does min--max prove trace finiteness, and is only Z claimed entire? | `eq:trace-bound`, `eq:source-derivatives`; EXP-001604 repair | OPEN |
| A3 | Are the cyclic determinant, weak mesh limit and absolute harmonic normalization exact? | `eq:cyclic-det`, `eq:weighted-loop-limit`, `sec:fk-identification`; EXP-001605 | OPEN; detailed content now integrated |
| A4 | Is the seam budget 288, including all endpoint multiplicities? | `eq:seam`, `eq:seam-trace-sandwich`; EXP-001589 | OPEN |
| A5 | Do two-sided volume bounds, arbitrary rectangular tiling and moving-beta secants prove the limit? | `eq:two-sided-pressure`, `eq:pressure-seam-rate`, `eq:open-pressure` | OPEN |
| A6 | Do KP assumptions hold for the non-radial R^8 potential? | `sec:dlr-specification`, `eq:dlr-potential-envelope`; EXP-001606 | OPEN; explicit parameter map integrated |
| A7 | Is the source-uniform moment finite before the Holder recursion is divided? | `eq:one-site-exponential`, `eq:periodic-holder-closure`; EXP-001606 | OPEN; full source-window proof integrated |
| A8 | Is the projective compactness direction alpha_(k+1)<alpha_k correct? | `eq:tempered-metric`, `eq:dlr-compact-set`, `eq:weighted-tail-direction`; EXP-001606 | OPEN; topology and tail proof integrated |
| A9 | Does the finite specification pass to the DLR limit on a determining class? | `eq:dlr-normalizer-lower`, `eq:kernel-source-lipschitz`, `sec:dlr-source-tangents`; EXP-001606 | OPEN; direct Feller/quotient proof integrated |
| A10 | Is the mixed log-density Hessian nonnegative, with the opposite sign to the action Hessian? | `eq:log-supermodular`; EXP-001604 correction and full conditioning induction | OPEN |
| A11 | Does association pass to bounded Borel loop tests and the actual selected limits? | `sec:fkg-loop-passage`, `eq:fkg-product-clipping`; EXP-001605 | OPEN; finite-loop proof integrated; spatial DLR prerequisites retained |
| A12 | Do the FSS prior, typed Poisson source and actual loop/UI passage preserve every factor? | `eq:fss-prior-coercivity`, `eq:fss-poisson-energy`, `eq:fss-square-shift`, `eq:fss-source-ui`; EXP-001607 | OPEN; full source/limit content integrated |
| A13 | Is the nonzero-mode sum uniform and the zero mode excluded? | `eq:duhamel-two-time`, `eq:infrared-bound`, `eq:infrared-continuous-tail`, `eq:infrared-discrete-tail`; EXP-001607 | OPEN; full Fourier and tail content integrated |
| A14 | Is scalar Jensen valid on the translated form domain? | `eq:collective-thermal-energy`, `eq:collective-jensen-chain`, `eq:double-commutator`; EXP-001608 | OPEN; thermal and form-domain argument integrated |
| A15 | Are the form identity, absolute energy sums and ordered spectral/coordinate cutoff passages valid? | `eq:form-identity`, `eq:collective-absolute-energy-sums`, `eq:collective-spectral-cutoff`, `eq:collective-loop-clipping`; EXP-001608 | OPEN; full passage integrated, not independently accepted |
| A16 | Does FKG supply exactly the expectation inequalities used? | `eq:fkg-local`, `eq:moment-chain`, `eq:collective-graph-expectation`; EXP-001608 | OPEN; pointwise/expectation distinction explicit |
| A17 | Does the squared-tail lemma justify the cusp at nondifferentiability? | `eq:griffiths-squared-tail`, `eq:composition-liminf-limsup`, `eq:cusp`; EXP-001609 | OPEN; full tail and moment/slope join integrated |
| A18 | Does the source-window limit preserve the local expectation in a zero-source DLR state? | `eq:dlr-local-clipping`, `eq:source-zero-tangent`, `eq:mu-plus`; EXP-001606 | OPEN; both clipping passages integrated |
| A19 | Are conclusions restricted to the nonempty strict sufficient regime, without identifying an exact critical temperature? | `eq:threshold-algebra`, `eq:beta-star`, `eq:cusp`; EXP-001609 | OPEN; equality and complement remain undecided |
| A20 | Are nonclaims, citations and the two branch limit orders synchronized? | `sec:composition-dictionary`, `thm:q3lock-composition`, `sec:crosswalk`, `sec:readiness`; EXP-001609 | OPEN; internal interface audit recorded, source/literature audit remains |
| A21 | Are the half measures finite and the Hilbert-kernel passage valid for bounded Borel reflection tests? | `eq:rp-local-measure`, `eq:hilbert-kernel-positive`, `eq:spatial-reflection-positive`; EXP-001607 | OPEN; direct proof integrated |
| A22 | Does the finite logarithmic-mean/Jensen proof give exactly the Falk--Bruch normalization, including degenerate energies and c=0? | `eq:falk-phi-concavity`, `eq:falk-spectral-weights`, `eq:finite-falk-bruch`; EXP-001608 | OPEN; direct proof of a standard inequality integrated |
| A23 | Does parity preserve the full zero-source specification, and does a bounded local observable distinguish the constructed states? | `eq:parity-specification-intertwining`, `eq:bounded-phase-witness`; EXP-001609 | OPEN; explicit kernel map and bounded witness integrated |

The v0.1.7 current-source ledger and EXP-001611 also require review of
Simon's Theorem 1.1 mass/harmonic/trace application and the bounded novelty
comparison. Their disposition is OPEN. The nonradial infrared method and
threshold shape are not claimed as new; the specialist must assess whether
the actual positive-lambda collective estimate is covered by an earlier theorem.

Locations above are stable TeX labels, not frozen equation numbers. The
v0.1.1 local repair is documented in
`strategy/q3lock-manuscript-content-repair-260906.md` (EXP-001604).
It does not enter PASS in this independent-review table.

## Mandatory hostile checks

1. Replace the corrected coefficient 288 by the historical 48 in a test
   configuration and confirm that the inequality fails.
2. Insert an extra beta into p'_L=E X_L/V and verify that the
   pressure/DLR dictionary becomes dimensionally inconsistent.
3. Try to infer a zero-mode lower bound from the local variance without
   subtracting nonzero Fourier modes; record the obstruction.
4. Try to pass a second moment through weak convergence without the Chernoff
   tail; retain the escaping-mass counterexample.
5. Try to extend association to an arbitrary mixture of associated states;
   retain the two-point negative-covariance counterexample.
6. Set A0=I3 or beta=beta_star and verify that the manuscript makes no
   phase-absence claim.

## Independent reviewer response block

Reviewer: ____________________  Date: ____________________

Scope reviewed: __________________________________________________________

Disposition (PASS / REPAIR / FAIL): ______________________________________

Location-specific findings and replacement text/equations:

___________________________________________________________________________

___________________________________________________________________________

The reviewer confirms that finite diagnostics were not treated as a substitute
for proof:  Yes / No

Signature or verifiable review record: ____________________________________
