# EXP-001079 / Dual-state fifth-moment necessity for modular cutoff locality

## Decision

EXP-001078 showed that even a finite-temperature Gibbs state for an abstract
dominating `K` does not justify the scalar `Q_sigma` transfer.  This checkpoint
tests the narrower equilibrium cutoff alternative: whether a bounded fifth
moment in the reference Gibbs state plus a local relative graph bound controls
the opposite-side spectral cutoff tail.

The answer is no for an exact finite Gibbs family.  This is a route-local
obstruction, not a counterexample to the actual Q3 Hamiltonian or its Gibbs
states.

## Exact witness

For `L in {4,16,64}`, let

```text
k     = diag(1,L)
rho_L = diag(L^6/(L^6+1), 1/(L^6+1))
B     = [[0,1],[1,0]]
P_R   = 1_[k<=2] = diag(1,0)
Q_R   = I-P_R = diag(0,1).
```

The state is exactly Gibbs for `k` at

```text
beta = 6*log(L)/(L-1) > 0,
```

because `rho_22/rho_11=L^-6=exp(-beta*(L-1))`.  The two relative graph
norms have squared spectra `{1,1/L}`, hence both norms equal one.

The exact quantities are

```text
M5_reference = Tr(rho_L k^5)              = L^5*(L+1)/(L^6+1) < 3/2,
M5_dual      = Tr(B rho_L B^* k^5)        = (L^11+1)/(L^6+1) > L^4,
tail         = ||Q_R B rho_L^(1/2)||_2^2  = L^6/(L^6+1) > 1/2.
```

Thus a uniformly bounded reference fifth moment does not make this opposite
tail small.  The missing input is a dual-state moment or an equivalent
modular-energy tail theorem.

## Adversarial review

1. **Gibbs identity — UPHELD.** The state ratio and positive finite beta are
   checked exactly.
2. **Spectral cutoff — UPHELD.** `P_R` and `Q_R` are the exact spectral
   projections of `k` for `R=2` and `L>2`.
3. **Relative bound — UPHELD.** Both squared graph matrices have spectra
   `{1,1/L}`, so the norm bound is not assumed.
4. **Moment direction — UPHELD.** Reference and dual fifth moments are kept
   distinct.
5. **Tail direction — UPHELD.** The tested tail is the opposite-side quantity
   that requires `B rho B^*` control.
6. **Exact growth — UPHELD.** The three fixtures use rational arithmetic, with
   symbolic ceiling and floor inequalities.
7. **Lean — UPHELD.** R261 formalizes only the rational finite witness and
   scope firewall.
8. **QFT promotion — UPHELD.** Actual Q3, OS/KMS/GNS, gap, continuum, C6,
   Sector A and Pre-A remain open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_fifth_moment_modular_cutoff_obstruction.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_fifth_moment_modular_cutoff_obstruction_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_state_fifth_moment_modular_cutoff_obstruction_verify.py
lake env lean Tect/R261.lean
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

The primary and independent lanes each pass `46/46`; the integrated verifier
passes `19/19` with Lean R261 passing.

## Boundary and next gate

This is a T0, claim-nonbearing finite dual-state/modular-cutoff obstruction.
It rejects only the one-sided reference-moment shortcut for this cutoff
architecture.  It does not reject the actual Q3 local energy, its dual Gibbs
states, or a stronger modular-tail theorem.

The next gate is to prove both one-sided and dual-state fifth-energy or
modular-tail bounds for the actual Q3 projected bond on a predeclared faithful
phase-pair/separating class.  Only after that can the equilibrium cutoff route
be used in direct `D` and `delta-D` convergence and then connected to the
common KMS/OS/GNS construction.
