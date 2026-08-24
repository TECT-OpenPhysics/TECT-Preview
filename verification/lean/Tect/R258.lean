import Mathlib

namespace Tect.R258

theorem root_m5_quarter_fixture : (79 / 60 : Rat)^4 >= 3 := by
  norm_num

theorem root_m5_quarter_minimal : (78 / 60 : Rat)^4 < 3 := by
  norm_num

theorem root_m5_three_twentieths_fixture : (71 / 60 : Rat)^20 >= 3^3 := by
  norm_num

theorem root_m5_three_twentieths_minimal : (70 / 60 : Rat)^20 < 3^3 := by
  norm_num

theorem root_m5_one_tenth_fixture : (67 / 60 : Rat)^10 >= 3 := by
  norm_num

theorem root_m5_one_tenth_minimal : (66 / 60 : Rat)^10 < 3 := by
  norm_num

theorem x_ceiling_fixture :
    (79 / 60 : Rat) + (1 / 4 : Rat) * (71 / 60 : Rat) = 129 / 80 := by
  norm_num

theorem p_sigma_ceiling_fixture :
    2 * (129 / 80 : Rat) + (9 / 2 : Rat) * (67 / 60 : Rat) = 33 / 4 := by
  norm_num

theorem q_sigma_ceiling_fixture :
    (3 / 2 : Rat) * (71 / 60 : Rat) = 71 / 40 := by
  norm_num

theorem two_orientation_fixture :
    2 * (33 / 4 : Rat) = 33 / 2 ∧ 2 * (71 / 40 : Rat) = 71 / 20 := by
  norm_num

theorem sqrt_two_fixture : (3 / 2 : Rat)^2 >= 2 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R258
