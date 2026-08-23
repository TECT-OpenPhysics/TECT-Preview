import Mathlib

namespace Tect.R217

theorem six_neighbour_count : (2 * 3 : Nat) = 6 := by
  norm_num

theorem one_step_type_factor : (1 + (1 / 5 : Rat) * (1 / 6 : Rat)) = 31 / 30 := by
  norm_num

theorem six_step_type_formula :
    (1 / 5 : Rat) * ((31 / 30 : Rat) ^ 4) ^ 6 =
      (1 / 5 : Rat) * (31 / 30 : Rat) ^ (4 * 6) := by
  norm_num [pow_mul]

theorem six_step_type_bound :
    (1 / 5 : Rat) * (31 / 30 : Rat) ^ (4 * 6) < 1 / 2 := by
  norm_num

theorem scalar_entire_weight_transport :
    (1 / 5 : Rat) * (31 / 30 : Rat) ^ (4 * 6) =
      (1 / 5 : Rat) * (1 + (1 / 5 : Rat) * (1 / 6 : Rat)) ^ (4 * 6) := by
  norm_num

end Tect.R217
