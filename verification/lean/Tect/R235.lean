import Mathlib

namespace Tect.R235

theorem coefficient_majorant_fixture :
    |(51 / 140 : Rat)| + |(153 / 1120 : Rat)| +
      |(2291 / 2240 : Rat)| + |(4531 / 35840 : Rat)| =
      59139 / 35840 := by
  norm_num

theorem majorant_positive_fixture :
    (59139 / 35840 : Rat) > 0 := by
  norm_num

theorem energy_exponent_fixture :
    (3 / 4 : Rat) < 1 := by
  norm_num

theorem coefficient_degree_fixture :
    (0 : Nat) <= 3 ∧ (1 : Nat) <= 3 ∧ (2 : Nat) <= 3 ∧ (3 : Nat) <= 3 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R235
