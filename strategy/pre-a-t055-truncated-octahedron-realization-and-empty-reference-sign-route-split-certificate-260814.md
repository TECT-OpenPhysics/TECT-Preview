# R-169 v1.0 certificate: truncated-octahedron realizations and the empty-reference sign route

Date: 2026-08-14  
Task: T-055  
Tier: T0, `claim_bearing:false`

Formal exploration: `EXP-000851` (reserved after the independently landed
geometry/Q3LOCK interface record `EXP-000850`).

## 1. Exact scope

This certificate does two things and no more.

First, it separates three meanings of "truncated octahedron": the exact
metric-regular BCC Voronoi cell, an affine-combinatorial translational tile,
and a statistically extracted Reading-H cell. Second, it proves a conditional
matched-renormalization theorem that transfers a certified finite-regulator
margin to a below-preregistered-reference limiting sign and a separate
transverse-Hessian margin to local stability modulo declared symmetries.

The scoped CLOSED children are

`PA-T055-TRUNCATED-OCTAHEDRON-BCC-VORONOI-AND-AFFINE-REALIZATION-FAMILY`

and

`PA-T055-MATCHED-RENORMALIZATION-EMPTY-REFERENCE-SIGN-AND-TRANSVERSE-STABILITY-REDUCTION`.

Neither child computes the TECT sign. The old BCC claim remains retired, and
`C6-BCC-PREMISE-BLOCKED` remains OPEN.

## 2. The exact metric-regular BCC Voronoi fixture

Let

```text
L = span_Z{(4,0,0),(0,4,0),(2,2,2)}
  = 4 Z^3 union ((2,2,2)+4 Z^3)
```

and let

```text
P = {x in R^3 : |x_i| <= 2 and sigma dot x <= 3
                  for every sigma in {+1,-1}^3}.
```

The coordinate inequalities are the perpendicular-bisector inequalities for
the six lattice vectors `+/-4e_i`. The other eight displayed inequalities are
the bisectors for the vectors `2 sigma`.

To see that no omitted lattice vector cuts `P`, write every lattice vector as
`v=2n`, where the three entries of `n` have the same parity. If `n` is even
and is not one of the six coordinate nearest vectors, or if `n` is odd and is
not one of the eight all-unit vectors, then

```text
2 sum_i |n_i| <= sum_i n_i^2.
```

For even entries this follows termwise from `k^2>=2|k|` for nonzero even
`k`. For odd entries outside the all-unit case, one entry has magnitude at
least three, so its surplus offsets the two possible unit deficits. Since
`|x_i|<=2`,

```text
x dot v <= 4 sum_i |n_i| <= 2 sum_i n_i^2 = |v|^2/2.
```

Thus every omitted Voronoi inequality is redundant and `P=Vor_L(0)`.

Exact intersection enumeration gives the 24 vertices obtained by permuting
`(0,+/-1,+/-2)`. Each of the six coordinate faces has four vertices and is a
square; each of the eight signed-diagonal faces has six vertices and is a
regular hexagon. Double-counting face-edge incidences gives 36 edges, hence
the f-vector is `(24,36,14)` and Euler's identity is `24-36+14=2`. The basis
determinant is 32, the fundamental volume.

This is the metric-regular reference. It is not evidence that TECT selects it.

## 3. Affine-combinatorial realizations are not a finite list

For `t>1`, put

```text
D_t = diag(t,1,t^(-1)).
```

Then `det(D_t)=1`. Applying `D_t` to the exact partition `P+L` proves that
`D_t P + D_t L` is again a face-to-face translational tiling. Invertibility
preserves the face lattice, so every cell still has six quadrilateral and
eight hexagonal descendants.

The opposite-cell translations through descendants of the six quadrilateral
facets have lengths `{4t,4,4/t}`. Their maximum/minimum ratio is `t^2`, an
Euclidean-similarity invariant. Therefore distinct `t>1` give pairwise
nonsimilar, noncubic affine-combinatorial realizations. There are uncountably
many.

This does not say that `D_t P` is the Euclidean Voronoi cell of `D_t L`; in
general it is not. It says only that it is an exact affine translational tile
with the same combinatorics. A finite candidate scan is consequently honest
only after it freezes a parameter domain, an equivalence relation, a
resolution, and a coverage error. Metric-regular, affine-combinatorial, and
statistically extracted meanings cannot be interchanged after data are seen.

This proves the exact obstruction

`NG-2026-08-14-PRE-A-T055-TRUNCATED-OCTAHEDRON-COMBINATORICS-AUTOMATIC-FINITE-REALIZATION-ENUMERATION`.

