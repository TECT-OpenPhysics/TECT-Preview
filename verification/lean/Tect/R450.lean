import Mathlib

namespace Tect.R450

theorem two_orientation_fourth_split (C T : ℝ) :
    (2 : ℝ) * C * T ^ 4 = C * T ^ 4 + C * T ^ 4 := by
  ring

theorem shell_tail_r1 :
    (3 : ℝ) * (4 * (1 : ℝ) ^ 2 + 8 * 1 + 14) * 2 ^ (1 - 1) = 78 := by
  norm_num

theorem shell_tail_r2 :
    (3 : ℝ) * (4 * (2 : ℝ) ^ 2 + 8 * 2 + 14) * (2 : ℝ)⁻¹ = 69 := by
  norm_num

theorem coefficient_weight_fixture (C : ℝ) (hC : 0 ≤ C) :
    (1 / 2 : ℝ) ^ 4 * C ≤ (1 : ℝ) ^ 4 * C := by
  norm_num [div_pow]
  nlinarith

end Tect.R450
