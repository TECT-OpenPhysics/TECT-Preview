# A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM -- spectral discretization to continuum PDE

**Tier**: T6 CONDITIONAL-THEOREM (TSv2) | **Lifecycle**: ACTIVE |
**Last review**: 2026-07-17

## Statement

This package asks whether the finite Fourier grids used by the full-production
Sector-A model approximate the continuum PDE proved in P2. It deliberately
does not treat N32/N64/N128 solver output as convergence evidence.

Conditional on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`, every P2 solution from
the declared `H2` balls has an explicit uniform `H6` bound on
`0.02 <= t <= 0.2`, the collocation/Galerkin residual mismatch is bounded by
an explicit `C N^-2`, and the exact Galerkin flow restarted at `t=0.02`
converges to the projected continuum solution in `L2` at an explicit
`E N^-4` rate.

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
- Named hypothesis: `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`, identifying the
  hash-pinned T5 P1 reference functional as canonical.
- Theorem scope: fixed torus, pinned production coefficients and positive
  floors, `eta_shell=0`, `R=0.5,1,2`, `tau=0.02`, `T=0.2`, and exact nonlinear
  Fourier projection. Finite-grid CPU/CUDA tests retain their own narrower
  recorded scopes.
- The quantitative gate `A3-FULL-DISCRETIZATION-CLOSURE` is closed in the
  theorem scope stated below.

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

Stage 6 supplies the qualitative solution-ball passage. For every initial
`H2` radius `R` and every `0 < tau <= T`, P2 smoothing gives a uniform
positive-time `H6` envelope. The fourth-order residual therefore lies in a
bounded `H2` ball. The Fourier tail and periodic aliasing estimates yield
`||P_N R(u)-R_N^C(P_Nu)||_L2 <= C(R,tau,T) N^-2`, uniformly over that P2
solution ball and time interval. The order/source audit passes 13/13.

Stage 7 now makes the first input to that enclosure computable.  A rigorous
max-norm-shell Fourier embedding bound and P2 energy dissipation yield an
explicit, all-time `H2` envelope for each declared initial ball.  For initial
radii `R=0.5, 1, 2`, the certified bounds are respectively `20.16099`,
`20.35978`, and `21.21616`.  The audit is 13/13 PASS and pins the P1 backend,
P1/P2 manifests, Class-II generator convention, and derived coefficients.
Stage 8 makes the positive-time theorem quantitative for `R=0.5,1,2`,
`tau=0.02`, and `T=0.2`. Explicit Fourier embeddings, Class-II derivative
envelopes retaining the `1e-12` floor, and two endpoint-Duhamel cancellations
give finite `B6(R,tau,T)`. The derived `log10 B6` bounds are 515.378, 515.751,
and 517.320; the corresponding `log10 C` bounds are 576.355, 576.770, and
578.513. The primary and independent audits pass 15/15 and 10/10.

For the mathematically dealiased exact Galerkin flow
`partial_t u_N + L u_N + P_N N(u_N)=0`, restarted by
`u_N(tau)=P_N u(tau)`, the proof yields
`sup_[tau,T] ||u_N-P_Nu||_L2 <= E(R,tau,T) N^-4`. This is a genuine
positive-time convergence theorem, but the deliberately worst-case constants
are astronomically large and are not useful error bars at practical grids.

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

The solution-ball and package commands are:

```bash
python codes/foundations/a3_full_production_solution_ball_bound.py
python codes/foundations/a3_full_production_energy_ball_envelope.py
python codes/foundations/a3_full_production_quantitative_majorant.py
python codes/foundations/a3_full_production_quantitative_majorant_independent.py
python codes/foundations/a3_full_production_verify.py --reuse-recorded-audits
```

Expected: `13/13 PASS`, `A3-FULL-SOLUTION-BALL-BOUND-PASS`; then
`13/13 PASS`, `A3-FULL-ENERGY-BALL-ENVELOPE-PASS`; then `15/15` and
`A3-FULL-QUANTITATIVE-MAJORANT-PASS`; then `10/10` and
`A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-PASS`; then `104/104`,
`A3-FULL-PRODUCTION-VERIFY-PASS`. The verifier's default (without
`--reuse-recorded-audits`) reruns CPU audits into a temporary directory and can
take substantially longer; the recorded mode validates their immutable results
and current source hashes without overwriting them.

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
5. **"Finite B6 and C automatically give a useful practical solver error
   bar."** UPHELD as false. The floor-sensitive enclosures are astronomically
   large; they prove convergence but do not certify historical grids.
6. **"Three-halves dealiasing is exact for the Class-II residual."** UPHELD as
   false. The density denominator is rational. Only the mathematical nonlinear
   projection `P_N N(u_N)` is exact Galerkin here.
7. **"T6 silently inherits the T5 P1 functional."** VALID WITH MITIGATION. The
   identification is explicit as `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`, while
   the P2 well-posedness input is already T6.

## No-overclaim

The T6 result is conditional on the canonical-functional identification and is
restricted to the declared positive-time solution balls and exact Galerkin
flow. It is not all-device GPU equivalence, historical-solver integration, a
license to label N32/N64/N128 Sector-B output as continuum PDE evidence, a
practically sharp error budget, minimizer/BCC selection, T7, or physical-domain
closure.

## Tier review

The v2.1 review promotes T4 to T6 in one step because the new result is a
complete conditional theorem rather than an enlarged evidence-only scope. It
has a self-contained proof, one named hypothesis covering the sub-T6 hard
input, explicit quantitative sanity checks, a non-importing independent audit,
a 104/104 integrated verifier, and a PUBLISHED bundle. The bundle contains 42
files and nine entry scripts, all PASS, with digest
`6bbf537dd44a6e727db59ebc99eb640265d98ed830e0b88ef6ad0de37e559910`.
T7 is prohibited by the named hypothesis and lack of public external
reproduction.

## Next action

Preserve this T6 package as the closed P3 baseline. Any sharp practical
constant, finite-oversampling solver bridge, historical-solver certificate,
`eta_shell` extension, lower-regularity data, or infinite-volume limit must be
registered as a separate claim. P4 may proceed without widening P3.
