# EXP-001199 — High-cutoff signed-cancellation certificate

## Result

The fixed two-site Q3 source-edge signed-cancellation stress passes both computational lanes. The primary lane passes 134/134 assertions; the independent lane passes 134/134. The integrated verifier passes 1381/1381 assertions, including Lean R358 with the pinned toolchain.

The graph and source support are held fixed at sites `{0,1}`. For each oscillator dimension
`d in {3,4,5,6,8,10,12,16,20,24}` and each `beta in {0.5,1,2}`, the audit rebuilds the exact overlapping union groups, the local Gibbs matrix, and the shifted energy weight. The forward signed group is compared with the explicitly reversed term order; raw, two-sided Gibbs, energy-weighted and absolute aggregates remain separate.

The signed energy-weighted coefficient per site is finite on every row, but it is not cutoff-stable on this grid:

- beta `0.5`: d=24 / d=3 endpoint ratio `27.178403353918984`; maximum `38.01539989463614` at d=20;
- beta `1`: d=24 / d=3 endpoint ratio `2.732285890441825`; maximum `8.670037823582929` at d=10;
- beta `2`: d=24 / d=3 endpoint ratio `1.390589686602203`; maximum `3.877228556898885` at d=4.

The endpoint signed-to-absolute ratios are `0.7092101515841736`, `0.7739775356170933` and `0.8276235228192911` for beta `0.5`, `1` and `2`, respectively. Thus exact union-support grouping gives substantial cancellation, but leaves a large finite remainder and does not provide a cutoff-, beta- or global-state-uniform coefficient. The signed values are nonmonotone at higher d, so the endpoint ratios are diagnostics rather than monotonicity claims.

## Interpretation

This is a finite, fixed-geometry route boundary. Exact sign grouping and reverse-order antisymmetry do not by themselves turn the local energy-weighted coefficient into a common-core history bound. The raw signed-group coefficient therefore cannot be promoted as an unqualified QFT input.

The audit does not establish divergence in the untruncated theory: all matrices are finite truncations, the state is a two-site induced Gibbs state, and the source edge is fixed. A different cancellation kernel or state-weighted spectral-window topology remains live, but it requires an analytic cutoff-uniform estimate and a proved transfer to a global state/common core before common-alpha promotion.

## Adversarial review

1. **Finite versus asymptotic:** all maxima and ratios are restricted to the ten registered dimensions and three beta values; no limit is asserted.
2. **Signed versus absolute:** signed union groups and absolute pair sums are computed separately, with no relabelling of one as the other.
3. **Reverse order:** each lane rebuilds the reversed term order and checks matrix-wise antisymmetry.
4. **Local versus global state:** `rho_U` is an induced finite two-site Gibbs matrix, not an infinite-volume KMS restriction.
5. **Weight orientation:** all four energy-weighted legs are evaluated separately; no commutation of the weight through the operator is assumed.
6. **Source/truncation boundary:** only the declared source edge and finite oscillator matrices are used; no external bond or exact untruncated CCR is inserted.
7. **Independent lane:** oscillator, support terms, Gibbs factors and signed groups are reconstructed without importing the primary implementation.
8. **Lean scope:** R358 checks fixture counts, exact rational slope arithmetic and the scope firewall only; matrix spectra and asymptotics remain Python evidence.
9. **QFT firewall:** common-core density, cutoff removal, thermodynamic history, exhaustion, common alpha, OS/KMS/GNS identification, a mass gap, continuum, C6, Sector A and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit/integrated.json
lake env lean Tect/R358.lean
```

The next proof target is a genuinely state-compatible cancellation kernel or spectral-window history estimate with an analytic cutoff-uniform common-core bound. Until that estimate is proved, the QFT bridge remains conditional and no common-alpha, OS/KMS/GNS, gap or continuum promotion is allowed.
