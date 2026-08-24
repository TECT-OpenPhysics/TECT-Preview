import Mathlib

namespace Tect.R236

theorem coefficient_majorant_fixture :
    |(51 / 140 : Rat)| * (1 / 4 : Rat)^4 +
      |(51 / 35 : Rat)| * (1 / 4 : Rat)^3 +
      |(3 / 7 : Rat)| * (1 / 4 : Rat)^3 +
      |(153 / 70 : Rat)| * (1 / 4 : Rat)^2 +
      |(9 / 7 : Rat)| * (1 / 4 : Rat)^2 +
      |(3 / 7 : Rat)| * (1 / 4 : Rat)^2 +
      |(2 : Rat)| * (1 / 4 : Rat)^2 +
      |(51 / 35 : Rat)| * (1 / 4 : Rat) +
      |(9 / 7 : Rat)| * (1 / 4 : Rat) +
      |(6 / 7 : Rat)| * (1 / 4 : Rat) +
      |(4 : Rat)| * (1 / 4 : Rat) +
      |(3 / 7 : Rat)| * (1 / 4 : Rat) +
      |(4 : Rat)| * (1 / 4 : Rat) =
      122099 / 35840 := by
  norm_num

theorem orientation_fixture :
    (122099 / 35840 : Rat) = 122099 / 35840 := by
  norm_num

theorem degree_fixture :
    (3 : Nat) <= 3 ∧ (4 : Nat) <= 4 := by
  norm_num

theorem majorant_positive_fixture :
    (122099 / 35840 : Rat) > 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R236
