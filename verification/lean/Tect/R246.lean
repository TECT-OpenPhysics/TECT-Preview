import Mathlib

namespace Tect.R246

theorem polarization_fixture :
    (1 - (3 / 5 : Rat)) = 2 / 5 := by
  norm_num

theorem rotation_squares_fixture :
    (3 / 5 : Rat)^2 = 9 / 25 ∧ (4 / 5 : Rat)^2 = 16 / 25 := by
  norm_num

theorem rotation_unitarity_fixture :
    (3 / 5 : Rat)^2 + (4 / 5 : Rat)^2 = 1 := by
  norm_num

theorem evolved_diagonal_fixture :
    (4 / 5 : Rat)^2 = 16 / 25 ∧ (3 / 5 : Rat)^2 = 9 / 25 := by
  norm_num

theorem evolved_norm_fixture :
    2 * ((4 / 5 : Rat) * (16 / 25 : Rat) + (1 / 5 : Rat) * (9 / 25 : Rat)) = 146 / 125 := by
  norm_num

theorem growth_fixture :
    (146 / 125 : Rat) - 2 / 5 = 96 / 125 ∧ (146 / 125 : Rat) > 2 / 5 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R246
