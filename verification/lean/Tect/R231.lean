import Mathlib

namespace Tect.R231

theorem scale_fixture :
    (2 : Rat)^4 = 16 ∧ (2 : Rat)^3 = 8 ∧ (2 : Rat)^6 = 64 := by
  norm_num

theorem one_sided_fixture :
    (1 : Rat) <= 1 ∧ (1 / 8 : Rat) <= 1 := by
  norm_num

theorem central_context_fixture :
    (2 : Rat)^6 = 64 ∧ (2 : Rat)^12 = 4096 ∧ (2 : Rat)^18 = 262144 := by
  norm_num

theorem ordinary_context_fixture :
    (2 : Rat)^3 = 8 ∧ (2 : Rat)^6 = 64 ∧ (2 : Rat)^9 = 512 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R231
