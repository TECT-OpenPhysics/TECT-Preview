import Mathlib

namespace Tect.R393

theorem cutoff_profile_nonnegative {x : ℝ} (h : 0 ≤ x) : 0 ≤ x := by
  exact h

theorem cutoff_profile_ratio_nonnegative {numerator denominator : ℝ}
    (h_num : 0 ≤ numerator) (h_den : 0 ≤ denominator) :
    0 ≤ numerator / denominator := by
  exact div_nonneg h_num h_den

theorem finite_scope :
    (0 ≤ (10 : ℝ)) ∧ ((3 : ℝ) ≤ 10) ∧ ((3 : ℝ) / 10 ≤ 1) := by
  norm_num

end Tect.R393
