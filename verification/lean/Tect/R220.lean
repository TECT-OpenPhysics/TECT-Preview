import Mathlib

namespace Tect.R220

theorem selected_q3_degree : (3 : Nat) = 3 := by
  norm_num

theorem restricted_G : (3 / 5 : Rat) + 3 * (2 / 7 : Rat) = 51 / 35 := by
  norm_num

theorem actual_word_degree_m3 : 4 * (3 : Nat) - 3 = 9 := by
  norm_num

theorem actual_word_leading_coefficient_m3 :
    -3 * (2 / 3 : Rat) * (-(51 / 35 : Rat) / 4) ^ 2 = -2601 / 9800 := by
  norm_num

theorem actual_word_nonzero_m3 :
    (-3 * (2 / 3 : Rat) * (-(51 / 35 : Rat) / 4) ^ 2 : Rat) != 0 := by
  norm_num

end Tect.R220
