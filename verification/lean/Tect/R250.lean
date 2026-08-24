import Mathlib

namespace Tect.R250

theorem fourth_moment_fixture :
    4 * (1 : Rat)^2 * 3 = 12 := by
  norm_num

theorem shifted_norm_fixture :
    64 * (1 : Rat)^2 * 3 + (1 / 4 : Rat)^4 = 49153 / 256 := by
  norm_num

theorem kinetic_coefficient_fixture :
    ((1 / 4 : Rat)^4) * (49153 / 256 : Rat) = 49153 / 65536 := by
  norm_num

theorem shifted_fourth_plus_fixture :
    ((3 : Rat) + 1 / 8)^4 <= 8 * ((3 : Rat)^4 + (1 / 8 : Rat)^4) := by
  norm_num

theorem shifted_fourth_minus_fixture :
    ((-3 : Rat) - 1 / 8)^4 <= 8 * ((-3 : Rat)^4 + (1 / 8 : Rat)^4) := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R250
