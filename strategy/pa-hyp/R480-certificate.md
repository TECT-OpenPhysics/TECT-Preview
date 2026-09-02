# R-480 Certificate: PAH-OMC-002 Conditional-Gibbs Projected Defect

## Result identity

- Result: `R-480`
- Exploration: `EXP-001367`
- Task: `T-054`
- Audit: `PAH-COND-GIBBS-BLOCK-001`
- Route: `PAH-OMC-002` conditional-Gibbs projected diagnostic
- Verdict: `ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL`
- Programme status: `HOLD_FOR_EVIDENCE`
- Tier: T0 claim-nonbearing, exact finite route-local defect
- Gate change: none
- PAH-001 mutation: none
- Q3LOCK import: none

## Hash-pinned authorities

- `strategy/pa-hyp/PAH-001-v1.json`
  SHA-256 `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- `strategy/pa-hyp/PAH-OMC-001-v1.json`
  SHA-256 `948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f`
- `strategy/pa-hyp/PAH-OMC-002-v1.json`
  SHA-256 `618265f978bae4e96e1330fbec0ce7af0bf1630d6f5a17f9029fcbde48de6876`
- `strategy/pa-hyp/PAH-OMC-002-manifest.json`
  SHA-256 `06967d09c536e6d237dd0e3da2cdf9e7778f6cdf3dd6e300e2f0b1974bacf05d`

## Exact finite scope

The audit instantiates the unchanged PAH-001 aperture terms on a finite
relational carrier.  The coarse carrier has vertices `v,w`, one oriented edge
`e=(v,w)`, and distinct anchors `C=v,O=w`.  The fine carrier retains `e` and
adds a fine-only vertex `z` with edge `d=(v,z)`.  The map `p_Omega` retains
`j_v,j_w,n_v,n_w,u_e` and forgets `j_z,n_z,u_d`, exactly as specified by the
PAH-OMC-002 map/kernel contract.  Both state spaces use `K=2`, `M_s=1`,
`M_psi=1`, `Q=0`, `epsilon=1/2`, `R_max=1`, `beta=1`, `nu=1`,
`lambda_s=1`, `kappa_s=1`; the remaining displayed couplings are positive
test inputs and their matter or plaquette terms vanish exactly because `Q=0`
and the carrier has no plaquettes.  Counting measure followed by the finite
Gibbs weight `exp(-beta F)` is used.  Markov time is external stochastic time.
No cutoff, lattice, volume, phase, aperture, observation-time, continuum or
physical limit is taken.

## Exact witness

Use the invariant cylinder observable `f(x)=j_v` and the coarse state
`x=(j_v,j_w,n_v,n_w,u_e)=(0,0,0,0,0)`.  The fine fibre has eight states:
`j_z=0,1` and four neutral `(n_z,u_d)` labels for each value.  Direct
evaluation of the unchanged aperture part of `F_rho` gives

```text
F_fine(j_z=0 | x) = F_fine(j_z=1 | x) = 3/8,
Delta F_coarse(AP(v,+)) = 0,
Delta F_fine(AP(v,+) | j_z=0) =  1/8,
Delta F_fine(AP(v,+) | j_z=1) = -1/8.
```

The retained aperture mobility has squared value
`s_v(before)s_v(after)=1/2` and is common across the fibre.  Therefore the
exact conditional rate ratio is

```text
E_kappa[c_fine]/c_coarse
  = (exp(-1/16) + exp(1/16))/2
  > 1,
```

and the normalized projected-generator defect is

```text
[(E_kappa L_(rho') I_p - L_rho)f](x) / sqrt(1/2)
  = (exp(-1/16) + exp(1/16))/2 - 1 > 0.
```

The corresponding absolute rate defect is numerically
`0.0013815175569305126`, inside the recorded interval `(0.00138,0.00139)`.
Thus `E_kappa L_(rho') I_p f != L_rho f` on this exact finite invariant
cylinder witness.  The conditional kernel normalizes and is gauge-equivariant
in the fixture, and the retained roots are inverse-closed, but those passes do
not repair the failed projected equality.

## Verification package

- Primary: `26/26 PASS`
- Non-importing independent: `20/20 PASS`
- Hostile: `12/12 PASS`; all `12/12` mutations rejected
- Integrated: `17/17 PASS`
- Lean 4.32.1 `verification/lean/Tect/R480.lean`: `PASS`
- Primary run: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-pah-omc002-conditional-kernel/primary.json`
- Independent run: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-pah-omc002-conditional-kernel/independent.json`
- Hostile run: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-pah-omc002-conditional-kernel/hostile.json`
- Integrated run: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-pah-omc002-conditional-kernel/integrated.json`

Reproduction from the repository root:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc002_conditional_kernel.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc002_conditional_kernel_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah_omc002_conditional_kernel_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah_omc002_conditional_kernel_verify.py
Set-Location E:\Dev\TECT\verification\lean; lake env lean Tect/R480.lean
```

## Route decision

Register only the route-local negative
`NG-2026-09-02-PAH-OMC-002-CONDITIONAL-GIBBS-PROJECTED-INTERTWINING`.
It retires the exact PAH-OMC-002 Gibbs fibre-average diagnostic for this
owner-specified finite map.  It does not retire PAH-001, does not prove a
global refinement no-go, and does not address other owner-authorized block
kernels or normalized defect notions.

## Non-claims

- PAH-001 and PAH-OMC-001 remain byte-unchanged and are not retroactively completed.
- The strong lift remains a separate target; projected equality is not substituted for it.
- No refinement family, uniform estimate, ordered limit, physical sector, or observable chain is admitted.
- No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills,
  continuum, mass-gap, cosmic-origin or TOE conclusion follows.
- Markov time is not quantum real time, proper time or Lorentzian time.

## Single next question

Can an owner-authorized block kernel other than the exact PAH-OMC-002
Gibbs-fibre average satisfy the projected identity without changing the strong
target or adding a new functional term?
