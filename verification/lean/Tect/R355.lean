import Mathlib

namespace Tect.R355

/- R355 checks only the exact source-amplitude grid, time-step,
   order/context and scope fixtures for EXP-001196.  It does not formalize
   matrix exponentials, Gibbs traces, commutator norms, recurrence estimates,
   common-core domains or thermodynamic limits. -/

theorem amplitude_grid_fixture :
    (3 : Rat) * 5 * 1 * 2 * 2 * 2 = 120 := by
  norm_num

theorem amplitude_count_fixture : (5 : Rat) = 5 := by
  norm_num

theorem time_horizon_fixture :
    2 * (1 / 18 : Rat) = 1 / 9 := by
  norm_num

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem order_context_fixture :
    (2 : Rat) * 2 = 4 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R355
