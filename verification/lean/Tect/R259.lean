import Mathlib

namespace Tect.R259

theorem pell_first : (7 : Rat)^2 - 2 * (5 : Rat)^2 = -1 := by
  norm_num

theorem pell_second : (41 : Rat)^2 - 2 * (29 : Rat)^2 = -1 := by
  norm_num

theorem pell_third : (239 : Rat)^2 - 2 * (169 : Rat)^2 = -1 := by
  norm_num

theorem k_sum_first : (1 / 2 : Rat) + (1 / 2 : Rat) = 1 := by
  norm_num

theorem a_power_first : (5 : Rat)^2 * (1 / 2 : Rat) = 25 / 2 := by
  norm_num

theorem q_squared_first : 2 * (5 / 2 : Rat) = 5 := by
  norm_num

theorem q_squared_second : 2 * (29 / 2 : Rat) = 29 := by
  norm_num

theorem q_squared_third : 2 * (169 / 2 : Rat) = 169 := by
  norm_num

theorem candidate_bound_first : (5 : Rat) > 9 / 4 := by
  norm_num

theorem candidate_bound_second : (29 : Rat) > 9 / 4 := by
  norm_num

theorem candidate_bound_third : (169 : Rat) > 9 / 4 := by
  norm_num

theorem ratio_first : (5 : Rat) / (9 / 4 : Rat) = 20 / 9 := by
  norm_num

theorem ratio_second : (29 : Rat) / (9 / 4 : Rat) = 116 / 9 := by
  norm_num

theorem ratio_third : (169 : Rat) / (9 / 4 : Rat) = 676 / 9 := by
  norm_num

theorem state_moment_fixture : (1 : Rat)^5 = 1 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R259
