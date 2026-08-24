import Mathlib

namespace Tect.R224

theorem cauchy_product_fixture : (19 / 9 : Rat) ≤ 34 / 9 := by
  norm_num

theorem field_radius_loss_constant :
    (1 / 2 : Rat) / ((1 / 2 : Rat) - 1 / 3)^2 = 18 := by
  norm_num

theorem source_radius_loss_constant :
    (1 / 3 : Rat) / ((1 / 3 : Rat) - 1 / 4)^2 = 48 := by
  norm_num

theorem field_derivative_fixture :
    (4 / 3 : Rat) ≤ 18 * 2 := by
  norm_num

theorem source_derivative_fixture :
    (11 / 9 : Rat) ≤ 48 * 2 := by
  norm_num

theorem geometric_full_fixture :
    1 / ((1 - (1 / 5 : Rat) * (1 / 2 : Rat))
      * (1 - (1 / 7 : Rat) * (1 / 3 : Rat))) = 7 / 6 := by
  norm_num

theorem geometric_tail_degree_three_fixture :
    (7 / 6 : Rat) - (
      1
      + ((1 / 10 : Rat) + 1 / 21)
      + ((1 / 100 : Rat) + 1 / 210 + 1 / 441)
      + ((1 / 1000 : Rat) + 1 / 2100 + 1 / 4410 + 1 / 9261))
      = 1919 / 9261000 := by
  norm_num

theorem geometric_tail_target_fixture :
    (1919 / 9261000 : Rat) < 1 / 100 := by
  norm_num

theorem formal_scope_fixture :
    (True ∧ True ∧ True) ∧ ¬False := by
  norm_num

end Tect.R224
