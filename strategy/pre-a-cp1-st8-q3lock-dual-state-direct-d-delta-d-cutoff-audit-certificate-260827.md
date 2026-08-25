# EXP-001123 — finite dual-state direct-D/delta-D cutoff audit

## Decision

The finite actual-Q3 matrix lane passes for both the reference Gibbs state and
the local-character dual state.  For each declared volume, oscillator
dimension, cutoff radius, time, and sign, the direct difference

```text
D_sigma(t) = alpha_t^(H+sigma W_L)(A) - alpha_t^H(A)
```

and the full-H modular derivative

```text
delta_H(D_sigma) = i[H,D_sigma]/hbar
```

have finite two-sided Gibbs seminorms.  The primary lane has 245 assertions,
the independent lane has 137 assertions, and the integrated verifier has
1706/1706 assertions with Lean R294 PASS.

The tested finite rows cover the two-site edge at dimensions 3–7 and the
four-site square at dimensions 3–4, three nonzero-tail radii
`L in {0.75,0.9,1.0}`, times `0.1,0.2`, and both cutoff signs.  The smallest
and largest recorded ratio among

```text
N_ref(D)/(t N_ref(W_L)), N_dual(D)/(t N_dual(W_L)),
N_ref(delta D)/N_ref(W_L), N_dual(delta D)/N_dual(W_L)
```

are `0.013509019647190305` and `0.705460895183117`.  The maximum observed
dual/reference root-seminorm amplification for the direct and modular rows is
`1.012589605649643` (finite diagnostic only).  The two lanes agree within the
declared relative tolerance `1e-7`.

## QFT-facing meaning

This advances the missing dual companion to the EXP-001113 conditional
direct-D/delta-D tail composition: the actual finite regulator does not show
an immediate dual-state blow-up on the declared rows.  It is not a dual
modular-tail theorem.  No volume-, source-, beta-, cutoff-, or exhaustion-
uniform constant is inferred from seven finite regulator rows, and no
unbounded common-core transfer is made.

## Adversarial review

1. **Dual state — UPHELD.** `rho_dual=A rho A*` is constructed and evaluated
   separately; it is not silently replaced by the reference Gibbs state.
2. **Cutoff placement — UPHELD.** Only intersite bond coordinates are replaced
   by the declared smooth spectral cutoff; onsite kinetic and quartic terms
   stay in the full finite regulator.
3. **Orientations — UPHELD.** Both `sigma=-1,+1` evolutions are computed, and
   every state seminorm keeps both trace legs.
4. **Modular convention — UPHELD.** The derivative uses the full `H` that
   defines the reference Gibbs state, not the cutoff Hamiltonian.
5. **Truncated CCR — UPHELD.** The result is finite matrix arithmetic only; no
   infinite-dimensional CCR or domain closure is inferred.
6. **Numerical range — UPHELD-OPEN.** The selected radii have nonzero tails;
   ratios are reported only on this finite range and are not asymptotic fits.
7. **Independent lane — UPHELD.** The primary and independent implementations
   rebuild tensor matrices separately and agree row-by-row within `1e-7`.
8. **Lean — UPHELD.** R294 checks only scalar two-sided bookkeeping, state
   normalization markers, orientation/edge counts, and the ratio identity.
9. **QFT promotion — UPHELD-OPEN.** Common alpha, OS/KMS/GNS identification,
   gap, continuum, C6, Sector A, and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit/integrated.json
```

Lean cross-check: `lake env lean Tect/R294.lean` from
`verification/lean/`.

## Boundary and next gate

The direct-D/delta-D thermodynamic gate remains open.  The next analytic task
is to turn the finite dual/reference comparison into a local modular-energy
tail estimate on one unbounded Q3 common core, with explicit source, volume,
beta, orientation, and cutoff dependence.  If that estimate cannot be made
uniform, the failure must be registered as a route-specific obstruction.

