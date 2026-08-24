import Mathlib

namespace Tect.R254

theorem remainder_factor_fixture :
    (1 / 100 : Rat)^4 / 4 = 1 / 400000000 := by
  norm_num

theorem remainder_upper_fixture :
    ((1 / 100 : Rat)^4 / 4) * 293764 = 73441 / 100000000 := by
  norm_num

theorem remainder_upper_unreduced_fixture :
    ((1 / 100 : Rat)^4 / 4) * 293764 = 293764 / 400000000 := by
  norm_num

theorem remainder_upper_small :
    (73441 / 100000000 : Rat) < 1 := by
  norm_num

theorem time_positive_fixture : (1 / 100 : Rat) > 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R254
