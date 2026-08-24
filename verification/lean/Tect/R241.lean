import Mathlib

namespace Tect.R241

theorem local_energy_shift_fixture :
    ((-9 / 2 : Rat) ^ 2) / (2 * (3 / 5 : Rat)) = 135 / 8 := by
  norm_num

theorem weight_ratio_fixture :
    (8 : Rat) / (3 / 5 : Rat) = 40 / 3 := by
  norm_num

theorem local_prefactor_fixture :
    (122099 / 35840 : Rat)^4 * (40 / 3 : Rat)^3 =
      222253407550105971601 / 696074612244480 := by
  norm_num

theorem conditional_power_fixture :
    (1 / 4 : Rat)^4 * (122099 / 35840 : Rat)^4 * (40 / 3 : Rat)^3 =
      222253407550105971601 / 178195100734586880 := by
  norm_num

theorem endpoint_weight_fixture :
    (1 : Rat)^4 <= (40 / 3 : Rat) *
      ((-9 / 2 : Rat) * (1 : Rat)^2 / 2 + (3 / 5 : Rat) * (1 : Rat)^4 / 4 +
        (-9 / 2 : Rat)^2 / (2 * (3 / 5 : Rat))) := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R241
