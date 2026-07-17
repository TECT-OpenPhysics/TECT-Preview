# A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM -- spectral discretization to continuum PDE

**Tier**: T3 COMPUTABLE-SCAFFOLD (TSv2) | **Lifecycle**: ACTIVE |
**Last review**: 2026-07-17

## Statement

This package asks whether the finite Fourier grids used by the full-production
Sector-A model approximate the continuum PDE proved in P2. It deliberately
does not treat N32/N64/N128 solver output as convergence evidence.

The spatial convention is frozen as follows. `P_N` is the real-L2 Fourier
projector, the exact Galerkin residual is `P_N R(Psi_N)`, and the current P1
backend residual is the gradient of a Fourier-collocation energy. These two
objects are kept distinct; their difference is measured as aliasing error.

Stage 1 passes on an analytic, nonzero-density, three-component complex
manufactured field with all Class-II coefficients active. Against same-backend
N24 and N32 oversampled references, the N8/N12/N16 collocation-to-projected
residual errors are `5.3301e-6`, `4.2482e-10`, and `6.6679e-12`. The two
observed algebraic rates are 23.28 and 14.44. Reference-grid uncertainty is at
most `2.3351e-14`; energy error reaches `2.2534e-16`; the real discrete
energy-gradient identity is within `1.0211e-8`.

## Scope and dependencies

- Hard dependencies: `A1-PRODUCTION-FUNCTIONAL-REALISATION` and
  `A2-FULL-PRODUCTION-WELLPOSED`.
- Named hypothesis: `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`.
- Scope: fixed torus, pinned production coefficients and positive floors,
  `eta_shell=0`, CPU complex128, stage-1 manufactured field.
- Open gate: `A3-FULL-DISCRETIZATION-CLOSURE`.

The frozen conventions and acceptance thresholds are in
`discretization_manifest.json`.

## Six required closure tests

1. Spectral Galerkin residual versus continuum residual.
2. Energy versus the discrete real gradient.
3. Finite-time solution convergence with temporal error separated from spatial
   error.
4. Hessian/Ritz convergence under an explicit isolated-eigenvalue-cluster
   condition.
5. CPU/GPU and complex64/complex128 cross-checks.
6. Manufactured-solution observed convergence order.

Stage 1 supplies a self-convergence precursor to item 1 and spatial parts of
items 2 and 6. Stage 2 closes the executable finite-time and manufactured-time
parts of items 3 and 6: RK4 rates are 4.016 and 4.008, and unforced trajectory
errors decrease from `1.3063e-8` at N8 to `1.3118e-14` at N16 against the N24
reference. Energy is nonincreasing on N8, N12, N16, N20, and N24. An
independent continuum-residual implementation, item 4, item 5, and the
integrated analytic convergence argument remain open.

## Reproduction

Run from the repository root in the same Torch-enabled Python environment used
for P1:

```bash
python codes/foundations/a3_full_production_spatial_consistency.py
```

Expected: `13/13 PASS`, `A3-FULL-SPATIAL-CONSISTENCY-PASS`, exit 0. Evidence is
stored at `runs/2026-07-17-spatial-consistency/result.json`.

Then run:

```bash
python codes/foundations/a3_full_production_finite_time_convergence.py
```

Expected: `10/10 PASS`, `A3-FULL-FINITE-TIME-CONVERGENCE-PASS`, exit 0. On the
current CPU/Torch environment the full two-reference run takes about 10--12
minutes.

## Devil's-advocate record

1. **"Fourier differentiation makes the current backend exact Galerkin."**
   UPHELD as false. Pointwise nonlinear products alias; the collocation and
   projected Galerkin residuals are measured separately.
2. **"A small N16 error proves every Sector-B run approximates the continuum
   PDE."** UPHELD as false. One manufactured spatial field does not establish
   finite-time or solution-dependent uniform estimates.
3. **"Energy convergence alone controls Hessian eigenvalues."** UPHELD as
   false. Ritz convergence also needs consistent Hessian action, compactness,
   residual bounds, and an isolated-cluster gap.
4. **"CPU complex128 is sufficient hardware validation."** UPHELD as false.
   CUDA and complex64 remain explicit unfinished matrix entries.

## No-overclaim

The present T3 record is a computable scaffold and a passed spatial baseline.
Its reference uses the same backend at higher resolution, so it is not yet an
independent continuum-residual check. It is not finite-time convergence, a
Hessian/Ritz theorem, hardware
equivalence, complex64 certification, historical-solver integration, a license
to label N32/N64/N128 Sector-B output as continuum PDE evidence, or a T5/T6/T7
result.

## Next action

Add the matrix-free Hessian/Ritz audit with an explicit isolated-cluster
condition, followed by the CPU/GPU and complex64/complex128 matrix. The
independent continuum residual and integrated proof remain required before
one-command integration and tier review.
