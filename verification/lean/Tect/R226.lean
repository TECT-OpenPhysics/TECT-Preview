import Mathlib

namespace Tect.R226

theorem edge_source_rate_fixture :
    (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (1 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (1 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 14 : Rat) * (1 / 4 : Rat)^4 = 69217 / 3584 := by
  norm_num

theorem edge_reverse_rate_fixture :
    (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (3 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (2 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 7 : Rat) * 64 * (1 / 4 : Rat)
      + (1 / 7 : Rat) * 16 * (1 / 4 : Rat)^2
      + (1 / 7 : Rat) * 4 * (1 / 4 : Rat)^3
      + (1 / 14 : Rat) * (1 / 4 : Rat)^4 = 69217 / 3584 := by
  norm_num

theorem bond_source_rate_fixture :
    (2 / 3 : Rat) * 4 * (1 / 4 : Rat)
      + (2 / 3 : Rat) * 4 * (1 / 4 : Rat)
      + (1 / 3 : Rat) * (1 / 4 : Rat)^2 = 65 / 48 := by
  norm_num

theorem onsite_source_rate_fixture :
    (3 / 5 : Rat) * (
      (64 : Rat) * (1 / 4 : Rat)
      + (3 / 2 : Rat) * 16 * (1 / 4 : Rat)^2
      + 4 * (1 / 4 : Rat)^3
      + (1 / 4 : Rat)^4 / 4) = 10791 / 1024 := by
  norm_num

theorem local_rate_fixture :
    (10791 / 1024 : Rat) + 3 * (69217 / 3584 : Rat) + 6 * (65 / 48 : Rat) = 549079 / 7168 := by
  norm_num

theorem weighted_local_rate_fixture :
    (1 / 8 : Rat) * (549079 / 7168 : Rat) = 549079 / 57344 := by
  norm_num

theorem mixed_transport_fixture :
    (2 : Rat) > (1 : Rat) * 1 := by
  norm_num

theorem scope_fixture : (True ∧ ¬False) := by
  norm_num

end Tect.R226
