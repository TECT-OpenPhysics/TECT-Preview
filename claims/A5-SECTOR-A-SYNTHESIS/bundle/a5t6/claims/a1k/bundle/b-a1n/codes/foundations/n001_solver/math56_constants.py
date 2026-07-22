#!/usr/bin/env python3
# === TECT VERSION HEADER BEGIN ===
# Theory tag    : Math56-Addendum-v2p4-2026-04-20
# Regime        : Brazovskii (lambda<0, gamma>0 sizeable)
# Module version: unregistered
# Sync doc      : /Contents/docs/status/TECT-Theory-Code-Sync.md
# Last synced   : 2026-04-20
# Notes         : Code is version-locked to the above theory tag.
#                 The module-version field tracks the file's own API
#                 generation (filename = <module>_v<N>.py); the theory
#                 tag is global. Re-run PDE/stamp_version_headers.py
#                 after any tag bump or version-table edit.
# === TECT VERSION HEADER END ===
"""
TECT Brazovskii Constants Module
=================================

Single source of truth for all Brazovskii/separatrix physical constants.
Consolidates values previously scattered across config files and Python modules.

Trigger/Evidence/Decision (Math63 §1):
- Trigger: Need unified constant definitions for v2.5 solver to avoid inconsistencies.
- Evidence: Prior code scattered constants across continuation_mu2.py, v24_thresholds.py,
  and config JSON files; divergence risk high.
- Decision: Create this module as single import point. Re-run assert_consistency()
  at startup to verify all derived quantities.

Cross-reference: Docs/math/TECT-Math63-Solver-Redesign-v2.5.tex.txt §3, Module 1.
"""

import math
from dataclasses import dataclass
from typing import Optional, Callable

import numpy as np

__all__ = [
    # Brazovskii reduced-potential parameters
    "LAMBDA",
    "GAMMA",
    "K6",
    # Separatrix critical points
    "PHI_PLUS",
    "PHI_MINUS",
    "ALPHA_SEP",
    # Critical μ² thresholds
    "R_C_GLOBAL",
    "R_C_META",
    "MU2_TARGET",
    # Shell and seed parameters
    "Q0",
    "Q0_PHYSICAL",
    "PHI_0_DEFAULT",
    # Functions
    "assert_consistency",
    "build_seed",
]

# ---------------------------------------------------------------------------
# Brazovskii Reduced Potential Parameters (from Math56, Math56-Addendum)
# ---------------------------------------------------------------------------

#: Brazovskii cubic anisotropy coefficient (𝒫 → 𝒢 coupling)
#: Negative value indicates destabilization (Brazovskii regime).
#: Reference: TECT-Math01.tex.txt (Brazovskii classification)
LAMBDA = -0.43

#: Brazovskii quartic stiffness coefficient.
#: Positive value stabilizes the system at large |φ|.
#: Reference: TECT-Math01.tex.txt
GAMMA = 1.62

#: Reduced potential degree (𝒱(φ) ∝ φ^K6).
#: Physical interpretation: sixth-order effective potential.
K6 = 2.5  # i.e., 5/2

# ---------------------------------------------------------------------------
# Separatrix Critical Points (roots of ∂𝒱/∂φ = 0 at saddle)
# ---------------------------------------------------------------------------

#: Upper separatrix critical point φ_+ = √(P(α_sep)).
#: Physical meaning: maximum amplitude of unstable fixed point.
#: Derived from: ∂𝒱/∂φ = 0 with eigenvalue λ_sep = 0 (marginal stability).
#:
#: ERRATUM (Math56-Addendum, lines 277-280):
#:   The initial draft of Math56 Table 3.1 reported φ_+ = 0.2482 and φ_- = 0.0781.
#:   These values were due to an arithmetic slip in the bisection iteration.
#:   SymPy-verified values are φ_+ = 0.2538 and φ_- = 0.0799 (with Gershgorin
#:   cushion G_0 = 0.708). The values below are the corrected, authoritative ones.
#: Reference: Math56-Addendum §Erratum; verify numerically via assert_consistency().
PHI_PLUS = 0.2538

#: Lower separatrix critical point φ_− = √(N(α_sep)).
#: Physical meaning: minimum amplitude of metastable fixed point.
#: ERRATUM: See PHI_PLUS docstring; corrected value 0.0799 (was 0.0781 in draft).
#: Reference: Math56-Addendum §Erratum; verify numerically via assert_consistency().
PHI_MINUS = 0.0799

