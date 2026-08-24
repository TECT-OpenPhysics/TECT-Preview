import Mathlib

namespace Tect.R242

theorem cube_constant_fixture :
    (3 : Rat) ^ ((3 : Nat) - 1) = 9 := by
  norm_num

theorem endpoint_cube_fixture :
    (5 + 1 + 1 : Rat)^3 <= 9 * ((5 : Rat)^3 + 1^3 + 1^3) := by
  norm_num

theorem fifth_dominates_third_fixture :
    (1 : Rat)^3 <= (1 : Rat)^5 ∧
      (2 : Rat)^3 <= (2 : Rat)^5 ∧
      (5 : Rat)^3 <= (5 : Rat)^5 := by
  norm_num

theorem bridge_fixture :
    9 * ((1 + 2 * (2 : Rat))^3 + 2 * (3 : Rat)) = 1179 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R242
