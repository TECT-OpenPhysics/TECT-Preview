import Mathlib

namespace Tect.R222

theorem onsite_bound_fixture :
    (3 / 5 : Rat) * ((3 / 2 : Rat)^3 * (1 / 2 : Rat)
      + (3 / 2 : Rat) * (3 / 2 : Rat)^2 * (1 / 2 : Rat)^2
      + (3 / 2 : Rat) * (1 / 2 : Rat)^3
      + (1 / 2 : Rat)^4 / 4) = 105 / 64 := by
  norm_num

theorem edge_bound_fixture :
    (2 / 7 : Rat) * (4 * (3 / 2 : Rat)^3 * (1 / 2 : Rat)
      + (7 / 2 : Rat) * (3 / 2 : Rat)^2 * (1 / 2 : Rat)^2
      + (3 / 2 : Rat) * (3 / 2 : Rat) * (1 / 2 : Rat)^3
      + (1 / 2 : Rat)^4 / 4) = 577 / 224 := by
  norm_num

theorem bond_bound_fixture :
    (2 / 3 : Rat) * (2 * (3 / 2 : Rat) * (1 / 2 : Rat)
      + (1 / 2 : Rat)^2 / 2) = 13 / 12 := by
  norm_num

theorem field_window_rate_fixture :
    (105 / 64 : Rat) + 3 * (577 / 224 : Rat) + 6 * (13 / 12 : Rat) = 7109 / 448 := by
  norm_num

theorem weighted_rate_fixture :
    (1 / 3 : Rat) * (7109 / 448 : Rat) = 7109 / 1344 := by
  norm_num

theorem local_choice_fixture : (1 + 3 + 6 : Nat) = 10 := by
  norm_num

end Tect.R222
