# R-415 certificate — Schur-certified two-scale semigroup budget

## Question

Can the late-time leg of the R-414 heat-trace bridge use the conservative
harmonic-extension/Schur gap from R-406, so that coarse inter-phase capacity
and block-mean-zero residual coercivity are explicit inputs to the finite
Green-trace budget?

## Finite statement

For a positive ordered spectrum of the normalized intrinsic graph operator,
write

```
H(t) = sum_k exp(-t lambda_k),
G    = sum_k 1/lambda_k.
```

The R-406 harmonic split supplies positive coarse and residual quantities
`kappa_coarse` and `kappa_residual`.  Define the conservative certified gap

```
kappa_S = half min(kappa_coarse, kappa_residual).
```

The finite variational check verifies `kappa_S <= lambda_1`, where
`lambda_1` is the first positive eigenvalue.  Therefore, for `t >= tau`,

```
H(t) <= H(tau) exp(-kappa_S (t-tau)),
integral_tau^infinity H(t) dt <= H(tau)/kappa_S.
```

The R-414 short-time envelope is retained.  For an R-412 profile with
`0 < alpha_UV < 1`, head length `r`, and UV coefficient `C_UV`, set

```
A_tau = r tau^alpha_UV + C_UV alpha_UV Gamma(alpha_UV).
```

Then the finite two-scale criterion is

```
G <= A_tau tau^(1-alpha_UV)/(1-alpha_UV) + H(tau)/kappa_S.
```

All constants are rowwise finite quantities.  No regulator-independent bound
is asserted.

## Verification

The fixture covers volume-two cutoff dimensions `4,5,6,8,10,12`, volume-three
cutoff dimensions `4,5`, beta values `{1/2,1,2,4,8}`, both collar
orientations, every R-406 conditional likelihood row, all 25 R-412 mixed
profiles, and heat times
`{1/16,1/8,1/4,1/2,1,2,4}` with `tau=1`.

- Primary: `10440/10440` assertions over 8 systems, 80 Gibbs/orientation
  profiles and 1030 conditional rows.
- Independent plain-loop reconstruction: `10439/10439` assertions on the
  same finite grid.
- Hostile lane: `9/9` shortcut mutations rejected.
- Integrated verifier: `50/50` checks.
- Lean: `lake env lean Tect/R415.lean` exits `0` (only unused-variable
  warnings).

The primary certified Schur gap range is
`[0.3172951609382775, 3.232260013170645]`; the first-positive gap range is
`[0.6310329497027756, 6.229495058532403]`; the coarse Schur range is
`[0.6345903218765556, 18.727067154255124]`; and the residual range is
`[2.0000155411351734, 30.07649788337455]`.  The split heat range is
`[0.001995374453234255, 0.5926882083380163]`.  The minimum short-power
slack is `1.057597874912107`, the minimum late-budget slack is
`0.00029867870471992557`, the minimum Green-trace slack is
`2.8762895669125346`, and the maximum Mellin residual is
`4.996003610813204e-16`.  Primary and independent invariants agree within
the declared `5e-6` cross-check tolerance.

## Adversarial review

The hostile suite rejects the following finite shortcuts:

- replacing the certified lower gap by a larger unverified gap, with late
  deficit `2.920502936517768`;
- omitting the finite IR head, with short-budget deficit
  `0.11755608825868386`;
- omitting the UV term, with short-budget deficit
  `0.13507226908622838`;
- omitting the late Schur budget, with Green deficit
  `0.4775461490944841`;
- shifting the late exponential incorrectly, with deficit
  `2.7432509056332397`;
- reversing heat-time order, producing increase
  `0.2894603181637101`;
- changing the Mellin sign, leaving residual
  `6.239564084015606`; and
- using `alpha=1`, which is rejected before integration.

These are finite convention and omission tests, not asymptotic
counterexamples.  The uniformity and physical objections remain upheld open.

## QFT-facing interpretation

The certified gap places the R-406 phase-capacity channel and the
block-mean-zero fluctuation channel inside the same proper-time budget.  This
is a finite interface toward broken-sector GNS coercivity and an eventual
OS/KMS/Hamiltonian bridge.  It is not a phase-selection result and not a
Yang--Mills mass-gap theorem.

## Boundary and next gate

R-415 is T0 and claim-nonbearing.  It proves no cutoff-, volume-, source-,
phase- or exhaustion-uniform Schur gap, UV coefficient or split heat value; no
common Hamiltonian core; no R-399 shell transfer; no OS/KMS/GNS
reconstruction; and no physical gap, continuum, C6, Sector-A or Pre-A
closure.  The next gate is a common-core estimate that controls both Schur
components and the split heat uniformly, identifies the coarse variables with
a controlled phase boundary, and transfers the budget to the R-399 shell.
If either Schur component collapses under a validated growing stress, retain
only the finite diagnostic and record the route-local obstruction.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge_hostile.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge_verify.py --self-test --reuse-existing
lake env lean verification/lean/Tect/R415.lean
```

The run artefacts are stored under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-{primary,independent,hostile,integrated}-pre_a_cp1_st8_q3lock_schur_certified_semigroup_bridge/`.
