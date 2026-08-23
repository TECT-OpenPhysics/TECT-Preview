import Mathlib

namespace Tect.R218

theorem three_dimensional_degree_bound : (2 * 3 : Nat) = 6 := by
  norm_num

theorem two_orientation_branch_factor :
    (1 + ((1 / 5 : Rat) + 2 * (1 / 10 : Rat)) * (1 / 7 : Rat)) = 37 / 35 := by
  norm_num

theorem iterated_branch_factor :
    ((37 / 35 : Rat) ^ 5) =
      (1 + ((1 / 5 : Rat) + 2 * (1 / 10 : Rat)) * (1 / 7 : Rat)) ^ 5 := by
  norm_num

theorem five_step_walk_oracle : (0 : Rat) <= (6 : Rat) ^ 5 := by
  norm_num

end Tect.R218