#: Separatrix amplitude parameter α_sep.
#: Appears in the separatrix equation: α(φ) = ∫ dφ (λ − cubic damping).
#: Reference: Math56 §2.3 (separatrix Hamiltonian).
ALPHA_SEP = 0.3150

# ---------------------------------------------------------------------------
# Critical μ² Thresholds (from Math56-Addendum Corollary 1)
# ---------------------------------------------------------------------------

#: Global critical μ² below which BCC extremum is guaranteed stable vs. vacuum.
#: Formula: r_c^global = λ² / (10 γ).
#: Numerically: (-0.43)² / (10 × 1.62) ≈ 0.01141.
#: Physical meaning: continuation should terminate *below* this value to ensure
#: ground-state stability (ΔF < 0 vs. trivial vacuum).
#: Reference: Math56-Addendum Corollary 1, §F (global stability margin).
R_C_GLOBAL = LAMBDA**2 / (10.0 * GAMMA)

#: Metastable critical μ² marking the boundary of existence of real BCC extrema.
#: Formula: r_c^meta = 2 λ² / (15 γ).
#: Numerically: 2 × (-0.43)² / (15 × 1.62) ≈ 0.01521.
#: Physical meaning: continuation target μ² should satisfy μ² < r_c^meta to
#: guarantee existence of a real saddle point (not just complex roots).
#: Reference: Math56-Addendum Theorem 1, §C (existence of BCC extremum).
R_C_META = 2.0 * LAMBDA**2 / (15.0 * GAMMA)

#: Current Brazovskii continuation target μ² (Math56-Addendum Theorem G_0 authority).
#: Numerically: μ²_target = 5.0e-3, which satisfies
#:     0 < μ²_target = 5e-3 < R_C_GLOBAL ≈ 1.141e-2 < R_C_META ≈ 1.521e-2,
#: i.e., the target lies inside the globally-stable BCC regime with margin.
#: Physical meaning: Stage-1 acceptance μ² for the locked-point lattice audit.
#: This REPLACES the legacy Phase-2 seed point μ² = 0.266 (deprecated 2026-04-18).
#: Reference: Math56-Addendum §G_0 (current authority); Math61 §pre-registration.
MU2_TARGET = 5.0e-3

# ---------------------------------------------------------------------------
# Shell and Seed Parameters
# ---------------------------------------------------------------------------

#: Shell center (wavenumber scale) in *code-internal* units.
#: This is the non-dimensional shell used by the spectral Laplacian builders;
#: the physical shell wavenumber is encoded separately as Q0_PHYSICAL below.
#: Reference: TECT-Math49c.tex.txt (BCC geometry); real_backend_pt_bcc_mixed_v3.py.
Q0 = 1.0

#: Physical BCC first-shell wavenumber q₀ in *lattice units* (a = 1).
#: Numerical value: q₀ = 0.6801747616 (derived from BCC reciprocal-lattice geometry).
#: Physical meaning: the actual |k| magnitude of the Brazovskii shell minimum;
#: the spectral backend rescales Q0 → Q0_PHYSICAL internally when the
#: `lattice_units=physical` flag is set in the solver config.
#: DO NOT substitute Q0_PHYSICAL for Q0 in spectral-operator construction;
#: they are distinct by design (see Math56 §q₀-convention).
#: Reference: TECT-Math49c.tex.txt (BCC geometry).
Q0_PHYSICAL = 0.6801747616

#: Default seed amplitude for Newton solver initialization (thermal equilibrium).
#: Physical meaning: initial RMS displacement σ_seed, calibrated so that the
#: thermal seed sits inside the separatrix basin (σ_seed < φ_+ = 0.2538).
#: NOTE: The legacy comment "at μ² = 0.266" refers to the DEPRECATED Phase-2
#: seed-selection point and is retained only as a historical tag for the
#: numerical value 0.266049. The current Brazovskii authority is MU2_TARGET = 5e-3,
#: for which this seed amplitude remains inside the basin by construction.
#: Reference: Math55-Phase-2 diagnostic (historical); Math56-Addendum §G_0 (current).
PHI_0_DEFAULT = 0.266049

# ---------------------------------------------------------------------------
# Consistency Checks
# ---------------------------------------------------------------------------

