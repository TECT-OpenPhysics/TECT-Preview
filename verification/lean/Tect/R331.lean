import Mathlib

namespace Tect.R331

/- Exact rational bookkeeping for the finite split-to-full comparison only. -/
def horizon_time (delta : Rat) (steps : Nat) : Rat :=
  delta * (steps : Rat)

theorem horizon_fixture : horizon_time (1 / 36) 12 = 1 / 3 := by
  norm_num [horizon_time]

theorem step_refinement_fixture :
    horizon_time (1 / 9) 3 = horizon_time (1 / 18) 6 ∧
      horizon_time (1 / 18) 6 = horizon_time (1 / 36) 12 := by
  norm_num [horizon_time]

theorem history_difference_fixture (delta : Rat) (steps : Nat) (right left : Rat) :
    horizon_time delta steps * right - horizon_time delta steps * left =
      horizon_time delta steps * (right - left) := by
  ring

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R331
