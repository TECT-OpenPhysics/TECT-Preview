import Mathlib

namespace Tect.R232

theorem source_rate_fixture :
    (1382807 / 7168 : Rat) = 1382807 / 7168 := by
  norm_num

theorem reverse_rate_fixture :
    (1382807 / 7168 : Rat) = 1382807 / 7168 := by
  norm_num

theorem product_power_fixture :
    (1382807 / 7168 : Rat)^2 > 0 ∧
      (1382807 / 7168 : Rat)^3 > 0 ∧
      (1382807 / 7168 : Rat)^4 > 0 := by
  norm_num

theorem exponent_fixture :
    (2 : Rat) * 6 * 2 * (1382807 / 7168) * (1 / 1000) =
      (4148421 / 896000 : Rat) := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R232