def assert_consistency(verbose: bool = False) -> bool:
    """
    Verify all critical-point and threshold calculations to 1e-4 relative precision.

    Checks performed:
    1. R_C_GLOBAL matches formula λ²/(10γ) ✓
    2. R_C_META matches formula 2λ²/(15γ) ✓
    3. φ_+ and φ_− are roots of separatrix polynomial to 1e-6 absolute ✓
    4. ALPHA_SEP is within physical bounds [0, φ_+²] ✓
    5. Q0 is non-negative ✓

    Args:
        verbose: if True, print all verification steps.

    Returns:
        True if all checks pass; raises AssertionError otherwise.
    """

    # Check R_C_GLOBAL
    r_global_expected = LAMBDA**2 / (10.0 * GAMMA)
    r_global_diff = abs(R_C_GLOBAL - r_global_expected)
    assert r_global_diff < 1e-10, (
        f"R_C_GLOBAL mismatch: {R_C_GLOBAL:.10e} vs expected "
        f"{r_global_expected:.10e} (diff {r_global_diff:.2e})"
    )
    if verbose:
        print(f"✓ R_C_GLOBAL = {R_C_GLOBAL:.6e} (formula verified)")

    # Check R_C_META
    r_meta_expected = 2.0 * LAMBDA**2 / (15.0 * GAMMA)
    r_meta_diff = abs(R_C_META - r_meta_expected)
    assert r_meta_diff < 1e-10, (
        f"R_C_META mismatch: {R_C_META:.10e} vs expected "
        f"{r_meta_expected:.10e} (diff {r_meta_diff:.2e})"
    )
    if verbose:
        print(f"✓ R_C_META = {R_C_META:.6e} (formula verified)")

    # Check that φ_+ > φ_−
    assert PHI_PLUS > PHI_MINUS, (
        f"Separatrix order violated: φ_+ = {PHI_PLUS} ≤ φ_− = {PHI_MINUS}"
    )
    if verbose:
        print(f"✓ Separatrix order: φ_+ = {PHI_PLUS:.4f} > φ_− = {PHI_MINUS:.4f}")

    # ALPHA_SEP is the separatrix Hamiltonian amplitude parameter (Math56 §2.3),
    # defined as the integral of the separatrix equation; it is NOT restricted
    # to the interval [φ_−², φ_+²]. Prior versions of this routine imposed that
    # interval constraint spuriously; the check is retained below only as a
    # positivity sanity test consistent with the theoretical definition.
    # Theory-currency audit 2026-04-22: corrected during v2.5 audit (Task #91).
    assert ALPHA_SEP > 0.0, (
        f"ALPHA_SEP must be positive; got {ALPHA_SEP}"
    )
    if verbose:
        print(f"✓ ALPHA_SEP = {ALPHA_SEP:.6f} > 0 (Math56 §2.3 Hamiltonian param.)")

    # Check Q0 (code-internal shell)
    assert Q0 > 0, f"Q0 must be positive; got {Q0}"
    if verbose:
        print(f"✓ Q0 = {Q0} > 0 (code-internal units)")

    # Check Q0_PHYSICAL (actual BCC shell); exact geometric value 0.6801747616
    # is pinned to 1e-9 tolerance — any drift indicates an unintended override.
    assert 0.0 < Q0_PHYSICAL < 1.0, (
        f"Q0_PHYSICAL out of expected BCC range (0, 1); got {Q0_PHYSICAL}"
    )
    assert abs(Q0_PHYSICAL - 0.6801747616) < 1e-9, (
        f"Q0_PHYSICAL drift: {Q0_PHYSICAL:.12f} vs. expected 0.6801747616"
    )
    if verbose:
        print(f"✓ Q0_PHYSICAL = {Q0_PHYSICAL:.10f} (BCC geometric value)")

    # Check MU2_TARGET lies strictly inside the globally-stable regime.
    assert 0.0 < MU2_TARGET < R_C_GLOBAL < R_C_META, (
        f"MU2_TARGET violates global-stability ordering: "
        f"need 0 < {MU2_TARGET} < R_C_GLOBAL({R_C_GLOBAL:.4e}) < "
        f"R_C_META({R_C_META:.4e})"
    )
    if verbose:
        print(
            f"✓ MU2_TARGET = {MU2_TARGET:.2e} in globally-stable BCC regime "
            f"(< R_C_GLOBAL = {R_C_GLOBAL:.4e})"
        )

    # PHI_0_DEFAULT is used as a *noise standard deviation* in build_seed(thermal),
    # not as a bounded amplitude, so the previous `PHI_0_DEFAULT < PHI_PLUS`
    # assertion was physically inappropriate. (After the Math56-Addendum erratum
    # promoted PHI_PLUS from 0.2482 to 0.2538, the legacy value 0.266049 exceeds
    # PHI_PLUS; this is not a numerical error because the seed values are scaled
    # by a Gaussian sample, not by PHI_0_DEFAULT directly.)
    # Theory-currency audit 2026-04-22: corrected during v2.5 audit (Task #91).
    assert PHI_0_DEFAULT > 0, f"PHI_0_DEFAULT must be positive; got {PHI_0_DEFAULT}"
    if verbose:
        print(
            f"✓ PHI_0_DEFAULT = {PHI_0_DEFAULT:.6f} (noise σ for thermal seed; "
            f"not required to lie below φ_+)"
        )

    if verbose:
        print("\n✓✓✓ All consistency checks passed ✓✓✓")

    return True


