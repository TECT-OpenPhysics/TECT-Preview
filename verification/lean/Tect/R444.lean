import Mathlib

namespace Tect.R444

theorem shell_count_n1 : 4 * (1 : Rat)^2 + 2 = 6 := by norm_num

theorem shell_count_n2 : 4 * (2 : Rat)^2 + 2 = 18 := by norm_num

theorem shell_count_n3 : 4 * (3 : Rat)^2 + 2 = 38 := by norm_num

theorem tail_formula_r1 :
    3 * (4 * (1 : Rat)^2 + 8 * 1 + 14) * (2 : Rat)^(1 - 1) = 78 := by
  norm_num

theorem tail_formula_r2 :
    3 * (4 * (2 : Rat)^2 + 8 * 2 + 14) / 2 = 69 := by
  norm_num

theorem tail_formula_r4 :
    3 * (4 * (4 : Rat)^2 + 8 * 4 + 14) / 8 = 165 / 4 := by
  norm_num

end Tect.R444
