import Mathlib

namespace Tect.R243

theorem coefficient_fixture :
    ((3 : Rat) / 5) / (4 * ((1 : Rat) / 100)) = 15 := by
  norm_num

theorem shift_fixture :
    2 * (3 / 5 : Rat) * ((-9 / 2 : Rat)^2 / (2 * (3 / 5 : Rat))) = (-9 / 2 : Rat)^2 := by
  norm_num [div_pow]

theorem pair_constant_fixture :
    1 + 2 * ((-9 / 2 : Rat)^2 / (2 * (3 / 5 : Rat))) = 139 / 4 := by
  norm_num

theorem endpoint_form_fixture :
    (-9 / 2 : Rat) * (2 : Rat)^2 / 2
        + (3 / 5 : Rat) * (2 : Rat)^4 / 4
        + ((-9 / 2 : Rat)^2 / (2 * (3 / 5 : Rat)))
      <= 15 * (1 + (1 / 100 : Rat) * (2 : Rat)^4)
        + ((-9 / 2 : Rat)^2 / (2 * (3 / 5 : Rat))) := by
  norm_num

theorem bridge_fixture :
    9 * (((139 / 4 : Rat)^3) + 2 * ((15 : Rat)^3) * 3)
      = 35834571 / 64 := by
  norm_num

theorem fifth_dominates_third_fixture :
    (1 : Rat)^3 <= (1 : Rat)^5 ∧
      (2 : Rat)^3 <= (2 : Rat)^5 ∧
      (5 : Rat)^3 <= (5 : Rat)^5 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R243
