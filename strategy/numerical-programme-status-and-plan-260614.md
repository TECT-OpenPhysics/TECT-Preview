# Numerical-programme status & supplementation plan (TECT PDE → flavour observables)

**Issued**: 2026-06-14 · **Type**: strategy / status (non-tier-bearing; cites claims by ID, performs no tier action) · **Bears on**: A2-PDE-WELLPOSED, B3-BCC-STRUCT, B4-MASS-GAP, E4-FERMION-MASSES, E5-CKM-MIXING, E6-PMNS-NEUTRINO

## 0. Why this note exists

An external dossier (the same one that located the Mudgal reference for T-030, see
`claims/B5-BEYOND-LAYER-BOUND/DR-2/notes/dr2-t030-consolidation-260614-v1.0` / R-043)
also delivered a meta-critique: that the whole TECT programme is bottlenecked
because *"there is no actual wavefunction `Ψ_actual(x)` — the nonlinear PDE has
never been solved on a real space grid, so the flavour observables (mass matrix,
CKM/PMNS) cannot be produced; the analytical work is an illusion."* This note
audits that claim against the actual repository state and converts the valid part
into a concrete supplementation plan.

## 1. Verdict on the external critique: OVERSTATED, with a valid kernel

**Overstated.** The BCC condensate *background* HAS been solved numerically, and
the linearisation/zero-mode machinery EXISTS:

- Solver: `Codes/pde/tect_newton_krylov.py`, `continuation_mu2(_v25/_fast).py`,
  `projector_spectral.py` (Newton–Krylov + μ²-continuation + spectral projector).
- Background runs (with RunRecorder `run_diagnostics.json` + `RESULT.md`):
  `Runs/continuation/math82H_groundstate_N32_*` (the multi-hour N=32 ground-state
  solve), `Runs/continuation/math236_*` (continuum-limit scan), `math55_endpoint_*`.
- Hessian / zero-mode infrastructure: `Math357` (Hessian-stability framework),
  `Math358` (Lanczos Hessian eigenvalues), `Math374` (canonical BCC Hessian
  implementation), `Math376` (production-state Hessian extraction),
  `Math166` (chiral zero-mode counting), `verify_disclination_zero_modes.py`.

So *"never solved the PDE / no `Ψ_actual(x)`"* is **false**: a numerical BCC
background and a working Hessian/zero-mode toolchain both exist (all in the FROZEN
`C:\Dev\TECT2\Contents`; this repository holds the analytical ledger).

**Valid kernel.** The *full production chain to flavour observables is incomplete*,
and the ledger reflects this honestly:

- **Continuum limit not converged.** `math236` continuum-limit scan
  (μ²=−0.7, N∈{16,32,64,128}) completed **only N=16** in its wall-time
  (≈11 h for that single point); Richardson fit reported `INSUFFICIENT_POINTS`
  (have 0–1 usable, need ≥3); overall **PARTIAL**.
- **Production Hessian is smoke-tested only.** `Math376` (production-state Hessian
  extraction) is **T4 STRONG EVIDENCE** — "script delivered + synthetic-state
  smoke-test pass; T6 promotion gated on operator-PC" — i.e. it has NOT been run
  on the real production background to completion.
- **Flavour observables are open.** `E4-FERMION-MASSES`, `E5-CKM-MIXING`,
  `E6-PMNS-NEUTRINO` are all **T1 (CONDITIONAL, GAP-3)**. The actual mass matrix /
  CKM / PMNS numbers have NOT been produced from real zero-mode overlap integrals.

**Net diagnosis.** The bottleneck is **compute + an unfinished production chain**,
not "never started" and not "the theory is wrong". The infrastructure exists; the
continuum-limit background and the downstream overlap→mass→mixing extraction have
not been carried to completion at production grade.

## 2. The production chain and where it stands

```
[freeze action + grid + μ²]            P1  — convention A1-KERNEL-CONV is T5-pinned;
                                              config_template_brazovskii.json exists      [DONE-ish]
   → [relax to BCC background Ψ̄_min(x)] P2  — solver works; single resolutions solved
                                              (N=32 ground state; N=16 scan); continuum
                                              limit (≥3 resolutions) NOT converged          [PARTIAL]
   → [build production Hessian at Ψ̄]    P3  — Math374 canonical impl; Math376 extraction
                                              smoke-tested on synthetic state only          [PARTIAL/T4]
   → [extract zero-mode eigenvectors]   P3  — Lanczos (Math358) available; not run on the
                                              real production background to gates           [NOT DONE]
   → [overlap integrals]                P4  — not computed                                  [NOT DONE]
   → [fermion mass matrix]              P4  — not assembled (E4 T1)                          [NOT DONE]
   → [diagonalise → CKM / PMNS]         P4  — not produced (E5, E6 T1)                       [NOT DONE]
```

The first link that is genuinely *blocking* is **P2 (continuum-limit background)**:
P3/P4 require a certified `Ψ̄_min(x)` at ≥3 resolutions, which `math236` did not
reach (compute-limited).

