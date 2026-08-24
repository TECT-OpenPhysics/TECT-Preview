import Mathlib

namespace Tect.R239

theorem quartic_square_identity :
    (3 / 5 : Rat) * ((1 : Rat) ^ 2 + (-9 / 2 : Rat) / (3 / 5)) ^ 2 / 4 =
      (3 / 5 : Rat) * ((1 : Rat) ^ 2 - (15 / 2 : Rat)) ^ 2 / 4 := by
  norm_num

theorem quartic_remainder_square :
    2 * ((1 : Rat) ^ 2 - (15 / 2 : Rat)) ^ 2 + 2 * ((15 / 2 : Rat) ^ 2) - (1 : Rat) ^ 4 =
      ((1 : Rat) ^ 2 - 15) ^ 2 := by
  norm_num

theorem coercivity_constant_fixture :
    (8 : Rat) / (3 / 5 : Rat) = 40 / 3 := by
  norm_num

theorem shift_fixture :
    ((-9 / 2 : Rat) ^ 2) / (2 * (3 / 5 : Rat)) = 135 / 8 := by
  norm_num

theorem minimum_square_fixture :
    (3 / 5 : Rat) * ((15 / 2 : Rat) + (-9 / 2 : Rat) / (3 / 5 : Rat)) ^ 2 / 4 = 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R239
