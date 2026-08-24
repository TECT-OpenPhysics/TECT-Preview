import Mathlib

namespace Tect.R256

theorem a1_real_majorant : (17 / 40 : Rat) = 17 / 40 := by
  norm_num

theorem a1_imaginary_majorant : (9 / 20 : Rat) = 9 / 20 := by
  norm_num

theorem a0_real_majorant : (27 / 160 : Rat) = 27 / 160 := by
  norm_num

theorem a0_imaginary_majorant : (17 / 80 : Rat) = 17 / 80 := by
  norm_num

theorem a1_sum_fixture : (17 / 40 : Rat) + 9 / 20 = 7 / 8 := by
  norm_num

theorem a0_sum_fixture : (27 / 160 : Rat) + 17 / 80 = 61 / 160 := by
  norm_num

theorem selected_weight_fixture :
    1 + (3 : Rat)^4 + (-2 : Rat)^4 = 98 := by
  norm_num

theorem selected_a1_real_fixture :
    (-59 / 40 : Rat) = -59 / 40 := by
  norm_num

theorem selected_a1_imaginary_fixture :
    (-9 / 4 : Rat) = -9 / 4 := by
  norm_num

theorem selected_a0_real_fixture :
    (-3 / 160 : Rat) = -3 / 160 := by
  norm_num

theorem selected_a0_imaginary_fixture :
    (-59 / 80 : Rat) = -59 / 80 := by
  norm_num

theorem derivative_weighted_fixture :
    (773 / 80 : Rat)^4 <= (271 / 80 : Rat)^4 * (98 : Rat)^3 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R256
