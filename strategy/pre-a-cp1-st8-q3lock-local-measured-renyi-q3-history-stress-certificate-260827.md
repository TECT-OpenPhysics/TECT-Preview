# EXP-001202 finite actual-Q3 local measured-Renyi history stress

## Question

Does the conditional local coordinate-marginal alpha=2 likelihood interface
remain finite across partial split histories and adjoints of the registered
finite Q3 split-step model, while source orientation, beta, spatial volume and
a small oscillator-cutoff stress are varied?

## Result

The primary lane and a non-importing independent lane reproduce the same 1,728
finite contexts. Every local coordinate likelihood and every declared tail
inequality is finite and passes its numerical self-test. The maximum sampled
likelihood is reported in the canonical run JSON; the route outcome is a finite
diagnostic relative to the preregistered threshold 4.

This is a route-local finite observation. It does not establish the uniform
local Renyi estimate required by the common-alpha gate.

## QFT interface

The tested object is the finite Gibbs state of the exact truncated Q3
Hamiltonian, evolved by explicit partial products of onsite and bond factors.
The coordinate measurement is local in the oscillator q eigenbasis. The finite
inequality checked is

`p_sigma(E) <= Q_2^(1/2) p_rho(E)^(1/2)`.

The live QFT connection is therefore the following conditional chain:

`local measured Renyi bound -> two-orientation Gaussian history tail -> common
core and exhaustion -> OS/KMS/GNS reconstruction -> phasewise gap`.

Only the first arrow's finite diagnostic was evaluated here. Volume-, source-,
beta- and cutoff-uniform analytic bounds, the split limit, Hamiltonian/OS
identification, KMS/GNS gap, regulator removal, continuum and all TECT gates
remain open.

## Adversarial review

1. **Finite-to-uniform promotion — UPHELD-OPEN.** A finite maximum over the
   declared contexts is not a volume-, cutoff- or beta-uniform theorem.
2. **State/reference orientation — UPHELD.** The reference is the unsplit
   finite Gibbs marginal; source signs, history signs and adjoints remain
   separate rows, with no global-state identification.
3. **Tail inequality — DISMISSED.** The alpha=2 event inequality is checked
   directly from the computed finite marginals; no Gaussian tail is silently
   substituted.
4. **Partial-history coverage — UPHELD-OPEN.** Only zero, first-term and full
   prefixes are sampled; all prefixes in the analytic gate remain open.
5. **Independent reconstruction — DISMISSED.** The independent lane rebuilds
   oscillator, Hamiltonian, Gibbs, source, prefix and marginal calculations
   without importing the primary module.
6. **Lean promotion — UPHELD-OPEN.** R361 checks exact counts and the finite-only
   firewall; it does not formalize matrix spectra or limits.

## Evidence

- Primary: `codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress.py`
- Independent: `codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress_independent.py`
- Integrated: `codes/foundations/pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress_verify.py`
- Lean: `verification/lean/Tect/R361.lean`
- Canonical primary/independent/integrated JSON files under
  `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-*local_measured_renyi_q3_history_stress/`

## Decision

Advance the QFT-facing local measured-Renyi route as a finite diagnostic only.
Do not close or promote the common-alpha gate. The next proof obligation is an
analytic Gibbs-tail/common-core estimate uniform in cutoff, source, volume,
beta and every partial history, or a formally scoped obstruction if that
estimate cannot be obtained.
