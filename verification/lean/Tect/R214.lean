import Mathlib

namespace Tect.R214

theorem q3_coefficient_fixture : (3 / 5 : Rat) + 3 * (2 / 7 : Rat) = 51 / 35 := by
  norm_num

theorem leading_coefficient_fixture : ((2 / 3 : Rat) * (51 / 35 : Rat)) / 2 = 17 / 35 := by
  norm_num

theorem source_weight_fixture : (10 : Rat) ^ 5 <= (1 + 10 : Rat) ^ 5 := by
  norm_num

theorem source_weight_ratio_fixture : ((17 / 35 : Rat) * (10 : Rat) ^ 5) / (11 : Rat) ^ 5 < 17 / 35 := by
  norm_num

theorem two_orientation_step : 1 + (1 + 2) * (1 / 5 : Rat) = 8 / 5 := by
  norm_num

theorem two_orientation_iterated : (8 / 5 : Rat) ^ 3 = 512 / 125 := by
  norm_num

end Tect.R214
