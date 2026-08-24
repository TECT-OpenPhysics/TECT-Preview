import Mathlib

namespace Tect.R229

theorem scale_fixture : (2 : Rat)^4 = 16 := by
  norm_num

theorem one_factor_fixture :
    (1 : Rat) <= 1 ∧ (1 / 8 : Rat) <= 1 := by
  norm_num

theorem repeated_product_fixture :
    (2 : Rat)^3 = 8 ∧ (8 : Rat) > 1 := by
  norm_num

theorem family_fixture :
    (2 : Rat)^3 = 8 ∧ (2 : Rat)^6 = 64 ∧ (2 : Rat)^9 = 512 := by
  norm_num

theorem scope_fixture : (True ∧ ¬False) := by
  norm_num

end Tect.R229
