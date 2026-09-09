# PAH-OMC-020 R-551 — exact finite second-order semigroup defect

## Scope

This checkpoint tests one precise implication only: whether the unchanged
PAH-001 generator identity registered by R-493 can be iterated at one fixed
finite successor pair and therefore exponentiated to a finite stationary
semigroup identity.  It uses the original external stochastic Markov time.
It does not add a rate, counterterm, carrier, state mixture, or physical
interpretation.

The preregistered witness is `n=3`, `n+1=4`, `R_max=1`,
`f=ell_(0,0)`, and `sample_state(4,3)`.  R-493's support calculation gives
`m_f=2`, hence `N(f)=max(2,m_f+1)=3`; the witness is exactly at the declared
threshold, not below it.

## Exact finding

The first-order defect is exactly zero:

```text
L_4 I_(3,4) f - I_(3,4) L_3 f = 0.
```

The second-order defect computed from the same directed roots, affected PAH
energy terms, midpoint rates and projection is

```text
D = L_4^2 I_(3,4) f - I_(3,4) L_3^2 f
  = 1/2 [ exp(-67/24) + exp(-59/24)
          - exp(-25/8) - exp(-17/8) ]
  = -1/2 exp(-25/8) (exp(1/3)-1)^2 (exp(1/3)+1) < 0.
```

The primary replay derives the exponential polynomial in the exact field
`Q(sqrt(2))` and checks every local affected-term delta against the full
frozen energy.  The independent replay recomputes both generator applications
using direct full-energy floating-point transitions.  The hostile replay
rejects a below-threshold witness, changed-rate mutation, constant-observable
mutation, and physical overclaim.  Lean 4.32.1 compiles the factorization,
strict sign, and finite non-promotion declarations.

## Verdict and boundary

`NEGATIVE_RESULT`, route-local and claim-nonbearing.  The fixed R-493
projection cannot be promoted to the asserted fixed-pair finite semigroup
intertwining for this exact witness.  This is not a universal no-go for a
separately source-authorized alternate refinement map, nor a proof that all
finite PAH semigroups fail.

No ordered `j`-before-anchored-`n` convergence, common infinite-volume process,
path law, closed operator, R-512 identification, continuum, physical Pre-A,
spacetime, gravity, QFT, Yang--Mills, mass-gap, cosmic-origin or TOE result is
claimed.  Markov time remains the external stochastic time declared by
PAH-001.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_second_order_defect.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/primary.json
python -X utf8 codes/foundations/pah_omc020_second_order_defect_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/independent.json
python -X utf8 codes/foundations/pah_omc020_second_order_defect_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/hostile.json
python -X utf8 verification/scripts/pah_omc020_second_order_defect_verify.py
Set-Location verification/lean; lean Tect/PahOmc020SecondOrderDefect.lean
```

Primary `11/11`, independent `8/8`, hostile `6/6`, integrated `7/7`.
