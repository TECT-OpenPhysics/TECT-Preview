# Q3LOCK collective thermal-polynomial integrability repair (EXP-001680)

## Scope

This is a proof-text repair for the A14 collective Jensen block.  It makes the
unbounded polynomial integrability used by the translated-form argument
explicit at fixed finite volume.  It does not sign A14--A17, prove the
spectral cutoff or Duhamel limit, promote R-497, or generate a PDF.

## Repair

At fixed `L` and `beta`, choose the same finite-volume form shift `C` as in the
coercive envelope so that

`U+C >= 1 + kappa sum_y |q_y|^4`, with `kappa=g/256` admissible.

For every multiplication polynomial `P` of degree at most four, the manuscript
now defines the positive form trace

`T_beta(P) = sum_i exp(-beta E_i) integral |P(q)| |psi_i(q)|^2 dq`

and proves its finiteness from `|P| <= K(1+w)` and the spectral sum of
`H+C`.  It also records explicitly that this is a spectral form sum, not a
cyclic trace containing an unbounded product.  Consequently the cubic
translation increment `Delta_t` has finite Gibbs absolute expectation and
`sum_i p_i |d_i| < infinity` before the scalar Jensen step is used.

## Boundary

The repair closes a previously compressed internal justification for the
finite translated-form Jensen calculation.  It does not establish a common
infinite-volume form domain, a uniform operator core, the ordered `M`/`R`
cutoff passage, the identification with `D_L(0,0)`, the thermodynamic lower
bound, the strict cusp, or the source-selected DLR pair.  A14--A17 remain
OPEN for signed independent mathematical review, and the package remains T0,
`claim_bearing=false`, `UNFROZEN_CONTENT_REVIEW`, and PDF DEFERRED.

## Reproducibility

The repair is part of the next fresh/integrated replay family.  The source
location is `manuscript.tex#lem:collective-polynomial-integrability` and the
energy estimate is `manuscript.tex#eq:collective-polynomial-trace`.
