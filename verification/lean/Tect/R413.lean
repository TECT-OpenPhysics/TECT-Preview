import Mathlib

namespace Tect.R413

theorem mellin_remainder_nonnegative {lambda tau : ℝ} (hlambda : 0 < lambda) (htau : 0 ≤ tau) :
    0 ≤ Real.exp (-tau * lambda) / lambda := by
  positivity

theorem heat_monotone {lambda t₁ t₂ : ℝ} (hlambda : 0 ≤ lambda) (h_time : t₁ ≤ t₂) :
    Real.exp (-t₂ * lambda) ≤ Real.exp (-t₁ * lambda) := by
  apply Real.exp_le_exp.mpr
  nlinarith

theorem uv_integral_positive {c a gamma t : ℝ} (hc : 0 < c) (ha : 0 < a)
    (hgamma : 0 < gamma) (ht : 0 < t) :
    0 < c * a * gamma * t ^ (-a) := by
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧
      (0 < (9 : ℝ) / 10) ∧ ((9 : ℝ) / 10 < 1) := by
  norm_num

end Tect.R413
