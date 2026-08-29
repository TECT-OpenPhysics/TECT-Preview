# R-416 certificate — log-domain and projected Schur cutoff stress

## Question

Can a log-domain Gibbs reconstruction and an explicit projection away from the
exact constant mode extend the R-415 Schur stress to larger cutoffs without
mistaking floating-point zero-mode drift for graph disconnection?

## New perspective

The stress separates three effects that are otherwise conflated in a raw
coordinate calculation:

1. coordinate Gibbs masses are reconstructed with log-sum-exp, so tiny
   probabilities are not lost before conditional normalization;
2. the intrinsic graph operator is evaluated on the orthogonal complement of
   the normalized vector `sqrt(pi)`, rather than trusting a numerically drifting
   raw zero eigenvalue; and
3. the R-406 harmonic coarse/residual decomposition is retained as a
   conservative Schur certificate below the projected positive gap.

This is a finite diagnostic interface, not an analytic replacement for a
common-core estimate.

## Finite statement

For energy eigenpairs `(E_n,v_n)` and coordinate basis `U`, define coordinate
Gibbs masses by the log-sum-exp of
`-beta(E_n-E_0)+log(abs(U_in)^2)`, followed by a common normalization.  Every
ordered one-site conditional row is formed from log-marginals.  For a positive
row `pi`, the normalized Laplacian has constant vector `sqrt(pi)`; its first
positive eigenvalue is computed after orthogonal projection away from that
vector.  The finite R-406 harmonic split supplies

```
kappa_S = half min(kappa_coarse,kappa_residual),
```

and the stress checks `kappa_S` against the projected positive graph gap.
Common scaling of all positive conditional weights must leave this intrinsic
operator unchanged.

## Verification

The fixture uses volume two, cutoff dimensions
`[4,6,8,10,12,14,16,18,20,24,28,30,32]`, beta values `{1/2,2,8}` and both
collar orientations.  It covers 13 systems, 78 profiles and 1410 conditional
rows.

- Primary: `4370/4370` assertions.
- Independent plain-loop lane: `4370/4370` assertions.
- Hostile lane: `9/9` assertions.
- Integrated verifier: `39/39` checks.
- Lean R416: `lake env lean Tect/R416.lean` exits `0`.

The primary projected-gap range is
`[0.6867237745188259, 11.524804493011532]`; the primary Schur-gap range is
`[0.3476008247075759, 5.985995817095592]`.  The primary coarse and residual
Schur ranges are respectively
`[0.6952016494151518, 62.06794691240475]` and
`[2.000015541135174, 13.392705028532543]`.  The independent minima agree with
the primary to the declared `5e-7` tight tolerance; eigensolver-sensitive
upper envelopes agree within the declared `1e-2` aggregate tolerance.

The maximum raw zero-mode residual is `1.0782998803365607` in the primary lane
and `1.1256888563326983` in the independent lane, while both projected gaps
remain positive.  The minimum log conditional mass is
`-41.760625060641004`, the maximum log condition number is
`40.18495540237028`, direct-density underflow rows are `0`, and the maximum
common-rescaling residual is `0.0`.

## Adversarial review

- The raw unprojected zero mode drifts at high cutoff; this is diagnosed rather
  than interpreted as disconnection.
- Projecting with the wrong constant vector gives a negative minimum
  `-38.090756543305964` and is rejected.
- Naive exponential formation underflows in two hostile entries, whereas the
  log-sum-exp normalizer remains finite.
- Multiplying all positive weights by the fixture factor `2` gives residual
  `0.0`; a nonpositive conditional row is rejected.
- The finite positive projected/Schur gaps do not establish cutoff, volume,
  source, phase or exhaustion uniformity; this objection remains upheld open.

## QFT-facing interpretation

The result removes a concrete numerical ambiguity in the proposed Schur route:
raw zero-mode drift is not by itself evidence of a collapsing finite graph gap.
It provides a better-conditioned finite target for a future analytic
common-core estimate and for transfer to the R-415 proper-time budget.  It does
not prove a uniform coercive bound, identify a phase, construct OS/KMS/GNS
states, or close C6, Sector-A, Pre-A, the continuum, or a Yang--Mills mass gap.

## Boundary and next gate

R-416 is T0 and claim-nonbearing.  The next gate is an analytic positive-measure
and conditional-marginal estimate on one Hamiltonian common core that controls
both Schur components uniformly in source, cutoff, volume, phase and
exhaustion, followed by transfer to the R-415 budget.  If a validated growing
stress produces a genuine projected or Schur collapse, retain the finite table
and record the obstruction without promotion.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress_hostile.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress_verify.py --self-test --reuse-existing
lake env lean verification/lean/Tect/R416.lean
```

The run artefacts are stored under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-{primary,independent,hostile,integrated}-preconditioned_schur_cutoff_stress/`.
