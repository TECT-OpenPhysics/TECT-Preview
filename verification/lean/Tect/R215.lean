import Mathlib

namespace Tect.R215

theorem q3_coefficient_fixture : (3 / 5 : Rat) + 3 * (2 / 7 : Rat) = 51 / 35 := by
  norm_num

theorem repeated_word_degree_m2 : 4 * 2 - 3 = (5 : Nat) := by
  norm_num

theorem repeated_word_degree_m3 : 4 * 3 - 3 = (9 : Nat) := by
  norm_num

theorem repeated_word_coefficient_m3 :
    -(3 : Rat) * (2 / 3 : Rat) * (-(51 / 35 : Rat) / 4) ^ 2 = -(2601 / 9800 : Rat) := by
  norm_num

theorem fixed_weight_gap_m3 : (9 : Nat) - 5 = 4 := by
  norm_num

end Tect.R215
