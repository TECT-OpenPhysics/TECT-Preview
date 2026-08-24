import Mathlib

namespace Tect.R228

theorem edge_rate_fixture :
    (203393 / 3584 : Rat) = 203393 / 3584 := by
  norm_num

theorem bond_rate_fixture :
    (97 / 48 : Rat) = 97 / 48 := by
  norm_num

theorem local_rate_fixture :
    (10791 / 1024 : Rat) + 3 * (203393 / 3584 : Rat) + 6 * (97 / 48 : Rat) = 1382807 / 7168 := by
  norm_num

theorem weighted_exponent_fixture :
    (2 : Rat) * (1382807 / 7168 : Rat) * 6 * 2 * (1 / 1000 : Rat) = 4148421 / 896000 := by
  norm_num

theorem distance_factor_fixture :
    (2 : Rat)^10 = 1024 := by
  norm_num

theorem finite_partial_fixture :
    (1 : Rat) + (4148421 / 896000 : Rat) + (4148421 / 896000 : Rat)^2 / 2 > 0 := by
  norm_num

theorem scope_fixture : (True ∧ ¬False) := by
  norm_num

end Tect.R228
