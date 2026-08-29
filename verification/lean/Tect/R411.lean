import Mathlib

namespace Tect.R411

theorem alpha_positive {a : ℝ} (ha : 0 < a) : 0 < a := ha

theorem sublinear_zeta_tail_nonnegative {s m : ℝ} (hs : 1 < s) (hm : 0 < m) :
    0 ≤ m ^ (1 - s) / (s - 1) := by
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R411
