# EXP-001200 — Low-energy spectral-window certificate

## Result

The fixed two-site Q3 source-edge spectral-window stress passes both computational lanes. The primary lane passes 187/187 assertions; the independent lane passes 187/187. The integrated verifier passes 3213/3213 assertions, including Lean R359 with the pinned toolchain.

The source edge `{0,1}` and graph volume are fixed. For oscillator dimensions
`d in {3,4,5,6,8,10,12,16,20,24}`, beta values `{0.5,1,2}`, and fixed local-energy thresholds `E in {0.5,1,2,4}`, the audit diagonalizes the induced two-site Hamiltonian. It projects the Gibbs square root to the spectral subspace with shifted energy at most `E`, and evaluates both the unnormalized window contribution and the conditional value normalized by the square root of the window mass.

All four windows have a stable finite tail spread on the declared cutoff tail `d >= 12`:

- maximum unnormalized tail spread ratio over all beta and E: `1.2183929213757922`;
- maximum conditional tail spread ratio: `1.2335104477603323`;
- registered acceptance threshold: `1.5`.

The full d=24/d=3 endpoint ratios range from `1.0652454717485893` to `2.9939611319329735`, depending on beta and E, so the low-energy stabilization is a windowed statement, not a full-state cutoff bound. Window masses are retained explicitly; across all rows they range from `0.240252108724294` to `1.0`, and ranks vary with the threshold and dimension. Reverse-order residuals pass the declared tolerance.

## Interpretation

A fixed low-energy spectral window removes the high-occupation growth seen in the full energy-weighted coefficient on this finite two-site fixture. This identifies a live QFT-facing topology: decompose a Gibbs/KMS approximation into a fixed-energy part and a complementary tail before attempting common-core transfer. The unnormalized window value is the contribution compatible with a later positive-state decomposition; the conditional value exposes normalization dependence.

This does not prove a global KMS state or a cutoff-uniform theorem. The projector, induced Gibbs state, geometry, sampled dimensions and energy thresholds are finite, while the spectral complement is not controlled analytically. The next required step is a uniform Gibbs-tail estimate for that complement, an oscillator-cutoff-independent common-core/window interface, and a volume/source-translation stress before any common-alpha promotion.

## Adversarial review

1. **Window versus full state:** the projected Gibbs square root is an unnormalized finite spectral contribution; the complement and global-state transfer remain open.
2. **Fixed-energy meaning:** thresholds are manifest inputs independent of oscillator dimension; rank and mass are reported rather than silently identified.
3. **Finite versus asymptotic:** tail ratios use only the ten registered dimensions and four tail rows; no limit is asserted.
4. **Signed versus absolute:** signed union groups, absolute pair aggregates and signed-to-absolute ratios remain separate in every window.
5. **Reverse order:** both lanes rebuild the reversed term order and check antisymmetry at every cutoff and beta.
6. **Weight orientation:** all four energy-weighted legs use the projected Gibbs square root separately; no commutation through the operator is assumed.
7. **State normalization:** unnormalized and conditional values are both reported; neither is called an infinite-volume state.
8. **Independent lane:** the independent implementation reconstructs oscillator, support terms, spectral projectors and weighted legs without importing the primary module.
9. **Lean scope:** R359 checks finite grid/window/count arithmetic and scope only; spectral projectors and QFT limits remain Python/open analysis.
10. **QFT firewall:** common-core density, global KMS transfer, thermodynamic history, exhaustion, common alpha, OS/KMS/GNS identification, a mass gap, continuum, C6, Sector A and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit/integrated.json
lake env lean Tect/R359.lean
```

The next proof target is an analytic spectral-window decomposition with a uniform Gibbs tail estimate, an oscillator-cutoff-independent common-core interface, and spatial/source-uniform testing. Until those are proved, the OS/KMS/GNS bridge and mass-gap claim remain conditional.
