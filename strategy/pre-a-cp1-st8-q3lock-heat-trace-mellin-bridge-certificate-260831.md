# R-413 certificate - Mellin heat-trace bridge for mixed IR/UV counting

## Scope

R-413 is a T0, claim-nonbearing finite checkpoint under EXP-001258.  Let
`lambda_1 <= ... <= lambda_m` be the positive spectrum of
`W = D_pi^(-1/2) L D_pi^(-1/2)`.  For any R-412 profile with split `r` and
`0 < alpha_IR,alpha_UV < 1`, put
`L_k=(k/C_IR)^(1/alpha_IR)` on the head and
`L_k=(k/C_UV)^(1/alpha_UV)` on the tail.  The finite Mellin identity is

```
tr(W^+) = integral_0^tau H(t) dt
          + sum_k exp(-tau lambda_k)/lambda_k,
H(t) = sum_k exp(-t lambda_k).
```

The second term is nonnegative.  The mode lower envelopes imply the finite
heat sum bound and the safe continuous UV comparison

```
H(t) <= sum_(k<=r) exp(-t L_k)
       + C_UV alpha_UV Gamma(alpha_UV) t^(-alpha_UV).
```

Integrating from zero to `tau` gives a finite short-time UV budget because
`alpha_UV<1`; the late remainder is bounded by the finite sum of
`exp(-tau L_k)/L_k`.

## Verification

The volume-two fixture uses dimensions `3,4,5,6,8,10,12`, beta in
`{1/2,1,2}`, both source signs, both history signs, both orderings, all
prefixes, both history adjoints and both collar orientations.  Every row
enumerates all 25 exponent pairs and every interior split, then checks seven
positive heat times and `tau=1`.

The primary lane passes `212594/212594` assertions over 7 systems, 2688
contexts and 21120 conditional rows.  The independent plain-loop lane passes
`149230/149230` on the same grid.  The hostile lane passes `8/8`, the
integrated verifier passes `44/44`, and Lean R413 compiles with exit code 0.
The inverse-trace range is `[0.44413751605172147,2.0052069566897663]`.
The primary/independent continuous-UV heat slack is
`2.4381603017647795e-05` (the independent value agrees within the declared
`5e-6` cross-check tolerance); the minimum short-time budget slack is
`0.1831599576706407`; the minimum Mellin remainder is
`0.0006317091718291228`; and the maximum Mellin identity residual is
`1.7763568394002505e-15`.  The largest observed heat value is
`4.564774679110289`, and the largest adjacent-time increase is negative
(`-1.2429200624632712e-05`), so the sampled heat trace is strictly decreasing.

## Adversarial review

1. **UV omission.**  On an exact two-mode toy, omitting the UV term leaves a
   short-time deficit `0.4323323583816936`; the shortcut is rejected.
2. **IR omission.**  Omitting the IR head from the late remainder leaves a
   toy deficit `0.3678794411714424`; the late budget must retain the head.
3. **Time exponent.**  Replacing `t^(-alpha_UV)` by `t^(alpha_UV)` gives a
   minimum toy slack `-0.56916836825572` and fails.
4. **Counting power.**  Replacing the reciprocal mode power by the direct
   `lambda^alpha` power gives a small-spectrum slack `-0.04092588658315521`.
5. **Time ordering.**  Reversing the time grid produces heat increases of
   `0.38489600036266314` and `1.476288952842503` on the selected rows.
6. **Mellin sign.**  Subtracting the late remainder instead of adding it
   produces residuals `1.2554255560671501` and `0.03827749454306026`.
7. **Divergent tail.**  A mutated `alpha_UV=1` is rejected before any
   integral budget is formed.
8. **Finite versus uniform.**  The row-wise optimizer and the seven heat
   times are diagnostics only; no common split or regulator-independent
   constant is inferred.

## Decision and next gate

R-413 advances a concrete heat-domain target: prove one controlled split time,
one IR/UV split rule and positive uniform constants on a Hamiltonian common
core, then transfer the short-time/late-time budget to the R-399 conditional
shell and combine it with the R-406 Schur residual.  The continuous UV term is
an explicit Mellin envelope, not a proof of ultraviolet renormalisation.

## Boundary

No cutoff-, volume-, source-, phase- or exhaustion-uniform budget is claimed.
No common core, common split rule, Hamiltonian-to-OS/KMS/GNS identification,
physical mass gap, continuum, C6, Sector-A or Pre-A closure follows.  No tier
change, negative result or PDF is issued.

**Proven in:** primary/independent/hostile/integrated scripts, Lean entrypoint,
the scope note, and saved run artefacts listed in the manifest.
