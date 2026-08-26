# EXP-001198 — Source-edge high-cutoff commutator certificate

## Result

The fixed two-site Q3 source-edge commutator stress passes both implementations. The primary lane passes 86/86 assertions; the independent lane passes 66/66. The integrated verifier passes 84/84 assertions and Lean R357 compiles with the pinned toolchain.

The source edge is held fixed at sites `{0,1}`. For each oscillator dimension
`d in {3,4,5,6,8,10,12,16,20,24}`, the calculation forms
`K_full = I + H - min(spec(H)) I`,
`K_edge = I + V_0 + V_1 + B_01 - min(spec(V_0+V_1+B_01)) I`,
and the right commutator operator
`C = [K_full,K_edge] K_full^(-1)`.

The explicit high-occupation core vectors are `|d-1,d-1>` and `|d-1,0>`. The diagonal vector satisfies the declared finite lower-bound diagnostic
`||[K_full,K_edge] psi|| / ||K_full psi|| >= (1/4)(d-2)`
for every listed dimension. Its ratio is `0.292347675047599` at `d=3` and `8.65366921692738` at `d=24`, a finite growth ratio of `29.60060898558`.

Across the grid, the primary maxima are:

- graph constant `||K_edge K_full^(-1)||`: `1.88843832098328`;
- form constant `lambda_max(K_full^(-1/2)K_edge K_full^(-1/2))`: `1.82494969105877`;
- global commutator constant `||C||`: `39.8709026914792`.

The independent values agree within the declared `1e-7` tolerance.

## Interpretation

This is a finite, fixed-geometry route boundary for the raw source-edge commutator coefficient. The explicit high-core vector shows that the tested right-commutator constant is not cutoff-stable on the declared truncations, even though the graph and form transfer constants remain near order one. Therefore this raw coefficient cannot be used as an unqualified cutoff-uniform common-core input.

The result is not an asymptotic theorem: finite truncations, a two-site graph and two explicit basis-vector families do not establish divergence in the untruncated theory. A cancellation-aware or state-weighted history topology remains live.

## Adversarial review

1. **Finite lower bound:** the linear inequality is checked only on the manifest dimensions and vectors; it is not presented as a limit statement.
2. **Truncation boundary:** all vectors and operators belong to the declared finite oscillator matrices; no exact untruncated CCR is assumed.
3. **Source locality:** `K_edge` contains only the two onsite potentials and the internal bond `B_01`; no external interaction is hidden.
4. **Graph versus form:** the commutator, graph and form constants are computed independently; form domination is not used to infer commutator control.
5. **Inverse stability:** `K_full` is shifted to spectral floor one before its inverse is used.
6. **Independent lane:** the second implementation reconstructs the oscillator, two-site Hamiltonian, source edge and high-core rows without importing the primary script.
7. **Route scope:** the finite cutoff trend rejects only this raw fixed-graph commutator input as a candidate uniform coefficient; it does not rule out cancellation-aware or state-weighted histories.
8. **QFT firewall:** common-core density, cutoff removal, exhaustion independence, common alpha, OS/KMS/GNS reconstruction, a mass gap, continuum, C6, Sector A and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-29-primary-pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-29-independent-pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress_verify.py
lake env lean Tect/R357.lean
```

The next analytic target is a cancellation-aware or state-weighted history estimate with a coefficient controlled on the common core, followed by an actual cutoff-uniform proof before any common-alpha promotion.