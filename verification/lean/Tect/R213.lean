import Mathlib

namespace Tect.R213

theorem shifted_response_identity (a q r g lambda c : ℚ) :
    2 * ((g + 3 * lambda) / 4 * (q ^ 4 - (q - a) ^ 4) - c * a * r) * (-c * a) =
      c * (g + 3 * lambda) / 2 * a ^ 5
        - 2 * c * (g + 3 * lambda) * q * a ^ 4
        + 3 * c * (g + 3 * lambda) * q ^ 2 * a ^ 3
        + (-2 * c * (g + 3 * lambda) * q ^ 3 + 2 * c ^ 2 * r) * a ^ 2 := by
  ring

theorem q3_coefficient_fixture :
    (3 / 5 : ℚ) + 3 * (2 / 7 : ℚ) = 51 / 35 := by
  norm_num

theorem leading_coefficient_fixture :
    (2 / 3 : ℚ) * ((3 / 5 : ℚ) + 3 * (2 / 7 : ℚ)) / 2 = 17 / 35 := by
  norm_num

theorem source_degree_gap : (5 : ℕ) - 1 = 4 := by
  norm_num

theorem fixture_response_at_zero :
    (17 / 35 : ℚ) * (10 : ℚ) ^ 5 = 340000 / 7 := by
  norm_num

theorem fixture_ratio_is_positive : (17 / 35 : ℚ) * (10 : ℚ) ^ 4 > 0 := by
  norm_num

end Tect.R213
