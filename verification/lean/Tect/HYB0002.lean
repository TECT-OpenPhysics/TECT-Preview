import Mathlib

namespace Tect.HYB0002

theorem quadratic_core_lower_bound :
    (4740336473 : ℚ) / 10000000000 - ((-9252754126 : ℚ) / 10000000000) ^ 2 /
        (4 * (1 : ℚ)) = 26000000000947494031 / 100000000000000000000 := by
  norm_num

theorem quadratic_core_lower_bound_positive :
    0 < (4740336473 : ℚ) / 10000000000 - ((-9252754126 : ℚ) / 10000000000) ^ 2 /
        (4 * (1 : ℚ)) := by
  norm_num

theorem potential_lower_bound_fixture :
    ((-43 : ℚ) / 100) ^ 3 / (12 * ((81 : ℚ) / 50) ^ 2) < 0 := by
  norm_num

theorem classii_determinant_positive :
    (18000000000 : ℚ) / 4000000000001 * (9375000000 : ℚ) / 4000000000001 -
        ((7500000000 : ℚ) / 4000000000001) ^ 2 > 0 := by
  norm_num

theorem gibbs_residual_zero_fixture :
    (((11 : ℚ) / 5) - (7 : ℚ) / 2 * ((2 : ℚ) / 7) ^ 2) +
        (1 / ((7 : ℚ) / 2)) *
          (-((7 : ℚ) / 2) * ((11 : ℚ) / 5) + ((7 : ℚ) / 2) ^ 2 * ((2 : ℚ) / 7) ^ 2) = 0 := by
  norm_num

end Tect.HYB0002
