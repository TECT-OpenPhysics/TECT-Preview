import Mathlib

namespace Tect.R225

theorem energy_ratio_fixture :
    (2 : Rat) / (1 / 128 : Rat) = 256 := by
  norm_num

theorem root_scale_fixture : (4 : Rat)^4 = 256 := by
  norm_num

theorem moment_ladder_fixture :
    ((4 : Rat)^0, (4 : Rat)^1, (4 : Rat)^2, (4 : Rat)^3)
      = (1, 4, 16, 64) := by
  norm_num

theorem onsite_source_rate_fixture :
    (3 / 5 : Rat) * (
      (64 : Rat) * (1 / 4 : Rat)
      + (3 / 2 : Rat) * 16 * (1 / 4 : Rat)^2
      + 4 * (1 / 4 : Rat)^3
      + (1 / 4 : Rat)^4 / 4) = 10791 / 1024 := by
  norm_num

theorem reverse_source_rate_fixture :
    (3 / 5 : Rat) * (
      (64 : Rat) * (1 / 4 : Rat)
      + (3 / 2 : Rat) * 16 * (1 / 4 : Rat)^2
      + 4 * (1 / 4 : Rat)^3
      + (1 / 4 : Rat)^4 / 4) = 10791 / 1024 := by
  norm_num

theorem weighted_rate_fixture :
    (1 / 8 : Rat) * (10791 / 1024 : Rat) = 10791 / 8192 := by
  norm_num

theorem scope_fixture : (True ∧ ¬False) := by
  norm_num

end Tect.R225
