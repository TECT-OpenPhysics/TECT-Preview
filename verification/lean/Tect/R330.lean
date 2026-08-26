import Mathlib

namespace Tect.R330

/- Exact rational bookkeeping for the finite split-history carrier only. -/
def volterra (delta : Rat) (steps : Nat) (value : Rat) : Rat :=
  delta * (steps : Rat) * value

theorem time_horizon_fixture : (6 : Rat) * (1 / 18) = 1 / 3 := by
  norm_num

theorem volterra_difference_fixture (delta : Rat) (steps : Nat) (right left : Rat) :
    volterra delta steps right - volterra delta steps left =
      volterra delta steps (right - left) := by
  simp [volterra]
  ring

theorem triangle_fixture (x y : Rat) : x - y ≤ |x| + |y| := by
  nlinarith [le_abs_self x, le_abs_self y, neg_le_abs x, neg_le_abs y]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R330
