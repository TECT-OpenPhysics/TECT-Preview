# Q3LOCK comparison audit: Kargol--Kozitsky asymmetric scalar theorem

Date: 2026-09-07. EXP-001618. T0 literature comparison,
claim_bearing=false, NO PRIORITY CLAIM. The paper PDF remains deferred until
content review and final organization.

## Primary source

A. Kargol and Y. Kozitsky, *A Phase Transition in a Quantum Crystal with
Asymmetric Potentials*, arXiv:math-ph/0611017v1 (8 November 2006),
`https://arxiv.org/pdf/math-ph/0611017`.

The checked locators are the abstract and pages 2--4: equations (1)--(7),
the scalar-potential hypothesis (4), Definition 1.3, and Theorem 1.4. The
paper considers a simple-cubic lattice in dimension `d`, a scalar displacement
`q_l in R`, a bilinear nearest-neighbour interaction with `J>0`, and a
continuous scalar onsite potential `V_0` satisfying a superquadratic lower
bound. Its Theorem 1.4 proves that for `d>=3`, sufficiently large mass and
interaction intensity yield a discontinuity of the thermodynamic global
polarization at some external field `h_*`.

## Exact boundary against Q3LOCK

| Source feature | Q3LOCK feature | Disposition |
|---|---|---|
| One scalar coordinate `q_l in R` | Eight coordinates `q_y in R^8` and collective direction `u` | Direct scalar theorem does not apply |
| Bilinear interaction `-J q_l q_l'` | Positive spatial difference energy plus a non-radial onsite `Q_3` locking polynomial | Direct interaction match absent |
| General/asymmetric scalar onsite potential | Even, non-radial eight-component Q3LOCK potential with positive `lambda` | Scalar reduction is not supplied |
| Discontinuity of a global scalar polarization at some `h_*` | Strict cusp at the parity-symmetric source `h=0` and two parity-related tempered Euclidean DLR states | Different conclusion and state construction |
| Scalar Euclidean path argument | Eight-component DLR specification and source-window tangent passage | No direct topology/specification import |

The source is therefore a substantive comparator and a warning against an
overstated novelty claim, but it is not a covering theorem for the Q3LOCK
result. In particular, the paper's word “asymmetric” means lack of scalar
`Z_2` symmetry; it does not mean an arbitrary finite-dimensional non-radial
vector potential. Conversely, the scalar theorem does not supply the
Q3LOCK-specific collective lower bound, the parity-at-zero source selection,
or the displayed source-to-zero DLR construction.

This comparison does not rule out another vector/anisotropic theorem or a
new reduction. It only fixes the exact reason why Kargol--Kozitsky Theorem 1.4
cannot be cited as the Q3LOCK theorem without an additional, separately
proved reduction. It also prevents calling the scalar discontinuity theorem a
proof of the stronger two-state statement in the present manuscript.

## Adversarial checks and disposition

1. **“General potential” means arbitrary vector potential.** Rejected: the
   source defines the onsite variable and potential on `R`, not `R^8`.
2. **A scalar projection along `u` is automatically a scalar reduction.**
   Rejected: the Q3 locking polynomial produces non-bilinear terms in the
   transverse coordinates; no conditional or invariant reduction is proved.
3. **A polarization discontinuity at an unspecified `h_*` is the same as the
   Q3LOCK zero-source parity cusp.** Rejected: the field location and the
   symmetry/state conclusions differ.
4. **The source's infrared proof can replace the Q3LOCK proof.** Rejected:
   its scalar Duhamel and path estimates are source-comparison evidence only;
   the Q3LOCK finite-vector FSS map, zero-mode subtraction, collective bound,
   and DLR passage remain separate.
5. **This boundary is a novelty certificate.** Rejected: no exhaustive search
   or specialist publication-value opinion has been completed.

## Resulting literature disposition

`Kargol--Kozitsky 0611017: DOES-NOT-APPLY directly; RETAIN AS CLOSE SCALAR
COMPARATOR.` The broader anisotropic/vector-theorem search and signed
specialist review remain open. This note changes no theorem, claim tier,
manuscript equation, source authority chain, or PDF status.
