# EXP-001201 - Spatial/source spectral-window stress certificate

## Result

The finite Q3 spatial/source spectral-window stress passes both computational lanes. The primary lane passes 322/322 assertions over 30 `(volume, cutoff, beta)` rows. The independent lane passes 322/322. The integrated verifier passes 12,595/12,595 assertions, including Lean R360 compiled with the pinned toolchain.

The fixture uses graph volumes `V in {2,4,6}`, oscillator cutoffs `d in {3,4,5,6,8}`, beta values `{0.5,2.0}`, fixed local-energy thresholds `E in {0.5,2.0,4.0}`, and registered source supports `{0,1}`, `{1,2}`, and `{3,4}` where available. Each selected union support `U` has `|U| <= 3` and is labelled by the source supports it touches. A separate induced Gibbs matrix is used for every union; records from distinct unions are never summed or normalized as one state.

For every row, the audit rebuilds forward and reversed overlapping term groups, checks reverse-order antisymmetry, diagonalizes the induced local Hamiltonian, projects the Gibbs square root to shifted energies at most `E`, and records signed and absolute weighted contributions, window mass, rank and tail mass. The result contains 156 `(V, beta, E, U)` summaries, each with three tail rows at `d >= 5`.

The finite tail diagnostic is not uniformly stable:

- stable summaries: `63/156`;
- summaries above the registered spread threshold `1.5`: `93/156`;
- maximum signed-weighted tail spread ratio: `1.9734189022408282`;
- maximum conditional tail spread ratio: `2.1596678443595425`;
- window masses across summaries range from `0.10199579573556163` to `1.0`, with ranks from `2` to `46`.

Thus the fixed-energy window remains a useful finite decomposition and identifies the exact spatial/source contexts that fail the current tail-stability threshold, but this experiment does not supply a source- or volume-uniform bound.

## Interpretation and QFT interface

This is a finite diagnostic on local Q3 oscillator matrices. It tests the QFT-facing route

`finite split-step history -> spectral window plus Gibbs complement -> common-core and cutoff/volume/beta uniformity -> thermodynamic/KMS state -> OS/KMS/GNS physical sector -> gap and continuum`.

The first arrow is represented only by finite matrix proxies here. The second arrow is not closed: the 93 unstable contexts are a route-local boundary showing that the present finite window cannot be promoted to a source/volume-uniform estimate under the registered threshold. The Gibbs complement, an actual Trotter defect, an oscillator-cutoff-independent common core, a thermodynamic history, exhaustion, common alpha, OS/KMS/GNS identification, the physical-sector gap, continuum, C6, Sector A and Pre-A remain open.

No global KMS state, cutoff-removal theorem, mass-gap result or Clay result is claimed.

## Adversarial review

1. **Union-level state separation:** local Gibbs matrices are kept separate for each `U`; no cross-union aggregation is treated as one state. UPHELD.
2. **Source and boundary coverage:** all registered finite source supports are retained and every selected union has source-touching labels. The coverage is finite and does not claim unlisted translations. UPHELD-OPEN.
3. **Fixed-energy meaning:** `E` is a manifest input independent of cutoff and volume; rank and Gibbs mass are recorded for each union. UPHELD.
4. **Finite versus asymptotic:** tail spreads use only `d={5,6,8}` and three finite volumes. No cutoff, spatial or thermodynamic limit is inferred. UPHELD-OPEN.
5. **Signed versus absolute:** signed and absolute aggregates remain separate for every union and window. UPHELD.
6. **Reverse order:** both lanes rebuild the reversed term order and compare all selected unions. UPHELD.
7. **Weight orientation:** each weighted leg inserts the projected Gibbs square root separately; no commutation through the operator is assumed. UPHELD.
8. **Independent implementation:** the independent lane reconstructs oscillator, local terms, projectors and union rows without importing the primary audit. UPHELD.
9. **QFT promotion:** the observed instability is retained as a route-local boundary; global Gibbs/KMS transfer, common core, actual history, OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open. UPHELD-OPEN.
10. **Lean scope:** R360 checks exact finite grid/count arithmetic and the finite-only scope firewall. Matrix spectra and all QFT limits remain Python/open analysis. UPHELD.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress/integrated.json
lake env lean Tect/R360.lean
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

The next proof target is not common-alpha promotion. It is an analytic replacement for the unstable finite proxy: either a source/volume-uniform spectral decomposition with a proved Gibbs-tail estimate and cutoff-independent common core, or a formal obstruction that specifies the missing hypotheses. Until that interface is supplied, the QFT bridge and all Pre-A/Sector-A gates remain conditional/open.