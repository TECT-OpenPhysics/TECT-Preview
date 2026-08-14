# R-169 v1.1 certificate: pinned-P1 BCC realization and empty-reference exclusion

Issued: 2026-08-14  
Task: T-055  
Exploration: EXP-000852  
Tier: T0, claim-bearing false

## 1. Result and scope

This certificate joins one new exact realization calculation to the already
proved R-157 coercivity theorem.  It constructs a smooth nonzero field on the
fixed side-16 P1/A2 torus whose modulus maxima form exactly the BCC lattice of
R-169 v1.0, identifies the resulting periodic Euclidean Voronoi cells, and
then applies R-157 to reject that field family against the zero reference.

The result is conditional on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL` and on
the exact hash-pinned neutral P1/A2 functional with `eta_shell=0`.  It is not a
new T6 theorem.  The energy and radial inequalities are inherited from R-157;
the new content is the explicit field-to-center-to-cell bridge and its exact
specialization.

The current Reading-H object is different: it is a finite momentum-shell
point set `Q` with amplitudes, compared with an isotropic Gaussian-Hartree
dressing `G_*`.  No registered authority maps `Q` or `G_*` to the P1 field,
fixes its phases and three-component polarization, or intertwines the two
energies and ensembles.  Consequently this certificate neither promotes nor
refutes the current B1/B3 Reading-H ranking.

## 2. Inherited R-157 theorem

Let

`H = H^2(T^3_16; C^3)`

and let `F_P1` be the exact hash-pinned neutral functional named in the
manifest.  R-157 proves, for every `Psi in H`,

`F_P1[Psi]-F_P1[0] >= g ||Psi||_2^2`,

where

`g = 719818750025582338837 / 5400000000000000000000 > 1/8`,       (2.1)

and independently

`<D F_P1(Psi),Psi> >= kappa ||Psi||_2^2`,

where

`kappa = 2101675000076747016511 / 8100000000000000000000 > 1/4`. (2.2)

Thus zero is the unique global minimizer and critical point in this
unconstrained linear field space.  Every nonzero local minimum or metastable
equilibrium would be a nonzero critical point and is therefore excluded.

More generally, if a preregistered realization map `iota` obeys
`iota(0)=0`, then every candidate with `iota(r)!=0` is rejected by (2.1) and
(2.2).  This statement is independent of the candidate's geometry once the
map and exact functional identity have been established.

## 3. Exact BCC-periodic P1 field

Put

`S = 4{(+/-1,+/-1,0),(+/-1,0,+/-1),(0,+/-1,+/-1)}`.             (3.1)

There are twelve distinct elements.  Fix `u in C^3`, `||u||=1`, and a
nonzero complex amplitude `A`.  On `T^3_16=R^3/(16 Z^3)` define

`Psi_A(x)=A u sum_(n in S) exp(2 pi i n dot x/16)`.              (3.2)

It is a smooth member of `H`.  Pairing opposite modes gives the real scalar
factor

`f(x)=4[pq+pr+qr]`,                                               (3.3)

where

`p=cos(pi x_1/2), q=cos(pi x_2/2), r=cos(pi x_3/2)`.

The construction uses a fixed common amplitude and polarization.  It is an
explicit mathematical P1 realization, not a claim that these choices are
selected by Reading-H or by a microscopic TECT map.

## 4. Deterministic center extraction

Define the centers without a visual or post-hoc rule:

`C_A = argmax_(x in T^3_16) |Psi_A(x)|`.                          (4.1)

The polynomial `h(p,q,r)=pq+pr+qr` is affine in each variable separately.
Its extrema on the cube `[-1,1]^3` therefore occur at cube vertices.  The
eight vertex values are two copies of `3` and six copies of `-1`.  Moreover,
`3-h=(1-pq)+(1-pr)+(1-qr)`, a sum of nonnegative terms.  Equality forces
`pq=pr=qr=1`, so the equality case for the absolute maximum is only

`(p,q,r)=(1,1,1)` or `(-1,-1,-1)`.                               (4.2)

It follows that `max |f|=12` and

`C_A = [4 Z^3 union ((2,2,2)+4 Z^3)] / 16 Z^3`.                  (4.3)

The two cosets contribute `4^3` points each, so there are exactly 128 centers
on the torus.

## 5. Translation lattice and Voronoi cells

Fourier uniqueness shows that a translation `y` preserves `f` exactly iff

`exp(2 pi i n dot y/16)=1` for every `n in S`.                    (5.1)

The integer span of `S` is `4 D_3`, where
`D_3={m in Z^3: m_1+m_2+m_3 is even}`.  The period group is therefore

`L=4 D_3^*=4 Z^3 union ((2,2,2)+4 Z^3)`.                         (5.2)

There is no extra anti-period for the modulus.  Indeed, if
`|f(x+y)|=|f(x)|` for all `x`, real analyticity gives
`f(x+y)=f(x)` identically or `f(x+y)=-f(x)` identically.  The latter would
require phase `-1` on every support mode.  But `S` contains vectors
`n_1,n_2,n_1+n_2`; the first two phases would multiply to `+1`, contradicting
the required phase `-1` on their sum.  Thus the exact modulus-period lattice
is also `L`.

R-169 v1.0 proves that the Euclidean Voronoi cell of `L` is

`P={|x_i|<=2, sigma dot x<=3 for sigma in {+1,-1}^3}`,            (5.3)

the regular truncated octahedron with 24 vertices, 36 edges, six square and
eight regular-hexagonal faces, and volume 32.  Since `16 Z^3` is a sublattice
of `L`, `P+L` descends to the side-16 torus.  The volume identity

`16^3 / 32 = 128`                                                (5.4)

agrees with (4.3).  This is an exact field-center/Voronoi-cell extraction for
the declared fixture.

## 6. Exact norm and empty-reference rejection

The twelve characters in (3.2) are orthogonal, and the torus volume is
`16^3`.  Hence

`||Psi_A||_2^2 = 12*16^3 |A|^2 = 49152 |A|^2`.                  (6.1)

Substitution into (2.1) gives

`F_P1[Psi_A]-F_P1[0]`

` >= [719818750025582338837/109863281250000000] |A|^2`

` > 6144 |A|^2 > 0`.                                            (6.2)

Likewise (2.2) gives

`<D F_P1(Psi_A),Psi_A>`

` >= [2101675000076747016511/164794921875000000] |A|^2`

` > 12288 |A|^2 > 0`.                                           (6.3)

Thus this exact BCC-periodic P1 realization fails the R-169 below-reference
sign gate and is not an unconstrained critical point, local minimum,
metastable equilibrium, or global minimizer.  The theorem eliminates this
candidate family; it does not select a replacement.

## 7. Perturbation transfer and its firewall

Let `F_tilde=F_P1+R`.  An energy-value domination

`R[Psi]-R[0] >= -delta ||Psi||_2^2`, `0<=delta<g`,               (7.1)

implies only

`F_tilde[Psi]-F_tilde[0] >= (g-delta)||Psi||_2^2`.               (7.2)

It preserves the below-reference exclusion.  It does not by itself exclude a
critical point.  For that conclusion one separately needs the radial bound

`<D R(Psi),Psi> >= -delta_r ||Psi||_2^2`, `0<=delta_r<kappa`,    (7.3)

which yields

`<D F_tilde(Psi),Psi> >= (kappa-delta_r)||Psi||_2^2`.            (7.4)

This separation is load-bearing.  A common counterterm basis with unfixed
nonconstant finite parts supplies neither (7.1) nor (7.3).  Only a common
state-independent scalar cancels automatically.

An exact one-variable counterfixture proves the distinction.  Let

`F_0(x)=x^2`,

`R(x)=-(3/4)x^2+x^2(x^2-1)^2`.

Then `R(x)-R(0)>=-(3/4)x^2` with `3/4<g_0=1`, while

`F_tilde(x)=(1/4)x^2+x^2(x^2-1)^2>0` for `x!=0`.                 (7.5)

Writing `y=x^2`, its nonzero stationary equation is
`3y^2-4y+5/4=0`, with roots `y=1/2` and `y=5/6`.  The second is a
strict local minimum with energy `25/108>0`.  Thus a value gap can exclude a
candidate from being the global reference winner while leaving a higher
nonzero local minimum.  Only (7.3) rules that out.

## 8. Ensemble and model escape routes

R-158 changes the variational problem.  At fixed charge the zero field and
the radial direction are not admissible; in the grand-canonical formulation
`Omega_mu=F_P1-mu Q` is a different functional.  Its registered nonzero shell
minimizer remains above the original neutral zero reference under `F_P1` and
has uniform registered local observables, so it is not this BCC fixture.

No conclusion here transfers automatically to a fixed-norm or fixed-charge
space, chemical potential, compact `CP^2` target, conserved dynamics,
historical nonvariational backend, signed A7 covariance-normal composite,
nonzero `eta_shell`, retuned coefficients, removed regularizers, another
functional, infinite volume, regulator removal, or a renormalized quantum
theory.  Every such escape must declare its new owner and repeat the matched
reference sign and stability tests.

## 9. Reading-H interface remains open

The B1 Reading-H authority defines `Q` as a finite point set on the Brazovskii
momentum shell with amplitudes, and `G_*` as a rotation-invariant dressing.
The live repository contains no deterministic `Q/G_* -> Psi` map and no
covariance/composite alternative with all of the following frozen:

1. Fourier phases and `C^3` polarizations;
2. torus, reciprocal-shell, amplitude, intensity and `L2` conventions;
3. the image of the reference;
4. a motif and deterministic center/tie rule;
5. the periodic Voronoi/Delaunay construction; and
6. an exact or error-budgeted energy and ensemble intertwiner.

Therefore the new closed child concerns only the explicit P1 fixture.  The
gate
`PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE` remains open.
It may close by a hash-identical P1 map, in which case R-157 eliminates every
nonzero image, or by an explicitly different model/observable route carrying
its own sign, stationarity, stability and limit proofs.

## 10. Devil's-advocate audit

1. **Sign and factor.** The candidate-minus-reference convention is used in
   (2.1), (6.2) and (7.2).  The twelve characters, volume `16^3`, energy gap
   and radial gap are independently recomputed by both executable lanes.
2. **Center convention.** Centers are the global maxima of the field modulus,
   not visually chosen extrema.  The minimum of `pq+pr+qr` is `-1`, so no
   negative extremum ties the absolute maximum `3`.
3. **Period convention.** The field and modulus period groups are checked
   separately.  The possible global anti-period is explicitly ruled out.
4. **Geometry convention.** The extracted cells are Euclidean Voronoi cells
   of the exact center lattice `L`.  No affine image from R-169 v1.0 is called
   Euclidean Voronoi without a new metric proof.
5. **Units and normalization.** The calculation uses the side-16 continuous
   torus and its `L2` integral, not a grid sum or unit-volume normalization.
6. **Hardcode masking.** Derived counts, fractions, lattice solutions and
   margins are recomputed from labelled inputs.  Expected values occur only
   in the manifest's `test_oracles` and are compared with independent output.
7. **Limit cases.** `A=0` is the reference and lies outside the extracted
   candidate rule; center extraction is not applied to it (formally its
   modulus argmax is the whole torus).  Without a norm-density floor no
   thermodynamic uniform margin is inferred.  At `delta=g` or
   `delta_r=kappa`, strictness is lost.
8. **Model boundary.** The exact fixture does not create the missing Reading-H
   map, and R-157 does not apply inside a constraint that removes zero or the
   radial direction.

External review is invited on the Fourier support, equality cases,
anti-period argument, torus normalization, inherited R-157 scope, and the
separation between value and radial perturbation bounds.

## 11. Verdict

Close only
`PA-T055-PINNED-P1-BCC-PERIODIC-REALIZATION-EMPTY-REFERENCE-EXCLUSION`.
Keep the Reading-H interface, Round-1 and `C6-BCC-PREMISE-BLOCKED` open.
Register no new negative; reuse the R-157 nonzero-equilibrium boundary and
the R-169 v1.0 nonconstant-finite-part boundary.

This is T0 and claim-bearing false.  It proves no physical or cosmic empty
reference, global vacuum, BCC resurrection, thermodynamic/continuum result,
physical Sector-A result, C6 conclusion, or Pre-A closure.  No R-169 v1.1 PDF
is issued.
