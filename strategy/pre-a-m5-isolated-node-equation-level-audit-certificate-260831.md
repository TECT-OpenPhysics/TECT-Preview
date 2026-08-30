# R-458 certificate: M5 chiral isolated-node equation-level audit

## Identity and route role

- Result: `R-458`
- Candidate: `PA-M5-ISOLATED-NODE-CHIRAL-HAMILTONIAN-v0`
- Exploration: `EXP-001331`
- Task: `T-054`
- Claim bearing: `false`; tier: `T0`
- Status: `M5_EQUATION_LEVEL_AUDITED_NOT_ADMITTED`
- Route role: additive finite design-quality gate after the M3 equation audit. It does not replace T-054, T-059, T-061, the source-owner order, or any promotion firewall.

## Exact finite scope

The parent design is used by reference without changing its periodic cubic
regulator, four-component complex field, canonical momentum, Wilson symbol,
`m=0` convention, Hamiltonian, or symplectic convention. The audit covers
`L=2,3,4,5,6,8`, the exact representation

`alpha_i = sigma_i tensor sigma_1`, `beta = I tensor sigma_3`,
`Gamma = I tensor sigma_2`,

and the finite symbol

`h(k) = sum_i sin(k_i a) alpha_i + r sum_i(1-cos(k_i a)) beta`.

No floating-point zero test is used for the node statement. The Wilson term is
handled with `1-cos(theta)=2 sin(theta/2)^2`; on the declared modular grid it
vanishes only when every mode coordinate is zero modulo `L`. The formal Taylor
check is truncated at degree four and is not a regulator or continuum bound.

## Audited identities and evidence

The primary exact matrix/finite-grid lane passes **56,076/56,076** assertions;
the non-importing independent lane passes **56,074/56,074**; the hostile lane
rejects **12/12** mutations; the integrated verifier and pinned Lean R458 pass.
Coverage is:

- 952 finite momentum modes, with 946 non-origin modes;
- 26 exact Clifford/chiral matrix checks;
- 2,500 symbol Hermiticity, square, chiral and quadratic-even checks;
- 6 formal Taylor checks (two per `r` value);
- 24 phase/chiral observable checks;
- 50,625 finite coercivity checks over the declared parameter and vector fixtures.

The finite statement is:

1. Every displayed matrix is Hermitian and an involution; the required
   anticommutators vanish exactly.
2. `h` is Hermitian and `h^2 = (sum sin^2 + w^2) I`; `Gamma h Gamma = -h`
   and `Gamma h^2 Gamma = h^2` for the exact integer coefficient fixtures.
3. The Wilson term and symbol zero are unique at the origin on each declared
   finite grid. Near the origin, the degree-two term of `h^2` is exactly
   `|k a|^2`, so the formal leading singular-value ratio is one.
4. The declared norm and chiral-density observables are invariant under the
   tested global phases and chiral involution. Positive kinetic, quadratic,
   quartic (`lambda >= 0`) and sextic (`eta > 0`) pieces give a finite lower
   bound. Canonical flow equivariance and global finite-flow interpretation
   remain conditional on the displayed generator and energy-conservation
   premise.

Lean `R458.lean` checks the scalar sum-of-squares node implication, the Wilson
positivity proxy, the chiral-even square identity, the sextic sign and the
source-owner firewall. Python performs the exact 4-by-4 matrix products and
finite-grid coverage.

## Adversarial disposition

The hostile mutations cover a Clifford entry/sign error, omission of the
Wilson term, unfixed mass, chiral-breaking term, nonpositive `eta` or `r`, a
broken `Gamma` involution, finite-to-continuum promotion, QFT/Yang--Mills
promotion, physical-empty relabeling, candidate selection without a map, and
source-owner admission. All are rejected. A finite node is not called a
physical Weyl/Dirac particle; chiral protection is restricted to the declared
symmetry class; and no matrix or Lean check is treated as a source-owned
dynamics or observation result.

## Assumptions, missing assumptions, and boundary

Assumptions are exactly the hash-pinned parent equations, the displayed
complex matrix representation, modular finite-grid convention, formal
small-angle series, and conditional canonical-generator interpretation.
Missing are a versioned source owner, state/ensemble or quantum representation,
uncertainty/covariance, a candidate-neutral dynamic discriminator, uniform
limits and counterterms, the complete `F_reg/F_lim/F_eff/F_obs` map, physical
projection, and a genuinely prospective holdout.

Therefore R-458 is a **T0 finite equation-level consistency audit only**. It
does not admit or select M5, close Pre-A or Sector-A, identify a QFT,
Yang--Mills or gravity model, establish a physical node or massless particle,
evaluate Reading-H physical-empty sign/stationarity/stability, or prove a
continuum or mass gap. Existing T-054/T-059/T-061 methods, owner order and
promotion firewalls are unchanged.

## Next gate

Use R-458 only as a finite M5 design-quality input. Do not score or select M5
until a source-owned generator/state/projection/boundary, complete uncertainty
and four-stage map, candidate-neutral two-time observable, and prospective
holdout are hash-pinned. Continue the unchanged T-054 Q3LOCK owner intake and
the T-059/T-061 observation-source intake; do not create another finite node
or mobility surrogate in the absence of a new owner hash.