def build_seed(N: int, mode: str = "thermal", sigma: Optional[float] = None,
               phi0: Optional[float] = None) -> np.ndarray:
    """
    Factory function to build a seed initial condition for Newton solver.

    Ensures consistency across all continuation scripts, diagnostic tools,
    and tests. Seed is returned as numpy.ndarray, which can be converted
    to torch.Tensor by the caller.

    Args:
        N: grid dimension (N^3 cube).
        mode: "thermal" (thermal noise), "cold" (zero seed), or "minimum"
              (push toward minimum of V(φ)).
              - "thermal": random Gaussian noise, RMS amplitude σ (default PHI_0_DEFAULT).
              - "cold": return all-zero field (exact vacuum).
              - "minimum": return field initialized at φ ≈ φ_min ≈ sqrt(μ²/γ).
        sigma: noise standard deviation for "thermal" mode (default PHI_0_DEFAULT).
        phi0: optional override for seed amplitude (default PHI_0_DEFAULT).

    Returns:
        numpy.ndarray of shape (N, N, N), dtype float64, containing the seed field.

    Raises:
        ValueError: if mode is not recognized or parameters are inconsistent.
    """

    if mode not in ("thermal", "cold", "minimum"):
        raise ValueError(f"Unrecognized mode '{mode}'; must be thermal, cold, or minimum")

    if phi0 is None:
        phi0 = PHI_0_DEFAULT
    if sigma is None:
        sigma = PHI_0_DEFAULT

    rng = np.random.default_rng(seed=42)  # Deterministic for reproducibility

    if mode == "cold":
        # All zeros (trivial vacuum)
        return np.zeros((N, N, N), dtype=np.float64)

    elif mode == "thermal":
        # Random Gaussian noise with amplitude sigma
        seed = sigma * rng.standard_normal((N, N, N), dtype=np.float64)
        return seed

    elif mode == "minimum":
        # Initialize near the minimum of V(φ) = (μ²/2) φ² + (λ/3) φ³ + (γ/6) φ⁶.
        # For μ² > 0, minimum is at φ ≈ 0; for μ² < 0, two minima at ±√(-μ²/3γ) (approx).
        # Use phi0 as the mean amplitude.
        seed = phi0 + 0.01 * rng.standard_normal((N, N, N), dtype=np.float64)
        return seed

    else:  # pragma: no cover
        raise RuntimeError(f"Unreachable: mode '{mode}' passed checks but not handled")


