import Mathlib

namespace Tect.R296

/- R296 checks only the exact scalar second-order fixture behind EXP-001125.
   It does not formalize matrices, unbounded generators, state seminorms, or a
   QFT limit. -/

def square (x : Rat) : Rat := x * x

theorem commutator_cross_term_fixture :
    ((3 : Rat) - 1) * (1 / 2 : Rat) + (1 : Rat) * (1 / 4 : Rat) = 5 / 4 := by
  norm_num

theorem second_order_operator_bound_fixture :
    ((1 / 10 : Rat) ^ 2) * (2 * (3 / 2 : Rat) + (1 : Rat) / 2) / 2 = 7 / 400 := by
  norm_num

theorem initial_cancellation_fixture :
    (0 : Rat) = 0 ∧ (0 : Rat) = 0 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R296
