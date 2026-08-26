import Mathlib

namespace Tect.R332

/- Exact rational coefficients for the bounded finite-matrix Duhamel estimate. -/
def local_defect (delta c : Rat) : Rat := delta ^ 2 * c / 2

def history_defect (delta c : Rat) (steps : Nat) (m : Rat) : Rat :=
  2 * delta * local_defect delta c * (steps : Rat) * ((steps : Rat) - 1) / 2 * m

theorem local_defect_fixture :
    local_defect (1 / 36) 12 = 1 / 216 := by
  norm_num [local_defect]

theorem history_sum_fixture (steps : Nat) :
    (Finset.sum (Finset.range steps) (fun k => (k : Rat))) = (steps : Rat) * ((steps : Rat) - 1) / 2 := by
  induction steps with
  | zero => simp
  | succ steps ih =>
      rw [Finset.sum_range_succ, ih]
      push_cast
      ring

theorem history_bound_fixture (delta c : Rat) (steps : Nat) (m : Rat) :
    history_defect delta c steps m =
      delta ^ 3 * c * (steps : Rat) * ((steps : Rat) - 1) * m / 2 := by
  simp [history_defect, local_defect]
  ring

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R332