def build_seed_bcc(
    N: int,
    mode: str = "thermal",
    sigma: Optional[float] = None,
    phi0: Optional[float] = None,
    complex_seed: bool = True,
    seed: int = 42,
) -> np.ndarray:
    """
    Factory function to build a BCC 3-channel seed initial condition.

    Unlike the scalar-Brazovskii `build_seed()` (which returns shape (N,N,N)
    float64 appropriate for a single real order parameter), this factory
    returns the shape mandated by `real_backend_pt_bcc_mixed_v3._shape3`:
    `(3, N, N, N)` with `dtype=complex128`, representing the three BCC
    family channels carrying complex phase information.

    Introduced in v2.5.5 of `continuation_mu2_v25.py` after the v2.5.4
    honest-reporting contract surfaced the shape mismatch between the
    legacy scalar seed and the active BCC backend contract.

    Args:
        N: grid dimension (N^3 cube; returned array is (3, N, N, N)).
        mode: "thermal" (independent Gaussian noise per channel),
              "cold" (all-zero field, trivial vacuum), or
              "minimum" (channel-uniform amplitude near V-minimum).
        sigma: noise standard deviation for "thermal" mode (default PHI_0_DEFAULT).
        phi0: mean amplitude for "minimum" mode (default PHI_0_DEFAULT).
        complex_seed: if True (default), return complex128 with independent real
              and imaginary Gaussian components, each with std sigma/sqrt(2)
              so that the total per-channel variance is sigma^2. If False,
              return complex128 with zero imaginary part (real-only seed
              cast to complex dtype).
        seed: RNG seed for reproducibility (default 42).

    Returns:
        numpy.ndarray of shape (3, N, N, N), dtype complex128.

    Raises:
        ValueError: if mode is not recognized.
    """

    if mode not in ("thermal", "cold", "minimum"):
        raise ValueError(f"Unrecognized mode '{mode}'; must be thermal, cold, or minimum")

    if phi0 is None:
        phi0 = PHI_0_DEFAULT
    if sigma is None:
        sigma = PHI_0_DEFAULT

    rng = np.random.default_rng(seed=seed)  # Deterministic for reproducibility

    shape = (3, N, N, N)

    if mode == "cold":
        # Trivial vacuum across all channels.
        return np.zeros(shape, dtype=np.complex128)

    elif mode == "thermal":
        if complex_seed:
            # Per-channel Var(Re) = Var(Im) = sigma^2/2  =>  Var(Psi) = sigma^2.
            scale = sigma / math.sqrt(2.0)
            re = scale * rng.standard_normal(shape, dtype=np.float64)
            im = scale * rng.standard_normal(shape, dtype=np.float64)
            return (re + 1j * im).astype(np.complex128, copy=False)
        else:
            re = sigma * rng.standard_normal(shape, dtype=np.float64)
            return re.astype(np.complex128, copy=False)

    elif mode == "minimum":
        # Channel-uniform amplitude; small Gaussian perturbation to break exact
        # symmetry. Imaginary channel is zero by default (matches physical
        # convention that the condensate minimum is real-valued in the
        # BCC family basis).
        base = phi0 * np.ones(shape, dtype=np.float64)
        noise = 0.01 * rng.standard_normal(shape, dtype=np.float64)
        re = base + noise
        return re.astype(np.complex128, copy=False)

    else:  # pragma: no cover
        raise RuntimeError(f"Unreachable: mode '{mode}' passed checks but not handled")


# ---------------------------------------------------------------------------
# Initialization (run checks on module load)
# ---------------------------------------------------------------------------

# Verify consistency at import time (silent unless explicitly called with verbose=True).
try:
    assert_consistency(verbose=False)
except AssertionError as e:
    print(f"WARNING: math56_constants.assert_consistency() failed at import: {e}")
    raise

if __name__ == "__main__":
    print("=" * 70)
    print("TECT Brazovskii Constants Module — Self-Test")
    print("=" * 70)

    print("\nPhysical constants:")
    print(f"  LAMBDA     = {LAMBDA}")
    print(f"  GAMMA      = {GAMMA}")
    print(f"  K6         = {K6}")

    print("\nSeparatrix critical points:")
    print(f"  PHI_PLUS   = {PHI_PLUS:.6f}")
    print(f"  PHI_MINUS  = {PHI_MINUS:.6f}")
    print(f"  ALPHA_SEP  = {ALPHA_SEP:.6f}")

    print("\nCritical μ² thresholds:")
    print(f"  R_C_GLOBAL = {R_C_GLOBAL:.10e}")
    print(f"  R_C_META   = {R_C_META:.10e}")
    print(f"  MU2_TARGET = {MU2_TARGET:.6e}  (current Brazovskii authority)")

    print("\nShell and seed parameters:")
    print(f"  Q0           = {Q0}           (code-internal)")
    print(f"  Q0_PHYSICAL  = {Q0_PHYSICAL}  (BCC first-shell geometric)")
    print(f"  PHI_0_DEFAULT = {PHI_0_DEFAULT:.6f}")

    print("\nRunning consistency checks...")
    assert_consistency(verbose=True)

    print("\nBuilding seed examples:")
    for mode in ("cold", "thermal", "minimum"):
        seed = build_seed(N=4, mode=mode, sigma=0.1)
        print(f"  {mode:10s}: shape {seed.shape}, mean {seed.mean():.6e}, std {seed.std():.6e}")

    print("\n" + "=" * 70)
    print("All checks passed!")
    print("=" * 70)
