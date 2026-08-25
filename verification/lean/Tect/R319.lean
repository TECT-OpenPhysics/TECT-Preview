import Mathlib

namespace Tect.R319

theorem source_rate_fixture : ((1 / 3 : Rat) * (51 / 35 : Rat)) / 4 = 17 / 140 := by
  norm_num

theorem source_margin_fixture : (1 / 5 : Rat) - 17 / 140 = 11 / 140 := by
  norm_num

theorem delta_generator_fixture : ((1 : Rat) / 1) * ((1 : Rat) / 1) = 1 := by
  norm_num

theorem source_norm_fixture (a : Rat) :
    (1 + |a|) / (1 + |a|) = 1 := by
  have h : (1 + |a|) ≠ 0 := by positivity
  exact div_self h

end Tect.R319
