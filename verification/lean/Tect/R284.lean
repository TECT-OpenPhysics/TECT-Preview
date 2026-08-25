import Mathlib

namespace Tect.R284

/- R284 is the rational composition only.  The R-167 fifth-moment inputs are
   cited premises in the surrounding manifest. -/

theorem m20_constant_fixture :
    2 * (1 / 2 : Rat) ^ 2 * (3 / 2 : Rat) * 2 ^ 5 * 5 = 120 := by
  norm_num

theorem uniform_tail_fixture :
    (2916 : Rat) * (1 / 3 : Rat) ^ 2 * 120 = 38880 ∧
      (38880 : Rat) / 4 = 9720 := by
  norm_num

theorem scope_fixture :
    (0 : Rat) < 120 ∧ (0 : Rat) < 38880 ∧ (38880 : Rat) / 25 < 38880 := by
  norm_num

end Tect.R284
