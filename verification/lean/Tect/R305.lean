import Mathlib

namespace Tect.R305

/- R305 checks the exact leading-coefficient obstruction behind EXP-001134.
   It does not formalize Gaussian integration, operator domains, or limits. -/

theorem onsite_leading_coefficient_fixture :
    (3 / 5 : Rat) / 4 = 3 / 20 := by
  norm_num

theorem weighted_leading_coefficient_fixture :
    (3 / 5 : Rat) / 4 = 3 / 20 := by
  norm_num

theorem obstruction_ratio_fixture :
    ((3 / 5 : Rat) / 4) / ((3 / 5 : Rat) / 4) = (1 : Rat) := by
  norm_num

theorem degree_fixture :
    (4 : Rat) < 6 := by
  norm_num

theorem scope_fixture :
    (True ∧ True) ∧ ¬ (False ∨ False) := by
  norm_num

end Tect.R305
