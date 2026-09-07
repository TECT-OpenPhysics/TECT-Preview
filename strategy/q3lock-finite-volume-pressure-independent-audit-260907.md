# Q3LOCK A1--A5 finite-volume and pressure audit

Date: 2026-09-07. Exploration: EXP-001632. Task: T-054.
Status: T0 internal adversarial audit, claim_bearing=false, not a signed
independent review.  The sole Q3LOCK research authority remains
EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.  The paper PDF remains
deferred.

## Scope

This audit checks only the first five load-bearing rows of
`publish/papers/q3lock-phase-coexistence/proof-audit.md`:

* A1: the printed eight-component Hamiltonian and common finite-volume form;
* A2: finite trace, min--max comparison, and the distinction between an
  entire partition function and a merely real-analytic logarithm;
* A3: cyclic time-mesh determinant, fixed-volume loop convergence, and the
  absolute harmonic Feynman--Kac normalization;
* A4: periodic seam counting and the trace sandwich; and
* A5: open-box pressure, arbitrary even rectangular exhaustions, and transfer
  from open to periodic cubes.

No infinite-volume, DLR, FKG, reflection, infrared, cusp, or phase claim is
accepted by this note.

## A1: model and form domain

The manuscript defines `q_y in R^8`, the collective unit vector
`u=8^(-1/2)(1,...,1)`, the onsite coordinate quartic, the nonnegative Q3
locking polynomial, and the spatial difference form before introducing
`H_L(h)`.  The declared form domain is

```text
H^1(R^(8V)) intersect L^2(R^(8V), (sum_y |q_y|^4) dq).
```

The Q3 and spatial terms are nonnegative.  The scalar inequality
`sum_e q_e^4 >= |q|^4/8`, followed by Young bounds for the residual quadratic
and source terms, leaves the positive coefficient `g/128` used in the
finite-volume residual lower bound.  This supplies a common closed
semibounded form at each fixed `L` and source window.  No radial or
O(8)-invariant assumption is inserted into this step.

The remaining external-review question is not the model transcription but
the precise choice of a common operator/form core when the harmonic
Feynman--Kac representation and later unbounded multipliers are invoked.

## A2: trace and source analyticity

From `R_(a,h) >= (g/128) sum_y |q_y|^4 - V C`, the form inequality
`H_L(h) >= H_a - V C` gives an eigenvalue-by-eigenvalue min--max comparison.
It therefore yields the displayed upper bound by the positive harmonic
oscillator trace; it does not use a false operator-monotonicity assertion for
the exponential.  Positivity of the trace follows from the finite confining
operator.

The integrated collective source is quartically dominated.  Young's
inequality gives exponential moments of every finite order, so the finite
volume `Z_L(z)` is entire in the complex source.  The manuscript correctly
does not infer that `log Z_L(z)` is globally entire: complex zeros can occur.
For real `h`, positivity of `Z_L(h)` gives local holomorphic logarithms and
real analyticity of the pressure, which is all that the later convexity
argument uses.

The remaining review point is to check the form realization and the
source-derivative interchange at the exact stated domain, rather than to
replace it by the stronger unbounded semigroup theorem that the manuscript
explicitly does not cite.

## A3: cyclic mesh, loop limit, and absolute normalization

For the cyclic mesh, the precision eigenvalues are the harmonic factor times
`a + 4 m eps^(-2) sin^2(pi n/N)`.  The recurrence with initial values
`T_0=2`, `T_1=2+t`, `T_j=(2+t)T_(j-1)-T_(j-2)` gives the cyclic determinant and
the displayed `2 sinh(N asinh(beta omega_a/(2N)))` expression.  The continuum
covariance is obtained from the summable Fourier series.

At fixed `L,beta,m,a`, the manuscript separately controls covariance error,
arbitrary-time increments, and fourth moments of the interpolated Gaussian.
This is the correct order for tightness: grid covariance convergence alone
would not prove weak convergence on the continuous-loop space.  The residual
weights then converge uniformly on compact loop sets, while the quartic lower
bound supplies a common upper bound and Jensen supplies a positive normalizer.
The resulting statement is weak convergence, not total variation.

