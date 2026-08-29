# R-421 certificate — tail-supported Hardy ground-state transform

## Decision

R-421 is a T0, claim-nonbearing interface result for T-054.  It proves and
executes the finite reversible ground-state transform that sits immediately
under the R-419 logarithmic Lyapunov corridor.  The finite tail-supported
Hardy consequence passes on the selected R-419 Q3 rows and on an independent
non-importing graph family.  No uniformity or physical promotion is made.

For positive normalized weights `pi`, symmetric nonnegative conductances `c`,
and a strictly positive vector `V`, define

```text
(L V)_i = pi_i^(-1) sum_j c_ij (V_j - V_i),
h_i     = -(L V)_i / V_i.
```

The finite identity checked by the package is

```text
E(f) = sum_i pi_i h_i f_i^2
       + 1/2 sum_ij c_ij V_i V_j (f_i/V_i - f_j/V_j)^2,
E(f) = 1/2 sum_ij c_ij (f_i-f_j)^2.
```

The second term is nonnegative.  Consequently, if `f` vanishes outside a
declared tail `T` and `h_i >= kappa > 0` on `T`, then

```text
E(f) >= kappa sum_{i in T} pi_i f_i^2.
```

The conclusion is deliberately restricted to tail-supported functions.  It
does not control a core offset or the core-to-tail boundary term for a general
observable.

## Fixed parent and scope

The Q3 parent is the hash-pinned R-419 manifest
`strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json`
with SHA-256
`d5e2139c1a8af9b11f13098a8aaafabf66560bf08f011afb18900f50ae7e2881`.
Its functional, oscillator, conductance, log-domain normalization, beta
values, volume/cutoff grid and collar orientations are not changed.  R-421
uses volumes/cutoffs `(2,3)`, `(2,6)`, `(2,12)`, `(3,3)`, `(3,4)` and `(4,4)`,
beta in `{1/2,2,8}`, both orientations, `alpha=1/40`, and tail threshold
`theta=4`.

The Q3 lane checks every declared conditional row for those systems.  For
each row it forms the R-419 Lyapunov vector, computes the rate, and evaluates
the identity on four deterministic tail-supported test vectors.  A row with
no tail is not silently used as evidence for the tail inequality.

## Verification

The primary script imports only the registered R-419/R-416 construction for
the Q3 rows and computes the transform independently from those inputs.  The
independent script does not import the primary implementation; it rebuilds
the conductance, generator, Lyapunov vector and identity on deterministic
reversible graph fixtures.  The hostile script rejects asymmetry, nonpositive
weights or Lyapunov vectors, the wrong rate sign, omitted ground-state
remainder, unsupported non-tail vectors and a forged rate floor.

The Lean file proves the two-state rational identity, nonnegative remainder,
and the corresponding tail inequality.  It is an algebraic cross-check only;
it does not formalize the Q3 diagonalization, arbitrary finite sums, common
core, or any limit.

Expected commands are:

```text
python codes/foundations/pre_a_cp1_st8_q3lock_tail_hardy_ground_state_transform.py
python codes/foundations/pre_a_cp1_st8_q3lock_tail_hardy_ground_state_transform_independent.py
python codes/foundations/pre_a_cp1_st8_q3lock_tail_hardy_ground_state_transform_hostile.py
python codes/foundations/pre_a_cp1_st8_q3lock_tail_hardy_ground_state_transform_verify.py
lake env lean verification/lean/Tect/R421.lean
```

The integrated run must report a PASS for all executable lanes while retaining
the result as finite and claim-nonbearing.

## Adversarial review

1. **Generator sign.**  Reversing the definition of `h` destroys the claimed
   tail lower bound; the hostile lane rejects it.
2. **Ground-state remainder.**  Dropping the weighted square leaves an
   incorrect identity even for two vertices; the mutation is rejected.
3. **Conductance symmetry.**  The transform uses `c_ij=c_ji`; an asymmetric
   matrix is rejected before evaluation.
4. **Support scope.**  The Hardy consequence is only for vectors zero on the
   core; a nonzero core component is rejected as an out-of-scope application.
5. **Positivity.**  Nonpositive `pi` or `V` invalidates the divisions and is
   rejected rather than regularized.
6. **Uniformity.**  A finite positive minimum is not relabelled as a uniform
   constant; the manifest keeps cutoff, volume, phase and exhaustion flags
   open.
7. **Physical promotion.**  The transform is not promoted to global
   Poincare, OS/KMS/GNS, C6, Sector-A, Pre-A, Yang--Mills or mass-gap closure.

## Boundary and next action

The exact finite identity is a genuine route advance: it turns a positive
R-419 tail drift into a directly usable tail-supported form bound.  The next
proof obligation is a domain-controlled version on one unbounded Q3 common
core, with a uniform rate and a variance decomposition that pays the core
mean and boundary capacity for arbitrary R-399 observables.  Only after that
transfer can a global Poincare or broken-sector GNS gate be revisited.

R-421 therefore changes no claim tier, registers no negative result, and makes
no physical statement.