## 4. Candidate and competitor freeze

Before a Reading-H scan, each realization record must freeze:

- the geometry meaning;
- the center-extraction rule, thresholds, tie breaking, boundary convention,
  input hash, and defect policy;
- the regulator, physical box and volume, equivalence group, realization
  parameters, and face-incidence or statistical observable;
- the parent functional, candidate and reference constraints, beta or ground
  convention, units, counterterm basis and coefficients including finite
  parts, renormalization conditions, and limit order;
- the exact symmetry group, full admissible tangent, transverse projector,
  Hessian form, and all error budgets.

The minimum competitor set contains the metric-regular BCC fixture, one
declared noncubic affine-combinatorial realization, the preregistered
zero/disordered reference, and one non-truncated negative control. Natural
foam analogues remain diagnostic controls rather than TECT dynamics.

## 5. Matched renormalization and what actually cancels

For regulator `a`, physical volume `V_L`, and one common parent, write

```text
Gamma_ren_(a,L)[phi]
  = Gamma_bare_(a,L)[phi]
    + sum_(nu=0)^m c_nu(a) O_(nu,a,L)[phi],
O_0[phi] = V_L.
```

The candidate and reference use the same state/configuration space, measure
or algebra, beta or ground convention, boundary conditions, units, bare
couplings, counterterm basis, coefficient trajectory including finite parts,
and renormalization conditions. Define

```text
Delta_(a,L)^r
  = V_L^(-1){Gamma_ren_(a,L)[phi_r]
             -Gamma_ren_(a,L)[phi_0]}.
```

The common state-independent scalar `c_0(a)V_L` cancels exactly. A common
state-dependent counterterm does not cancel merely because its coefficient is
the same:

```text
Delta O_nu^r
  = V_L^(-1){O_nu[phi_r]-O_nu[phi_0]}
```

remains in the answer for `nu>=1`. Its finite part must be fixed by common
renormalization conditions or bounded uniformly over one preregistered scheme
class. A common counterterm basis without its finite parts is not a sign
definition.

The reference `0` is a preregistered constrained zero/disordered branch. It is
not automatically physical or cosmic empty space, and another unconstrained
equilibrium phase of the same Hamiltonian cannot provide a strict bulk
empty-reference sign.

## 6. Signed-limit theorem

Freeze the order

```text
d_a^r = lim_(L->infinity along the declared van-Hove sequence)
          Delta_(a,L)^r,
DeltaF_ren^r = lim_(a downarrow 0) d_a^r.
```

No exchange of these limits is asserted. Suppose certified approximants obey

```text
|Delta_(a,L)^r-Deltahat_(a,L)^r| <= e_num,
|Delta_(a,L)^r-d_a^r|            <= e_TD,
|d_a^r-DeltaF_ren^r|             <= e_UV,
scheme variation                 <= e_sch.
```

If one fixed `eta>0` satisfies, eventually along this path,

```text
Deltahat_(a,L)^r + e_num + e_TD + e_UV + e_sch <= -eta,
```

then the triangle inequality gives

```text
DeltaF_ren^r <= -eta < 0.
```

Conversely, an eventual certified lower bound at zero rejects the candidate
on the declared path. A negative number at each finite regulator is not a
strict limiting sign without a uniform margin: `Delta_n=-1/n<0` but
`lim_n Delta_n=0`.

This theorem proves only "below the preregistered reference in the frozen
scheme and limit order." It does not prove global selection among all states.

## 7. Transverse-Hessian theorem

Require full regulated stationarity

```text
D Gamma_ren_(a,L)[phi_r] = 0
```

on the full admissible tangent, not only within the candidate ansatz. Let
`N_(a,L)^r` be the orthogonal complement of the exact symmetry/gauge orbit
tangent inside that full tangent, and put

```text
lambda_perp_(a,L)
  = inf_{v in N_(a,L)^r, ||v||=1}
      <v,D^2 Gamma_ren_(a,L)[phi_r]v>.
```

Assume a declared identification of the regulated candidates and transverse
spaces with the limiting candidate and form domain. Also require that the
limiting candidate is stationary on its limiting symmetry slice, either as an
explicit premise or by certified convergence of the regulated gradients with
a residual tending to zero. Hessian convergence alone does not remove the
linear Taylor term. If the total certified form error is `e_H` and

```text
lambdahat_perp_(a,L)-e_H >= kappa > 0
```

eventually, form-liminf passage gives limiting transverse coercivity at least
`kappa`. If the stationary limiting Hessian is locally `M`-Lipschitz on the
symmetry slice,
Taylor's theorem gives

