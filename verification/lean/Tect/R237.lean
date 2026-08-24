import Mathlib

namespace Tect.R237

theorem graph_constant_fixture :
    (122099 / 35840 : Rat) > 0 := by
  norm_num

theorem product_fixture :
    (122099 / 35840 : Rat)^2 > 0 ∧
      (122099 / 35840 : Rat)^3 > 0 ∧
      (122099 / 35840 : Rat)^4 > 0 := by
  norm_num

theorem volume_monotone_fixture :
    (2 : Nat) <= 3 ∧ (3 : Nat) <= 4 := by
  norm_num

theorem source_radius_fixture :
    (1 / 4 : Rat) > 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R237
