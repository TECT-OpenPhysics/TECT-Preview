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
reference. Energy is nonincreasing on N8, N12, N16, N20, and N24.

Stage 3 now closes the executable Hessian/Ritz item in its declared scope. The
homogeneous 12-real-dimensional Fourier block has an isolated lowest cluster
with gap `0.1368657` and maximum Ritz-residual/gap `1.0061e-8`. At the
nonuniform Class-II stress field, the fixed-subspace Ritz errors are
`1.5199e-3`, `4.7888e-7`, and `2.7136e-8`, with observed orders 19.89 and 9.98.
This certifies the invariant-block cluster and grid convergence of the declared
non-invariant Ritz matrix; it is not the full spectrum of a Sector-B solution.

Stage 4 now closes the declared hardware/precision matrix. The independently
implemented portable functional matches the hash-pinned canonical CPU
complex128 reference on CPU and on the recorded CUDA environment
(`torch 2.13.0+cu130`, one NVIDIA GeForce RTX 5070 Laptop GPU). All six
assertions pass. CUDA complex128 has maximum energy/residual errors
`5.7489e-16` and `1.7181e-15`; CUDA complex64 has `8.5245e-8` and
`3.7843e-7`, respectively. Both are within the frozen acceptance limits. This
is a recorded-device result, not a claim about every GPU.

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

Hessian/Ritz and hardware/precision commands are:

```bash
python codes/foundations/a3_full_production_hessian_ritz_convergence.py
python codes/foundations/a3_full_production_hardware_precision.py
```

Expected: `13/13 PASS` and `A3-FULL-HESSIAN-RITZ-CONVERGENCE-PASS`; then
`6/6 available assertions PASS` and `A3-FULL-HARDWARE-PRECISION-PASS` in a
CUDA-enabled Torch build. The recorded CUDA evidence is hash-checked against
the current canonical backend and frozen manifest.

Stage 5 closes the independent manufactured-field quadrature proxy for item 1.
Each `S_N` field is Fourier-prolonged exactly to M24 and M32, evaluated by the
portable functional's real gradient, then projected back by `P_N`. The
prolongation mismatch is at most `3.0848e-16`, the portable/canonical residual
comparison is exact on every sampled grid, and M24/M32 projection uncertainty
is at most `2.5180e-14`. Canonical collocation-to-independent-proxy errors are
`5.3301e-6`, `4.2482e-10`, and `6.6668e-12`, with rates 23.28 and 14.44.
This is an independently implemented quadrature proxy for an analytic field;
it is not yet a uniform continuum theorem for every P2 solution.

Run it with:

```bash
python codes/foundations/a3_full_production_independent_galerkin.py
```

Expected: `11/11 PASS`, `A3-FULL-INDEPENDENT-GALERKIN-PASS`, exit 0.

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
4. **"One GPU run validates every accelerator and precision regime."** UPHELD
   as false. The CPU/CUDA complex128/64 matrix is closed only for the recorded
   N8 fields and RTX 5070 Laptop GPU environment; broader device coverage is
   not asserted.

## No-overclaim

The present T3 record includes an independent manufactured-field
continuum-quadrature proxy and a recorded CUDA consistency matrix, but not a
uniform error theorem for arbitrary P2 solutions. It is not all-device GPU
equivalence, historical-solver integration, a license to label N32/N64/N128
Sector-B output as continuum PDE evidence, or a T5/T6/T7 result.

## Next action

Prove the uniform continuum-quadrature/Galerkin error bound and build the
integrated one-command verifier before independent reproduction and tier review.
