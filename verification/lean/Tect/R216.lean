import Mathlib

namespace Tect.R216

theorem q3_rate_fixture : ((1 / 3 : Rat) * (51 / 35 : Rat)) / 4 = 17 / 140 := by
  norm_num

theorem sigma_margin_fixture : (1 / 5 : Rat) - 17 / 140 = 11 / 140 := by
  norm_num

theorem sigma_margin_positive : (0 : Rat) < 11 / 140 := by
  norm_num

theorem source_prefactor_fixture : (2 / 3 : Rat) * (1 / 3 : Rat) = 2 / 9 := by
  norm_num

theorem m3_summand_fixture :
    (3 : Rat) * (2 / 3 : Rat) * (51 / 140 : Rat) ^ 2 * (1 / 3 : Rat) ^ 3 / 6 = 2601 / 1587600 := by
  norm_num

end Tect.R216
