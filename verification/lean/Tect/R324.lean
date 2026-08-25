import Mathlib

namespace Tect.R324

/- R324 checks exact rational four-context accounting and the conditional
   recurrence coefficient for EXP-001154.  It does not formalize the actual
   Q3 recurrence, commutator decay, operator domains or thermodynamic limits. -/

theorem adjoint_invariance_fixture :
    ((1 / 4 : Rat)^4 + (-1 / 3 : Rat)^4) =
      ((-1 / 4 : Rat)^4 + (1 / 3 : Rat)^4) ∧
    (abs (1 / 4 : Rat) + abs (-1 / 3 : Rat)) =
      (abs (-1 / 4 : Rat) + abs (1 / 3 : Rat)) := by
  norm_num

theorem four_context_sum_fixture :
    4 * (83497217154884689002533 / 43535646720 : Rat) =
      83497217154884689002533 / 10883911680 := by
  norm_num

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem response_fixture :
    (31 / 18 : Rat)^6 * (1 / 2 : Rat)^10 =
      887503681 / 34828517376 := by
  norm_num

theorem four_context_cauchy_fixture :
    4 * (1 / 3 : Rat) * (887503681 / 34828517376 : Rat) =
      887503681 / 26121388032 := by
  norm_num

theorem product_cost_fixture :
    2 * (2 : Rat)^2 + (7 / 2 : Rat)^2 = 81 / 4 ∧
      21 * (81 / 4 : Rat) = 1701 / 4 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R324
