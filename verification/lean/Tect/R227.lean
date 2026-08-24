import Mathlib

namespace Tect.R227

theorem energy_ratio_fixture :
    (2 : Rat) / (1 / 128 : Rat) = 256 := by
  norm_num

theorem root_scale_fixture : (4 : Rat)^4 = 256 := by
  norm_num

theorem neighbour_weight_root_fixture : (2 : Rat)^4 = 16 := by
  norm_num

theorem powered_scalar_fixture :
    (1 : Rat)^2 * 16 <= (1 + 16)^3 := by
  norm_num

theorem edge_weighted_rate_fixture :
    (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 64 * 2 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 64 * 4 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * 2 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 7 : Rat) * 64 * 8 * (1 / 4 : Rat)
      + (1 / 7 : Rat) * 16 * 4 * (1 / 4 : Rat)^2
      + (1 / 7 : Rat) * 4 * 2 * (1 / 4 : Rat)^3
      + (1 / 14 : Rat) * (1 / 4 : Rat)^4 = 203393 / 3584 := by
  norm_num

theorem edge_relabelled_rate_fixture :
    (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 64 * 2 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 64 * 4 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * 2 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 7 : Rat) * 64 * 8 * (1 / 4 : Rat)
      + (1 / 7 : Rat) * 16 * 4 * (1 / 4 : Rat)^2
      + (1 / 7 : Rat) * 4 * 2 * (1 / 4 : Rat)^3
      + (1 / 14 : Rat) * (1 / 4 : Rat)^4 = 203393 / 3584 := by
  norm_num

theorem bond_weighted_rate_fixture :
    (2 / 3 : Rat) * 4 * (1 / 4 : Rat)
      + (2 / 3 : Rat) * 4 * 2 * (1 / 4 : Rat)
      + (1 / 3 : Rat) * (1 / 4 : Rat)^2 = 97 / 48 := by
  norm_num

theorem onsite_rate_fixture :
    (3 / 5 : Rat) * (
      (64 : Rat) * (1 / 4 : Rat)
      + (3 / 2 : Rat) * 16 * (1 / 4 : Rat)^2
      + 4 * (1 / 4 : Rat)^3
      + (1 / 4 : Rat)^4 / 4) = 10791 / 1024 := by
  norm_num

theorem local_rate_fixture :
    (10791 / 1024 : Rat) + 3 * (203393 / 3584 : Rat) + 6 * (97 / 48 : Rat) = 1382807 / 7168 := by
  norm_num

theorem weighted_local_rate_fixture :
    (1 / 8 : Rat) * (1382807 / 7168 : Rat) = 1382807 / 57344 := by
  norm_num

theorem scope_fixture : (True ∧ ¬False) := by
  norm_num

end Tect.R227