## 3. Supplementation plan (adapted to existing infrastructure)

This is NOT a from-scratch protocol (the external "N-001" largely reinvents what
`Math374`/`Math376`/RunRecorder already provide). The plan re-uses the existing
drivers and adds the missing PASS/FAIL gating and the downstream extraction.

**P1 — Freeze (cheap; mostly done).**
Pin the canonical Class-II action/convention (A1-KERNEL-CONV, T5), the box `L`,
the μ² operating point, and the seed. Record the freeze as a one-page config
manifest so P2–P4 are reproducible.

**P2 — Continuum-limit background (the unblocking step; compute-bound).**
Run the μ²-continuation ground-state solve to a fixed residual tolerance,
producing certified `Ψ̄_min(x)` arrays and a Richardson extrapolation. **Resolution
count (operator correction):** the quadratic Richardson `f(a)=f_∞+A₁a+A₂a²` has
three parameters, so three resolutions give **zero residual degrees of freedom —
that is a fit, not a convergence certificate.** Require **≥4 resolutions**
(e.g. N∈{16,32,64,128}) so the fit is over-determined and the residual is a real
error estimate; OR adopt a **pre-justified lower-order ansatz** `f(a)=f_∞+A₁a`
(justified from the discretisation order) **with an independent error check**
(e.g. a held-out resolution, or a second observable). *Binding constraint*:
compute — the N=16 point alone took ≈11 h on CPU; N=64/128 need HPC/GPU.
Deliverable: `run_diagnostics.json` + `RESULT.md` per resolution; overall PASS
requires the over-determined (≥4-point) Richardson or the ansatz+error-check, gates green.

**P3 — Production-state Hessian + zero modes (depends on P2).**
Run `Math376` extraction on the *real* converged background (not synthetic):
build the canonical BCC Hessian (`Math374`), Lanczos the low spectrum
(`Math358`), and extract the chiral zero-mode subspace (`Math166`). **Zero-mode
comparison (operator correction):** compare across refinement by the **null-space
PROJECTOR / subspace** (e.g. principal angles between the zero-mode subspaces, or
`‖P_h − P_{h'}‖`), **NOT the individual eigenvectors** (which are basis-/gauge-/
degeneracy-dependent and not pointwise comparable). Gate with the four PASS/FAIL
certificates (Math374/376 + external N-001): **(G1) residual** (‖∇F[Ψ̄]‖ below tol),
**(G2) Hermiticity/symmetry** of the Hessian, **(G3) BCC order parameter** in band,
**(G4) zero-mode projector consistency** (count matches `Math166`; the subspace
projector stable in principal angle under refinement).

**P4 — Flavour observables (depends on P3).**
Compute the zero-mode overlap integrals on the background array, assemble the
charged-fermion mass matrix, and diagonalise → Yukawa hierarchy (E4), CKM (E5),
PMNS (E6). This is the step that moves E4/E5/E6 off T1. Each number ships a
reproducible script + self-test asserts + JSON (the §6 code-discipline standard)
and a `RESULT.md`.

**Cross-cutting**: every run uses `RunRecorder` (`run_diagnostics.json` +
`RESULT.md`) per the universal numerical-run-recording standard; production runs
resume in the frozen `TECT2` tree or a fresh run workspace (this repo records the
plan and will ingest the resulting certificates as claim evidence).

## 4. Recommendation

1. The analytical T-030 frontier is **settled** (R-043: lattice closed, real-sphere
   open-in-literature, non-load-bearing) — do not spend further effort there.
2. The high-value mainline is **P2 → P3 → P4** (production-run completion toward
   flavour observables). **P2 (continuum-limit background) is the single
   unblocking step**, and it is **compute-bound** (HPC/GPU), not method-bound.
3. Concrete next action: scope P2 as an HPC/GPU job (N∈{16,32,64}, fixed residual,
   >=4-resolution Richardson, or a justified low-order ansatz + independent error check) with the four PASS/FAIL gates pre-registered; only then are
   P3/P4 (Hessian → overlaps → CKM/PMNS) executable.

## 5. Honest caveats

- This note performs **no tier action**; E4/E5/E6 stay T1, Math376 stays T4 until
  the runs above complete and pass their gates.
- The diagnosis rests on the repository state as inspected on 2026-06-14
  (`Codes/pde/`, `Runs/continuation/`, `Docs/math/Math357/358/374/376/166`,
  `CLAIMS.md` tiers). The heavy numerical assets live in the FROZEN
  `C:\Dev\TECT2\Contents`.
- "Compute-bound" is a real but surmountable constraint; it is not a statement
  that the theory cannot produce the numbers.

**Cross-references**: R-043 (T-030 consolidation, the analytical-frontier settlement);
A2-PDE-WELLPOSED, B3-BCC-STRUCT, B4-MASS-GAP (background); E4/E5/E6 (the targets);
`Math374`/`Math376` (Hessian); `Math358` (Lanczos); `Math166` (zero modes);
RunRecorder / numerical-run-recording standard.
