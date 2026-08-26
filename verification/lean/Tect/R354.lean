import Mathlib

namespace Tect.R354

/- R354 formalizes only the exact parameter-grid, time-step, order/context and
   scope fixtures for EXP-001195.  It does not formalize finite matrix
   exponentials, Gibbs traces, commutator norms, recurrence estimates,
   common-core domains or thermodynamic limits. -/

theorem parameter_grid_fixture :
    (3 : Rat) * 2 * 2 * 2 * 2 * 3 = 144 := by
  norm_num

theorem beta_count_fixture : (3 : Rat) = 3 := by
  norm_num

theorem support_count_fixture : (2 : Rat) = 2 := by
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

end Tect.R354
