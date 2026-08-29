# R-414 certificate — two-scale semigroup criterion for the normalized Green trace

## Question

Can the finite R-413 Mellin identity be reorganized into two budgets that
separate ultraviolet proper-time integrability from infrared spectral decay?

## Finite statement

Let the positive ordered spectrum of the normalized intrinsic operator be
`0 < lambda_1 <= ... <= lambda_m`, let

```
H(t) = sum_k exp(-t lambda_k),
G    = sum_k 1/lambda_k,
```

and fix `tau > 0`.  For any R-412 profile with an interior head length `r`
and UV exponent `0 < alpha < 1`, define

```
A_tau = r tau^alpha + C_UV alpha Gamma(alpha).
gamma  = lambda_1.
```

The finite lower-envelope inequality implies, for `0 < t <= tau`,

```
H(t) <= A_tau t^(-alpha).
```

The first positive eigenvalue gives, for `t >= tau`,

```
H(t) <= H(tau) exp(-gamma (t-tau)).
```

Consequently,

```
integral_0^tau H(t) dt <= A_tau tau^(1-alpha)/(1-alpha),
integral_tau^infinity H(t) dt <= H(tau)/gamma,
G <= A_tau tau^(1-alpha)/(1-alpha) + H(tau)/gamma.
```

The last display is a finite criterion.  It identifies three inputs that a
future uniform proof must control: the UV coefficient `A_tau`, the IR gap
`gamma`, and the split-time heat value `H(tau)`.

## Verification

The fixture uses the actual R-399 conditional likelihood rows for volume two,
cutoff dimensions `3,4,5,6,8,10,12`, beta values `{1/2,1,2}`, both source
signs, both history signs and orderings, all prefixes, both history adjoints,
and both collar orientations.  Every R-412 exponent pair and interior split
is evaluated at heat times
`{1/16,1/8,1/4,1/2,1,2,4}` with `tau=1`.

- Primary: `191471/191471` assertions.
- Independent plain-loop reconstruction: `191470/191470` assertions.
- Hostile lane: `9/9` mutations rejected.
- Integrated verifier: `42/42` checks.
- Lean: `lake env lean Tect/R414.lean` exits `0`.

The primary range of the first positive gap is
`[0.7570174175402339,5.647863075935399]`; the split-time heat value is
`[0.0036012445961644186,0.5926882083380163]`; and the selected finite Green
bound is `[3.6173095936923008,6.21959891996888]`.  The minimum Green-bound
slack is `2.936364851149518`, the minimum short-time power slack is
`1.117251065898148`, the minimum late-time exponential slack is zero at the
split point, and the maximum Mellin identity residual is
`3.885780586188048e-16`.  The independent lane agrees on these invariants
within the declared `5e-6` tolerance.

## Adversarial review

The hostile lane uses exact toy spectra to reject omission of the finite IR
head (`0.11755608825868386` short-budget deficit), omission of the UV term
(`0.13507226908622838` deficit), replacing the smallest positive eigenvalue
by the largest (`2.920502936517768` late-budget deficit), omitting the late
budget (`0.4775461490944841` Green-trace deficit), and shifting the late
exponential with the wrong time origin (`2.7432509056332397` deficit).  It
also rejects reversed time ordering (`0.2894603181637101` heat increase), a
wrong Mellin sign (`6.239564084015606` residual), and `alpha=1` before an
integral is formed.  These are finite shortcut tests, not asymptotic
counterexamples.

## QFT-facing interpretation

The split is a controlled proper-time interface: short Euclidean time carries
the UV power law, while late Euclidean time carries the IR decay rate.  In an
actual QFT construction this can be inserted between a Hamiltonian resolvent
estimate and an OS/KMS/GNS two-point function, but only after the constants are
uniform on one common core and the R-399 shell and R-406 Schur residual have
been transferred.

## Boundary and next gate

R-414 is T0 and claim-nonbearing.  It proves no cutoff-, volume-, source-,
phase- or exhaustion-uniform UV coefficient or IR gap, no common split rule,
no common Hamiltonian core, no OS/KMS/GNS reconstruction, no physical mass
gap, and no continuum, C6, Sector-A or Pre-A closure.  The next proof
obligation is an analytic estimate for `A_tau`, `gamma`, and `H(tau)` on one
Hamiltonian common core, followed by transfer to the R-399 shell and the
R-406 harmonic/Schur split.  If the first positive gap collapses under a
validated growing-cutoff or growing-volume stress, retain only the UV half
and record that route-local obstruction.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge_hostile.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge_verify.py --self-test --reuse-existing
lake env lean verification/lean/Tect/R414.lean
```

The run artefacts are stored under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-{primary,independent,hostile,integrated}-pre_a_cp1_st8_q3lock_two_scale_semigroup_bridge/`.
