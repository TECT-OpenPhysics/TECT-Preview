import Mathlib

namespace Tect.R352

/-- The positive rank-one B fixture has determinant zero. -/
theorem rank_one_b_fixture :
    (1 : Rat) * 4 - (-2) * (-2) = 0 := by
  norm_num

/-- A positive K=A+B fixture has determinant one. -/
theorem generic_form_order_shortcut_counterexample :
    (1 : Rat) * 5 - (-2) * (-2) = 1 := by
  norm_num

/-- The exact determinant of K^4-A^4 is negative. -/
theorem fourth_difference_determinant_negative :
    (169 : Rat) * 984 - (-408) * (-408) = -168 ∧ (-168 : Rat) < 0 := by
  norm_num

end Tect.R352