The absolute trace step is correctly isolated from a normalized path-measure
identity.  Simon's finite-dimensional free-bridge theorem is the imported
input; the mass change, harmonic bridge density, truncation of an unbounded
residual from above, and Tonelli trace identity are manuscript arguments.
They require a signed check of form convergence, kernel continuity, and the
majorant, but they do not silently import an infinite-volume theorem.

## A4: periodic seam

For an even `L>=4` cube, the periodic-to-open difference has `3 L^2` added
bonds.  Each bond contributes two endpoints and each endpoint has eight
scalar coordinates, giving `48 L^2` scalar endpoint occurrences.  The
coordinate inequality

```text
c x^2 <= (eta g/24) x^4 + 6 c^2/(eta g)
```

combined with at most three seam occurrences per scalar coordinate produces
the quartic budget `eta Q_L` and the constant `288 c^2 L^2/(eta g)`.  Thus the
coefficient 288 is the endpoint count multiplied by the scalar Young
constant; replacing it by the historical 48 would omit the three endpoint
incidences and is not the displayed inequality.

Using the retained quartic lower bound gives
`H_op <= H_per <= (1+eta) H_op + D_L`.  The trace sandwich follows from the
same eigenvalue comparison and is used without differentiating a finite-
volume trace with respect to `eta`.

## A5: open pressure and periodic transfer

Cutting positive crossing bonds makes the open-box log trace subadditive.
Tiling an arbitrary even rectangle by a fixed even block plus finitely many
remainder rectangles makes the remainder-volume fraction tend to zero.  The
two-sided harmonic/Jensen and coercive bounds provide a finite lower and upper
normalization for the remainder contribution, so the subadditive infimum is a
finite limit along arbitrary even rectangular exhaustions.

For the seam transfer, the manuscript enlarges the beta and source window,
uses convex endpoint secants in beta and source, and chooses `eta=L^(-1/2)`.
This avoids an illicit exchange of a volume limit with a beta derivative.  The
result is a local-uniform periodic pressure limit and, at differentiability
points of the limiting pressure, convergence of the finite-volume source
derivatives.  No differentiability at the origin is assumed.

The signed review must still inspect the form-to-trace comparison with a
possibly nonpositive open Hamiltonian, the finite partition of the remainder
region in the arbitrary-rectangle argument, and the exact enlarged compact
parameter window used by the secant bounds.  These are the remaining A5
interfaces, not reasons to promote the row internally.

## Adversarial dispositions

| Objection | Internal disposition | Boundary |
|---|---|---|
| An entire `Z_L(z)` implies an entire `log Z_L(z)` | Rejected | Complex zeros still require local logarithms only. |
| The seam coefficient 288 is an arbitrary safety factor | Rejected at the displayed counting level | The endpoint multiplicity and Young allocation are explicit; an independent referee must still check the form inequality. |
| Grid covariance convergence alone proves the continuous-loop limit | Rejected | The manuscript separately supplies arbitrary-time tightness and fourth moments. |
| A normalized KP/Feynman--Kac identity proves the absolute heat trace | Rejected | The harmonic factor and Tonelli trace step are retained as manuscript obligations. |
| Pointwise pressure convergence alone proves the periodic source derivative limit | Rejected | Local-uniform convergence and convex secant squeezing are used. |
| These finite-volume checks prove the DLR phase theorem | Rejected | A6--A23 and the external reviews remain open. |

## Disposition and next gate

No contradictory algebraic or limit-order defect was found in this bounded
internal reread.  The result is an **advanced T0 internal A1--A5 audit**, not
`PASS` in the independent-review table.  A1--A5 remain `OPEN` until a
reviewer supplies location-specific acceptance or repairs, especially for
the finite-dimensional form/kernel interface and the pressure seam transfer.

The next gate is an independent review of these five rows against the cited
Simon input and the exact form/trace hypotheses, followed by a separate audit
of A6--A13.  No claim tier, publication status, priority statement, or PDF
status changes.

## Explicit nonclaims

This note does not prove infinite-volume compactness, continuous-loop FKG,
reflection positivity, an infrared lower bound, a strict cusp, DLR
multiplicity, extremality, purity, clustering, KMS dynamics, a ground-state
gap, a continuum limit, a physical vacuum, or any TECT/C6/CP1/Sector-A
conclusion.  The strict sufficient regime and all later phase conclusions
remain conditional on the unresolved gates.
