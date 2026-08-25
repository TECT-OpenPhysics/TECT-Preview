import Mathlib

namespace Tect.R327

/- R327 checks only exact rational fixtures for EXP-001157.  It does not
   formalize finite matrix exponentials, Gibbs states, shape changes, operator
   domains, uniform estimates or thermodynamic limits. -/

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem time_horizon_fixture :
    6 * (1 / 18 : Rat) = 1 / 3 := by
  norm_num

theorem case_count_fixture :
    (5 : Rat) = 5 := by
  norm_num

theorem order_count_fixture :
    (2 : Rat) * 2 = 4 := by
  norm_num

theorem source_count_fixture :
    (2 : Rat) = 2 := by
  norm_num

theorem beta_fixture :
    (1 / 2 : Rat) < 1 ∧ (1 : Rat) < 2 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R327
