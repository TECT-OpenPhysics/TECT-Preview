import Mathlib

namespace Tect.R253

theorem shifted_fourth_first_fixture :
    32 * (3 : Rat) + (1 / 4 : Rat)^4 / 2 = 49153 / 512 := by
  norm_num

theorem shifted_fourth_second_fixture :
    32 * (3 : Rat) + (-1 / 3 : Rat)^4 / 2 = 15553 / 162 := by
  norm_num

theorem l1_amplitude_fixture :
    |(1 / 4 : Rat)| + |(-1 / 3 : Rat)| = 7 / 12 := by
  norm_num

theorem kinetic_bound_fixture :
    2 * (2 : Rat)^3 *
        ((1 / 4 : Rat)^4 * (49153 / 512 : Rat) +
          (-1 / 3 : Rat)^4 * (15553 / 162 : Rat)) =
      1341774241 / 53747712 := by
  norm_num

theorem kinetic_ceiling_fixture :
    (1341774241 / 53747712 : Rat) < 25 := by
  norm_num

theorem force_upper_fixture :
    2 * (7 / 12 : Rat)^2 * 423000 = 287875 := by
  norm_num

theorem force_ceiling_fixture :
    (287875 : Rat) < 537^2 := by
  norm_num

theorem full_triangle_upper_fixture :
    (5 + 537 : Rat)^2 = 293764 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R253
