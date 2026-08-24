import Mathlib

namespace Tect.R233

theorem bounded_evaluation_fixture :
    |(-833139 / 35840 : Rat)| <= 1382807 / 7168 := by
  norm_num

theorem product_bound_fixture :
    (1382807 / 7168 : Rat)^2 > 0 ∧
      (1382807 / 7168 : Rat)^3 > 0 ∧
      (1382807 / 7168 : Rat)^4 > 0 := by
  norm_num

theorem obstruction_fixture :
    |(84794793 / 7168 : Rat)| > 1382807 / 7168 := by
  norm_num

theorem generator_radius_failure :
    (32 : Rat) > 4 ∧ (1 / 4 : Rat) > 0 := by
  norm_num

theorem qft_scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R233
