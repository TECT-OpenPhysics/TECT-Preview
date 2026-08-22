# R-194 — Sharp running-mass counterterm boundary

## 1. Result and scope

EXP-000932 establishes R-194 as a T0, claim-nonbearing exact algebra and
route-boundary audit for `A6-CLASSII-COUNTERTERM-CLOSURE`. It does not change
the A6 claim tier or close either A6 open gate.

## 2. Exact boundary

For the pinned Fierz density, with `s=|Psi_1|^2+|Psi_2|^2`,
`rho=s+|Psi_3|^2`, and `g=a+2*b+c`,

```text
W_eps=9*g*s-6*b*s^2/(rho+eps)
       -3*c*s^2*(rho+2*eps)/(rho+eps)^2.
```

The minimal pointwise running coefficient is `h_min=9*g`, because

```text
h_min*s-W_eps
 = 6*b*s^2/(rho+eps)
   +3*c*s^2*(rho+2*eps)/(rho+eps)^2 >= 0
```

on the registered production scope `b,c>0`. For `h<h_min`, the ratio of
the difference to a fixed positive `s` tends to `h-h_min<0` as the third
component grows, so the smaller coefficient fails. At `h=h_min`, the same
ratio tends to zero. This is a sharp local threshold followed by a
noncoercive escape, not a uniform stability estimate.

## 3. Cross-check lanes

The repository-pinned Lean file `verification/lean/Tect/R194.lean` compiles
without `sorry`, `admit`, `axiom` or `unsafe`. It proves the endpoint identity,
endpoint nonnegativity, and a pinned exact sub-threshold witness. The primary
and non-importing independent Fraction lanes derive all coefficients from
the hash-pinned A1 manifest and reproduce the exact rational checks. The
integrated verifier checks all source hashes, child agreement, Lean output,
hostile mutations and the declared no-overclaim boundary.

## 4. Adversarial review

1. **Sign/factor objection — UPHELD against a bad repair.** The endpoint
   identity retains both rational correction terms and the factor 9.
2. **Coefficient objection — UPHELD against hardcoding.** `a,b,c` are loaded
   from the A1 manifest; no derived decimal is used as an authority input.
3. **Uniformity objection — UPHELD.** The threshold gives no positive uniform
   `kappa*s` because of the large third-component escape.
4. **Local-to-global objection — UPHELD.** The local algebra is not a spatial
   partition/tightness estimate and cannot be promoted to a Gibbs theorem.

## 5. Boundary and next obligation

The existing fixed-parameter subtraction no-go is strengthened without
registering a new negative. The next admissible route must freeze all
relevant coefficient trajectories, including third-component terms, and then
prove spatially correlated partition and tightness estimates. A6,
A7-self-coupling, A13, Pre-A and physical-empty/C6 gates remain open.

No R-194 PDF is issued.