```text
Gamma(phi_r+v)-Gamma(phi_r)
  >= (kappa/4)||v||^2
```

for transverse `||v||<=kappa/(2M)`. This is strict local stability modulo the
declared group. Merely nonnegative curvature gives only semistability. Sign
plus local stability still does not give exhaustive or global selection.

## 8. Exact finite-part and route-split fixture

Consider the polynomial, independent of `z`,

```text
Phi_(alpha,tau)(x,y,z)
  = x^2(x^2-1)^2 + alpha(2x^2-x^4)
    +(1-tau x^2)y^2+y^4.
```

Project out the `z` zero direction. At

```text
h=(1,0,0),  zero=(0,0,0),  r=(2,0,0)
```

the candidate and reference are stationary and exact differentiation gives

```text
Phi(h)-Phi(zero) = alpha,
Phi(r)            = 36-8alpha,
H_h^perp          = diag(8-8alpha,2-2tau).
```

For `(alpha,tau)=(1/4,0)`, the candidate beats the tested competitor
`1/4<34` and is strictly transverse-stable with Hessian `diag(6,2)`, but it
lies above the reference by `1/4`. For `(-1/4,2)`, it lies below the reference
by `-1/4` but is a transverse saddle with Hessian `diag(10,-2)`.

The `alpha(2x^2-x^4)` term is a shared, nonconstant, symmetry-allowed finite
direction. Leaving its finite coefficient free changes both the relative sign
and the Hessian, while a shared scalar still cancels. Thus a common
counterterm basis without fixed finite parts does not determine the sign.
This proves

`NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN`.

The fixture also sharpens, but does not replace, the existing retired-BCC
boundary: tested ranking and local stability do not imply a below-reference
sign, and a below-reference sign does not imply stability.

## 9. Nonduplication and open parents

`R-2026-06-23-b3-bcc-structural-selection` remains the model-specific
retirement authority. `NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR`
remains the scalar absolute-anchor boundary.
`NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE`
remains the same-Hamiltonian equilibrium comparator boundary.

The new finite-part obstruction is different: a nonconstant common operator
changes candidate and reference by different amounts, so sharing only the
basis leaves the relative sign and Hessian unfixed. The new realization
obstruction is also different: it rejects a finite exhaustive geometric list
before any energy is computed.

EXP-000847--849 prioritize and calibrate the geometry programme; they contain
no matched-scheme sign or Hessian theorem. R-169 v1.0 supplies those exact
reductions without promoting a physical result.

## 10. Devil's-advocate and code-discipline audit

1. **Sign.** The relative density is always candidate minus reference. The
   certified upper margin therefore has the form `estimate+errors<=-eta`.
2. **Factors and conventions.** The Voronoi plane for lattice vector `v` is
   `x dot v=|v|^2/2`; the Hessian is the real second variation after symmetry
   directions are removed. Face-edge incidences are divided by two.
3. **Units.** The geometry fixture is dimensionless. The theorem compares
   densities in one declared physical-volume and energy-unit convention.
4. **Convergence.** The van-Hove limit precedes the continuum limit. No limit
   exchange, single-box inference, or pointwise-to-uniform inference is used.
5. **Hardcode masking.** Both executable lanes derive vertices, incidences,
   determinants, renormalization differences, margins, gradients, and Hessians
   from labelled inputs. Expected values are isolated as `test_oracles`.
6. **Limit cases.** `t=1` returns the metric BCC point; singular `t` is
   excluded. `eta=0` gives no strict sign. `kappa=0` gives no strict local
   minimum. `Delta_n=-1/n` audits loss of strictness in the limit.
7. **Adverse interpretations.** An affine tile is not silently called a
   Euclidean Voronoi cell; a constrained reference is not silently called
   physical empty space; a local minimum is not called a global vacuum.

External adversarial review is invited on the lattice parity argument, affine
similarity invariant, counterterm finite-part convention, error composition,
symmetry-slice form passage, and polynomial fixture.

## 11. Reproduction and no-overclaim

The primary, non-importing independent, and integrated scripts recompute all
exact fixtures. During proof development they run with `--staged --no-store`;
formal integration stores three JSON artifacts under the C6 run tree.

No TECT realization energy, Reading-H center extraction, exhaustive geometric
classification, physical-empty reference, global vacuum, BCC resurrection,
C6 spacetime result, Sector-A result, or Pre-A closure is established. Both
`C6-BCC-PREMISE-BLOCKED` and
`PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE` remain OPEN. No R-169
v1.0 PDF is issued.
