import Mathlib

namespace Tect.R212

theorem poisson_rate_fixture : (1 : Real) * 6 * (1 / 3) = 2 := by
  norm_num

theorem weighted_rate_fixture : ((1 : Real) * 6 * (1 / 3)) * 2 = 4 := by
  norm_num

theorem distance_weight_fixture : (2 : Real) ^ 10 = 1024 := by
  norm_num

theorem finite_distance_fixture : (0 : Real) < 10 := by
  norm_num

theorem factorial_path_term_nonnegative (n : Nat) :
    0 <= ((2 : Real) ^ n) / (Nat.factorial n) := by
  positivity

end Tect.R212
