import Mathlib

namespace Tect.R325

/- R325 checks only the exact rational fixtures used by EXP-001155.  It does
   not formalize the finite matrix exponentials, Gibbs traces, commutator
   seminorm, actual recurrence, unbounded domains or thermodynamic limits. -/

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem time_horizon_fixture :
    6 * (1 / 18 : Rat) = 1 / 3 := by
  norm_num

theorem source_support_fixture :
    (2 : Rat) = 2 := by
  norm_num

theorem context_count_fixture :
    (2 : Rat) * 2 = 4 := by
  norm_num

theorem recurrence_shape_fixture :
    (1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat)) - 1 = 13 / 18 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R325
