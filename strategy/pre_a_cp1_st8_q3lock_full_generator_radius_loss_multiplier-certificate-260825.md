# Full-generator radius-loss multiplier certificate

## Scope

This T0, claim-nonbearing checkpoint determines the continuity shape required
by the quartic entire source topology from EXP-001115. It is scalar weighted
function arithmetic plus a conditional recurrence, not an unbounded Q3 theorem.

## Radius loss

For `||f||_sigma = sup_(x>=0) |f(x)| exp(-sigma x^4)`, multiplication by a
quartic source factor is measured from radius `sigma+delta` to `sigma`. With
`y=x^4`,

`sup_(x>=0) x^(4n) exp(-delta x^4)
 = sup_(y>=0) y^n exp(-delta y)
 = (n/(e delta))^n`.

The maximum occurs at `y=n/delta`. At the same radius (`delta=0`), the
multiplier `x^(4n)` is unbounded. Thus a Banach estimate at one fixed entire
radius cannot control the quartic source generator; a Frechet/radius-loss
scale is required by this scalar test.

If one *assumes* that the actual Q3 shifted-force insertion obeys this scalar
multiplier on one common core, and that each of six neighbours and both source
orientations contributes the same `M_1(delta)`, then the scalar recurrence

`B_(N+1) <= (1 + 12 M_1(delta) T/N) B_N`

has the conditional limit envelope `exp(12 M_1(delta) T) B_0`. The package
does not prove the assumptions. For `delta=1/10` and `T=1/5`, the exponent is
`24/e`.

## Adversarial review

1. **Calculus versus operator — OPEN.** The maximum formula is a weighted
   scalar-function result, not a Q3 operator norm or domain theorem.
2. **Same radius — UPHELD.** The polynomial multiplier itself is unbounded at
   `delta=0`; this rejects only the same-radius candidate.
3. **Recurrence — OPEN.** The six-neighbour/two-orientation recurrence is an
   explicit conditional input and does not conceal word incidence or Q3 force
   insertion.
4. **Volume/exhaustion — OPEN.** A scalar constant does not prove all-shape
   exhaustion Cauchy or common-alpha convergence.
5. **QFT promotion — OPEN.** KMS/GNS, gap, continuum, C6, Sector A and Pre-A
   remain open.
6. **Lean — UPHELD.** R288 checks rational fixtures only.

## Next gate

Prove the actual Q3 shifted-force insertion into a radius-loss seminorm on a
single common CCR core, with volume and orientation control. Then retest the
conditional recurrence against the dual modular and exhaustion requirements.

## Non-claims

This certificate does not prove actual Q3 dynamics, a thermodynamic QFT,
KMS/GNS, a gap or continuum limit, C6, Sector A, Pre-A, TECT production, or a
Clay result.
