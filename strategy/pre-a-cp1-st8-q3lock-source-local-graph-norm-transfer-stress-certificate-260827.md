# EXP-001197 — Source-local graph-norm transfer certificate

## Result

The finite Q3 source-local graph/form/commutator stress passes in both independently implemented lanes. The primary lane passes 1292/1292 assertions; the independent lane passes 1196/1196. The integrated verifier passes 206/206 assertions and Lean R356 compiles under the pinned toolchain.

The matrix family contains 38 source-weight scenarios across the registered volumes V=2,4,6, the manifest oscillator dimensions, and the declared translated supports. Each scenario tests both the onsite source potential weight and the source-edge weight. The explicit total-occupation-at-most-two polynomial proxy contributes 544 core-basis rows.

For each scenario the shifted full weight is
`K_Lambda = I + H_Lambda - min(spec(H_Lambda)) I` and the source weights are shifted positive before inverse powers are formed. The measured quantities are the form constant
`lambda_max(K_Lambda^(-1/2) K_S K_Lambda^(-1/2))`, the graph constant
`||K_S K_Lambda^(-1)||`, and the right graph-commutator constant
`||[K_Lambda,K_S] K_Lambda^(-1)||`.

Primary maxima are:

- form constant: `1.8039836560045446`;
- graph constant: `1.865789999507254`;
- commutator constant: `4.015684693477961`.

The independent maxima agree within the declared `1e-7` lane tolerance. On the V=2 source-edge row, the commutator constant changes from `1.5449241615861335` at oscillator dimension 3 to `4.015684693477961` at dimension 8, a finite cutoff growth ratio of `2.5992762579071593`, above the preregistered diagnostic threshold `1.5`.

## Interpretation

The finite calculation supplies a concrete QFT-facing calibration: source-local Q3 potential weights can be compared to the full shifted Hamiltonian without replacing an operator graph estimate by a form estimate, and the exact commutator cost is visible. It also identifies cutoff sensitivity in the source-edge commutator route.

This is T0, claim-nonbearing evidence. The cutoff trend is a finite route diagnostic only. It is not an asymptotic divergence theorem and does not reject other cancellation-aware or state-weighted topologies.

## Adversarial review

1. **Operator versus form:** form, graph, and commutator constants are computed separately; no form-order implication is used as an operator-order theorem.
2. **Source support:** the source weight contains only onsite terms on the declared support, plus bonds internal to that support; crossing bonds remain outside the source weight.
3. **Core scope:** only the finite tensor Fock span with total occupation at most two is tested. No density, domain closure, or cutoff removal is inferred.
4. **Inverse stability:** the full and source weights are shifted to floor one before `K_Lambda^{-1}` and `K_Lambda^{-1/2}` are formed. No Gibbs inverse or modular floor is introduced.
5. **Independent reconstruction:** the second lane rebuilds oscillator, graph, Hamiltonian, source weights and core rows without importing the primary implementation.
6. **Cutoff trend:** the V=2 dimension-3-to-8 ratio is recorded as a sampled diagnostic; it is not a global no-go statement.
7. **QFT firewall:** common unbounded-core construction, exhaustion independence, common alpha, Hamiltonian-to-OS identification, KMS/GNS reconstruction, a mass gap, the continuum, C6, Sector A and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-29-primary-pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-29-independent-pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress_verify.py
lake env lean Tect/R356.lean
```

The next analytic target is a source-, volume- and cutoff-uniform commutator/graph estimate on a declared Q3 common core. Until that estimate is proved, no common-alpha or thermodynamic QFT promotion is allowed.