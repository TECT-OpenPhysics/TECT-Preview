import Mathlib

namespace Tect.R261

theorem gibbs_ratio_first : (1 : Rat) / 4^6 = 1 / 4^6 := by norm_num
theorem gibbs_ratio_second : (1 : Rat) / 16^6 = 1 / 16^6 := by norm_num
theorem gibbs_ratio_third : (1 : Rat) / 64^6 = 1 / 64^6 := by norm_num

theorem reference_moment_first : (4 : Rat)^5 * (4 + 1) / (4^6 + 1) < 3 / 2 := by norm_num
theorem reference_moment_second : (16 : Rat)^5 * (16 + 1) / (16^6 + 1) < 3 / 2 := by norm_num
theorem reference_moment_third : (64 : Rat)^5 * (64 + 1) / (64^6 + 1) < 3 / 2 := by norm_num

theorem dual_moment_first : ((4 : Rat)^11 + 1) / (4^6 + 1) > 4^4 := by norm_num
theorem dual_moment_second : ((16 : Rat)^11 + 1) / (16^6 + 1) > 16^4 := by norm_num
theorem dual_moment_third : ((64 : Rat)^11 + 1) / (64^6 + 1) > 64^4 := by norm_num

theorem tail_first : (4 : Rat)^6 / (4^6 + 1) > 1 / 2 := by norm_num
theorem tail_second : (16 : Rat)^6 / (16^6 + 1) > 1 / 2 := by norm_num
theorem tail_third : (64 : Rat)^6 / (64^6 + 1) > 1 / 2 := by norm_num

theorem reference_ceiling_first : (3 / 2 : Rat) - 4^5 * (4 + 1) / (4^6 + 1) > 0 := by norm_num
theorem reference_ceiling_second : (3 / 2 : Rat) - 16^5 * (16 + 1) / (16^6 + 1) > 0 := by norm_num
theorem reference_ceiling_third : (3 / 2 : Rat) - 64^5 * (64 + 1) / (64^6 + 1) > 0 := by norm_num

theorem tail_floor_first : (4 : Rat)^6 / (4^6 + 1) - 1 / 2 > 0 := by norm_num
theorem tail_floor_second : (16 : Rat)^6 / (16^6 + 1) - 1 / 2 > 0 := by norm_num
theorem tail_floor_third : (64 : Rat)^6 / (64^6 + 1) - 1 / 2 > 0 := by norm_num

theorem relative_bound_fixture : (1 : Rat) <= 1 ∧ (1 / 64 : Rat) <= 1 := by norm_num
theorem scope_fixture : True ∧ ¬False := by norm_num

end Tect.R261
