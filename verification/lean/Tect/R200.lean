import Mathlib

namespace Tect.R200

theorem stationary_current_zero (m beta x : ℚ) (hb : beta ≠ 0) :
    m * ((x) + beta⁻¹ * (-beta * x)) = 0 := by
  field_simp [hb]
  ring

theorem mobility_a_rates :
    (-(1 : ℚ) * 1, -(1 : ℚ) * 1) = (-1, -1) := by norm_num

theorem mobility_b_rates :
    (-(2 : ℚ) * 1, -(3 : ℚ) * 1) = (-2, -3) := by norm_num

theorem distinct_first_rate : (1 : ℚ) ≠ 2 := by norm_num

theorem distinct_second_rate : (1 : ℚ) ≠ 3 := by norm_num

end Tect.R200
