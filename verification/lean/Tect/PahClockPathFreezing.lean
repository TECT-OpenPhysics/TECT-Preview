import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

open MeasureTheory Filter
open scoped Topology
namespace Tect.PahClockPathFreezing

-- Parameterized deterministic, supplied-moment and domination bridges only.
-- Finite jump construction, source rates, clock inverse and cutoff decay
-- remain analytic obligations in the accompanying certificate.

theorem supplied_factorial_moment_identity
    (mean factorial second intensity : Real)
    (hmean : mean = intensity)
    (hfactorial : factorial = intensity^2)
    (hsplit : second = factorial + mean) :
    second = intensity + intensity^2 := by
  rw [hsplit, hmean, hfactorial]
  ring

theorem path_envelope_square (d delta count : Real)
    (hcount : 0 <= delta * count)
    (hdom : |d| <= delta * count) :
    d^2 <= delta^2 * count^2 := by
  have h := (sq_le_sq₀ (abs_nonneg d) hcount).2 hdom
  simpa only [sq_abs, mul_pow] using h

theorem inverse_clock_horizon (c elapsed tau horizon : Real)
    (hc : 0 < c) (hlower : c * elapsed <= tau)
    (hupper : tau <= horizon) : elapsed <= horizon / c := by
  apply (le_div_iff₀ hc).2
  nlinarith

theorem supplied_path_second_moment_bound
    {Omega : Type*} [MeasurableSpace Omega] (mu : Measure Omega)
    (D N : Omega -> Real) (delta intensity : Real)
    (hD : Integrable (fun w => (D w)^2) mu)
    (hN : Integrable (fun w => (N w)^2) mu)
    (hcount : forall w, 0 <= delta * N w)
    (hdom : forall w, |D w| <= delta * N w)
    (hmoment : (∫ w, (N w)^2 ∂mu) = intensity + intensity^2) :
    (∫ w, (D w)^2 ∂mu) <= delta^2 * (intensity + intensity^2) := by
  have hpoint : (fun w => (D w)^2) ≤ᵐ[mu]
      (fun w => delta^2 * (N w)^2) :=
    Filter.Eventually.of_forall (fun w => path_envelope_square
      (D w) delta (N w) (hcount w) (hdom w))
  calc
    (∫ w, (D w)^2 ∂mu) <=
        (∫ w, delta^2 * (N w)^2 ∂mu) :=
          integral_mono_ae hD (hN.const_mul (delta^2)) hpoint
    _ = delta^2 * (intensity + intensity^2) := by
      rw [integral_const_mul, hmoment]

theorem vanishing_path_moment_by_domination
    (err delta : Nat -> Real) (C : Real)
    (hzero : Tendsto delta atTop (nhds 0))
    (hnonneg : forall n, 0 <= err n)
    (hupper : forall n, err n <= (delta n)^2 * C) :
    Tendsto err atTop (nhds 0) := by
  have hbound : Tendsto (fun n => (delta n)^2 * C) atTop (nhds 0) := by
    simpa using (hzero.pow 2).mul_const C
  exact squeeze_zero hnonneg hupper hbound

end Tect.PahClockPathFreezing
