import Mathlib

namespace Tect.R395

theorem gentle_sqrt_bound {distance tail : ℝ}
    (h_tail : 0 ≤ tail) (h_distance : 0 ≤ distance)
    (h_square : distance ^ 2 ≤ 4 * tail) :
    distance ≤ 2 * Real.sqrt tail := by
  have h_sqrt : 0 ≤ Real.sqrt tail := Real.sqrt_nonneg tail
  have h_sq : (Real.sqrt tail) ^ 2 = tail := by
    simpa using Real.sq_sqrt h_tail
  by_contra h_not
  have h_gt : 2 * Real.sqrt tail < distance := lt_of_not_ge h_not
  nlinarith

theorem sqrt_monotone {left right : ℝ}
    (h_left : 0 ≤ left) (h_order : left ≤ right) :
    Real.sqrt left ≤ Real.sqrt right := by
  exact Real.sqrt_le_sqrt h_order

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ ((1 : ℝ) / 2 ≤ 2) := by
  norm_num

end Tect.R395
