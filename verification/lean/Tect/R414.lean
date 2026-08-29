import Mathlib

namespace Tect.R414

theorem late_exponential_factor_nonnegative {h gamma dt : ℝ}
    (hh : 0 ≤ h) (hgamma : 0 ≤ gamma) (hdt : 0 ≤ dt) :
    0 ≤ h * Real.exp (-gamma * dt) := by
  positivity

theorem semigroup_bound_nonnegative {h gamma : ℝ}
    (hh : 0 ≤ h) (hgamma : 0 < gamma) :
    0 ≤ h / gamma := by
  positivity

theorem uv_power_integral_positive {a tau c : ℝ}
    (ha : 0 < a) (halt : a < 1) (htau : 0 < tau) (hc : 0 ≤ c) :
    0 ≤ c * tau ^ (1 - a) / (1 - a) := by
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧
      (0 < (9 : ℝ) / 10) ∧ ((9 : ℝ) / 10 < 1) := by
  norm_num

end Tect.R414
