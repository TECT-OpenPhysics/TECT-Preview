import Mathlib

namespace Tect.R321

/- R321 checks only the exact rational bookkeeping for EXP-001151.  It does
   not formalize the nonnegative recurrence hypothesis, commutator response,
   finite-volume dynamics, or a thermodynamic limit. -/

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem spatial_penalty_fixture :
    (1 : Rat) / (2 ^ 10) = 1 / 1024 := by
  norm_num

theorem six_step_response_fixture :
    ((31 / 18 : Rat) ^ 6) / (2 ^ 10) = 887503681 / 34828517376 := by
  norm_num

theorem cauchy_coefficient_fixture :
    (2 * (1 / 3 : Rat)) * (((31 / 18 : Rat) ^ 6) / (2 ^ 10)) =
      887503681 / 52242776064 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R321
