import Mathlib

namespace Tect.R221

theorem source_only_onsite : (3 / 5 : Rat) / 4 = 3 / 20 := by
  norm_num

theorem source_only_edge :
    (2 / 7 : Rat) * (1 / 4 + 1 / 2 + 1 / 2 + 1 / 2 + 1 / 4) = 4 / 7 := by
  norm_num

theorem source_only_bond :
    (2 / 3 : Rat) * (1 / 2 + 1 + 1 / 2) = 4 / 3 := by
  norm_num

theorem local_rate_fixture :
    ((3 / 20 : Rat) + 3 * (4 / 7 : Rat)) * (1 / 2 : Rat) ^ 4
      + 6 * (4 / 3 : Rat) * (1 / 2 : Rat) ^ 2 = 4741 / 2240 := by
  norm_num

theorem weighted_rate_fixture :
    (1 / 3 : Rat) * (4741 / 2240 : Rat) = 4741 / 6720 := by
  norm_num

theorem local_choice_fixture : (1 : Nat) + 3 + 6 = 10 := by
  norm_num

end Tect.R221
