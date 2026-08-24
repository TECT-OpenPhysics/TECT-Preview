import Mathlib

namespace Tect.R257

theorem a1_sum_fixture : (7 / 8 : Rat) = 7 / 8 := by
  norm_num

theorem a0_sum_fixture : (61 / 160 : Rat) = 61 / 160 := by
  norm_num

theorem m_plus_fixture :
    (7 / 8 : Rat) * 5 + (61 / 160 : Rat) * 3 = 883 / 160 := by
  norm_num

theorem m_minus_fixture :
    (7 / 8 : Rat) * 7 + (61 / 160 : Rat) * 4 = 153 / 20 := by
  norm_num

theorem m_two_orientation_fixture :
    (883 / 160 : Rat) + 153 / 20 = 2107 / 160 := by
  norm_num

theorem m_delta_plus_fixture :
    (7 / 8 : Rat) * 2 + (61 / 160 : Rat) * 1 = 341 / 160 := by
  norm_num

theorem m_delta_minus_fixture :
    (7 / 8 : Rat) * 3 + (61 / 160 : Rat) * 2 = 271 / 80 := by
  norm_num

theorem m_delta_two_orientation_fixture :
    (341 / 160 : Rat) + 271 / 80 = 883 / 160 := by
  norm_num

theorem third_scale_fixture :
    ((1 / 100 : Rat)^3) / 6 = 1 / 6000000 := by
  norm_num

theorem third_bound_fixture :
    (1 / 6000000 : Rat) * (2107 / 160 : Rat) = 2107 / 960000000 := by
  norm_num

theorem third_modular_bound_fixture :
    (1 / 6000000 : Rat) * (883 / 160 : Rat) = 883 / 960000000 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R257
