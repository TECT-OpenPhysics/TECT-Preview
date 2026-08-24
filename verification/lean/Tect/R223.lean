import Mathlib

namespace Tect.R223

theorem onsite_norm_fixture :
    (3 / 5 : Rat) * ((1 / 2 : Rat)^3 * (1 / 3 : Rat)
      + (3 / 2 : Rat) * (1 / 2 : Rat)^2 * (1 / 3 : Rat)^2
      + (1 / 2 : Rat) * (1 / 3 : Rat)^3
      + (1 / 3 : Rat)^4 / 4) = 17 / 270 := by
  norm_num

theorem edge_norm_fixture :
    (2 / 7 : Rat) * (4 * (1 / 2 : Rat)^3 * (1 / 3 : Rat)
      + (7 / 2 : Rat) * (1 / 2 : Rat)^2 * (1 / 3 : Rat)^2
      + (3 / 2 : Rat) * (1 / 2 : Rat) * (1 / 3 : Rat)^3
      + (1 / 3 : Rat)^4 / 4) = 191 / 2268 := by
  norm_num

theorem bond_norm_fixture :
    (2 / 3 : Rat) * (2 * (1 / 2 : Rat) * (1 / 3 : Rat)
      + (1 / 3 : Rat)^2 / 2) = 7 / 27 := by
  norm_num

theorem bientire_rate_fixture :
    (17 / 270 : Rat) + 3 * (191 / 2268 : Rat) + 6 * (7 / 27 : Rat) = 7073 / 3780 := by
  norm_num

theorem weighted_rate_fixture :
    (1 / 5 : Rat) * (7073 / 3780 : Rat) = 7073 / 18900 := by
  norm_num

theorem local_choice_fixture : (1 + 3 + 6 : Nat) = 10 := by
  norm_num

end Tect.R223
