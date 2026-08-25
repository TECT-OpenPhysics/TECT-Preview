import Mathlib

namespace Tect.R318

theorem q3_source_rate_fixture : ((1 / 3 : Rat) * (51 / 35 : Rat)) / 4 = 17 / 140 := by
  norm_num

theorem q3_source_sigma_margin : (1 / 5 : Rat) - 17 / 140 = 11 / 140 := by
  norm_num

theorem q3_source_prefactor : (2 / 3 : Rat) * (1 / 3 : Rat) = 2 / 9 := by
  norm_num

theorem source_weight_norm_fixture (a : Rat) (_sigma : Rat) :
    ((1 + |a|) * (1 + |a|)) * (1 / ((1 + |a|) * (1 + |a|))) = 1 := by
  have h : (1 + |a|) * (1 + |a|) ≠ 0 := by positivity
  field_simp

end Tect.R318
